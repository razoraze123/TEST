# Color constants
SIDEBAR_DARK = "#23272F"
PRIMARY_BLUE = "#3386FF"
BACKGROUND_DARK = "#121212"
SURFACE_DARK = "#1e1e1e"
HOVER_DARK = "#2b2b2b"
TEXT_LIGHT = "#f5f5f5"
BORDER_DARK = "#333"

BACKGROUND_LIGHT = "#ffffff"
SURFACE_LIGHT = "#f0f0f0"
TEXT_DARK = "#000000"
BORDER_LIGHT = "#ccc"
HOVER_LIGHT = "#e0e0e0"

# Dark and light theme QSS
DARK_THEME = f"""
QWidget {{
    background-color: {BACKGROUND_DARK};
    color: {TEXT_LIGHT};
    font-size: 14px;
}}
QPushButton {{
    background: {PRIMARY_BLUE};
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background: {HOVER_DARK};
}}
QLineEdit, QSpinBox {{
    background-color: {SURFACE_DARK};
    border: 1px solid {BORDER_DARK};
    padding: 4px;
}}
QTextEdit {{
    background-color: {SURFACE_DARK};
    color: {TEXT_LIGHT};
}}
#Sidebar {{
    background-color: {SIDEBAR_DARK};
    border: none;
    color: white;
}}
QListWidget::item {{padding: 8px; margin: 2px; border-radius: 6px;}}
QListWidget::item:selected {{background: {PRIMARY_BLUE};}}
QFrame[card="true"] {{background: #414141; border-radius: 8px; padding: 16px;}}
"""

LIGHT_THEME = f"""
QWidget {{
    background-color: {BACKGROUND_LIGHT};
    color: {TEXT_DARK};
    font-size: 14px;
}}
QPushButton {{
    background: {PRIMARY_BLUE};
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background: {HOVER_LIGHT};
}}
QLineEdit, QSpinBox {{
    background-color: {SURFACE_LIGHT};
    border: 1px solid {BORDER_LIGHT};
    padding: 4px;
}}
QTextEdit {{
    background-color: {SURFACE_LIGHT};
    color: {TEXT_DARK};
}}
#Sidebar {{
    background-color: {SIDEBAR_DARK};
    border: none;
    color: white;
}}
QListWidget::item {{padding: 8px; margin: 2px; border-radius: 6px;}}
QListWidget::item:selected {{background: {PRIMARY_BLUE};}}
QFrame[card="true"] {{background: #eee; border-radius: 8px; padding: 16px;}}
"""

THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}

def apply_theme(widget, theme="dark"):
    """Apply the selected theme to the given widget."""
    qss = THEMES.get(theme, "")
    widget.setStyleSheet(qss)


def style_progress_bar(bar):
    """Apply consistent styling to a QProgressBar widget."""
    bar.setStyleSheet(
        "QProgressBar {border:1px solid #444; border-radius:8px; text-align:center; height:25px;}"
        f"QProgressBar::chunk {{background-color:{PRIMARY_BLUE}; border-radius:8px;}}"
    )
