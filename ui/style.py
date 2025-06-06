"""Styling helpers with customizable palettes and themes."""

# Default color palettes --------------------------------------------

DARK_PALETTE = {
    "SIDEBAR": "#23272F",
    "PRIMARY": "#3386FF",
    "BACKGROUND": "#121212",
    "SURFACE": "#1e1e1e",
    "HOVER": "#2b2b2b",
    "TEXT": "#f5f5f5",
    "BORDER": "#333",
}

LIGHT_PALETTE = {
    "SIDEBAR": "#23272F",
    "PRIMARY": "#3386FF",
    "BACKGROUND": "#ffffff",
    "SURFACE": "#f0f0f0",
    "HOVER": "#e0e0e0",
    "TEXT": "#000000",
    "BORDER": "#ccc",
}

# Backwards compatibility constants used across the codebase
PRIMARY_BLUE = DARK_PALETTE["PRIMARY"]
SIDEBAR_DARK = DARK_PALETTE["SIDEBAR"]
SURFACE_DARK = DARK_PALETTE["SURFACE"]
BACKGROUND_DARK = DARK_PALETTE["BACKGROUND"]
HOVER_DARK = DARK_PALETTE["HOVER"]
TEXT_LIGHT = DARK_PALETTE["TEXT"]
BORDER_DARK = DARK_PALETTE["BORDER"]

BACKGROUND_LIGHT = LIGHT_PALETTE["BACKGROUND"]
SURFACE_LIGHT = LIGHT_PALETTE["SURFACE"]
TEXT_DARK = LIGHT_PALETTE["TEXT"]
BORDER_LIGHT = LIGHT_PALETTE["BORDER"]
HOVER_LIGHT = LIGHT_PALETTE["HOVER"]


def build_stylesheet(palette: dict, font_size: int = 14) -> str:
    """Return a QSS string using *palette* and *font_size*."""

    return f"""
QWidget {{
    background-color: {palette['BACKGROUND']};
    color: {palette['TEXT']};
    font-size: {font_size}px;
}}
QPushButton {{
    background: {palette['PRIMARY']};
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background: {palette['HOVER']};
}}
QLineEdit, QSpinBox {{
    background-color: {palette['SURFACE']};
    border: 1px solid {palette['BORDER']};
    padding: 4px;
}}
QTextEdit {{
    background-color: {palette['SURFACE']};
    color: {palette['TEXT']};
}}
#Sidebar {{
    background-color: {palette['SIDEBAR']};
    border: none;
    color: white;
}}
QListWidget::item {{padding: 8px; margin: 2px; border-radius: 6px;}}
QListWidget::item[header="true"] {{
    background-color: #1e1e1e;
    color: #f5f5f5;
    margin-top: 6px;
    font-weight: bold;
}}
QListWidget::item:selected {{background: {palette['PRIMARY']};}}
QFrame[card="true"] {{background: #414141; border-radius: 8px; padding: 16px;}}
CollapsibleSection {{
    background-color: {palette['SURFACE']};
    border: 1px solid {palette['BORDER']};
    border-radius: 6px;
    padding: 4px;
}}
CollapsibleSection:hover {{
    background-color: {palette['HOVER']};
}}
"""


THEMES = {
    "dark": DARK_PALETTE,
    "light": LIGHT_PALETTE,
}


def apply_theme(
    widget,
    theme: str = "dark",
    *,
    font_size: int = 14,
    palette: dict | None = None,
) -> None:
    """Apply the selected theme with custom palette and font size."""

    pal = palette or THEMES.get(theme, DARK_PALETTE)
    widget.setStyleSheet(build_stylesheet(pal, font_size))


def style_progress_bar(bar):
    """Apply consistent styling to a QProgressBar widget."""
    bar.setStyleSheet(
        "QProgressBar {border:1px solid #444; border-radius:8px; text-align:center; height:25px;}"
        f"QProgressBar::chunk {{background-color:{DARK_PALETTE['PRIMARY']}; border-radius:8px;}}"
    )


def style_table_widget(table, theme: str = "dark", font_size: int = 14) -> None:
    """Apply consistent styling to table widgets."""
    pal = THEMES.get(theme, DARK_PALETTE)
    table.setStyleSheet(
        f"QTableWidget {{background-color:{pal['SURFACE'] if theme=='dark' else pal['BACKGROUND']}; color:{pal['TEXT']}; gridline-color:{pal['BORDER']};}}"
        f"QHeaderView::section {{background-color:{pal['SIDEBAR'] if theme=='dark' else pal['SURFACE']}; color:{pal['TEXT']}; border:1px solid {pal['BORDER']}; padding:4px; font-size:{font_size}px;}}"
    )
