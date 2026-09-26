from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


BACKGROUND = "#0B0D12"
SIDEBAR = "#0F1218"
SURFACE = "#141821"
SURFACE_ALT = "#191E28"
BORDER = "#262C38"
TEXT = "#F4F7FB"
TEXT_MUTED = "#8D97A8"
TEXT_SUBTLE = "#667085"
ACCENT = "#7C5CFC"
ACCENT_HOVER = "#8D72FF"
ACCENT_SOFT = "#201A46"
SUCCESS = "#35D07F"
DANGER = "#FF6B7A"
WARNING = "#F6C85F"


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(SURFACE))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE_ALT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(SURFACE_ALT))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(TEXT_SUBTLE))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)


STYLESHEET = f"""
* {{
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow,
QWidget#Root {{
    background: {BACKGROUND};
}}

QFrame#Sidebar {{
    background: {SIDEBAR};
    border-right: 1px solid {BORDER};
}}

QFrame#TopBar {{
    background: transparent;
    border-bottom: 1px solid {BORDER};
}}

QFrame#Card,
QFrame#Panel {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QFrame#Inspector {{
    background: {SURFACE};
    border-left: 1px solid {BORDER};
}}

QLabel#PageTitle {{
    font-size: 27px;
    font-weight: 700;
}}

QLabel#PageSubtitle {{
    color: {TEXT_MUTED};
    font-size: 13px;
}}

QLabel#MetricTitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 600;
}}

QLabel#MetricValue {{
    font-size: 30px;
    font-weight: 720;
}}

QLabel#SectionTitle {{
    font-size: 15px;
    font-weight: 650;
}}

QLabel#Muted,
QLabel#Meta {{
    color: {TEXT_MUTED};
}}

QLabel#Success {{
    color: {SUCCESS};
    font-weight: 650;
}}

QLabel#BrandMark {{
    background: {ACCENT};
    color: white;
    border-radius: 10px;
    font-size: 18px;
    font-weight: 800;
}}

QPushButton {{
    background: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 9px;
    padding: 8px 12px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: #202632;
    border-color: #343C4B;
}}

QPushButton#PrimaryButton {{
    background: {ACCENT};
    border-color: {ACCENT};
    color: white;
}}

QPushButton#PrimaryButton:hover {{
    background: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}

QPushButton#NavButton {{
    background: transparent;
    border: none;
    border-radius: 9px;
    text-align: left;
    padding: 10px 12px;
    color: {TEXT_MUTED};
    font-weight: 550;
}}

QPushButton#NavButton:hover {{
    background: {SURFACE_ALT};
    color: {TEXT};
}}

QPushButton#NavButton:checked {{
    background: {ACCENT_SOFT};
    color: #D9D0FF;
}}

QLineEdit,
QPlainTextEdit,
QComboBox,
QSpinBox {{
    background: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 9px;
    padding: 8px 10px;
    selection-background-color: {ACCENT};
}}

QLineEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
QSpinBox:focus {{
    border-color: {ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QTableWidget,
QTableView,
QListWidget {{
    background: transparent;
    border: none;
    gridline-color: {BORDER};
    outline: none;
}}

QTableWidget::item,
QTableView::item {{
    border-bottom: 1px solid {BORDER};
    padding: 9px 8px;
}}

QTableWidget::item:selected,
QTableView::item:selected,
QListWidget::item:selected {{
    background: {ACCENT_SOFT};
    color: {TEXT};
}}

QHeaderView::section {{
    background: {SURFACE};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 9px 8px;
    font-size: 11px;
    font-weight: 650;
}}

QListWidget::item {{
    border-radius: 8px;
    padding: 9px 10px;
    margin: 2px 0;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 9px;
    margin: 3px;
}}

QScrollBar::handle:vertical {{
    background: #343B49;
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 9px;
}}

QScrollBar::handle:horizontal {{
    background: #343B49;
    border-radius: 4px;
    min-width: 24px;
}}

QSplitter::handle {{
    background: {BORDER};
}}

QToolTip {{
    background: {SURFACE_ALT};
    color: {TEXT};
    border: 1px solid {BORDER};
    padding: 6px;
}}
"""
