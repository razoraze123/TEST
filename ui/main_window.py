from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,  # added QGridLayout
    QListWidgetItem,
    QLabel,
    QLineEdit,
    QCheckBox,
    QStackedLayout,
    QStyle,
    QFrame,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QDateEdit,
    QDoubleSpinBox,
    QComboBox,
    QMessageBox,
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
import config
import config_manager
import logging
from accounting import import_releve, Transaction


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
        self.journal_transactions: list[Transaction] = []
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
        self.cb_dark_theme = QCheckBox("Th\u00e8me sombre")
        self.cb_dark_theme.setChecked(config.THEME == "dark")
        self.cb_dark_theme.stateChanged.connect(self._toggle_theme)
        self.header_layout.addWidget(self.cb_dark_theme)
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

        self.sidebar.add_section("🛒  E-commerce")
        ecommerce_items = [
            ("Accueil", QStyle.SP_DesktopIcon),
            ("Scraper", QStyle.SP_FileIcon),
            ("Scraping d'image", QStyle.SP_DirIcon),
            ("Scraping d'images avancé", QStyle.SP_DirIcon),
            ("Images avancées", QStyle.SP_DirIcon),
            ("Sélecteur visuel", QStyle.SP_DialogOpenButton),
            ("Optimiseur d'images", QStyle.SP_ComputerIcon),
            ("API Flask", QStyle.SP_BrowserReload),
        ]
        for text, icon in ecommerce_items:
            it = QListWidgetItem(self.style().standardIcon(icon), text)
            self.sidebar.addItem(it)

        self.sidebar.addItem(QListWidgetItem(""))
        self.sidebar.add_section("📒  Comptabilité")
        accounting_items = [
            ("Journal", QStyle.SP_FileDialogInfoView),
            ("Paramètres", QStyle.SP_FileDialogDetailedView),
        ]
        for text, icon in accounting_items:
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
        self.page_image_adv = super()._create_advanced_image_page()
        self.page_selector = super()._create_visual_selector_page()
        self.page_optimizer = super()._create_optimizer_page()
        self.page_api = super()._create_api_page()
        self.page_settings = super()._create_settings_page()
        self.page_journal = self._create_journal_page()

        for p in [
            self.page_dashboard,
            self.page_scraper,
            self.page_image,
            self.page_image_adv,
            self.page_selector,
            self.page_optimizer,
            self.page_api,
            self.page_settings,
            self.page_journal,
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
        apply_theme(self, config.THEME)

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
    def _create_journal_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Journal comptable"))

        btn_layout = QHBoxLayout()
        self.btn_import_tx = RoundButton("Importer relevé…")
        self.btn_import_tx.clicked.connect(self._import_bank_statement)
        btn_layout.addWidget(self.btn_import_tx)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        # filters
        filter_layout = QHBoxLayout()
        self.filter_start = QDateEdit()
        self.filter_start.setCalendarPopup(True)
        self.filter_end = QDateEdit()
        self.filter_end.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("Du"))
        filter_layout.addWidget(self.filter_start)
        filter_layout.addWidget(QLabel("au"))
        filter_layout.addWidget(self.filter_end)
        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText("Libellé contient…")
        filter_layout.addWidget(self.filter_text)
        self.filter_min = QDoubleSpinBox()
        self.filter_min.setDecimals(2)
        self.filter_min.setRange(-1e9, 1e9)
        filter_layout.addWidget(QLabel("Min"))
        filter_layout.addWidget(self.filter_min)
        self.filter_max = QDoubleSpinBox()
        self.filter_max.setDecimals(2)
        self.filter_max.setRange(-1e9, 1e9)
        filter_layout.addWidget(QLabel("Max"))
        filter_layout.addWidget(self.filter_max)
        self.filter_type = QComboBox()
        self.filter_type.addItems(["Tous", "Débit", "Crédit"])
        filter_layout.addWidget(self.filter_type)
        filter_layout.addStretch(1)
        layout.addLayout(filter_layout)

        self.table_journal = QTableWidget(0, 5)
        self.table_journal.setHorizontalHeaderLabels(
            ["Date", "Libellé", "Montant", "Débit", "Crédit"]
        )
        layout.addWidget(self.table_journal)

        for w in [
            self.filter_start,
            self.filter_end,
            self.filter_text,
            self.filter_min,
            self.filter_max,
            self.filter_type,
        ]:
            signal = getattr(w, "textChanged", None) or getattr(w, "valueChanged", None) or getattr(w, "dateChanged", None) or getattr(w, "currentIndexChanged", None)
            if signal:
                signal.connect(self._apply_journal_filters)

        layout.addStretch(1)
        return page

    # ------------------------------------------------------------------
    def _import_bank_statement(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un relevé",
            "",
            "Fichiers CSV/Excel (*.csv *.xls *.xlsx)"
        )
        if not path:
            return
        try:
            self.journal_transactions = import_releve(path)
        except Exception as e:
            logging.exception("Erreur import relev\u00e9")
            QMessageBox.critical(self, "Erreur d'import", str(e))
            return
        self._apply_journal_filters()

    # ------------------------------------------------------------------
    def _apply_journal_filters(self):
        txs = list(self.journal_transactions)

        start = self.filter_start.date().toPython() if self.filter_start.date().isValid() else None
        end = self.filter_end.date().toPython() if self.filter_end.date().isValid() else None
        text = self.filter_text.text().lower().strip()
        min_val = self.filter_min.value()
        max_val = self.filter_max.value()
        type_val = self.filter_type.currentText()

        filtered = []
        for tx in txs:
            if start and tx.date < start:
                continue
            if end and tx.date > end:
                continue
            if text and text not in tx.description.lower():
                continue
            if min_val and tx.montant < min_val:
                continue
            if max_val and tx.montant > max_val:
                continue
            if type_val == "D\u00e9bit" and not tx.debit:
                continue
            if type_val == "Cr\u00e9dit" and not tx.credit:
                continue
            filtered.append(tx)

        self.table_journal.setRowCount(len(filtered))
        for i, tx in enumerate(filtered):
            self.table_journal.setItem(i, 0, QTableWidgetItem(str(tx.date)))
            self.table_journal.setItem(i, 1, QTableWidgetItem(tx.description))
            self.table_journal.setItem(i, 2, QTableWidgetItem(f"{tx.montant:.2f}"))
            self.table_journal.setItem(i, 3, QTableWidgetItem(tx.debit))
            self.table_journal.setItem(i, 4, QTableWidgetItem(tx.credit))

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

    # ------------------------------------------------------------------
    def _toggle_theme(self, state=None):
        theme = "dark" if self.cb_dark_theme.isChecked() else "light"
        apply_theme(self, theme)
        data = config_manager.load()
        data["THEME"] = theme
        config_manager.save(data)
        config.reload()
