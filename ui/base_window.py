import sys
import os
import json
import hashlib
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
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
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
from ui.components import RoundButton, Sidebar, show_success, show_error
from ui.style import apply_theme
from scraper_woocommerce import ScraperCore
from optimizer import ImageOptimizer
import config
import config_manager


class ConsoleOutput(QObject):
    """Redirect writes to a Qt signal."""

    outputWritten = Signal(str)

    def write(self, text):
        self.outputWritten.emit(str(text))

    def flush(self):
        pass


class Worker(QThread):
    """Run a function in a separate thread and emit progress."""

    progress = Signal(int)
    status = Signal(str)
    result = Signal(object)

    def __init__(self, func, *args, console_output=None, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.console_output = console_output
        self._running = True
        self.start_time = None

    class _StopException(Exception):
        pass

    def _report(self, value):
        self.progress.emit(value)
        if self.isInterruptionRequested():
            raise Worker._StopException()

    def stop(self):
        """Request the worker to stop."""
        self._running = False
        self.requestInterruption()

    def run(self):
        self.status.emit("start")
        self.start_time = QTime.currentTime()
        res = None
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        if self.console_output:
            sys.stdout = self.console_output
            sys.stderr = self.console_output
        try:
            res = self.func(self._report, lambda: self.isInterruptionRequested(), *self.args, **self.kwargs)
        except Worker._StopException:
            self.status.emit("interrupted")
            res = None
        finally:
            if self.console_output:
                sys.stdout = orig_stdout
                sys.stderr = orig_stderr
            self.status.emit("done")
            self.result.emit(res)


class TabProgress(QObject):
    """Handle progress display and timing for a single tab."""

    def __init__(self, progress_bar, label_time, console, parent=None):
        super().__init__(parent)
        self.progress_bar = progress_bar
        self.label_time = label_time
        self.console = console

        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._tick_progress)

        self.target_progress = 0
        self.current_progress = 0
        self.current_worker = None
        self.time_samples = deque(maxlen=5)
        self.last_progress_value = 0
        self.last_progress_time = None
        self.last_time_update = QTime.currentTime()

        self.time_effect = QGraphicsOpacityEffect(self.label_time)
        self.label_time.setGraphicsEffect(self.time_effect)
        self.fade_anim = QPropertyAnimation(self.time_effect, b"opacity", self)
        self.fade_anim.setDuration(300)

    def start(self, worker):
        self.progress_bar.setValue(0)
        self.label_time.setText("")
        self.target_progress = 0
        self.current_progress = 0
        self.current_worker = worker
        self.time_samples.clear()
        self.last_progress_value = 0
        self.last_progress_time = None
        self.last_time_update = QTime.currentTime()
        self.timer.start()
        worker.finished.connect(self.stop)

    def stop(self):
        self.current_worker = None
        self.timer.stop()

    def update_progress(self, value):
        self.target_progress = value
        if value >= 100:
            self.label_time.setText("Terminé !")
        elif self.label_time.text() == "Terminé !":
            self.label_time.setText("")

    def _tick_progress(self):
        if self.current_progress < self.target_progress:
            self.current_progress += min(1, self.target_progress - self.current_progress)
        elif self.current_progress > self.target_progress:
            self.current_progress -= min(1, self.current_progress - self.target_progress)

        value = int(self.current_progress)
        self.progress_bar.setValue(value)
        hue = int(value * 1.2)
        color = QColor.fromHsv(hue, 255, 200).name()
        self.progress_bar.setStyleSheet(
            f"QProgressBar {{border:1px solid #444; border-radius:8px; text-align:center; height:25px;}}"
            f"QProgressBar::chunk {{background-color:{color}; border-radius:8px;}}"
        )
        now = QTime.currentTime()
        if self.current_worker and value > 0:
            if self.last_progress_time is None:
                self.last_progress_time = now
            if value > self.last_progress_value:
                dt = self.last_progress_time.msecsTo(now) / 1000
                dp = value - self.last_progress_value
                if dt > 0 and dp > 0:
                    self.time_samples.append(dt / dp)
                self.last_progress_time = now
                self.last_progress_value = value

            if self.last_time_update.msecsTo(now) >= 1000:
                self.last_time_update = now
                if self.time_samples:
                    avg = sum(self.time_samples) / len(self.time_samples)
                    remaining = avg * (100 - value)
                else:
                    elapsed_ms = self.current_worker.start_time.msecsTo(now)
                    elapsed = elapsed_ms / 1000
                    remaining = elapsed * (100 - value) / value
                m, s = divmod(int(remaining), 60)
                h, m = divmod(m, 60)
                if remaining <= 5:
                    msg = "Extraction en cours, presque terminé..."
                else:
                    msg = f"Temps restant estimé : {h:02d}:{m:02d}:{s:02d}"
                if msg != self.label_time.text():
                    self.label_time.setText(msg)
                    self.time_effect.setOpacity(0.0)
                    self.fade_anim.stop()
                    self.fade_anim.setStartValue(0.0)
                    self.fade_anim.setEndValue(1.0)
                    self.fade_anim.start()
        else:
            if self.progress_bar.value() < 100:
                self.label_time.setText("")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WooCommerce Scraper")
        self.resize(900, 600)
        self.scraper = ScraperCore()
        self._threads = []
        self.extra_links = {}
        self._setup_ui()
        
        self._redirect_console()
        self._show_page(self.page_scraper)

        # per-tab progress managers
        self.scraper_tab = TabProgress(self.progress_bar, self.label_time, self.console_scraper, self)
        self.images_tab = TabProgress(self.progress_bar_img, self.label_time_img, self.console_images, self)
        self.optimizer_tab = TabProgress(self.progress_bar_opt, self.label_time_opt, self.console_optimizer, self)

    def _redirect_console(self):
        self.console_output_scraper = ConsoleOutput()
        self.console_output_scraper.outputWritten.connect(self.console_scraper.append)
        self.console_output_images = ConsoleOutput()
        self.console_output_images.outputWritten.connect(self.console_images.append)
        self.console_output_optimizer = ConsoleOutput()
        self.console_output_optimizer.outputWritten.connect(self.console_optimizer.append)

    def _run_async(self, tab, func, *args, console_output=None, **kwargs):
        if console_output is None:
            console_output = self.console_output_scraper
        worker = Worker(func, *args, console_output=console_output, **kwargs)

        console_widget = tab.console if tab else self.console_scraper
        worker.status.connect(console_widget.append)
        worker.result.connect(self._show_result)

        if tab:
            worker.progress.connect(tab.update_progress)
            tab.start(worker)

        def on_finished():
            self._threads.remove(worker)
            print("Thread terminé")

        worker.finished.connect(on_finished)
        worker.finished.connect(worker.deleteLater)
        self._threads.append(worker)
        worker.start()

    def _show_result(self, message):
        if message:
            show_success(message, self)

    def _show_page(self, page):
        self.stack.setCurrentWidget(page)

    # --- UI construction -------------------------------------------------
    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar using custom widget
        self.sidebar = Sidebar()
        for text in [
            "Scraper",
            "Scraping d'image",
            "Optimiser Images",
            "Sélecteur visuel",
            "API Flask",
            "Paramètres",
        ]:
            self.sidebar.addItem(text)

        main_layout.addWidget(self.sidebar)

        # Stacked pages
        self.stack = QStackedLayout()
        main_layout.addLayout(self.stack)

        # Pages
        self.page_scraper = self._create_scraper_page()
        self.page_image = self._create_image_page()
        self.page_selector = self._create_visual_selector_page()
        self.page_optimizer = self._create_optimizer_page()
        self.page_api = self._create_api_page()
        self.page_settings = self._create_settings_page()

        self.stack.addWidget(self.page_scraper)
        self.stack.addWidget(self.page_image)
        self.stack.addWidget(self.page_selector)
        self.stack.addWidget(self.page_optimizer)
        self.stack.addWidget(self.page_api)
        self.stack.addWidget(self.page_settings)

        pages = [
            self.page_scraper,
            self.page_image,
            self.page_optimizer,
            self.page_selector,
            self.page_api,
            self.page_settings,
        ]
        self.sidebar.currentRowChanged.connect(lambda i: self.stack.setCurrentWidget(pages[i]))

        # Apply centralized theme
        apply_theme(self)

    def _create_scraper_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        id_layout = QHBoxLayout()
        self.input_start = QLineEdit()
        self.input_start.setPlaceholderText("ID début")
        self.input_end = QLineEdit()
        self.input_end.setPlaceholderText("ID fin")
        id_layout.addWidget(QLabel("ID début"))
        id_layout.addWidget(self.input_start)
        id_layout.addWidget(QLabel("ID fin"))
        id_layout.addWidget(self.input_end)
        layout.addLayout(id_layout)

        folder_layout = QVBoxLayout()

        parent_layout = QHBoxLayout()
        self.input_parent = QLineEdit()
        self.input_parent.setPlaceholderText("Dossier parent")
        parent_layout.addWidget(self.input_parent)
        btn_parent = RoundButton("Parcourir…")
        btn_parent.clicked.connect(self._choose_parent)
        parent_layout.addWidget(btn_parent)
        folder_layout.addLayout(parent_layout)

        name_layout = QHBoxLayout()
        self.input_folder_name = QLineEdit()
        self.input_folder_name.setPlaceholderText("Nom dossier de résultats")
        name_layout.addWidget(self.input_folder_name)
        btn_new_folder = RoundButton("Créer dossier")
        btn_new_folder.clicked.connect(self._create_folder)
        name_layout.addWidget(btn_new_folder)
        folder_layout.addLayout(name_layout)

        self.label_full_path = QLabel("")
        folder_layout.addWidget(self.label_full_path)

        self.input_parent.textChanged.connect(self._update_full_path)
        self.input_folder_name.textChanged.connect(self._update_full_path)
        self._update_full_path()

        layout.addLayout(folder_layout)

        liens_layout = QHBoxLayout()
        self.input_liens_file = QLineEdit(self.scraper.liens_id_txt)
        liens_layout.addWidget(self.input_liens_file)
        btn_liens = RoundButton("Charger fichier")
        btn_liens.clicked.connect(self._choose_liens_file)
        liens_layout.addWidget(btn_liens)
        btn_add_link = RoundButton("Ajouter lien")
        btn_add_link.clicked.connect(self._add_single_link)
        liens_layout.addWidget(btn_add_link)
        layout.addLayout(liens_layout)

        self.cb_variantes = QCheckBox("Scraper variantes")
        self.cb_concurrents = QCheckBox("Scraper concurrents")
        self.cb_export_json = QCheckBox("Exporter JSON")
        layout.addWidget(self.cb_variantes)
        layout.addWidget(self.cb_concurrents)
        layout.addWidget(self.cb_export_json)

        batch_json_layout = QHBoxLayout()
        batch_json_layout.addWidget(QLabel("Taille batch JSON"))
        self.spin_json_batch = QSpinBox()
        self.spin_json_batch.setRange(1, 1000)
        self.spin_json_batch.setValue(50)
        batch_json_layout.addWidget(self.spin_json_batch)
        layout.addLayout(batch_json_layout)

        self.btn_start = RoundButton("Lancer l'exécution")
        self.btn_start.clicked.connect(self._on_start_scraper)
        layout.addWidget(self.btn_start)
        self.btn_stop = RoundButton("Arrêter", color="secondary")
        self.btn_stop.clicked.connect(lambda: self._stop_worker(self.scraper_tab))
        layout.addWidget(self.btn_stop)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet(
            "QProgressBar {border:1px solid #444; border-radius:8px; text-align:center; height:25px;}"
            "QProgressBar::chunk {background-color:#444; border-radius:8px;}"
        )
        layout.addWidget(self.progress_bar)
        self.label_time = QLabel("")
        layout.addWidget(self.label_time)

        # Console for scraper tab
        self.console_scraper = QTextEdit()
        self.console_scraper.setReadOnly(True)
        self.console_scraper.setFixedHeight(200)

        btn_clear_console = RoundButton("Vider la console", color="secondary")
        btn_clear_console.clicked.connect(self.console_scraper.clear)
        layout.addWidget(btn_clear_console)
        layout.addWidget(self.console_scraper)

        return page

    def _create_image_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        dest_layout = QHBoxLayout()
        self.input_img_folder = QLineEdit()
        self.input_img_folder.setPlaceholderText("Dossier images")
        dest_layout.addWidget(self.input_img_folder)
        btn_dest = RoundButton("Parcourir…")
        btn_dest.clicked.connect(self._choose_img_folder)
        dest_layout.addWidget(btn_dest)
        layout.addLayout(dest_layout)

        links_layout = QHBoxLayout()
        self.input_img_links = QLineEdit(self.scraper.liens_id_txt)
        links_layout.addWidget(self.input_img_links)
        btn_links = RoundButton("Charger fichier")
        btn_links.clicked.connect(self._choose_img_links)
        links_layout.addWidget(btn_links)
        layout.addLayout(links_layout)

        single_layout = QHBoxLayout()
        self.input_single_url = QLineEdit()
        self.input_single_url.setPlaceholderText("Lien produit")
        btn_test = RoundButton("Tester lien")
        btn_test.clicked.connect(self._on_test_single_image)
        single_layout.addWidget(self.input_single_url)
        single_layout.addWidget(btn_test)
        layout.addLayout(single_layout)

        self.cb_preview_images = QCheckBox("Afficher aperçu images")
        layout.addWidget(self.cb_preview_images)

        # Filtering controls ---------------------------------------
        size_layout = QHBoxLayout()
        self.cb_filter_size = QCheckBox("Taille >=")
        self.spin_min_w = QSpinBox()
        self.spin_min_w.setRange(0, 5000)
        self.spin_min_w.setValue(0)
        self.spin_min_h = QSpinBox()
        self.spin_min_h.setRange(0, 5000)
        self.spin_min_h.setValue(0)
        size_layout.addWidget(self.cb_filter_size)
        size_layout.addWidget(self.spin_min_w)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.spin_min_h)
        layout.addLayout(size_layout)

        ratio_layout = QHBoxLayout()
        self.cb_filter_ratio = QCheckBox("Ratio >=")
        self.spin_ratio = QDoubleSpinBox()
        self.spin_ratio.setDecimals(2)
        self.spin_ratio.setRange(0.1, 10.0)
        self.spin_ratio.setSingleStep(0.1)
        self.spin_ratio.setValue(1.0)
        ratio_layout.addWidget(self.cb_filter_ratio)
        ratio_layout.addWidget(self.spin_ratio)
        layout.addLayout(ratio_layout)

        type_layout = QHBoxLayout()
        self.cb_filter_type = QCheckBox("Type")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["png", "jpg", "jpeg", "webp"])
        type_layout.addWidget(self.cb_filter_type)
        type_layout.addWidget(self.combo_type)
        layout.addLayout(type_layout)

        self.btn_start_images = RoundButton("Lancer scraping images")
        self.btn_start_images.clicked.connect(self._on_start_images)
        layout.addWidget(self.btn_start_images)
        self.btn_stop_images = RoundButton("Arrêter", color="secondary")
        self.btn_stop_images.clicked.connect(lambda: self._stop_worker(self.images_tab))
        layout.addWidget(self.btn_stop_images)

        self.progress_bar_img = QProgressBar()
        self.progress_bar_img.setRange(0, 100)
        self.progress_bar_img.setFixedHeight(25)
        self.progress_bar_img.setStyleSheet(
            "QProgressBar {border:1px solid #444; border-radius:8px; text-align:center; height:25px;}"
            "QProgressBar::chunk {background-color:#444; border-radius:8px;}"
        )
        layout.addWidget(self.progress_bar_img)
        self.label_time_img = QLabel("")
        layout.addWidget(self.label_time_img)

        # Console for image scraping tab
        self.console_images = QTextEdit()
        self.console_images.setReadOnly(True)
        self.console_images.setFixedHeight(200)

        btn_clear_console_img = RoundButton("Vider la console", color="secondary")
        btn_clear_console_img.clicked.connect(self.console_images.clear)
        layout.addWidget(btn_clear_console_img)
        layout.addWidget(self.console_images)

        self.preview_list = QListWidget()
        self.preview_list.setViewMode(QListWidget.IconMode)
        self.preview_list.setIconSize(QSize(80, 80))
        self.preview_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.preview_list)

        btn_save = RoundButton("Enregistrer la sélection")
        btn_save.clicked.connect(self._save_selected_images)
        layout.addWidget(btn_save)

        return page

    def _create_visual_selector_page(self):
        from ui.visual_selector import VisualSelectorPage
        page = VisualSelectorPage()
        return page

    def _create_optimizer_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        folder_layout = QHBoxLayout()
        self.input_opt_folder = QLineEdit()
        self.input_opt_folder.setPlaceholderText("Dossier à optimiser")
        folder_layout.addWidget(self.input_opt_folder)
        btn_browse = RoundButton("Parcourir…")
        btn_browse.clicked.connect(self._choose_opt_folder)
        folder_layout.addWidget(btn_browse)
        layout.addLayout(folder_layout)

        self.btn_start_opt = RoundButton("Lancer l’optimisation")
        self.btn_start_opt.clicked.connect(self._on_start_optimizer)
        layout.addWidget(self.btn_start_opt)
        self.btn_stop_opt = RoundButton("Arrêter", color="secondary")
        self.btn_stop_opt.clicked.connect(lambda: self._stop_worker(self.optimizer_tab))
        layout.addWidget(self.btn_stop_opt)

        self.progress_bar_opt = QProgressBar()
        self.progress_bar_opt.setRange(0, 100)
        self.progress_bar_opt.setFixedHeight(25)
        self.progress_bar_opt.setStyleSheet(
            "QProgressBar {border:1px solid #444; border-radius:8px; text-align:center; height:25px;}"
            "QProgressBar::chunk {background-color:#444; border-radius:8px;}"
        )
        layout.addWidget(self.progress_bar_opt)
        self.label_time_opt = QLabel("")
        layout.addWidget(self.label_time_opt)

        self.console_optimizer = QTextEdit()
        self.console_optimizer.setReadOnly(True)
        self.console_optimizer.setFixedHeight(200)

        console_btns = QHBoxLayout()
        btn_clear = RoundButton("Vider la console", color="secondary")
        btn_clear.clicked.connect(self.console_optimizer.clear)
        console_btns.addWidget(btn_clear)
        btn_save = RoundButton("Sauvegarder log")
        btn_save.clicked.connect(self._save_opt_log)
        console_btns.addWidget(btn_save)
        layout.addLayout(console_btns)
        layout.addWidget(self.console_optimizer)

        return page

    def _create_api_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.btn_activate_flask = RoundButton("Activer Flask")
        self.btn_activate_flask.clicked.connect(self._on_activate_flask)
        layout.addWidget(self.btn_activate_flask)
        self.btn_stop_api = RoundButton("Arrêter", color="secondary")
        self.btn_stop_api.clicked.connect(self._stop_worker)
        layout.addWidget(self.btn_stop_api)

        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Batch"))
        self.spin_batch = QSpinBox()
        self.spin_batch.setRange(1, 1000)
        self.spin_batch.setValue(15)
        batch_layout.addWidget(self.spin_batch)
        layout.addLayout(batch_layout)

        fiches_layout = QHBoxLayout()
        self.input_fiche_folder = QLineEdit()
        self.input_fiche_folder.setPlaceholderText("Dossier des fiches")
        fiches_layout.addWidget(self.input_fiche_folder)
        btn_browse_fiche = RoundButton("Parcourir")
        btn_browse_fiche.clicked.connect(self._choose_fiche_folder)
        fiches_layout.addWidget(btn_browse_fiche)
        layout.addLayout(fiches_layout)

        btn_upload = RoundButton("Uploader fiche")
        btn_list = RoundButton("Lister fiches")
        btn_upload.clicked.connect(self._on_upload_fiche)
        btn_list.clicked.connect(self._on_list_fiches)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_upload)
        btn_layout.addWidget(btn_list)
        layout.addLayout(btn_layout)

        return page

    def _create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Chemin du chromedriver (optionnel)"))
        driver_layout = QHBoxLayout()
        self.input_driver_path = QLineEdit(config.CHROME_DRIVER_PATH or "")
        self.input_driver_path.setPlaceholderText(
            "Laisser vide pour téléchargement automatique"
        )
        btn_driver = RoundButton("Parcourir")
        btn_driver.clicked.connect(self._choose_driver_path)
        self.input_driver_path.editingFinished.connect(self._save_config)
        driver_layout.addWidget(self.input_driver_path)
        driver_layout.addWidget(btn_driver)
        layout.addLayout(driver_layout)

        layout.addWidget(QLabel("Chemin du navigateur Chrome (optionnel)"))
        binary_layout = QHBoxLayout()
        self.input_binary_path = QLineEdit(config.CHROME_BINARY_PATH or "")
        self.input_binary_path.setPlaceholderText(
            "Laisser vide si Chrome est dans le PATH"
        )
        btn_binary = RoundButton("Parcourir")
        btn_binary.clicked.connect(self._choose_binary_path)
        self.input_binary_path.editingFinished.connect(self._save_config)
        binary_layout.addWidget(self.input_binary_path)
        binary_layout.addWidget(btn_binary)
        layout.addLayout(binary_layout)

        layout.addWidget(QLabel("Chemin d'optipng.exe"))
        optipng_layout = QHBoxLayout()
        self.input_optipng_path = QLineEdit(config.OPTIPNG_PATH)
        btn_optipng = RoundButton("Parcourir…")
        btn_optipng.clicked.connect(self._choose_optipng_path)
        self.input_optipng_path.editingFinished.connect(self._save_config)
        optipng_layout.addWidget(self.input_optipng_path)
        optipng_layout.addWidget(btn_optipng)
        layout.addLayout(optipng_layout)

        layout.addWidget(QLabel("Chemin de cwebp.exe"))
        cwebp_layout = QHBoxLayout()
        self.input_cwebp_path = QLineEdit(config.CWEBP_PATH)
        btn_cwebp = RoundButton("Parcourir…")
        btn_cwebp.clicked.connect(self._choose_cwebp_path)
        self.input_cwebp_path.editingFinished.connect(self._save_config)
        cwebp_layout.addWidget(self.input_cwebp_path)
        cwebp_layout.addWidget(btn_cwebp)
        layout.addLayout(cwebp_layout)

        self.cb_headless = QCheckBox("Mode sans tête (headless)")
        self.cb_headless.setChecked(True)
        layout.addWidget(self.cb_headless)

        return page

    def _stop_worker(self, tab=None):
        if tab:
            if tab.current_worker:
                tab.current_worker.stop()
        else:
            for t in (self.scraper_tab, self.images_tab, self.optimizer_tab):
                if t.current_worker:
                    t.current_worker.stop()

    # --- Logic ----------------------------------------------------------
    def _on_start_scraper(self):
        start_id = self.input_start.text().strip().upper()
        end_id = self.input_end.text().strip().upper()
        liens_file = self.input_liens_file.text().strip() or None
        ids = self.scraper.charger_liste_ids(liens_file)

        try:
            start_idx = ids.index(start_id) if start_id else 0
        except ValueError:
            start_idx = 0
        try:
            end_idx = ids.index(end_id) if end_id else len(ids) - 1
        except ValueError:
            end_idx = len(ids) - 1

        ids_selectionnes = ids[start_idx:end_idx + 1]

        parent = self.input_parent.text().strip() or self.scraper.base_dir
        name = self.input_folder_name.text().strip() or "results"
        base = parent

        driver_path = self.input_driver_path.text() or config.CHROME_DRIVER_PATH
        binary_path = self.input_binary_path.text() or config.CHROME_BINARY_PATH
        headless = self.cb_headless.isChecked()

        def task(progress_callback, should_stop):
            self.scraper.prepare_results_dir(base, name)
            id_url_map = self.scraper.charger_liens_avec_id(liens_file)
            id_url_map.update(self.extra_links)

            sections = []
            if self.cb_variantes.isChecked():
                sections.append('variantes')
            if self.cb_concurrents.isChecked():
                sections.append('concurrents')
            if self.cb_export_json.isChecked():
                sections.append('json')

            total = len(sections)
            done = 0
            summary = []

            def scaled_progress(p):
                overall = int(done / total * 100 + p / total)
                progress_callback(overall)

            if 'variantes' in sections:
                ok, err = self.scraper.scrap_produits_par_ids(
                    id_url_map, ids_selectionnes, driver_path, binary_path,
                    progress_callback=scaled_progress, should_stop=should_stop,
                    headless=headless)
                summary.append(f"Variantes: {ok} OK, {err} erreurs")
                done += 1

            if 'concurrents' in sections:
                ok, err = self.scraper.scrap_fiches_concurrents(
                    id_url_map, ids_selectionnes, driver_path, binary_path,
                    progress_callback=scaled_progress, should_stop=should_stop,
                    headless=headless)
                summary.append(f"Concurrents: {ok} OK, {err} erreurs")
                done += 1

            if 'json' in sections:
                self.scraper.export_fiches_concurrents_json(
                    self.spin_json_batch.value(), progress_callback=scaled_progress, should_stop=should_stop)
                summary.append("Export JSON terminé")
                done += 1

            progress_callback(100)
            return "\n".join(summary)

        self._run_async(self.scraper_tab, task, console_output=self.console_output_scraper)

    def _on_activate_flask(self):
        folder = self.input_fiche_folder.text() or self.scraper.save_directory
        batch = self.spin_batch.value()

        def task(progress_callback, should_stop):
            self.scraper.run_flask_server(folder, batch)

        self._run_async(None, task, console_output=self.console_output_scraper)

    def _on_upload_fiche(self):
        folder = self.input_fiche_folder.text()

        def task(progress_callback, should_stop):
            if not folder:
                print("Aucun dossier de fiches défini.")
                return
            for filename in os.listdir(folder):
                if filename.endswith(".txt"):
                    path = os.path.join(folder, filename)
                    self.scraper.upload_fiche(path)

        self._run_async(None, task, console_output=self.console_output_scraper)

    def _on_list_fiches(self):
        def task(progress_callback, should_stop):
            self.scraper.list_fiches()

        self._run_async(None, task, console_output=self.console_output_scraper)

    def _choose_parent(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier")
        if folder:
            self.input_parent.setText(folder)

    def _update_full_path(self):
        parent = self.input_parent.text() or self.scraper.base_dir
        name = self.input_folder_name.text() or "results"
        self.label_full_path.setText(os.path.join(parent, name))

    def _choose_fiche_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier des fiches")
        if folder:
            self.input_fiche_folder.setText(folder)

    def _choose_driver_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir chromedriver")
        if path:
            self.input_driver_path.setText(path)
            self._save_config()

    def _choose_binary_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir le binaire Chrome")
        if path:
            self.input_binary_path.setText(path)
            self._save_config()

    def _choose_optipng_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir optipng")
        if path:
            self.input_optipng_path.setText(path)
            self._save_config()

    def _choose_cwebp_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir cwebp")
        if path:
            self.input_cwebp_path.setText(path)
            self._save_config()

    def _create_folder(self):
        name, ok = QInputDialog.getText(self, "Créer dossier", "Nom du dossier")
        if ok and name:
            base = self.input_parent.text() or self.scraper.base_dir
            final_name = name
            path = os.path.join(base, final_name)

            if os.path.exists(path):
                suffix = 1
                # Find next available suffix
                new_path = os.path.join(base, f"{name}_{suffix}")
                while os.path.exists(new_path):
                    suffix += 1
                    new_path = os.path.join(base, f"{name}_{suffix}")

                reply = QMessageBox.warning(
                    self,
                    "Dossier existe",
                    f"{path} existe déjà.\nCréer {os.path.basename(new_path)} ?",
                    QMessageBox.Yes | QMessageBox.Cancel,
                )

                if reply == QMessageBox.Yes:
                    final_name = os.path.basename(new_path)
                    path = new_path
                else:
                    return

            try:
                os.makedirs(path, exist_ok=False)
                self.input_parent.setText(base)
                self.input_folder_name.setText(final_name)
                self._update_full_path()
                show_success(f"Créé : {path}", self)
            except Exception as e:
                show_error(f"Erreur création : {e}", self)

    def _choose_liens_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir fichier liens")
        if path:
            self.input_liens_file.setText(path)

    def _choose_img_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier images")
        if folder:
            self.input_img_folder.setText(folder)

    def _choose_img_links(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir fichier liens")
        if path:
            self.input_img_links.setText(path)

    def _choose_opt_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier à optimiser")
        if folder:
            self.input_opt_folder.setText(folder)

    def _save_opt_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder log", filter="Text files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.console_optimizer.toPlainText())

    def _save_config(self):
        data = config_manager.load()
        data.update({
            "CHROME_DRIVER_PATH": self.input_driver_path.text().strip() or None,
            "CHROME_BINARY_PATH": self.input_binary_path.text().strip() or None,
            "OPTIPNG_PATH": self.input_optipng_path.text().strip() or config.OPTIPNG_PATH,
            "CWEBP_PATH": self.input_cwebp_path.text().strip() or config.CWEBP_PATH,
        })
        config_manager.save(data)
        config.reload()
    def _on_start_images(self):
        dest = self.input_img_folder.text().strip() or os.path.join(self.scraper.base_dir, "images")
        links_file = self.input_img_links.text().strip() or self.scraper.liens_id_txt
        urls = self.scraper.charger_liste_urls(links_file)
        show_preview = self.cb_preview_images.isChecked()
        headless = self.cb_headless.isChecked()
        self.preview_list.clear()
        self.pending_images = []

        min_w = self.spin_min_w.value() if self.cb_filter_size.isChecked() else 0
        min_h = self.spin_min_h.value() if self.cb_filter_size.isChecked() else 0
        ratio = self.spin_ratio.value() if self.cb_filter_ratio.isChecked() else 0.0
        ftype = self.combo_type.currentText() if self.cb_filter_type.isChecked() else ""

        def preview(temp_path, final_path):
            if show_preview:
                item = QListWidgetItem(QIcon(temp_path), os.path.basename(final_path))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setData(Qt.UserRole, (temp_path, final_path))
                self.preview_list.addItem(item)
                self.pending_images.append((temp_path, final_path))

        def task(progress_callback, should_stop):
            return self.scraper.scrap_images(
                urls,
                dest,
                driver_path=self.input_driver_path.text() or config.CHROME_DRIVER_PATH,
                binary_path=self.input_binary_path.text() or config.CHROME_BINARY_PATH,
                progress_callback=progress_callback,
                preview_callback=preview,
                should_stop=should_stop,
                headless=headless,
                collect_only=show_preview,
                min_width=min_w,
                min_height=min_h,
                min_ratio=ratio,
                file_type=ftype,
            )

        self._run_async(self.images_tab, task, console_output=self.console_output_images)

    def _on_test_single_image(self):
        url = self.input_single_url.text().strip()
        if not url:
            show_error("Veuillez saisir un lien valide", self)
            return
        dest = self.input_img_folder.text().strip() or os.path.join(self.scraper.base_dir, "images")
        show_preview = self.cb_preview_images.isChecked()
        headless = self.cb_headless.isChecked()
        self.preview_list.clear()
        self.pending_images = []

        min_w = self.spin_min_w.value() if self.cb_filter_size.isChecked() else 0
        min_h = self.spin_min_h.value() if self.cb_filter_size.isChecked() else 0
        ratio = self.spin_ratio.value() if self.cb_filter_ratio.isChecked() else 0.0
        ftype = self.combo_type.currentText() if self.cb_filter_type.isChecked() else ""

        def preview(temp_path, final_path):
            if show_preview:
                item = QListWidgetItem(QIcon(temp_path), os.path.basename(final_path))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setData(Qt.UserRole, (temp_path, final_path))
                self.preview_list.addItem(item)
                self.pending_images.append((temp_path, final_path))

        def task(progress_callback, should_stop):
            return self.scraper.scrap_images(
                [url],
                dest,
                driver_path=self.input_driver_path.text() or config.CHROME_DRIVER_PATH,
                binary_path=self.input_binary_path.text() or config.CHROME_BINARY_PATH,
                progress_callback=progress_callback,
                preview_callback=preview,
                should_stop=should_stop,
                headless=headless,
                collect_only=show_preview,
                min_width=min_w,
                min_height=min_h,
                min_ratio=ratio,
                file_type=ftype,
            )

        self._run_async(self.images_tab, task, console_output=self.console_output_images)

    def _save_selected_images(self):
        if not getattr(self, "pending_images", None):
            return
        dest_hashes = set()

        def file_hash(path):
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()

        for root, _, files in os.walk(self.input_img_folder.text() or os.path.join(self.scraper.base_dir, "images")):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    dest_hashes.add(file_hash(fp))
                except Exception:
                    pass

        for i in range(self.preview_list.count()):
            item = self.preview_list.item(i)
            temp_path, final_path = item.data(Qt.UserRole)
            if item.checkState() != Qt.Checked:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                continue
            h = file_hash(temp_path)
            if h in dest_hashes:
                os.remove(temp_path)
                continue
            dest_hashes.add(h)
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            if os.path.exists(final_path):
                os.remove(final_path)
            os.rename(temp_path, final_path)

        show_success("Images sauvegardées", self)
        self.preview_list.clear()
        self.pending_images = []

    def _on_start_optimizer(self):
        folder = self.input_opt_folder.text().strip()
        if not folder:
            show_error("Veuillez choisir un dossier valide", self)
            return

        optipng = self.input_optipng_path.text().strip() or config.OPTIPNG_PATH
        cwebp = self.input_cwebp_path.text().strip() or config.CWEBP_PATH
        self._save_config()

        missing = []
        if not os.path.isfile(optipng):
            missing.append((optipng, "https://sourceforge.net/projects/optipng/"))
        if not os.path.isfile(cwebp):
            missing.append((cwebp, "https://developers.google.com/speed/webp/download"))
        if missing:
            msg = "<b>Outils manquants :</b><ul>"
            for path, url in missing:
                msg += f"<li>{path} (<a href='{url}'>télécharger</a>)</li>"
            msg += "</ul>"
            box = QMessageBox(self)
            box.setWindowTitle("Outils manquants")
            box.setTextFormat(Qt.RichText)
            box.setText(msg)
            box.exec()
            return

        image_files = []
        for root, _, filenames in os.walk(folder):
            for f in filenames:
                if f.lower().endswith((".png", ".webp")):
                    image_files.append(os.path.join(root, f))

        if not image_files:
            show_error("Aucun fichier PNG ou WebP trouvé dans ce dossier", self)
            return

        optimizer = ImageOptimizer(optipng, cwebp)

        def task(progress_callback, should_stop):
            total = len(image_files)
            for i, log in enumerate(optimizer.iter_optimize_folder(folder), 1):
                if should_stop():
                    break
                self.console_output_optimizer.outputWritten.emit(log)
                progress_callback(int(i / total * 100))
            progress_callback(100)
            return f"Optimisation terminée : {total} fichier(s)"

        self._run_async(self.optimizer_tab, task, console_output=self.console_output_optimizer)

    def _add_single_link(self):
        text, ok = QInputDialog.getText(self, "Ajouter lien", "ID|URL")
        if ok and text:
            parts = text.split("|", 1)
            if len(parts) == 2:
                ident, url = parts[0].strip().upper(), parts[1].strip()
                self.extra_links[ident] = url
                self.scraper_tab.console.append(f"Ajouté {ident} -> {url}")
            else:
                show_error("Utiliser ID|URL", self)

    def closeEvent(self, event):
        """Ensure all running threads are stopped before closing."""
        for worker in list(self._threads):
            worker.stop()
            worker.quit()
            worker.wait()
        print("Tous les threads correctement arrêtés, fermeture propre.")
        super().closeEvent(event)
