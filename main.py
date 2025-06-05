import sys
import os
import json
from collections import deque

from PySide6.QtCore import (
    QObject,
    Signal,
    Qt,
    QThread,
    QTime,
    QTimer,
    QPropertyAnimation,
    QSize,
)
from PySide6.QtGui import QColor, QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedLayout,
    QProgressBar,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QGraphicsOpacityEffect,
)
from ui.base_window import MainWindow
from ui.main_window import DashboardWindow
import config



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    # Pour tester : lancez une action puis fermez la fenêtre.
    # Aucun message "QThread: Destroyed while thread" ne doit apparaître.
    sys.exit(app.exec())
