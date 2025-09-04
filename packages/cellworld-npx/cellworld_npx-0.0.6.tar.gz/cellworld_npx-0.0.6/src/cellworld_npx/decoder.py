import numpy as np
import statsmodels.api as sm
from scipy.spatial.distance import squareform, pdist, cdist
from scipy.special import factorial
from scipy.stats import norm
from tqdm import tqdm
import pandas as pd
import math


class BayesDecoder(object):

    def __init__(self, encoding_model='quadratic', bins=50):
        self.encoding_model = encoding_model
        self.bins = bins
        return
    
    def fit(self, X_b_train, y_train):
        # format input bins
        if type(self.bins) is int:
            input_x_range = np.linspace(0, 1, self.bins)
            input_y_range = np.linspace(0, 1, self.bins)
        else:
            input_x_range = self.bins
            input_y_range = self.bins
        input_mat = np.meshgrid(input_x_range, input_y_range)
        xs=np.reshape(input_mat[0],[input_x_range.shape[0]*input_y_range.shape[0],1])
        ys=np.reshape(input_mat[1],[input_x_range.shape[0]*input_y_range.shape[0],1])
        input_xy=np.concatenate((xs,ys),axis=1)

        # setup interaction covariates for x and y
        if self.encoding_model=='quadratic':
            input_xy_modified=np.empty([input_xy.shape[0],5])
            input_xy_modified[:,0]=input_xy[:,0]**2
            input_xy_modified[:,1]=input_xy[:,0]
            input_xy_modified[:,2]=input_xy[:,1]**2
            input_xy_modified[:,3]=input_xy[:,1]
            input_xy_modified[:,4]=input_xy[:,0]*input_xy[:,1]
            y_train_modified=np.empty([y_train.shape[0],5])
            y_train_modified[:,0]=y_train[:,0]**2
            y_train_modified[:,1]=y_train[:,0]
            y_train_modified[:,2]=y_train[:,1]**2
            y_train_modified[:,3]=y_train[:,1]
            y_train_modified[:,4]=y_train[:,0]*y_train[:,1]

        # fit tuning curves for each neuron
        n = X_b_train.shape[1]
        tuning_all = np.zeros([n,input_xy.shape[0]])
        for j in range(n):
            #print(j, np.sum(X_b_train[:,j:j+1]))
            if self.encoding_model == 'linear':
                tuning = glm_run(y_train, X_b_train[:,j:j+1], input_xy)
            if self.encoding_model == 'quadratic':
                tuning = glm_run(y_train_modified, X_b_train[:,j:j+1], input_xy_modified)
            tuning_all[j,:] = np.squeeze(tuning)
        self.tuning_all = tuning_all
        self.input_xy = input_xy

        # get velocity at each bin step to (optionally) use for temporal smoothing of predictions later
        dx = np.sqrt(np.sum(np.diff(y_train, axis=0)**2, axis=1))
        std = np.sqrt(np.mean(dx**2))
        self.std = std

    def predict(self, X_b_test, y_test, return_posterior=False, smooth_constraint=True):

        tuning_all = self.tuning_all  # place fields
        input_xy = self.input_xy      # position bins
        std = self.std                # average "velocity"

        if smooth_constraint:
            # probability distribution based on distance from each bin in the space, scaled by average speed
            dists = squareform(pdist(input_xy), 'euclidean')
            prob_dists = norm.pdf(dists, 0, std)

        # initialize
        loc_idx = np.argmin(cdist(y_test[0:1,:], input_xy))
        y_test_predicted = np.empty([X_b_test.shape[0], 2])
        nt = X_b_test.shape[0]
        posterior = []

        # loop through each time point
        for t in tqdm(range(nt), desc='Reconstructing location...'):
            rs = X_b_test[t,:].astype(int)
            rs[rs > 170] = 170

            # bayes rule
            probs = np.exp(-tuning_all) * tuning_all ** rs[:,np.newaxis] / factorial(rs[:,np.newaxis])
            probs_final = np.prod(probs, axis=0)
            if smooth_constraint:
                probs_final = probs_final * prob_dists[loc_idx,:]
            loc_idx = np.argmax(probs_final)
            y_test_predicted[t,:] = input_xy[loc_idx,:]
            if return_posterior:
                posterior.append(probs_final)
            
        if return_posterior:
            return y_test_predicted, posterior
        else:
            return y_test_predicted  


#GLM helper function for the NaiveBayesDecoder
def glm_run(Xr, Yr, X_range):

    X2 = sm.add_constant(Xr)

    poiss_model = sm.GLM(Yr, X2, family=sm.families.Poisson())
    try:
        glm_results = poiss_model.fit()
        #glm_results = poiss_model.fit_regularized(alpha=0.1, L1_wt=0) # regularization does not work well here
        Y_range=glm_results.predict(sm.add_constant(X_range))
    except np.linalg.LinAlgError:
        print("\nWARNING: LinAlgError")
        Y_range=np.mean(Yr)*np.ones([X_range.shape[0],1])
    except ValueError:
        print("\nWARNING: ValueError")
        Y_range=np.mean(Yr)*np.ones([X_range.shape[0],1])

    return Y_range

def process_bins(binned_data, splits=list(), bins_before=5, bins_current=1, bins_after=4):        
    if not splits:
        splits = [range(0,len(df))]

    assert bins_current == 1, f'bins_current must be 1'      
    bins_before, bins_current, bins_after = int(bins_before), int(bins_current), int(bins_after)

    output = []
    if (bins_before == 0) & (bins_current == 1) & (bins_after == 0):
        for s in splits:
            output.append(binned_data.iloc[s])
        return output
    
    else:
        N = bins_before + bins_current + bins_after
        for s in splits:
            # bin neural data (sum spikes per history window)
            X = np.vstack(binned_data.iloc[s].neural_data)
            m = X.shape[1]
            X_b = []
            for i in range(m):
                X_b.append(N*np.convolve(X[:,i], np.ones((N,))/N, mode='valid'))
            X_b = np.vstack(X_b).T.tolist()

            # align non-neural data according to history window
            df = binned_data.iloc[s]
            new_df = pd.DataFrame()
            new_df['neural_data'] = X_b
            cols = [c for c in binned_data.columns.to_list() if 'neural_data' not in c]
            for c in cols:
                y = np.array(df[c].values)
                if len(y.shape) == 1:
                    y = y[:,np.newaxis]
                if bins_before > 0 and bins_after > 0:
                    y = y[bins_before:-bins_after,:]
                if bins_before > 0 and bins_after == 0:
                    y = y[bins_before:,:]
                new_df[c] = y.tolist()
            output.append(new_df)
        return output