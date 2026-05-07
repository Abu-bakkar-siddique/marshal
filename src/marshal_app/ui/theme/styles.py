from __future__ import annotations

from marshal_app.ui.theme.palette import (
    ACCENT,
    BG,
    BORDER,
    DANGER,
    MUTED,
    SURFACE,
    TEXT,
)


APP_STYLE_SHEET = f"""
QMainWindow {{
    background: {BG};
}}

QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: "DejaVu Sans";
    font-size: 12px;
}}

QLabel#SidebarTitle,
QLabel#ProjectTitle {{
    font-size: 18px;
    font-weight: 600;
}}

QLabel#SidebarSubtitle,
QLabel#ProjectSubtitle,
QLabel#EmptyStateMessage {{
    color: {MUTED};
}}

QLabel#Eyebrow,
QLabel#SectionTitle {{
    color: {MUTED};
    font-size: 11px;
    font-weight: 500;
}}

QLabel#ProgressPercentage {{
    color: {MUTED};
    font-size: 11px;
    font-weight: 600;
}}

QFrame#TaskCard,
QListWidget#ProjectList,
QListWidget#TaskListWidget {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 0px;
}}

QFrame#ProgressHeader {{
    background: transparent;
    border: none;
}}

QPushButton {{
    background: transparent;
    border: none;
    border-radius: 0px;
    padding: 2px 0px;
    color: {TEXT};
    text-align: left;
}}

QPushButton:hover {{
    color: {ACCENT};
}}

QPushButton#CardActionButton,
QPushButton#SecondaryActionButton {{
    padding: 2px 0px;
}}

QPushButton#CardActionButton {{
    color: {MUTED};
}}

QPushButton#CardActionButton:hover {{
    color: {TEXT};
}}

QListWidget#ProjectList {{
    background: transparent;
    border: none;
    outline: none;
}}

QListWidget#ProjectList::item {{
    padding: 3px 0;
}}

QListWidget#ProjectList::item:selected {{
    background: transparent;
    color: {ACCENT};
}}

QListWidget#TaskListWidget {{
    outline: none;
    background: transparent;
    border: none;
}}

QListWidget#TaskListWidget::item {{
    margin: 0;
    background: transparent;
}}

QListWidget#TaskListWidget::item:selected,
QListWidget#TaskListWidget::item:focus,
QListWidget#TaskListWidget::item:selected:active {{
    background: transparent;
    border: none;
}}

QScrollArea,
QAbstractScrollArea {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: transparent;
    border: none;
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.12);
    border: none;
    border-radius: 5px;
    min-height: 28px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(255, 255, 255, 0.18);
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
    border: none;
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    border: none;
    height: 10px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: rgba(255, 255, 255, 0.12);
    border: none;
    border-radius: 5px;
    min-width: 28px;
}}

QScrollBar::handle:horizontal:hover {{
    background: rgba(255, 255, 255, 0.18);
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: transparent;
    border: none;
    width: 0;
}}

QProgressBar {{
    background: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 0px;
    min-height: 3px;
    max-height: 3px;
}}

QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 0px;
}}

QFrame#TaskCard[active="true"] {{
    border: 1px solid rgba(249, 112, 112, 0.25);
    background: rgba(249, 112, 112, 0.04);
}}

QFrame#TaskCard[keyboardSelected="true"] {{
    border: 1px solid rgba(255, 255, 255, 0.10);
    background: rgba(255, 255, 255, 0.02);
}}

QFrame#TaskCard[moveMode="true"] {{
    border: 1px dashed rgba(255, 255, 255, 0.16);
    background: rgba(255, 255, 255, 0.03);
}}

QFrame#TaskCard[done="true"] QLabel#TaskTitle,
QFrame#TaskCard[done="true"] QLabel#TaskDetail,
QFrame#TaskCard[done="true"] QLabel#TaskState {{
    color: {MUTED};
}}

QLabel#TaskTitle {{
    font-size: 13px;
    font-weight: 500;
}}

QLabel#TaskState {{
    padding: 0px;
    font-size: 10px;
    font-weight: 600;
}}

QLabel#TaskState[stateKind="active"] {{
    background: transparent;
    color: {DANGER};
    border: none;
}}

QLabel#TaskDetail,
QLabel#EmptyStateTitle {{
    color: {MUTED};
}}
"""
