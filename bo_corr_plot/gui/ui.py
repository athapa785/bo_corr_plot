from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

from .dialogs import InfoDialog
from .param_widget import ParameterWidget
from .pyqtgraph_widget import PyQtGraphWidget


class MainWindow(QWidget):
    def __init__(self, start_callback):
        super().__init__()
        self.start_callback = start_callback
        self.initUI()
        self.best_x = None
        self.best_pred_x = None

    def initUI(self):
        main_layout = QVBoxLayout()

        # First Line: Input and Objective PVs
        pv_layout = QHBoxLayout()
        input_pv_label = QLabel("Input PV:")
        self.input_pv_edit = QLineEdit("")
        pv_layout.addWidget(input_pv_label)
        pv_layout.addWidget(self.input_pv_edit)

        objective_pv_label = QLabel("Objective PV:")
        self.objective_pv_edit = QLineEdit("")
        pv_layout.addWidget(objective_pv_label)
        pv_layout.addWidget(self.objective_pv_edit)
        main_layout.addLayout(pv_layout)

        # Second Line: Initial value, Min, Max, %, Wait Time
        control_layout = QHBoxLayout()

        initial_value_label = QLabel("Initial Value:")
        self.initial_value_edit = QLineEdit("0.0")
        control_layout.addWidget(initial_value_label)
        control_layout.addWidget(self.initial_value_edit)

        self.param_widget = ParameterWidget()  # Handles Min and Max range
        control_layout.addWidget(self.param_widget)

        percentage_label = QLabel("±%:")
        self.percentage_spin = QDoubleSpinBox()
        self.percentage_spin.setRange(0.0, 100.0)
        self.percentage_spin.setValue(7.0)  # Default to 7%
        self.percentage_spin.setSingleStep(1.0)
        self.percentage_spin.valueChanged.connect(self.update_param_range)
        control_layout.addWidget(percentage_label)
        control_layout.addWidget(self.percentage_spin)

        wait_label = QLabel("Wait Time (s):")
        self.wait_spin = QDoubleSpinBox()
        self.wait_spin.setRange(0.0, 100.0)
        self.wait_spin.setValue(3.0)
        self.wait_spin.setSingleStep(0.5)
        control_layout.addWidget(wait_label)
        control_layout.addWidget(self.wait_spin)

        main_layout.addLayout(control_layout)

        # Third Line: Number of iterations, Acquisition function, and Exploration Param
        settings_layout = QHBoxLayout()

        iter_label = QLabel("Number of Iterations:")
        self.iter_edit = QLineEdit("25")
        settings_layout.addWidget(iter_label)
        settings_layout.addWidget(self.iter_edit)

        acq_label = QLabel("Acquisition Function:")
        self.acq_combo = QComboBox()
        self.acq_combo.addItems(["EI", "UCB"])
        settings_layout.addWidget(acq_label)
        settings_layout.addWidget(self.acq_combo)

        expl_label = QLabel("Exploration Param (kappa or xi):")
        self.expl_spin = QDoubleSpinBox()
        self.expl_spin.setRange(0.0, 10.0)
        self.expl_spin.setValue(0.01)
        self.expl_spin.setSingleStep(0.01)
        settings_layout.addWidget(expl_label)
        settings_layout.addWidget(self.expl_spin)

        # Info Dialog Button
        help_button = QPushButton("?")
        help_button.setFixedWidth(30)
        help_button.clicked.connect(self.show_info_dialog)
        settings_layout.addWidget(help_button)

        main_layout.addLayout(settings_layout)

        # Optimization Status and Set Buttons
        status_layout = QHBoxLayout()

        # Status labels
        self.current_value_label = QLabel("Current Value of Input PV: N/A")
        self.best_value_label = QLabel("Sampled Best Value: N/A at X: N/A")
        self.best_predicted_label = QLabel("Predicted Best Value: N/A at X: N/A")

        # Set parameter buttons
        self.set_param_button = QPushButton("Set Param to Best X")
        self.set_param_button.setEnabled(False)
        self.set_param_button.clicked.connect(self.set_param_to_best_x)

        self.set_pred_param_button = QPushButton("Set Param to Pred. Best X")
        self.set_pred_param_button.setEnabled(False)
        self.set_pred_param_button.clicked.connect(self.set_param_to_best_pred_x)

        # Add labels and buttons to layout
        status_layout.addWidget(self.current_value_label)
        status_layout.addWidget(self.best_value_label)
        status_layout.addWidget(self.best_predicted_label)
        status_layout.addWidget(self.set_param_button)
        status_layout.addWidget(self.set_pred_param_button)

        main_layout.addLayout(status_layout)

        # Run Button
        self.run_button = QPushButton("Run Optimization")
        self.run_button.clicked.connect(self.run_clicked)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        # Plot Widget
        self.plot_widget = PyQtGraphWidget()
        main_layout.addWidget(self.plot_widget)

        # Message Bar
        self.message_label = QLabel("Ready")
        main_layout.addWidget(self.message_label, alignment=Qt.AlignRight)

        self.setLayout(main_layout)
        self.setWindowTitle("Bayesian Optimization GUI")

    def update_param_range(self):
        """
        Update the parameter range based on the initial value and percentage spinbox.
        """
        try:
            initial_value = float(self.initial_value_edit.text())
            percentage = self.percentage_spin.value() / 100.0
            min_range = initial_value * (1.0 - percentage)
            max_range = initial_value * (1.0 + percentage)
            self.param_widget.set_range(min_range, max_range)
        except ValueError:
            pass  # Ignore invalid input

    def run_clicked(self):
        """
        Trigger the optimization process.
        """
        input_pv = self.input_pv_edit.text().strip()
        objective_pv = self.objective_pv_edit.text().strip()
        wait_time = self.wait_spin.value()
        n_iter = int(self.iter_edit.text())
        acquisition = self.acq_combo.currentText().lower()
        exploration_param = self.expl_spin.value()

        self.start_callback(n_iter, acquisition, self, exploration_param, input_pv, objective_pv, wait_time)

    def update_labels(self, current_x, best_value, best_x, best_pred_val, best_pred_x):
        """
        Update the labels for current input PV or X value, best sampled value, and predicted best value.
        """
        self.current_value_label.setText(f"Current Value of Input PV: {current_x:.4f}")
        self.best_value_label.setText(f"Sampled Best Value: {best_value:.4f} at X: {best_x:.4f}")
        self.best_predicted_label.setText(f"Predicted Best Value: {best_pred_val:.4f} at X: {best_pred_x:.4f}")
        self.best_x = best_x
        self.best_pred_x = best_pred_x
        self.set_param_button.setEnabled(True)
        self.set_pred_param_button.setEnabled(True)

    def update_message(self, message):
        """
        Update the status message at the bottom of the GUI.
        """
        self.message_label.setText(message)

    def show_info_dialog(self):
        """
        Show an informational dialog box for acquisition functions.
        """
        dialog = InfoDialog(self)
        dialog.exec_()

    def set_param_to_best_x(self):
        """
        Set the parameter range to be centered around the best sampled X.
        """
        if self.best_x is not None:
            self.param_widget.set_range(self.best_x - 1, self.best_x + 1)

    def set_param_to_best_pred_x(self):
        """
        Set the parameter range to be centered around the predicted best X.
        """
        if self.best_pred_x is not None:
            self.param_widget.set_range(self.best_pred_x - 1, self.best_pred_x + 1)