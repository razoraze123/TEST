from PySide6.QtCore import QObject, Signal, Slot, QUrl
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineScript
import PySide6

import os
import logging

from urllib.parse import urlparse
import storage

# Try loading qwebchannel.js from the packaged resources first.
_local_qwebchannel = os.path.join(
    os.path.dirname(__file__), "resources", "qwebchannel.js"
)
if os.path.isfile(_local_qwebchannel):
    with open(_local_qwebchannel, "r", encoding="utf-8") as f:
        QWEBCHANNEL_JS = f.read()
else:
    # Fall back to the copy shipped with PySide6
    _pyside_path = os.path.join(
        os.path.dirname(PySide6.__file__),
        "Qt",
        "resources",
        "qtwebchannel",
        "qwebchannel.js",
    )
    with open(_pyside_path, "r", encoding="utf-8") as f:
        QWEBCHANNEL_JS = f.read()


def load_selectors():
    return storage.load_selectors()


def save_selector(url: str, selector: str) -> None:
    storage.save_selector(url, selector)


class JSBridge(QObject):
    selectorReceived = Signal(str)
    hoverReceived = Signal(str)

    @Slot(str)
    def selectorSelected(self, selector):
        logging.info("Selector selected: %s", selector)
        self.selectorReceived.emit(selector)

    @Slot(str)
    def elementHovered(self, selector):
        logging.info("Selector hovered: %s", selector)
        self.hoverReceived.emit(selector)


class VisualSelectorWindow(QWidget):
    """Fenêtre contenant l'aperçu web du sélecteur."""

    selectorReceived = Signal(str)
    hoverReceived = Signal(str)
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aperçu sélecteur")
        layout = QVBoxLayout(self)

        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        # Bridge JS -> Python
        self.bridge = JSBridge()
        self.bridge.selectorReceived.connect(self.selectorReceived)
        self.bridge.hoverReceived.connect(self.hoverReceived)
        self.channel = QWebChannel()
        self.channel.registerObject("pyObj", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        # Chargement automatique de qwebchannel.js
        self._qweb_script = QWebEngineScript()
        self._qweb_script.setSourceCode(QWEBCHANNEL_JS)
        self._qweb_script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        self._qweb_script.setWorldId(QWebEngineScript.MainWorld)
        self.webview.page().scripts().insert(self._qweb_script)

        self.webview.loadFinished.connect(self.inject_js)

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)

    # ------------------------------------------------------------------
    def load_url(self, url: str) -> None:
        self.webview.load(QUrl(url))

    # ------------------------------------------------------------------
    def highlight_selector(self, selector: str) -> None:
        if not selector:
            return
        js = f"""
            (function() {{
                document.querySelectorAll('.__py_highlight').forEach(function(e) {{
                    e.style.outline = e.__oldOutline || '';
                    e.classList.remove('__py_highlight');
                }});
                try {{
                    document.querySelectorAll('{selector}').forEach(function(el) {{
                        el.__oldOutline = el.style.outline;
                        el.style.outline = '2px dashed blue';
                        el.classList.add('__py_highlight');
                    }});
                }} catch(e) {{}}
            }})();
        """
        self.webview.page().runJavaScript(js)

    # ------------------------------------------------------------------
    def inject_js(self) -> None:
        logging.info("Injecting JavaScript into page")

        js_channel = """
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pyObj = channel.objects.pyObj;
            });
        """

        js = """
            (function() {
                function cssPath(el) {
                    if (!(el instanceof Element)) return '';
                    var path = [];
                    while (el.nodeType === Node.ELEMENT_NODE) {
                        var selector = el.nodeName.toLowerCase();
                        if (el.id) {
                            selector += '#' + el.id;
                            path.unshift(selector);
                            break;
                        } else {
                            var sib = el, nth = 1;
                            while (sib = sib.previousElementSibling) {
                                if (sib.nodeName.toLowerCase() === selector)
                                    nth++;
                            }
                            if (nth !== 1)
                                selector += ':nth-of-type(' + nth + ')';
                        }
                        path.unshift(selector);
                        el = el.parentNode;
                    }
                    return path.join(' > ');
                }

                function highlight(el) {
                    el.__oldOutline = el.style.outline;
                    el.style.outline = '2px solid red';
                }

                function unhighlight(el) {
                    el.style.outline = el.__oldOutline || '';
                }

                document.addEventListener('mouseover', function(e) {
                    highlight(e.target);
                    var sel = cssPath(e.target);
                    if (window.pyObj && window.pyObj.elementHovered) {
                        window.pyObj.elementHovered(sel);
                    }
                }, true);

                document.addEventListener('mouseout', function(e) {
                    unhighlight(e.target);
                }, true);

                document.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    var sel = cssPath(e.target);
                    if (window.pyObj && window.pyObj.selectorSelected) {
                        window.pyObj.selectorSelected(sel);
                    }
                }, true);
            })();
        """

        page = self.webview.page()

        def _after_check(res):
            logging.info("QWebChannel present: %s", res)
            assert res, "qwebchannel.js not loaded"
            page.runJavaScript(js_channel)
            page.runJavaScript(js)

        page.runJavaScript("typeof QWebChannel !== 'undefined'", _after_check)


class VisualSelectorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        url_layout = QHBoxLayout()
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("URL de la page")
        self.btn_open = QPushButton("Ouvrir")
        url_layout.addWidget(self.input_url)
        url_layout.addWidget(self.btn_open)
        layout.addLayout(url_layout)

        sel_layout = QHBoxLayout()
        self.input_selector = QLineEdit()
        self.input_selector.setPlaceholderText("Sélecteur généré")
        self.btn_copy = QPushButton("Copier")
        self.btn_test = QPushButton("Tester")
        self.btn_save = QPushButton("Sauvegarder")
        sel_layout.addWidget(self.input_selector)
        sel_layout.addWidget(self.btn_copy)
        sel_layout.addWidget(self.btn_test)
        sel_layout.addWidget(self.btn_save)
        layout.addLayout(sel_layout)

        # Fenêtre externe contenant la page web
        self.selector_window = VisualSelectorWindow(self)
        self.selector_window.selectorReceived.connect(self.input_selector.setText)
        self.selector_window.closed.connect(self._on_window_closed)

        self.btn_open.clicked.connect(self.load_url)
        self.btn_copy.clicked.connect(self.copy_selector)
        self.btn_test.clicked.connect(self.on_test_selector)
        self.btn_save.clicked.connect(self.save_current_selector)
        self.input_selector.textChanged.connect(self.on_test_selector)

    # ------------------------------------------------------------------
    def on_test_selector(self):
        selector = self.input_selector.text().strip()
        self.highlight_selector(selector)

    def highlight_selector(self, selector: str):
        self.selector_window.highlight_selector(selector)

    def load_url(self):
        url = self.input_url.text().strip()
        if url:
            if not self.selector_window.isVisible():
                self.selector_window.show()
            self.selector_window.load_url(url)
            saved = load_selectors().get(urlparse(url).netloc)
            if saved:
                self.input_selector.setText(saved)

    def copy_selector(self):
        QApplication.clipboard().setText(self.input_selector.text())

    def save_current_selector(self):
        url = self.input_url.text().strip()
        selector = self.input_selector.text().strip()
        if url and selector:
            save_selector(url, selector)

    def _on_window_closed(self) -> None:
        pass
