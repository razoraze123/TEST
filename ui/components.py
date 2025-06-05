from PySide6.QtWidgets import (
    QPushButton,
    QListWidget,
    QFrame,
    QGraphicsDropShadowEffect,
    QWidget,
    QLabel,
    QVBoxLayout,
    QGraphicsOpacityEffect,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, QPoint
from PySide6.QtWidgets import QApplication

from . import style


class RoundButton(QPushButton):
    """Push button with rounded corners and primary/secondary color options."""

    def __init__(self, text="", color="primary", radius=20, parent=None):
        super().__init__(text, parent)
        self._color = color
        self._radius = radius
        self._update_style()

    def _update_style(self):
        if self._color == "primary":
            base = QColor(style.PRIMARY_BLUE)
        else:
            base = QColor(getattr(style, "SURFACE_DARK", "#555555"))
        hover = base.lighter(120).name()
        self.setStyleSheet(
            f"QPushButton {{background-color: {base.name()}; color: white; "
            f"border:none; border-radius: {self._radius}px; padding: 6px 12px;}}"
            f"QPushButton:hover {{background-color: {hover};}}"
        )


class Sidebar(QListWidget):
    """Sidebar list with optional collapse/expand behaviour."""

    def __init__(self, collapsible=False, parent=None):
        super().__init__(parent)
        self.collapsible = collapsible
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"background-color: {style.SIDEBAR_DARK}; border:none;")
        self._expanded_width = 150
        self._collapsed_width = 40
        self._stored_texts = []
        self.collapsed = False
        self.setFixedWidth(self._expanded_width)

    def collapse(self):
        if not self.collapsible or self.collapsed:
            return
        self._stored_texts = [self.item(i).text() for i in range(self.count())]
        for i in range(self.count()):
            self.item(i).setText("")
        self.setFixedWidth(self._collapsed_width)
        self.collapsed = True

    def expand(self):
        if not self.collapsible or not self.collapsed:
            return
        for i, text in enumerate(self._stored_texts):
            self.item(i).setText(text)
        self.setFixedWidth(self._expanded_width)
        self.collapsed = False

    def toggle(self):
        if self.collapsed:
            self.expand()
        else:
            self.collapse()


class Card(QFrame):
    """Simple card frame with drop shadow and padding."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", True)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)
        self.setContentsMargins(16, 16, 16, 16)


class Toast(QWidget):
    """Transient message overlay that fades in and out."""

    def __init__(self, message, parent=None, duration=2000, background="#323232", color="white"):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.ToolTip
        )
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.duration = duration
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        self.setStyleSheet(
            f"background:{background}; color:{color}; border-radius:6px;"
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.adjustSize()
        parent = self.parent() if self.parent() else self.window()
        if parent:
            geo = parent.geometry()
            pos = QPoint(
                geo.x() + (geo.width() - self.width()) // 2,
                geo.y() + geo.height() - self.height() - 40,
            )
            self.move(pos)

        self.effect.setOpacity(0.0)
        self.anim.stop()
        self.anim.setDuration(200)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()
        QTimer.singleShot(self.duration, self.fade_out)

    def fade_out(self):
        self.anim.stop()
        self.anim.setDuration(400)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.close)
        self.anim.start()


def show_success(message, parent=None):
    """Display a success toast on the active window."""
    if parent is None:
        parent = QApplication.activeWindow()
    if parent is None:
        return
    toast = Toast(message, parent, background=style.PRIMARY_BLUE)
    toast.show()


def show_error(message, parent=None):
    """Display an error toast on the active window."""
    if parent is None:
        parent = QApplication.activeWindow()
    if parent is None:
        return
    toast = Toast(message, parent, background="#c0392b")
    toast.show()

