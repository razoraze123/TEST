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

from ui.base_window import MainWindow
from ui.style import apply_theme


class DashboardWindow(MainWindow):
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
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)
        self.label_welcome = QLabel(f"Bienvenue, {self.user_name} !")
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("Recherche...")
        header_layout.addWidget(self.label_welcome)
        header_layout.addStretch(1)
        header_layout.addWidget(self.edit_search)
        main_layout.addWidget(header)

        # Body ---------------------------------------------------------
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        main_layout.addLayout(body_layout, 1)

        # Sidebar menu
        self.sidebar = Sidebar()
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
        body_layout.addWidget(self.sidebar)

        # Stacked pages
        stack_container = QWidget()
        self.stack = QStackedLayout(stack_container)
        body_layout.addWidget(stack_container, 1)

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

        # Apply centralized theme
        apply_theme(self)

    # ------------------------------------------------------------------
    def _create_dashboard_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

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
            layout.addWidget(frame, row, col)

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
