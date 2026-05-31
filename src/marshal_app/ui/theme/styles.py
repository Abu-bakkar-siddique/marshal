from __future__ import annotations


APP_STYLE_SHEET = """
QMainWindow {
    background: #252525;
}

QWidget {
    background: #1c1c1c;
    color: #e8e8e8;
    font-family: "DejaVu Sans";
    font-size: 13px;
}

QSplitter::handle {
    background: rgba(255, 255, 255, 0.08);
    width: 1px;
}

QWidget#Sidebar {
    background: #252525;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

QWidget#ProjectView {
    background: #1c1c1c;
}

QWidget#PlanningView {
    background: #1c1c1c;
}

QLabel#SidebarTitle {
    background: #252525;
    color: #606060;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 1px;
    padding: 0 14px 14px 14px;
}

QLabel#SidebarSectionLabel {
    background: #252525;
    color: #606060;
    font-size: 10px;
    text-transform: uppercase;
    padding: 0 14px 6px 14px;
}

QListWidget#ProjectList {
    background: #252525;
    border: none;
    outline: none;
    padding: 0;
}

QListWidget#ProjectList::item {
    color: #a0a0a0;
    padding: 7px 14px 7px 12px;
    border-left: 2px solid transparent;
}

QListWidget#ProjectList::item:hover {
    color: #e8e8e8;
}

QListWidget#ProjectList::item:selected,
QListWidget#ProjectList::item:selected:active,
QListWidget#ProjectList::item:selected:!active {
    background: #1c1c1c;
    color: #e8e8e8;
    border-left: 2px solid #e8e8e8;
}

QFrame#ProjectHeader {
    background: #1c1c1c;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

QLabel#ProjectTitle {
    color: #e8e8e8;
    font-size: 15px;
    font-weight: 500;
}

QLabel#ProjectSubtitle {
    color: #a0a0a0;
    font-size: 12px;
}

QFrame#ProgressHeader {
    background: #1c1c1c;
    border: none;
}

QProgressBar {
    background: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 1px;
    min-height: 2px;
    max-height: 2px;
}

QProgressBar::chunk {
    background: #e8e8e8;
    border-radius: 1px;
}

QLabel#ProgressPercentage {
    color: #606060;
    font-size: 11px;
    font-weight: 400;
}

QLabel#Eyebrow,
QLabel#SectionTitle {
    color: #606060;
    font-size: 10px;
    font-weight: 500;
}

QLabel#SectionTitle {
    padding: 10px 22px 4px 22px;
}

QPushButton,
QPushButton#SidebarActionButton,
QPushButton#SecondaryActionButton {
    background: transparent;
    border: none;
    border-radius: 0px;
    color: #606060;
    text-align: left;
}

QPushButton:hover {
    color: #e8e8e8;
}

QPushButton#IconButton {
    color: #606060;
    border: none;
    border-radius: 4px;
    padding: 0;
    text-align: center;
    font-size: 14px;
}

QPushButton#IconButton:hover {
    color: #e8e8e8;
    background: #252525;
}

QPushButton#SidebarActionButton {
    background: #252525;
    padding: 6px 14px;
    font-size: 12px;
}

QPushButton#PrimaryActionButton {
    background: #e8e8e8;
    color: #1c1c1c;
    padding: 6px 12px;
    border: 1px solid #e8e8e8;
}

QPushButton#PrimaryActionButton:hover {
    background: #ffffff;
    border-color: #ffffff;
}

QFrame#AddRow {
    background: #1c1c1c;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

QPushButton#AddTaskButton {
    background: transparent;
    border: none;
    color: #606060;
    font-size: 13px;
    padding-left: 24px;
}

QListWidget#TaskListWidget {
    outline: none;
    background: transparent;
    border: none;
}

QListWidget#TaskListWidget::item {
    margin: 0;
    background: transparent;
}

QListWidget#TaskListWidget::item:selected,
QListWidget#TaskListWidget::item:focus,
QListWidget#TaskListWidget::item:selected:active {
    background: transparent;
    border: none;
}

QFrame#TaskCard {
    background: #1c1c1c;
    border: none;
    border-bottom: 1px solid transparent;
}

QFrame#TaskCard:hover,
QFrame#TaskCard[expanded="true"],
QFrame#TaskCard[keyboardSelected="true"] {
    background: #252525;
}

QFrame#TaskCard[expanded="true"] {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

QFrame#TaskCard[moveMode="true"] {
    background: #303030;
}

QCheckBox#TaskCheck {
    spacing: 0;
    min-width: 14px;
    max-width: 14px;
    min-height: 14px;
    max-height: 14px;
}

QCheckBox#TaskCheck::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    background: transparent;
}

QCheckBox#TaskCheck::indicator:checked {
    background: #e8e8e8;
    border: 1px solid #e8e8e8;
    image: none;
}

QLabel#TaskTitle {
    color: #e8e8e8;
    font-size: 13px;
    font-weight: 400;
}

QFrame#TaskCard[done="true"] QLabel#TaskTitle {
    color: #606060;
    text-decoration: line-through;
}

QLabel#TaskDetail {
    color: #a0a0a0;
    font-size: 12px;
    line-height: 160%;
    padding: 4px 0 2px 24px;
}

QLabel#ActiveDot {
    background: #e8e8e8;
    border-radius: 2px;
    min-width: 5px;
    max-width: 5px;
    min-height: 5px;
    max-height: 5px;
}

QLabel#ExpandButton {
    color: transparent;
    font-size: 12px;
}

QFrame#TaskCard:hover QLabel#ExpandButton,
QFrame#TaskCard[expanded="true"] QLabel#ExpandButton,
QFrame#TaskCard[keyboardSelected="true"] QLabel#ExpandButton {
    color: #606060;
}

QPushButton#CardActionButton {
    color: transparent;
    font-size: 11px;
    padding: 0;
}

QFrame#TaskCard:hover QPushButton#CardActionButton {
    color: #606060;
}

QFrame#TaskCard QPushButton#CardActionButton:hover {
    color: #e8e8e8;
}

QFrame#SectionLine {
    color: rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.08);
    max-height: 1px;
}

QLabel#SectionDividerTitle {
    color: #606060;
    font-size: 10px;
    font-weight: 400;
    text-transform: uppercase;
}

QScrollArea,
QAbstractScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    border: none;
    width: 4px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 2px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.15);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    border: none;
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    border: none;
    height: 4px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 2px;
    min-width: 28px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(255, 255, 255, 0.15);
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    border: none;
    width: 0;
}

QLineEdit,
QTextEdit,
QPlainTextEdit {
    background: #252525;
    color: #e8e8e8;
    border: 1px solid rgba(255, 255, 255, 0.08);
    selection-background-color: #303030;
}

QLabel#EmptyStateTitle,
QLabel#EmptyStateMessage {
    color: #606060;
}

QFrame#PlanningHeader {
    background: #1c1c1c;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

QLabel#PlanningTitle {
    color: #e8e8e8;
    font-size: 15px;
    font-weight: 500;
}

QLabel#PlanningSubtitle,
QLabel#PlanningStatus,
QLabel#PlanningQuestion {
    color: #a0a0a0;
    font-size: 12px;
}

QLabel#PlanningQuestion {
    color: #e8e8e8;
}

QLabel#PlanningSectionTitle {
    color: #606060;
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
}

QPlainTextEdit#PlanningInput,
QPlainTextEdit#PlanningFeedback,
QPlainTextEdit#PlanningConversation,
QPlainTextEdit#PlanningDraft,
QPlainTextEdit#PlanningStructured {
    background: #252525;
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #e8e8e8;
    padding: 8px;
}
"""
