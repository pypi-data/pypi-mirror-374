from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(name='cellworld_npx',
      description='Dombeck/MacIver labs neuroethology analysis package - combined cellworld behavior and neuropixels recordings',
      author='Chris Angeloni',
      author_email='chris.angeloni@gmail.com',
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      install_requires=['numpy', 
                        'scipy', 
                        'matplotlib', 
                        'json-cpp', 
                        'cellworld', 
                        'npyx', 
                        'pandas', 
                        'astropy', 
                        'rtree', 
                        'kilosort', 
                        'torch', 
                        'filterpy', 
                        'opencv-python', 
                        'tables'],
      extras_require={'kilosort': 'kilosort'},
      license='MIT',
      version='0.0.6',
      zip_safe=False)
