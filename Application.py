import sys
import logger_setup  # noqa: F401  # configure logging
from PySide6.QtWidgets import QApplication
from ui.main_window import DashboardWindow


def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
