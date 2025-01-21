# bo_corr_plot/core/process.py

import numpy as np
from PyQt5.QtCore import QTimer

from ..gui.ui import MainWindow
from ..epics.epics_interface import get_objective_value
from ..data.mock_data import objective_function

# BoTorch / GPyTorch imports
import torch
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_model
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition.analytic import ExpectedImprovement, UpperConfidenceBound
from botorch.optim import optimize_acqf

# We use propose_location_botorch from bo.py
from .bo import propose_location_botorch


class BOController:
    def __init__(self):
        self.window = MainWindow(self.start_optimization, self.abort_optimization)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_iteration)

    def start_optimization(self, n_iter, acquisition_function, window,
                           exploration_param, input_pv, objective_pv, wait_time):
        """
        Called when the user clicks "Run Optimization."
        """
        self.n_iter = n_iter
        self.current_iter = 0
        self.acquisition_function = acquisition_function  # "ei" or "ucb"
        self.window = window
        self.exploration_param = exploration_param
        self.input_pv = input_pv.strip()
        self.objective_pv = objective_pv.strip()
        self.wait_time = wait_time

        # Determine if we use mock data or real EPICS
        use_mock_data = not self.input_pv or not self.objective_pv
        if use_mock_data:
            print("Input PV or Objective PV not provided. Using mock data.")
            self.window.update_message("Warning: Missing PVs. Using mock data.")
        else:
            print(f"Using Input PV: {self.input_pv}, Objective PV: {self.objective_pv}")

        # Dynamically set range from the widget (this might come from the PV or default)
        if use_mock_data:
            self.window.param_widget.set_default_range()
        else:
            self.window.param_widget.set_range_from_pv(self.input_pv)

        # Bounds
        min_range, max_range = self.window.param_widget.get_range()
        print(f"Starting optimization with range: Min = {min_range}, Max = {max_range}")
        self.bounds = np.array([[min_range, max_range]])

        # Generate initial samples (Latin Hypercube)
        X_initial = self.window.param_widget.get_initial_samples(n_samples=5)  # 5 initial points
        Y_initial = []
        for x_val in X_initial:
            # Evaluate objective (EPICS or mock)
            if use_mock_data:
                y_val = objective_function(x_val[0])
            else:
                y_val = get_objective_value(x_val[0], self.input_pv, self.objective_pv, self.wait_time)
            Y_initial.append([y_val])

        self.X_samples = X_initial  # shape (n_init, 1)
        self.Y_samples = np.array(Y_initial)  # shape (n_init, 1)

        # Create a 1D evaluation grid for plotting
        self.X_eval_np = np.linspace(min_range, max_range, 1000).reshape(-1, 1)
        self.X_eval_torch = torch.tensor(self.X_eval_np, dtype=torch.float)

        # Convert existing data to torch Tensors
        self.X_samples_torch = torch.tensor(self.X_samples, dtype=torch.float)
        self.Y_samples_torch = torch.tensor(self.Y_samples, dtype=torch.float)

        # Display status
        self.window.update_message("Starting optimization...")

        # Do an initial “BoTorch” style plot with the current data 
        # (We do not have a fitted model yet, but we can do a quick fit here to plot)
        self.fit_botorch_model()  # Fit once so we can show an initial GP
        self.window.plot_widget.update_plot_botorch(
            self.model,
            self.X_eval_np,
            self.X_eval_torch,
            self.X_samples,
            self.Y_samples,
            iteration=self.current_iter,
            acquisition_function=self.acquisition_function,
            exploration_param=self.exploration_param
        )

        # Start timer: each tick => run_iteration()
        self.timer.start(1000)  # 1 second per iteration

    def abort_optimization(self):
        """
        Abort the optimization process.
        """
        self.timer.stop()
        self.window.update_message("Optimization aborted.")

    def run_iteration(self):
        """
        Called each second by self.timer, runs one BO iteration until we hit self.n_iter.
        """
        if self.current_iter < self.n_iter:
            self.window.update_message(f"Running iteration {self.current_iter + 1}...")

            # 1) Fit the BoTorch model to the current data
            self.fit_botorch_model()

            # 2) Build the acquisition function
            acq_fn = self.get_acquisition_function()

            # 3) Propose a new sample
            X_next_torch = propose_location_botorch(self, acq_fn)
            X_next = X_next_torch.numpy()
            x_val = float(X_next[0, 0])

            # 4) Evaluate the objective at x_val
            y_val = get_objective_value(x_val, self.input_pv, self.objective_pv, self.wait_time)

            # 5) Update data (both np and torch)
            self.X_samples = np.vstack((self.X_samples, [[x_val]]))
            self.Y_samples = np.vstack((self.Y_samples, [[y_val]]))
            self.X_samples_torch = torch.tensor(self.X_samples, dtype=torch.float)
            self.Y_samples_torch = torch.tensor(self.Y_samples, dtype=torch.float)

            # 6) Find the best sampled point so far
            best_idx = np.argmax(self.Y_samples)
            best_value = self.Y_samples[best_idx][0]
            best_x = self.X_samples[best_idx][0]

            # 7) Find the best predicted point from the model’s mean on a 1D grid
            self.model.eval()
            with torch.no_grad():
                posterior = self.model(self.X_eval_torch)
                mean = posterior.mean.squeeze(-1).numpy()  # shape (1000,)
            best_pred_idx = np.argmax(mean)
            best_pred_val = mean[best_pred_idx]
            best_pred_x = self.X_eval_np[best_pred_idx][0]

            # 8) Update the GUI labels
            self.window.update_labels(
                x_val, best_value, best_x, best_pred_val, best_pred_x
            )

            # 9) Re-plot with updated data
            self.window.plot_widget.update_plot_botorch(
                self.model,
                self.X_eval_np,
                self.X_eval_torch,
                self.X_samples,
                self.Y_samples,
                iteration=self.current_iter + 1,
                acquisition_function=self.acquisition_function,
                exploration_param=self.exploration_param
            )

            self.current_iter += 1

        else:
            self.timer.stop()
            self.window.update_message("Optimization complete!")

    def fit_botorch_model(self):
        """
        Build a SingleTaskGP from current data and fit it with MLL.
        """
        self.model = SingleTaskGP(self.X_samples_torch, self.Y_samples_torch)
        mll = ExactMarginalLogLikelihood(self.model.likelihood, self.model)
        fit_gpytorch_model(mll)

    def get_acquisition_function(self):
        """
        Return a BoTorch acquisition function (EI or UCB).
        """
        if self.acquisition_function == "ei":
            # best_f = best observed so far
            best_f = self.Y_samples_torch.max().item()
            acq_fn = ExpectedImprovement(self.model, best_f=best_f)
        else:
            # UCB with 'beta' ~ exploration_param
            acq_fn = UpperConfidenceBound(self.model, beta=self.exploration_param)
        return acq_fn