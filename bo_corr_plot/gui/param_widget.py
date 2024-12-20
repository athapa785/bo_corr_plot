from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import epics
from scipy.stats.qmc import LatinHypercube


class ParameterWidget(QObject):
    range_updated = pyqtSignal()  # Signal to notify range updates

    DEFAULT_MIN = -2.0
    DEFAULT_MAX = 10.0
    DEFAULT_PERCENTAGE = 7.0  # Default percentage for dynamic range adjustment

    def __init__(self, min_range_edit, max_range_edit, percentage_spinbox):
        """
        Initialize ParameterWidget with references to the UI components.
        """
        super().__init__()
        self.min_range_edit = min_range_edit
        self.max_range_edit = max_range_edit
        self.percentage_spinbox = percentage_spinbox

        # Track if the user manually updates the range
        self.user_modified_range = False

        # Connect signals to monitor user input
        self.min_range_edit.textChanged.connect(self.on_range_field_changed)
        self.max_range_edit.textChanged.connect(self.on_range_field_changed)

    def set_default_range(self):
        """
        Set the range to default values.
        """
        self.set_range(self.DEFAULT_MIN, self.DEFAULT_MAX)

    def set_range(self, min_range, max_range):
        """
        Set the range values in the UI fields.
        """
        self.min_range_edit.setText(f"{min_range:.4f}")
        self.max_range_edit.setText(f"{max_range:.4f}")

    def get_range(self):
        """
        Retrieve the current range from the UI fields. 
        Prioritize user input over auto-populated values.
        """
        try:
            min_val = float(self.min_range_edit.text())
            max_val = float(self.max_range_edit.text())
            if min_val < max_val:
                return min_val, max_val
            else:
                raise ValueError("Min range must be less than max range.")
        except ValueError:
            return self.DEFAULT_MIN, self.DEFAULT_MAX

    def set_range_from_pv(self, input_pv, percentage=None):
        """
        Dynamically adjust the range based on the initial value of the Input PV.
        If the PV is unavailable, fallback to default range.
        """
        if self.user_modified_range:
            # If the user modified the range, do not overwrite it
            return

        try:
            initial_value = epics.caget(input_pv)
            if initial_value is None:
                raise ValueError("Input PV could not be read.")

            # Calculate dynamic range
            percentage = percentage or self.DEFAULT_PERCENTAGE
            min_range = initial_value * (1.0 - percentage / 100.0)
            max_range = initial_value * (1.0 + percentage / 100.0)
            self.set_range(min_range, max_range)

        except Exception as e:
            print(f"Error reading PV or setting range: {e}")
            self.set_default_range()

    def on_range_field_changed(self):
        """
        Mark that the user has manually updated the range fields.
        Disable the percentage spinbox to avoid conflicts.
        """
        self.user_modified_range = True
        self.percentage_spinbox.setEnabled(False)
        self.range_updated.emit()  # Notify that the range was updated

    def get_initial_samples(self, n_samples=5):
        """
        Generate Latin Hypercube samples within the range.
        """
        min_range, max_range = self.get_range()
        sampler = LatinHypercube(d=1)
        scaled_samples = sampler.random(n_samples) * (max_range - min_range) + min_range
        return scaled_samples.reshape(-1, 1)