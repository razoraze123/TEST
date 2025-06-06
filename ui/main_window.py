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
    QDialog,
    QMessageBox,
    QInputDialog,
    QCheckBox,
)
from ui.components import Sidebar, RoundButton, Card, show_success, show_error
from ui.transaction_dialog import TransactionDialog
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
import logger_setup  # noqa: F401  # configure logging
from accounting import (
    import_releve,
    Transaction,
    JournalEntry,
    CATEGORIES_KEYWORDS,
    suggere_rapprochements,
    rapprocher,
    rapport_par_categorie,
    export_transactions,
    export_entries,
)

logger = logging.getLogger(__name__)


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
        self.journal_entries: list[JournalEntry] = []
        self.filtered_transactions: list[Transaction] = []
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
            ("Comptabilité", QStyle.SP_FileDialogContentsView),
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
        self.page_comptabilite = self._create_comptabilite_page()

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
            self.page_comptabilite,
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
        self.btn_report = RoundButton("Rapport rapide")
        self.btn_report.clicked.connect(self._show_report)
        btn_layout.addWidget(self.btn_report)
        self.btn_add_tx = RoundButton("Ajouter")
        self.btn_add_tx.clicked.connect(self._add_transaction)
        btn_layout.addWidget(self.btn_add_tx)
        self.btn_edit_tx = RoundButton("Modifier")
        self.btn_edit_tx.clicked.connect(self._edit_transaction)
        btn_layout.addWidget(self.btn_edit_tx)
        self.btn_delete_tx = RoundButton("Supprimer")
        self.btn_delete_tx.clicked.connect(self._delete_transaction)
        btn_layout.addWidget(self.btn_delete_tx)
        self.btn_reconcile = RoundButton("Rapprocher")
        self.btn_reconcile.clicked.connect(self._reconcile_transaction)
        btn_layout.addWidget(self.btn_reconcile)
        self.btn_export = RoundButton("Exporter")
        self.btn_export.clicked.connect(self._export_journal)
        btn_layout.addWidget(self.btn_export)
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
        self.filter_category = QComboBox()
        self.filter_category.addItem("Toutes")
        self.filter_category.addItems(list(CATEGORIES_KEYWORDS.keys()) + ["Autre"])
        filter_layout.addWidget(self.filter_category)
        self.cb_unreconciled = QCheckBox("Non rapprochées")
        filter_layout.addWidget(self.cb_unreconciled)
        filter_layout.addStretch(1)
        layout.addLayout(filter_layout)

        self.table_journal = QTableWidget(0, 7)
        self.table_journal.setHorizontalHeaderLabels(
            ["Date", "Libellé", "Montant", "Débit", "Crédit", "Catégorie", "État"]
        )
        self.table_journal.itemChanged.connect(self._on_cat_changed)
        style.style_table_widget(self.table_journal, config.THEME)
        layout.addWidget(self.table_journal)

        for w in [
            self.filter_start,
            self.filter_end,
            self.filter_text,
            self.filter_min,
            self.filter_max,
            self.filter_type,
            self.filter_category,
            self.cb_unreconciled,
        ]:
            signal = getattr(w, "textChanged", None) or getattr(w, "valueChanged", None) or getattr(w, "dateChanged", None) or getattr(w, "currentIndexChanged", None)
            if signal:
                signal.connect(self._apply_journal_filters)

        layout.addStretch(1)
        return page

    # ------------------------------------------------------------------
    def _create_comptabilite_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Comptabilit\u00e9"))

        btn_layout = QHBoxLayout()
        btn_import = RoundButton("Importer relev\u00e9\u2026")
        btn_layout.addWidget(btn_import)
        btn_report = RoundButton("Rapport rapide")
        btn_layout.addWidget(btn_report)
        btn_add = RoundButton("Ajouter")
        btn_layout.addWidget(btn_add)
        btn_edit = RoundButton("Modifier")
        btn_layout.addWidget(btn_edit)
        btn_delete = RoundButton("Supprimer")
        btn_layout.addWidget(btn_delete)
        btn_reconcile = RoundButton("Rapprocher")
        btn_layout.addWidget(btn_reconcile)
        btn_export = RoundButton("Exporter")
        btn_layout.addWidget(btn_export)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        filter_layout = QHBoxLayout()
        filter_start = QDateEdit()
        filter_start.setCalendarPopup(True)
        filter_end = QDateEdit()
        filter_end.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("Du"))
        filter_layout.addWidget(filter_start)
        filter_layout.addWidget(QLabel("au"))
        filter_layout.addWidget(filter_end)
        filter_text = QLineEdit()
        filter_text.setPlaceholderText("Libell\u00e9 contient\u2026")
        filter_layout.addWidget(filter_text)
        filter_min = QDoubleSpinBox()
        filter_min.setDecimals(2)
        filter_min.setRange(-1e9, 1e9)
        filter_layout.addWidget(QLabel("Min"))
        filter_layout.addWidget(filter_min)
        filter_max = QDoubleSpinBox()
        filter_max.setDecimals(2)
        filter_max.setRange(-1e9, 1e9)
        filter_layout.addWidget(QLabel("Max"))
        filter_layout.addWidget(filter_max)
        filter_type = QComboBox()
        filter_type.addItems(["Tous", "D\u00e9bit", "Cr\u00e9dit"])
        filter_layout.addWidget(filter_type)
        filter_category = QComboBox()
        filter_category.addItem("Toutes")
        filter_category.addItems(list(CATEGORIES_KEYWORDS.keys()) + ["Autre"])
        filter_layout.addWidget(filter_category)
        cb_unreconciled = QCheckBox("Non rapproch\u00e9es")
        filter_layout.addWidget(cb_unreconciled)
        filter_layout.addStretch(1)
        layout.addLayout(filter_layout)

        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels(
            ["Date", "Libell\u00e9", "Montant", "D\u00e9bit", "Cr\u00e9dit", "Cat\u00e9gorie", "\u00c9tat"]
        )
        layout.addWidget(table)

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
        logger.info("D\u00e9but import du fichier %s", path)
        try:
            self.journal_transactions = import_releve(path)
        except Exception as e:
            logger.exception("Erreur lors de l'import du relev\u00e9 %s", path)
            QMessageBox.critical(self, "Erreur d'import", str(e))
            return
        logger.info(
            "Import du fichier %s termin\u00e9 : %d lignes trait\u00e9es",
            path,
            len(self.journal_transactions),
        )
        self._apply_journal_filters()

    # ------------------------------------------------------------------
    def _add_transaction(self):
        dlg = TransactionDialog(self)
        if dlg.exec() == QDialog.Accepted:
            tx = dlg.get_transaction()
            self.journal_transactions.append(tx)
            show_success("Op\u00e9ration ajout\u00e9e", self)
            self._apply_journal_filters()

    # ------------------------------------------------------------------
    def _edit_transaction(self):
        indexes = self.table_journal.selectionModel().selectedRows()
        if not indexes:
            return
        row = indexes[0].row()
        if row >= len(self.filtered_transactions):
            return
        tx = self.filtered_transactions[row]
        dlg = TransactionDialog(self, tx)
        if dlg.exec() == QDialog.Accepted:
            new_tx = dlg.get_transaction()
            idx_all = self.journal_transactions.index(tx)
            self.journal_transactions[idx_all] = new_tx
            show_success("Op\u00e9ration modifi\u00e9e", self)
            self._apply_journal_filters()

    # ------------------------------------------------------------------
    def _delete_transaction(self):
        indexes = self.table_journal.selectionModel().selectedRows()
        if not indexes:
            return
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            "Supprimer les op\u00e9rations s\u00e9lectionn\u00e9es ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            show_error("Suppression annul\u00e9e", self)
            return
        rows = sorted([i.row() for i in indexes], reverse=True)
        for row in rows:
            if row < len(self.filtered_transactions):
                tx = self.filtered_transactions[row]
                if tx in self.journal_transactions:
                    self.journal_transactions.remove(tx)
        show_success("Op\u00e9ration supprim\u00e9e", self)
        self._apply_journal_filters()

    # ------------------------------------------------------------------
    def _export_journal(self):
        choice, ok = QInputDialog.getItem(
            self,
            "Exporter journal",
            "Donn\u00e9es",
            ["Transactions", "\u00c9critures"],
            0,
            False,
        )
        if not ok:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter",
            filter="Excel (*.xlsx);;CSV (*.csv)",
        )
        if not path:
            return
        try:
            if choice == "Transactions":
                export_transactions(self.journal_transactions, path)
            else:
                export_entries(self.journal_entries, path)
            show_success("Export r\u00e9ussi", self)
        except Exception as e:
            show_error(f"Erreur export: {e}", self)

    # ------------------------------------------------------------------
    def _reconcile_transaction(self):
        indexes = self.table_journal.selectionModel().selectedRows()
        if not indexes:
            return
        row = indexes[0].row()
        if row >= len(self.filtered_transactions):
            return
        tx = self.filtered_transactions[row]
        suggestions = suggere_rapprochements(tx, self.journal_entries, self.journal_transactions)
        entry = None
        if suggestions:
            entry = suggestions[0]
        elif self.journal_entries:
            items = [f"{e.date} {e.account_code} {e.debit or e.credit}" for e in self.journal_entries]
            item, ok = QInputDialog.getItem(self, "Choisir une écriture", "Écriture", items, 0, False)
            if not ok:
                return
            entry = self.journal_entries[items.index(item)]
        else:
            QMessageBox.information(self, "Aucune écriture", "Aucune écriture disponible")
            return
        rapprocher(tx, entry)
        show_success("Opération rapprochée", self)
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
        cat_val = self.filter_category.currentText()
        unreconciled_only = self.cb_unreconciled.isChecked()

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
            if cat_val != "Toutes" and tx.categorie != cat_val:
                continue
            if unreconciled_only and tx.journal_entry_id:
                continue
            filtered.append(tx)

        self.table_journal.blockSignals(True)
        self.table_journal.setRowCount(len(filtered))
        self.filtered_transactions = filtered
        for i, tx in enumerate(filtered):
            self.table_journal.setItem(i, 0, QTableWidgetItem(str(tx.date)))
            self.table_journal.setItem(i, 1, QTableWidgetItem(tx.description))
            self.table_journal.setItem(i, 2, QTableWidgetItem(f"{tx.montant:.2f}"))
            self.table_journal.setItem(i, 3, QTableWidgetItem(tx.debit))
            self.table_journal.setItem(i, 4, QTableWidgetItem(tx.credit))
            item_cat = QTableWidgetItem(tx.categorie)
            item_cat.setFlags(item_cat.flags() | Qt.ItemIsEditable)
            self.table_journal.setItem(i, 5, item_cat)
            etat = "Rapproché" if tx.journal_entry_id else "à rapprocher"
            self.table_journal.setItem(i, 6, QTableWidgetItem(etat))
        self.table_journal.blockSignals(False)

    # ------------------------------------------------------------------
    def _on_cat_changed(self, item):
        if item.column() != 5:
            return
        row = item.row()
        if 0 <= row < len(getattr(self, "filtered_transactions", [])):
            self.filtered_transactions[row].categorie = item.text()

    # ------------------------------------------------------------------
    def _show_report(self):
        start = self.filter_start.date().toPython() if self.filter_start.date().isValid() else None
        end = self.filter_end.date().toPython() if self.filter_end.date().isValid() else None
        totals = rapport_par_categorie(self.journal_transactions, start, end)
        if not totals:
            QMessageBox.information(self, "Rapport", "Aucune transaction")
            return
        lines = [f"{cat}: {total:.2f}" for cat, total in totals.items()]
        QMessageBox.information(self, "Rapport", "\n".join(lines))

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
        style.style_table_widget(self.table_journal, theme)
        data = config_manager.load()
        data["THEME"] = theme
        config_manager.save(data)
        config.reload()
