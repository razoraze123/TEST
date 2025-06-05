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

import json
import os
from urllib.parse import urlparse

# Path to the JSON file storing selectors
SELECTORS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "selectors.json")


def load_selectors():
    if os.path.isfile(SELECTORS_FILE):
        try:
            with open(SELECTORS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_selectors(data):
    try:
        with open(SELECTORS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde sélecteurs: {e}")


def save_selector(url, selector):
    data = load_selectors()
    domain = urlparse(url).netloc or url
    data[domain] = selector
    save_selectors(data)


class JSBridge(QObject):
    selectorReceived = Signal(str)

    @Slot(str)
    def selectorSelected(self, selector):
        self.selectorReceived.emit(selector)


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
        self.btn_save = QPushButton("Sauvegarder")
        sel_layout.addWidget(self.input_selector)
        sel_layout.addWidget(self.btn_copy)
        sel_layout.addWidget(self.btn_save)
        layout.addLayout(sel_layout)

        # Bridge for JS -> Python communication
        self.bridge = JSBridge()
        self.bridge.selectorReceived.connect(self.input_selector.setText)
        self.channel = QWebChannel()
        self.channel.registerObject("pyObj", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        self.btn_open.clicked.connect(self.load_url)
        self.btn_copy.clicked.connect(self.copy_selector)
        self.btn_save.clicked.connect(self.save_current_selector)
        self.webview.loadFinished.connect(self.inject_js)

    def load_url(self):
        url = self.input_url.text().strip()
        if url:
            self.webview.load(QUrl(url))

    def copy_selector(self):
        QApplication.clipboard().setText(self.input_selector.text())

    def save_current_selector(self):
        url = self.input_url.text().strip()
        selector = self.input_selector.text().strip()
        if url and selector:
            save_selector(url, selector)

    def inject_js(self):
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
                document.addEventListener('mouseover', function(e){
                    e.target.__oldOutline = e.target.style.outline;
                    e.target.style.outline = '2px solid red';
                }, true);
                document.addEventListener('mouseout', function(e){
                    e.target.style.outline = e.target.__oldOutline || '';
                }, true);
                document.addEventListener('click', function(e){
                    e.preventDefault();
                    e.stopPropagation();
                    var sel = cssPath(e.target);
                    if (window.pyObj && window.pyObj.selectorSelected) {
                        window.pyObj.selectorSelected(sel);
                    }
                }, true);
            })();
        """
        self.webview.page().runJavaScript(js)
