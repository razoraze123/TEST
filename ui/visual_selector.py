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

        self.webview = QWebEngineView()
        layout.addWidget(self.webview, 1)

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

        # Bridge for JS -> Python communication
        self.bridge = JSBridge()
        self.bridge.selectorReceived.connect(self.input_selector.setText)
        self.channel = QWebChannel()
        self.channel.registerObject("pyObj", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        # Load qwebchannel.js at document creation
        self._qweb_script = QWebEngineScript()
        self._qweb_script.setSourceCode(QWEBCHANNEL_JS)
        self._qweb_script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        self._qweb_script.setWorldId(QWebEngineScript.MainWorld)
        self.webview.page().scripts().insert(self._qweb_script)

        self.btn_open.clicked.connect(self.load_url)
        self.btn_copy.clicked.connect(self.copy_selector)
        self.btn_test.clicked.connect(self.on_test_selector)
        self.btn_save.clicked.connect(self.save_current_selector)
        self.input_selector.textChanged.connect(self.on_test_selector)
        self.webview.loadFinished.connect(self.inject_js)

    # ------------------------------------------------------------------
    def on_test_selector(self):
        selector = self.input_selector.text().strip()
        self.highlight_selector(selector)

    def highlight_selector(self, selector: str):
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

    def load_url(self):
        url = self.input_url.text().strip()
        if url:
            self.webview.load(QUrl(url))
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

    def inject_js(self):
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
                    console.log('hover', sel);
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
                    console.log('click', sel);
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
