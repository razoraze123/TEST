import sys
import os

from PySide6.QtCore import QObject, Signal, Qt, QThread
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
    QVBoxLayout,
    QWidget,
)
from scraper_woocommerce import ScraperCore
import config


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

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._running = True

    def _report(self, value):
        self.progress.emit(value)

    def stop(self):
        """Request the worker to stop."""
        self._running = False
        self.requestInterruption()

    def run(self):
        self.status.emit("start")
        res = None
        try:
            res = self.func(self._report, *self.args, **self.kwargs)
        finally:
            self.status.emit("done")
            self.result.emit(res)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WooCommerce Scraper")
        self.resize(900, 600)
        self.scraper = ScraperCore()
        self._threads = []
        self._setup_ui()
        self._redirect_console()

    def _redirect_console(self):
        self.console_output = ConsoleOutput()
        self.console_output.outputWritten.connect(self.console.append)
        sys.stdout = self.console_output
        sys.stderr = self.console_output

    def _run_async(self, func, *args, **kwargs):
        worker = Worker(func, *args, **kwargs)
        worker.status.connect(self.console.append)
        worker.progress.connect(self.progress_bar.setValue)
        worker.result.connect(self._show_result)
        def on_finished():
            self._threads.remove(worker)
            print("Thread terminé")

        worker.finished.connect(on_finished)
        worker.finished.connect(worker.deleteLater)
        self.progress_bar.setValue(0)
        self._threads.append(worker)
        worker.start()

    def _show_result(self, message):
        if message:
            QMessageBox.information(self, "Terminé", message)

    # --- UI construction -------------------------------------------------
    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        self.btn_scraper = QPushButton("Scraper")
        self.btn_api = QPushButton("API Flask")
        self.btn_settings = QPushButton("Param\u00e8tres")
        for btn in (self.btn_scraper, self.btn_api, self.btn_settings):
            btn.setMinimumHeight(40)
            sidebar_layout.addWidget(btn)

        main_layout.addWidget(sidebar)

        # Stacked pages
        self.stack = QStackedLayout()
        main_layout.addLayout(self.stack)

        # Pages
        self.page_scraper = self._create_scraper_page()
        self.page_api = self._create_api_page()
        self.page_settings = self._create_settings_page()

        self.stack.addWidget(self.page_scraper)
        self.stack.addWidget(self.page_api)
        self.stack.addWidget(self.page_settings)

        self.btn_scraper.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_scraper))
        self.btn_api.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_api))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_settings))

        self.stack.setCurrentWidget(self.page_scraper)

        # Dark theme
        self.setStyleSheet(
            """
            QWidget {
                background-color: #121212;
                color: #f5f5f5;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1e1e1e;
                border: 1px solid #333;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
            QLineEdit, QSpinBox {
                background-color: #1e1e1e;
                border: 1px solid #333;
                padding: 4px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #f5f5f5;
            }
            QCheckBox {
                padding: 2px;
            }
            """
        )

    def _create_scraper_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        id_layout = QHBoxLayout()
        self.input_start = QLineEdit()
        self.input_start.setPlaceholderText("ID d\u00e9but")
        self.input_end = QLineEdit()
        self.input_end.setPlaceholderText("ID fin")
        id_layout.addWidget(QLabel("ID d\u00e9but"))
        id_layout.addWidget(self.input_start)
        id_layout.addWidget(QLabel("ID fin"))
        id_layout.addWidget(self.input_end)
        layout.addLayout(id_layout)

        folder_layout = QHBoxLayout()
        self.input_folder = QLineEdit()
        self.input_folder.setPlaceholderText("Nom dossier de r\u00e9sultats")
        folder_layout.addWidget(self.input_folder)
        btn_browse = QPushButton("Parcourir")
        btn_browse.clicked.connect(self._choose_folder)
        folder_layout.addWidget(btn_browse)
        layout.addLayout(folder_layout)

        self.cb_variantes = QCheckBox("Scraper variantes")
        self.cb_concurrents = QCheckBox("Scraper concurrents")
        self.cb_export_json = QCheckBox("Exporter JSON")
        layout.addWidget(self.cb_variantes)
        layout.addWidget(self.cb_concurrents)
        layout.addWidget(self.cb_export_json)

        self.btn_start = QPushButton("Lancer l'ex\u00e9cution")
        self.btn_start.clicked.connect(self._on_start_scraper)
        layout.addWidget(self.btn_start)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(200)
        layout.addWidget(self.console)

        return page

    def _create_api_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.btn_activate_flask = QPushButton("Activer Flask")
        self.btn_activate_flask.clicked.connect(self._on_activate_flask)
        layout.addWidget(self.btn_activate_flask)

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
        btn_browse_fiche = QPushButton("Parcourir")
        btn_browse_fiche.clicked.connect(self._choose_fiche_folder)
        fiches_layout.addWidget(btn_browse_fiche)
        layout.addLayout(fiches_layout)

        btn_upload = QPushButton("Uploader fiche")
        btn_list = QPushButton("Lister fiches")
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

        layout.addWidget(QLabel("Chemin du chromedriver"))
        driver_layout = QHBoxLayout()
        self.input_driver_path = QLineEdit(config.CHROME_DRIVER_PATH)
        btn_driver = QPushButton("Parcourir")
        btn_driver.clicked.connect(self._choose_driver_path)
        driver_layout.addWidget(self.input_driver_path)
        driver_layout.addWidget(btn_driver)
        layout.addLayout(driver_layout)

        layout.addWidget(QLabel("Chemin du navigateur Chrome"))
        binary_layout = QHBoxLayout()
        self.input_binary_path = QLineEdit(config.CHROME_BINARY_PATH)
        btn_binary = QPushButton("Parcourir")
        btn_binary.clicked.connect(self._choose_binary_path)
        binary_layout.addWidget(self.input_binary_path)
        binary_layout.addWidget(btn_binary)
        layout.addLayout(binary_layout)

        return page

    # --- Logic ----------------------------------------------------------
    def _on_start_scraper(self):
        start_id = self.input_start.text().strip().upper()
        end_id = self.input_end.text().strip().upper()
        ids = self.scraper.charger_liste_ids()

        try:
            start_idx = ids.index(start_id) if start_id else 0
        except ValueError:
            start_idx = 0
        try:
            end_idx = ids.index(end_id) if end_id else len(ids) - 1
        except ValueError:
            end_idx = len(ids) - 1

        ids_selectionnes = ids[start_idx:end_idx + 1]

        result_folder = self.input_folder.text() or "results"

        driver_path = self.input_driver_path.text() or config.CHROME_DRIVER_PATH
        binary_path = self.input_binary_path.text() or config.CHROME_BINARY_PATH

        def task(progress_callback):
            self.scraper.prepare_results_dir(self.scraper.base_dir, result_folder)
            id_url_map = self.scraper.charger_liens_avec_id()

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
                    id_url_map, ids_selectionnes, driver_path, binary_path, progress_callback=scaled_progress)
                summary.append(f"Variantes: {ok} OK, {err} erreurs")
                done += 1

            if 'concurrents' in sections:
                ok, err = self.scraper.scrap_fiches_concurrents(
                    id_url_map, ids_selectionnes, driver_path, binary_path, progress_callback=scaled_progress)
                summary.append(f"Concurrents: {ok} OK, {err} erreurs")
                done += 1

            if 'json' in sections:
                self.scraper.export_fiches_concurrents_json(self.spin_batch.value(), progress_callback=scaled_progress)
                summary.append("Export JSON terminé")
                done += 1

            progress_callback(100)
            return "\n".join(summary)

        self._run_async(task)

    def _on_activate_flask(self):
        folder = self.input_fiche_folder.text() or self.scraper.save_directory
        batch = self.spin_batch.value()

        def task(progress_callback):
            self.scraper.run_flask_server(folder, batch)

        self._run_async(task)

    def _on_upload_fiche(self):
        folder = self.input_fiche_folder.text()

        def task(progress_callback):
            if not folder:
                print("Aucun dossier de fiches défini.")
                return
            for filename in os.listdir(folder):
                if filename.endswith(".txt"):
                    path = os.path.join(folder, filename)
                    self.scraper.upload_fiche(path)

        self._run_async(task)

    def _on_list_fiches(self):
        def task(progress_callback):
            self.scraper.list_fiches()

        self._run_async(task)

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier")
        if folder:
            self.input_folder.setText(folder)

    def _choose_fiche_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier des fiches")
        if folder:
            self.input_fiche_folder.setText(folder)

    def _choose_driver_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir chromedriver")
        if path:
            self.input_driver_path.setText(path)

    def _choose_binary_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir le binaire Chrome")
        if path:
            self.input_binary_path.setText(path)

    def closeEvent(self, event):
        """Ensure all running threads are stopped before closing."""
        for worker in list(self._threads):
            worker.stop()
            worker.quit()
            worker.wait()
        print("Tous les threads correctement arrêtés, fermeture propre.")
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Pour tester : lancez une action puis fermez la fenêtre.
    # Aucun message "QThread: Destroyed while thread" ne doit apparaître.
    sys.exit(app.exec())
