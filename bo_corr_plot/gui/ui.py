from PyQt5.QtWidgets import QWidget
from epics import caget, caput  # Import epics for PV handling
from .dialogs import InfoDialog
from .components import create_main_layout

class MainWindow(QWidget):
    def __init__(self, start_callback, abort_callback):
        super().__init__()
        self.start_callback = start_callback
        self.abort_callback = abort_callback
        self.initUI()
        self.best_x = None
        self.best_pred_x = None
        self.initial_input_value = None

    def initUI(self):
        main_layout = create_main_layout(self)
        self.setLayout(main_layout)
        self.setWindowTitle("Bae: A Bayesian Optimization GUI")

    def update_fields_from_pv(self):
        """
        Update the Initial Value, Min Range, and Max Range fields based on the Input PV.
        """
        input_pv = self.input_pv_edit.text().strip()
        if input_pv:
            initial_value = caget(input_pv)
            if initial_value is not None:
                self.initial_value_edit.setText(f"{initial_value:.4f}")
                self.initial_input_value = initial_value  # Store the initial value
                percentage = self.percentage_spinbox.value() / 100.0
                min_range = initial_value * (1.0 - percentage)
                max_range = initial_value * (1.0 + percentage)
                self.param_widget.set_range(min_range, max_range)
            else:
                self.update_message(f"Error: Could not read Input PV '{input_pv}'")
        else:
            self.initial_value_edit.clear()
            self.param_widget.set_range(None, None)

    def abort_clicked(self):
        """
        Abort the optimization process and reset the Input PV to its initial value.
        """
        if self.abort_callback:
            self.abort_callback()
        if self.initial_input_value is not None:
            input_pv = self.input_pv_edit.text().strip()
            caput(input_pv, self.initial_input_value)
            self.update_message("Optimization aborted and input PV reset to its initial value.")

    def update_param_range(self):
        """
        Update the parameter range based on the initial value and percentage spinbox.
        """
        try:
            initial_value = float(self.initial_value_edit.text())
            percentage = self.percentage_spinbox.value() / 100.0
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