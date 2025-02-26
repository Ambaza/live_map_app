import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from map_widget import MapWidget
from csv_loader import load_csv_coordinates

class LiveMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Map Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create map widget
        self.map_widget = MapWidget()
        layout.addWidget(self.map_widget)
        
        # Create button to load CSV file
        self.load_csv_button = QPushButton("Load CSV Coordinates")
        self.load_csv_button.clicked.connect(self.load_csv_data)
        layout.addWidget(self.load_csv_button)
    
    def load_csv_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            coordinates = load_csv_coordinates(file_path)
            self.map_widget.add_coordinates(coordinates)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LiveMapApp()
    window.show()
    sys.exit(app.exec_())
