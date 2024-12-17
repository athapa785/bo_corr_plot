import time
from epics import caget, caput
import numpy as np
from ..data.mock_data import objective_function


def get_objective_value(x_value, input_pv, objective_pv, wait_time=3.0):
    """
    Reads the objective value from the EPICS PVs or falls back to mock data.
    """
    y_value = None
    if input_pv and objective_pv:
        try:
            caput(input_pv, x_value)  # Set input PV
            time.sleep(wait_time)  # Wait for the system to stabilize
            y_value = caget(objective_pv)  # Read objective PV

            if y_value is None or np.isnan(y_value):
                print(f"EPICS failed to read {objective_pv}. Falling back to mock data.")
                y_value = objective_function(x_value)
            else:
                print(f"Using EPICS PV. X: {x_value}, Y: {y_value}")
        except Exception as e:
            print(f"EPICS exception: {e}. Falling back to mock data.")
            y_value = objective_function(x_value)
    else:
        print(f"Input or Objective PV not provided. Falling back to mock data. X: {x_value}")
        y_value = objective_function(x_value)

    return y_value