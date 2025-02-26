# main.py
import sys  # Import system module for command line arguments
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog  # Import necessary PyQt5 widgets
from csv_loader import load_csv_coordinates  # Import function to load CSV data
from map_widget import MapWidget  # Import the map widget to display the map
import pandas as pd  # Import pandas for reading CSV headers
from PyQt5.QtWidgets import QDialog, QFormLayout, QComboBox, QDialogButtonBox  # Import dialog widgets for column selection

# Dialog for selecting CSV columns manually
class ColumnSelectorDialog(QDialog):
    def __init__(self, columns):
        super().__init__()
        self.setWindowTitle("Select CSV Columns")
        layout = QFormLayout(self)  # Set the layout for the dialog

        # Create a combo box for selecting the Longitude (X) column
        self.x_field = QComboBox()
        self.x_field.addItems(columns)
        layout.addRow("Longitude (X):", self.x_field)

        # Create a combo box for selecting the Latitude (Y) column
        self.y_field = QComboBox()
        self.y_field.addItems(columns)
        layout.addRow("Latitude (Y):", self.y_field)

        # Create a combo box for selecting the Altitude (Z) column, optional field
        self.z_field = QComboBox()
        self.z_field.addItems(["None"] + columns)
        layout.addRow("Altitude (Z):", self.z_field)

        # Create a combo box for selecting the Precision (M) column, optional field
        self.m_field = QComboBox()
        self.m_field.addItems(["None"] + columns)
        layout.addRow("Precision (M):", self.m_field)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # Retrieve selected column names
    def get_selected_columns(self):
        return {
            "X": self.x_field.currentText(),
            "Y": self.y_field.currentText(),
            "Z": self.z_field.currentText() if self.z_field.currentText() != "None" else None,
            "M": self.m_field.currentText() if self.m_field.currentText() != "None" else None,
        }

# Main application window
class LiveMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Map Viewer")  # Set the window title
        self.setGeometry(100, 100, 1200, 800)  # Set the window geometry

        central_widget = QWidget()  # Create central widget
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)  # Set layout for the central widget

        self.map_widget = MapWidget()  # Create the map widget
        layout.addWidget(self.map_widget)  # Add the map widget to the layout

        # Create a button to load CSV coordinates
        self.load_csv_button = QPushButton("Load CSV Coordinates")
        self.load_csv_button.clicked.connect(self.load_csv_data)
        layout.addWidget(self.load_csv_button)

    # Function to load CSV data and add coordinates to the map
    def load_csv_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if not file_path:
            return

        # Read only the header row to get column names with specified encoding
        try:
            df = pd.read_csv(file_path, nrows=1, encoding='latin-1')
            column_names = list(df.columns)
        except Exception as e:
            print(f"Error reading CSV headers: {e}")
            return

        # Show dialog to select the appropriate CSV columns
        dialog = ColumnSelectorDialog(column_names)
        if dialog.exec_():
            selected_columns = dialog.get_selected_columns()
            coordinates = load_csv_coordinates(file_path, selected_columns)
            self.map_widget.add_coordinates(coordinates)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LiveMapApp()
    window.show()
    sys.exit(app.exec_())
