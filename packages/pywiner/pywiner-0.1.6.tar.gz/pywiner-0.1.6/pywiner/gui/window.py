import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize

class HoverableLabel(QLabel):
    def __init__(self, parent, on_enter=None, on_leave=None):
        super().__init__(parent)
        self.on_enter_func = on_enter
        self.on_leave_func = on_leave
        self.setMouseTracking(True)

    def enterEvent(self, event):
        if self.on_enter_func:
            self.on_enter_func()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.on_leave_func:
            self.on_leave_func()
        super().leaveEvent(event)

class Window(QWidget):
    def __init__(self, title, width, height, background_color=None):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(width, height)
        self.widgets = []
        
        if background_color:
            self.setStyleSheet(f"background-color: {background_color};")
            
    def add_text(self, text, x=0, y=0, font_size=12, font_family="Arial", color="black", on_hover=None, on_leave=None):
        text_label = HoverableLabel(self, on_enter=on_hover, on_leave=on_leave)
        text_label.setText(text)
        text_label.move(x, y)
        
        font = QFont(font_family, font_size)
        text_label.setFont(font)
        
        text_label.setStyleSheet(f"color: {color};")
        
        text_label.show()
        self.widgets.append(text_label)
        return text_label

    def add_image(self, image_path, x=0, y=0, width=None, height=None, on_hover=None, on_leave=None):
        image_label = HoverableLabel(self, on_enter=on_hover, on_leave=on_leave)
        pixmap = QPixmap(image_path)
        
        if width and height:
            pixmap = pixmap.scaled(QSize(width, height), Qt.AspectRatioMode.KeepAspectRatio)
        
        image_label.setPixmap(pixmap)
        image_label.move(x, y)
        image_label.show()
        self.widgets.append(image_label)
        return image_label
    
    def add_button(self, text, x, y, width=100, height=30, on_click=None):
        button = QPushButton(text, self)
        button.move(x, y)
        button.setFixedSize(width, height)
        
        if on_click:
            button.clicked.connect(on_click)
            
        button.show()
        self.widgets.append(button)
        return button

    def run(self):
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    my_window = Window(
        title="Complete Pywiner Window",
        width=800,
        height=600,
        background_color="lightgray"
    )
    
    my_window.add_text(
        text="Hello, Pywiner World!",
        x=50,
        y=50,
        font_size=20,
        font_family="Comic Sans MS",
        color="blue"
    )
    
    my_window.add_image(
        image_path="logo.png",
        x=200,
        y=200,
        width=200,
        height=200
    )

    my_window.run()
    sys.exit(app.exec())