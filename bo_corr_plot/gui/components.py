from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
from .param_widget import ParameterWidget
from .pyqtgraph_widget import PyQtGraphWidget


def create_main_layout(main_window):
    """
    Create and return the main layout for the application.
    """
    main_layout = QVBoxLayout()

    # First Line: Input and Objective PVs
    pv_layout = QHBoxLayout()
    input_pv_label = QLabel("Input PV:")
    main_window.input_pv_edit = QLineEdit("")
    main_window.input_pv_edit.editingFinished.connect(main_window.update_fields_from_pv)  # Connect signal to update fields
    pv_layout.addWidget(input_pv_label)
    pv_layout.addWidget(main_window.input_pv_edit)

    objective_pv_label = QLabel("Objective PV:")
    main_window.objective_pv_edit = QLineEdit("")
    pv_layout.addWidget(objective_pv_label)
    pv_layout.addWidget(main_window.objective_pv_edit)
    main_layout.addLayout(pv_layout)

    # Second Line: Initial value, Min, Max, %, Wait Time
    control_layout = QHBoxLayout()

    initial_value_label = QLabel("Initial Value:")
    main_window.initial_value_edit = QLineEdit("0.0")
    control_layout.addWidget(initial_value_label)
    control_layout.addWidget(main_window.initial_value_edit)

    min_range_label = QLabel("Min Range:")
    main_window.min_range_edit = QLineEdit("")
    control_layout.addWidget(min_range_label)
    control_layout.addWidget(main_window.min_range_edit)

    max_range_label = QLabel("Max Range:")
    main_window.max_range_edit = QLineEdit("")
    control_layout.addWidget(max_range_label)
    control_layout.addWidget(main_window.max_range_edit)

    percentage_label = QLabel("±%:")
    main_window.percentage_spinbox = QDoubleSpinBox()
    main_window.percentage_spinbox.setRange(0.0, 100.0)
    main_window.percentage_spinbox.setValue(7.0)  # Default to 7%
    main_window.percentage_spinbox.setSingleStep(1.0)
    control_layout.addWidget(percentage_label)
    control_layout.addWidget(main_window.percentage_spinbox)

    wait_label = QLabel("Wait Time (s):")
    main_window.wait_spin = QDoubleSpinBox()
    main_window.wait_spin.setRange(0.0, 100.0)
    main_window.wait_spin.setValue(3.0)
    main_window.wait_spin.setSingleStep(0.5)
    control_layout.addWidget(wait_label)
    control_layout.addWidget(main_window.wait_spin)

    main_layout.addLayout(control_layout)
    
    
    # Initialize ParameterWidget
    main_window.param_widget = ParameterWidget(main_window.min_range_edit, main_window.max_range_edit, main_window.percentage_spinbox)
    
    # Third Line: Number of iterations, Acquisition function, and Exploration Param
    settings_layout = QHBoxLayout()

    iter_label = QLabel("Number of Iterations:")
    main_window.iter_edit = QLineEdit("25")
    settings_layout.addWidget(iter_label)
    settings_layout.addWidget(main_window.iter_edit)

    acq_label = QLabel("Acquisition Function:")
    main_window.acq_combo = QComboBox()
    main_window.acq_combo.addItems(["EI", "UCB"])
    settings_layout.addWidget(acq_label)
    settings_layout.addWidget(main_window.acq_combo)

    expl_label = QLabel("Exploration Param (kappa or xi):")
    main_window.expl_spin = QDoubleSpinBox()
    main_window.expl_spin.setRange(0.0, 10.0)
    main_window.expl_spin.setValue(0.01)
    main_window.expl_spin.setSingleStep(0.01)
    settings_layout.addWidget(expl_label)
    settings_layout.addWidget(main_window.expl_spin)

    # Info Dialog Button
    help_button = QPushButton("?")
    help_button.setFixedWidth(30)
    help_button.clicked.connect(main_window.show_info_dialog)
    settings_layout.addWidget(help_button)

    main_layout.addLayout(settings_layout)

    # Optimization Status and Set Buttons
    status_layout = QHBoxLayout()

    # Status labels
    main_window.current_value_label = QLabel("Current Value of Input PV: N/A")
    main_window.best_value_label = QLabel("Sampled Best Value: N/A at X: N/A")
    main_window.best_predicted_label = QLabel("Predicted Best Value: N/A at X: N/A")

    # Set parameter buttons
    main_window.set_param_button = QPushButton("Set Param to Best X")
    main_window.set_param_button.setEnabled(False)
    main_window.set_param_button.clicked.connect(main_window.set_param_to_best_x)

    main_window.set_pred_param_button = QPushButton("Set Param to Pred. Best X")
    main_window.set_pred_param_button.setEnabled(False)
    main_window.set_pred_param_button.clicked.connect(main_window.set_param_to_best_pred_x)

    # Add labels and buttons to layout
    status_layout.addWidget(main_window.current_value_label)
    status_layout.addWidget(main_window.best_value_label)
    status_layout.addWidget(main_window.best_predicted_label)
    status_layout.addWidget(main_window.set_param_button)
    status_layout.addWidget(main_window.set_pred_param_button)

    main_layout.addLayout(status_layout)

    # Plot Widget
    main_window.plot_widget = PyQtGraphWidget()
    main_layout.addWidget(main_window.plot_widget)

    # Run and Abort Buttons
    button_layout = QHBoxLayout()

    main_window.run_button = QPushButton("Run Optimization")
    main_window.run_button.clicked.connect(main_window.run_clicked)
    main_window.run_button.setFixedHeight(30)
    button_layout.addWidget(main_window.run_button)

    main_window.abort_button = QPushButton("Abort")
    main_window.abort_button.clicked.connect(main_window.abort_clicked)
    main_window.abort_button.setFixedHeight(30)        
    button_layout.addWidget(main_window.abort_button)

    main_layout.addLayout(button_layout)

    # Message Bar
    main_window.message_label = QLabel("Ready")
    main_layout.addWidget(main_window.message_label, alignment=Qt.AlignRight)

    return main_layout