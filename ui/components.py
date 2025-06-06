from PySide6.QtWidgets import (
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QGraphicsDropShadowEffect,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsOpacityEffect,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QTimer,
    QEasingCurve,
    QPoint,
    QObject,
    Signal,
)
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


class _GlobalSignals(QObject):
    """Container for application-wide signals."""

    collapse_sections = Signal()


global_signals = _GlobalSignals()


class CollapsibleSection(QWidget):
    """Vertical collapsible section with a clickable header."""

    item_clicked = Signal(str)

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._expanded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.btn_header = QPushButton(f"\u25B6 {title}")
        self.btn_header.setCheckable(True)
        self.btn_header.setFlat(True)
        self.btn_header.setCursor(Qt.PointingHandCursor)
        self.btn_header.setStyleSheet("text-align:left; padding:6px;")
        layout.addWidget(self.btn_header)

        self.container = QWidget()
        self.container.setMaximumHeight(0)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 0, 0, 0)
        self.container_layout.setSpacing(2)
        layout.addWidget(self.container)

        self.anim = QPropertyAnimation(self.container, b"maximumHeight", self)
        self.anim.setDuration(150)

        self.btn_header.clicked.connect(self._on_header_clicked)
        global_signals.collapse_sections.connect(self._collapse)

    # ------------------------------------------------------------------
    def add_item(self, text: str, icon=None) -> QPushButton:
        """Add a clickable item button and return it."""
        btn = QPushButton(text)
        btn.setIcon(icon) if icon else None
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("text-align:left; padding:4px 6px;")
        btn.clicked.connect(lambda: self.item_clicked.emit(text))
        self.container_layout.addWidget(btn)
        return btn

    # ------------------------------------------------------------------
    def _on_header_clicked(self) -> None:
        global_signals.collapse_sections.emit()
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self) -> None:
        self._expanded = True
        self.btn_header.setText(f"\u25BC {self._title}")
        end = self.container_layout.sizeHint().height()
        self.anim.stop()
        self.anim.setStartValue(0)
        self.anim.setEndValue(end)
        self.anim.start()

    def _collapse(self) -> None:
        if not self._expanded:
            return
        self._expanded = False
        self.btn_header.setText(f"\u25B6 {self._title}")
        self.anim.stop()
        self.anim.setStartValue(self.container.height())
        self.anim.setEndValue(0)
        self.anim.start()


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

        # width animation
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(200)

        # small badge for notifications
        self.badge = QLabel("0", self)
        self.badge.setStyleSheet(
            "background:#c0392b; color:white; border-radius:8px; padding:2px 6px;"
        )
        self.badge.hide()

    def add_section(self, text: str, icon: str | None = None):
        """Insert a non-selectable header item."""
        display = f"{icon}  {text}" if icon else text
        item = QListWidgetItem(display)
        item.setFlags(Qt.NoItemFlags)
        item.setData(Qt.UserRole, "true")
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        item.setBackground(QColor(style.SURFACE_DARK))
        self.addItem(item)
        return item

    def collapse(self):
        if not self.collapsible or self.collapsed:
            return
        self._stored_texts = [self.item(i).text() for i in range(self.count())]
        for i in range(self.count()):
            self.item(i).setText("")
        self._anim.stop()
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(self._collapsed_width)
        self._anim.start()
        self.collapsed = True

    def expand(self):
        if not self.collapsible or not self.collapsed:
            return
        for i, text in enumerate(self._stored_texts):
            self.item(i).setText(text)
        self._anim.stop()
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(self._expanded_width)
        self._anim.start()
        self.collapsed = False

    def toggle(self):
        if self.collapsed:
            self.expand()
        else:
            self.collapse()

    # ------------------------------------------------------------------
    def set_badge_count(self, count: int) -> None:
        """Display *count* in the notification badge."""
        if count > 0:
            self.badge.setText(str(count))
            self.badge.show()
        else:
            self.badge.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.badge.isVisible():
            self.badge.move(self.width() - self.badge.width() - 4, 4)


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

