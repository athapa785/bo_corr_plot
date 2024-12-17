from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
import numpy as np


class ParameterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # Min and Max range fields
        self.min_range_edit = QLineEdit("-2.0")
        self.max_range_edit = QLineEdit("10.0")

        layout.addWidget(QLabel("Min Range:"))
        layout.addWidget(self.min_range_edit)
        layout.addWidget(QLabel("Max Range:"))
        layout.addWidget(self.max_range_edit)

        self.setLayout(layout)

    def get_range(self):
        """
        Get the current range for the parameter.
        """
        try:
            min_val = float(self.min_range_edit.text())
            max_val = float(self.max_range_edit.text())
            return min_val, max_val
        except ValueError:
            return -2.0, 10.0

    def set_range(self, min_range, max_range):
        """
        Set the range for the parameter.
        """
        self.min_range_edit.setText(f"{min_range:.4f}")
        self.max_range_edit.setText(f"{max_range:.4f}")

    def set_default_range(self):
        """
        Set the default range for the parameter.
        """
        self.set_range(-2.0, 10.0)

    def set_range_from_pv(self, input_pv):
        """
        Dynamically set the range based on the input PV.
        """
        initial_value = 0.0  # Replace with actual PV reading logic if available
        min_range = initial_value * 0.93
        max_range = initial_value * 1.07
        self.set_range(min_range, max_range)

    def get_initial_samples(self):
        """
        Generate initial samples based on the current range.
        """
        min_range, max_range = self.get_range()
        return np.array([[min_range], [max_range]])