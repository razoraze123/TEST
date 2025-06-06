import sys
import logger_setup  # noqa: F401  # configure logging
from PySide6.QtWidgets import QApplication
from ui.main_window import DashboardWindow
import storage
import db
import scheduler


def main():
    db.init_engine(storage.db_path())
    storage.init_db()

    app = QApplication(sys.argv)
    window = DashboardWindow()
    scheduler.set_notify_callback(window.show_notification)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
