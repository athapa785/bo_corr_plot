from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acquisition Function Info")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        info_text = (
            "<b>Acquisition Functions:</b><br><br>"
            "<b>Expected Improvement (EI):</b><br>"
            "This function measures the expected improvement over the current best observed value. "
            "It balances exploitation and exploration by considering the probability of improving "
            "over the best solution found so far.<br>"
            "<i>Parameter (xi):</i> A small positive number. Increasing xi encourages more exploration. "
            "Common values range from 0.0 to 0.1.<br><br>"
            
            "<b>Upper Confidence Bound (UCB):</b><br>"
            "This function considers both the predicted mean and uncertainty of the model. "
            "By adding a multiple of the standard deviation, it encourages exploring areas "
            "with high uncertainty.<br>"
            "<i>Parameter (kappa):</i> Controls the exploration-exploitation trade-off. "
            "A higher kappa means more exploration. Typical values might range from about 1.0 to 5.0, "
            "but can vary depending on the problem.<br><br>"
            
            "Adjusting these parameters helps control how aggressively the optimizer searches for "
            "new, potentially better areas (exploration) versus refining known good areas (exploitation)."
        )

        label = QLabel(info_text)
        label.setWordWrap(True)
        layout.addWidget(label)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)