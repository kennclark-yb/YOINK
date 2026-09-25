ACCENT = "#4D7CFE"

WINDOW_BG = "#09090B"
CARD_BG = "#141518"
CARD_BORDER = "#303137"

TEXT = "#F2F2F4"
MUTED = "#92949D"
INPUT_BG = "#0F1012"

HOVER_BG = "#1B1D22"
DANGER = "#FF5C5C"


APP_STYLE = f"""
QLabel {{
    color: {TEXT};
}}

QLineEdit {{
    background: {INPUT_BG};
    color: {TEXT};
    border: 1px solid {CARD_BORDER};
    border-radius: 9px;
    padding: 0 12px;
    selection-background-color: {ACCENT};
}}

QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}

QLineEdit[urlValid="false"] {{
    border: 1px solid {DANGER};
}}

QLabel#UrlError {{
    color: {DANGER};
    font-size: 9px;
    font-weight: 600;
    padding-left: 2px;
}}

QLabel#ExtractionError {{
    color: #B8A56A;
    font-size: 9px;
    font-weight: 600;
    padding-left: 2px;
}}

QRadioButton {{
    color: {TEXT};
    spacing: 7px;
}}

QRadioButton::indicator {{
    width: 13px;
    height: 13px;
    border-radius: 7px;
    border: 1px solid #555861;
    background: {INPUT_BG};
}}

QRadioButton::indicator:hover {{
    border: 1px solid {ACCENT};
}}

QRadioButton::indicator:checked {{
    border: 1px solid {ACCENT};
    background: {ACCENT};
}}

QLabel#ExtractionError[inputError="true"] {{
    color: {DANGER};
}}

QRadioButton:disabled {{
    color: #777A84;
}}

QRadioButton::indicator:disabled {{
    border: 1px solid #3A3C44;
    background: {INPUT_BG};
}}

QRadioButton::indicator:checked:disabled {{
    background: #52618A;
}}

QFrame#Card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 14px;
}}
"""
