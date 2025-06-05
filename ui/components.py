from PySide6.QtWidgets import QPushButton, QListWidget, QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

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

