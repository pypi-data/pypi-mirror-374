import cv2
import numpy as np
from json_cpp import JsonObject, JsonList
from cellworld import World
from tqdm import tqdm

class Cameras(JsonList):
    def __init__(self):
        super().__init__(list_type=Camera)


class Camera(JsonObject):
    def __init__(self, name=str(), root=str(), 
                 roi=(224,351,10,14), 
                 corner_pixels=[(403, 199), (408, 294), (189, 292), (189, 201)],
                 homography_pixels=[(404, 198), (405, 289), (190, 290), (192, 199), (258, 34), (338, 34)],
                 homography_method='perspective'):
        self.name = name
        self.root = root
        self.fps = float()
        self.frame_count = int()
        self.width = int()
        self.height = int()
        self.roi = roi
        self.corner_pixels = corner_pixels
        self.homography_pixels = homography_pixels
        self.homography_method = homography_method
        self.get_capture_properties()
        self.get_canonical_transform()

    def select_roi(self):
        cap = cv2.VideoCapture(self.root)
        ret, frame = cap.read()
        print("Please select the ROI by dragging a box.")
        self.roi = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select ROI")  # Close the ROI selection window
        cap.release()

    def select_corners(self):
        cap = cv2.VideoCapture(self.root)
        ret, frame = cap.read()
        selected_points = []

        def select_point(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and len(selected_points) < 4:
                selected_points.append((x, y))
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow("Select 4 Points", frame)

        cv2.namedWindow("Select 4 Points")
        cv2.setMouseCallback("Select 4 Points", select_point)

        while True:
            cv2.imshow("Select 4 Points", frame)
            key = cv2.waitKey(1) & 0xFF
            if len(selected_points) == 4:
                break
            if key == 27:  # Esc to quit early
                break

        cv2.destroyAllWindows()
        cap.release()
        self.corner_pixels = selected_points
        return selected_points
    
    def select_homography(self):
        cap = cv2.VideoCapture(self.root)
        for i in range(10):
            ret, frame = cap.read()
        selected_points = []
        calibration_labels = ['Box Upper Right', 'Box Lower Right', 'Box Lower Left', 'Box Upper Left', 'Box Left Nut', 'Box Right Nut']

        def select_point(event, x, y, flags, param):
            global selected_point
            if event == cv2.EVENT_LBUTTONDOWN and len(selected_points) < 6:
                selected_points.append((x, y))
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow("Select 6 Points", frame)

        cv2.namedWindow("Select 6 Points")
        cv2.setMouseCallback("Select 6 Points", select_point)

        print(f'Select points in the following order:')
        for i,l in enumerate(calibration_labels):
            print(f'\t{i}) {l}')
        while True:
            cv2.imshow("Select 6 Points", frame)
            key = cv2.waitKey(1) & 0xFF
            if len(selected_points) == 6:
                break
            if key == 27:  # Esc to quit early
                break

        cv2.destroyAllWindows()
        cap.release()
        self.homography_pixels = selected_points
        return selected_points
    
    def get_canonical_transform(self):
        if 'perspective' in self.homography_method:
            pixel_coordinates = np.array(self.corner_pixels, dtype='float32')
            canonical_coordinates = np.array(get_entry_box_coordinates(), dtype='float32')
            self.transform = cv2.getPerspectiveTransform(pixel_coordinates, canonical_coordinates)
        else:
            pixel_coordinates = np.array(self.homography_pixels, dtype='float32')
            canonical_coordinates = np.array(get_entry_box_coordinates() + get_start_cell_coordinates(), dtype='float32')
            self.transform, _ = cv2.findHomography(pixel_coordinates, canonical_coordinates, method=cv2.RANSAC)

    def get_capture_properties(self):
        cap = cv2.VideoCapture(self.root)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

    def apply_transform(self, points):
        assert hasattr(self, 'transform'), f'Camera must have a transform to apply a transform'
        return pixels_to_canonical(points, self.transform)

def pixels_to_canonical(points, transform, method='perspective'):
    assert points.shape[1] == 2, 'second dimension of points must be len 2'
    points = points.astype('float32')[:,np.newaxis,:]
    canonical_points = cv2.perspectiveTransform(points, transform).squeeze()
    canonical_points[np.all(canonical_points == 0, axis=1)] = np.nan
    return canonical_points


def get_entry_box_coordinates(cell_to_door=0.075384, box_depth=0.0635, box_width = 0.1524, canonical_to_meters=2.34):
    # w = World.get_from_parameters_names('hexagonal', 'canonical', '00_00')
    radius = 0.0271 # radius = w.implementation.cell_transformation.size / 2
    x_location = 0.03125 # x_location = w.cells[0].location.x
    cell_width = radius * np.cos(np.deg2rad(30))
    habitat_edge = x_location - cell_width
    cell_to_door = cell_to_door / canonical_to_meters
    box_depth = box_depth / canonical_to_meters
    box_width = box_width / canonical_to_meters
    box_coordinates = [
        [habitat_edge - cell_to_door, 0.5 - box_width/2],
        [habitat_edge - cell_to_door - box_depth, 0.5 - box_width/2],
        [habitat_edge - cell_to_door - box_depth, 0.5 + box_width/2],
        [habitat_edge - cell_to_door, 0.5 + box_width/2],
    ]
    return box_coordinates

def get_start_cell_coordinates(nut_separation=0.06, canonical_to_meters=2.34):
    x_location = 0.03125
    y_location = 0.5
    offset = nut_separation / 2 / canonical_to_meters
    return [[x_location, y_location+offset], [x_location, y_location-offset]]



def get_roi_intensity(filename, ROI=(224,351,10,14), progress_bar=True, background_roi=(343,343,94,26)):
    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if progress_bar:
        pbar = tqdm(total=length, desc='loading entrance video')
    values = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        led = frame[ROI[1]:(ROI[1]+ROI[3]),ROI[0]:(ROI[0]+ROI[2]+1),1]
        background = frame[background_roi[1]:(background_roi[1]+background_roi[3]),
                           background_roi[0]:(background_roi[0]+background_roi[2]+1),1]
        values.append(np.mean(led) - np.mean(background))
        if progress_bar:
            pbar.update(1)

    cap.release()
    return values, fps