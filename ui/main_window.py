from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,  # added QGridLayout
    QListWidgetItem,
    QLabel,
    QLineEdit,
    QStackedLayout,
    QStyle,
    QFrame,
)
from ui.components import Sidebar, RoundButton, Card
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from pathlib import Path
import tomllib
from ui import style

from ui.base_window import MainWindow
from ui.style import apply_theme
from ui.responsive import ResponsiveMixin


def _get_project_info():
    """Return application name and version from pyproject.toml."""
    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        proj = data.get("project", {})
        return proj.get("name", "Application"), proj.get("version", "")
    except Exception:
        return "Application", ""


class DashboardWindow(ResponsiveMixin, MainWindow):
    """Main window with modern dashboard layout."""

    def __init__(self, user_name="Utilisateur"):
        self.user_name = user_name
        super().__init__()

    # ------------------------------------------------------------------
    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header -------------------------------------------------------
        header = QFrame()
        header.setObjectName("Header")
        self.header_layout = QHBoxLayout(header)
        self.header_layout.setContentsMargins(10, 10, 10, 10)
        self.header_layout.setSpacing(10)
        self.label_welcome = QLabel(f"Bienvenue, {self.user_name} !")
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("Recherche...")
        self.header_layout.addWidget(self.label_welcome)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.edit_search)
        main_layout.addWidget(header)

        # Body ---------------------------------------------------------
        self.body_layout = QHBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        main_layout.addLayout(self.body_layout, 1)

        # Sidebar menu
        self.sidebar = Sidebar(collapsible=True)
        self.sidebar._expanded_width = 180
        self.sidebar.setFixedWidth(180)
        self.sidebar.setSpacing(4)

        items = [
            ("Accueil", QStyle.SP_DesktopIcon),
            ("Scraper", QStyle.SP_FileIcon),
            ("Scraping d'image", QStyle.SP_DirIcon),
            ("Sélecteur visuel", QStyle.SP_DialogOpenButton),
            ("Optimiseur d'images", QStyle.SP_ComputerIcon),
            ("API Flask", QStyle.SP_BrowserReload),
            ("Paramètres", QStyle.SP_FileDialogDetailedView),
        ]
        for text, icon in items:
            it = QListWidgetItem(self.style().standardIcon(icon), text)
            self.sidebar.addItem(it)
        self.sidebar.setCurrentRow(0)
        self.body_layout.addWidget(self.sidebar)

        # Stacked pages
        stack_container = QWidget()
        self.stack = QStackedLayout(stack_container)
        self.body_layout.addWidget(stack_container, 1)
        self.body_layout.setStretch(1, 1)

        # Pages from base class
        self.page_dashboard = self._create_dashboard_page()
        self.page_scraper = super()._create_scraper_page()
        self.page_image = super()._create_image_page()
        self.page_selector = super()._create_visual_selector_page()
        self.page_optimizer = super()._create_optimizer_page()
        self.page_api = super()._create_api_page()
        self.page_settings = super()._create_settings_page()

        for p in [
            self.page_dashboard,
            self.page_scraper,
            self.page_image,
            self.page_selector,
            self.page_optimizer,
            self.page_api,
            self.page_settings,
        ]:
            self.stack.addWidget(p)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)

        # Footer -------------------------------------------------------
        name, version = _get_project_info()
        footer = QFrame()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 4, 10, 4)
        footer_layout.setSpacing(0)
        footer_label = QLabel(f"{name} v{version}")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_layout.addStretch(1)
        footer_layout.addWidget(footer_label)
        footer_layout.addStretch(1)
        footer.setStyleSheet(
            f"background-color: {style.SURFACE_DARK}; color: {style.TEXT_LIGHT}; font-size: 12px;"
        )
        main_layout.addWidget(footer)

        # Apply centralized theme
        apply_theme(self)

    # ------------------------------------------------------------------
    def _create_dashboard_page(self):
        page = QWidget()
        self.dashboard_grid = QGridLayout(page)
        self.dashboard_grid.setSpacing(20)
        self.dashboard_grid.setContentsMargins(20, 20, 20, 20)

        def add_card(text, icon, row, col, callback=None):
            frame = Card()
            frame.setCursor(Qt.PointingHandCursor)
            v = QVBoxLayout(frame)
            btn = RoundButton(text)
            btn.setIcon(self.style().standardIcon(icon))
            btn.setFlat(True)
            v.addStretch(1)
            v.addWidget(btn, alignment=Qt.AlignCenter)
            v.addStretch(1)
            if callback:
                btn.clicked.connect(callback)
                frame.mousePressEvent = lambda e, b=btn: b.click()
            self.dashboard_grid.addWidget(frame, row, col)

        add_card(
            "Nouvelle tâche",
            QStyle.SP_FileDialogNewFolder,
            0,
            0,
            lambda: self.stack.setCurrentWidget(self.page_scraper),
        )
        add_card(
            "Modèles",
            QStyle.SP_DirIcon,
            0,
            1,
            lambda: self.stack.setCurrentWidget(self.page_image),
        )
        add_card(
            "Tutoriels",
            QStyle.SP_MessageBoxInformation,
            1,
            0,
        )
        return page

    # ------------------------------------------------------------------
    def apply_responsive(self, values):
        """Adjust margins, spacings and sidebar state on resize."""
        margin = values.get("margin", 20)
        spacing = values.get("spacing", 20)
        font = values.get("font", 14)
        collapse = values.get("collapse", False)

        self.header_layout.setContentsMargins(margin, margin, margin, margin)
        self.header_layout.setSpacing(spacing)
        self.body_layout.setSpacing(spacing)
        self.dashboard_grid.setSpacing(spacing)
        self.dashboard_grid.setContentsMargins(margin, margin, margin, margin)

        self.label_welcome.setStyleSheet(f"font-size: {font + 2}px;")
        self.edit_search.setStyleSheet(f"font-size: {font}px;")

        if collapse:
            self.sidebar.collapse()
        else:
            self.sidebar.expand()
