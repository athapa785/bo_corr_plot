import numpy as np

# Define the objective function to be optimized
def objective_function(x):
    return (x - 0.5)**2 * np.sin(x) + np.cos(2*x) + np.random.normal(0, 5)

# Define the search bounds
bounds = np.array([[-2.0, 10.0]])

# Initial samples
initial_samples = np.array([[-1.0], [3.0]])