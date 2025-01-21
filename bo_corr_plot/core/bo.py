# bo_corr_plot/core/bo.py
import torch
from botorch.optim import optimize_acqf

def propose_location_botorch(self, acq_fn):
    """
    Return the next best location to sample using BoTorch's optimize_acqf.
    `self` is the BOController instance.
    """
    bounds_torch = torch.tensor(self.bounds, dtype=torch.float).T  # shape: (2,1)
    candidate, _ = optimize_acqf(
        acq_function=acq_fn,
        bounds=bounds_torch,
        q=1,
        num_restarts=10,
        raw_samples=50,
    )
    return candidate.detach()