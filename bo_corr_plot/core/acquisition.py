import numpy as np
from scipy.stats import norm

def expected_improvement(X, X_sample, Y_sample, gpr, xi=0.01):
    mu, sigma = gpr.predict(X, return_std=True)
    mu_sample_opt = np.max(gpr.predict(X_sample))

    with np.errstate(divide='warn'):
        imp = mu - mu_sample_opt - xi
        Z = imp / sigma
        ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
        ei[sigma == 0.0] = 0.0
        
    return ei

def upper_confidence_bound(X, X_sample, Y_sample, gpr, kappa=2.576):
    mu, sigma = gpr.predict(X, return_std=True)
    return mu + kappa * sigma