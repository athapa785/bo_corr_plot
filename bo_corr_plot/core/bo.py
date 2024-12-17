import numpy as np
from scipy.optimize import minimize

def propose_location(acquisition, X_sample, Y_sample, gpr, bounds, n_restarts=25):
    dim = X_sample.shape[1]
    max_val = -1
    max_x = None
    
    def max_obj(X):
        return -acquisition(X.reshape(-1, dim), X_sample, Y_sample, gpr)
    
    for x0 in np.random.uniform(bounds[:, 0], bounds[:, 1], size=(n_restarts, dim)):
        res = minimize(max_obj, x0=x0, bounds=bounds, method='L-BFGS-B')
        if res.fun < max_val or max_x is None:
            max_val = res.fun
            max_x = res.x
            
    return max_x.reshape(-1, 1)