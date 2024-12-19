import numpy as np
from PyQt5.QtCore import QTimer

from .gui.ui import MainWindow
from .core.acquisition import expected_improvement, upper_confidence_bound
from .core.bo import propose_location
from .epics.epics_interface import get_objective_value
from .data.mock_data import objective_function

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel


class BOController:
    def __init__(self):
        self.window = MainWindow(self.start_optimization)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_iteration)

    def start_optimization(self, n_iter, acquisition_function, window, exploration_param, input_pv, objective_pv, wait_time):
        self.n_iter = n_iter
        self.current_iter = 0
        self.acquisition_function = acquisition_function
        self.window = window
        self.exploration_param = exploration_param
        self.input_pv = input_pv.strip()
        self.objective_pv = objective_pv.strip()
        self.wait_time = wait_time

        # Check if EPICS PVs are available
        use_mock_data = not self.input_pv or not self.objective_pv
        if use_mock_data:
            print("Input PV or Objective PV not provided. Using mock data.")
            self.window.update_message("Warning: Missing PVs. Using mock data.")
        else:
            print(f"Using Input PV: {self.input_pv}, Objective PV: {self.objective_pv}")

        # Dynamically set range based on Input PV or fallback to default
        if use_mock_data:
            self.window.param_widget.set_default_range()
        else:
            self.window.param_widget.set_range_from_pv(self.input_pv)

        # Fetch range
        min_range, max_range = self.window.param_widget.get_range()
        self.bounds = np.array([[min_range, max_range]])

        # Initialize the GP and data
        self.kernel = (
            ConstantKernel(1.0, (1e-2, 1e2)) *
            Matern(length_scale=1.0, length_scale_bounds=(1e-2, 1e2), nu=2.5) +
            WhiteKernel(noise_level=1e0, noise_level_bounds=(1e-4, 1e1))
        )
        self.gpr = GaussianProcessRegressor(kernel=self.kernel, alpha=1e-4)

        # Initial samples
        X_initial = self.window.param_widget.get_initial_samples()
        Y_initial = []
        for x_val in X_initial:
            y_val = get_objective_value(x_val[0], self.input_pv, self.objective_pv, self.wait_time) if not use_mock_data else objective_function(x_val[0])
            Y_initial.append([y_val])

        self.X_samples = X_initial
        self.Y_samples = np.array(Y_initial)

        self.X = np.linspace(min_range, max_range, 1000).reshape(-1, 1)

        self.window.update_message("Starting optimization...")

        # Initial plot update
        self.window.plot_widget.update_plot(
            self.gpr,
            self.X,
            self.X_samples,
            self.Y_samples,
            self.current_iter,
            self.acquisition_function,
            self.exploration_param
        )

        self.timer.start(1000)  # 1 second delay per iteration

    def run_iteration(self):
        if self.current_iter < self.n_iter:
            self.window.update_message(f"Running iteration {self.current_iter + 1}...")

            # Fit GP
            self.gpr.fit(self.X_samples, self.Y_samples)

            # Adjust acquisition function for exploration vs. exploitation
            if self.acquisition_function == 'ei':
                acq_func = lambda X, Xs, Ys, g: expected_improvement(X, Xs, Ys, g, xi=self.exploration_param)
            else:
                acq_func = lambda X, Xs, Ys, g: upper_confidence_bound(X, Xs, Ys, g, kappa=self.exploration_param)

            # Propose new sample
            X_next = propose_location(acq_func, self.X_samples, self.Y_samples, self.gpr, self.bounds)
            Y_next_val = get_objective_value(X_next[0, 0], self.input_pv, self.objective_pv, self.wait_time)
            Y_next = np.array([[Y_next_val]])

            self.X_samples = np.vstack((self.X_samples, X_next))
            self.Y_samples = np.vstack((self.Y_samples, Y_next))

            # Calculate sampled and predicted best
            best_idx = np.argmax(self.Y_samples)
            best_value = self.Y_samples[best_idx][0]
            best_x = self.X_samples[best_idx][0]

            Y_pred, _ = self.gpr.predict(self.X, return_std=True)
            best_pred_idx = np.argmax(Y_pred)
            best_pred_val = Y_pred[best_pred_idx]
            best_pred_x = self.X[best_pred_idx][0]

            # Update labels
            self.window.update_labels(X_next[-1][0], best_value, best_x, best_pred_val, best_pred_x)

            # Update plot
            self.window.plot_widget.update_plot(
                self.gpr,
                self.X,
                self.X_samples,
                self.Y_samples,
                self.current_iter + 1,
                self.acquisition_function,
                self.exploration_param
            )

            self.current_iter += 1
        else:
            # All iterations done
            self.timer.stop()
            self.window.update_message("Optimization complete!")
