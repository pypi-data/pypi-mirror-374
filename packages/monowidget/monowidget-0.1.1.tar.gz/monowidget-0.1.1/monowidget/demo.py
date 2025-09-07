import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from monowidget import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MonoWidget Example")
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create Mono object
        mono = Mono([
            MonoAttr("username", "Alice", label="Username"),
            MonoAttr("age", 30, range=(18, 100), label="Age"),
            MonoAttr("active", True, label="Active"),
            MonoAttr("theme", "dark", enum=["light", "dark", "auto"], label="Theme"),
        ])
        
        # Create Inspector and add to layout
        inspector = QMonoInspector(mono)
        main_layout.addWidget(inspector)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())