import sys
import logger_setup  # noqa: F401  # configure logging
from PySide6.QtWidgets import QApplication
from ui.main_window import DashboardWindow
import config
import storage
import db
import scheduler


def main():
    db.init_engine(storage.db_path())
    storage.init_db()
    scheduler.init_scheduler()
    app = QApplication(sys.argv)
    window = DashboardWindow()
    scheduler.set_notify_callback(window.show_notification)
    if config.ENABLE_FLASK_API.lower() == "true":
        window.start_api_server()
    window.show()
    app.aboutToQuit.connect(window.stop_api_server)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
