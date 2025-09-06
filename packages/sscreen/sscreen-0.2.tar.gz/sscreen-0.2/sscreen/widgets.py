from PyQt6.QtWidgets import QPushButton, QLabel

class SButton:
    def __init__(self, parent, text='Button', callback=None, bg='#2196F3', fg='#fff', font='Arial', font_size=12):
        self.button = QPushButton(text, parent.window)
        self.button.setStyleSheet(f'background-color: {bg}; color: {fg}; font-family: {font}; font-size: {font_size}pt; border-radius: 5px;')
        if callback:
            self.button.clicked.connect(callback)

    def move(self, x, y):
        self.button.move(x, y)

    def resize(self, w, h):
        self.button.resize(w, h)

class SLabel:
    def __init__(self, parent, text='Label', bg=None, fg='#000', font='Arial', font_size=12):
        self.label = QLabel(text, parent.window)
        style = f'color: {fg}; font-family: {font}; font-size: {font_size}pt;'
        if bg:
            style += f' background-color: {bg};'
        self.label.setStyleSheet(style)

    def move(self, x, y):
        self.label.move(x, y)

    def resize(self, w, h):
        self.label.resize(w, h)
