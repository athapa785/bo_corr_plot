import sys
from PyQt5.QtWidgets import QApplication
import qdarkstyle
from .bo_controller import BOController

def main():
    """Main function to launch the GUI."""
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    controller = BOController()
    controller.window.resize(800, 800)
    controller.window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()