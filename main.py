# main.py
import sys  # Import system module for command line arguments
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QFileDialog, QDialog, QFormLayout, QComboBox, QDialogButtonBox,
    QListWidget, QHBoxLayout
)  # Import necessary PyQt5 widgets
import pandas as pd  # Import pandas for reading CSV headers
from csv_loader import load_csv_coordinates  # Import function to load CSV data
from map_widget import MapWidget  # Import the map widget to display the map

# Dialog for selecting CSV columns and icon type
class ColumnSelectorDialog(QDialog):
    def __init__(self, columns):
        super().__init__()
        self.setWindowTitle("Select CSV Columns and Icon")
        layout = QFormLayout(self)  # Set layout for the dialog

        # Combo box for selecting the Longitude (X) column
        self.x_field = QComboBox()
        self.x_field.addItems(columns)
        layout.addRow("Longitude (X):", self.x_field)

        # Combo box for selecting the Latitude (Y) column
        self.y_field = QComboBox()
        self.y_field.addItems(columns)
        layout.addRow("Latitude (Y):", self.y_field)

        # Combo box for selecting the Altitude (Z) column, optional field
        self.z_field = QComboBox()
        self.z_field.addItems(["None"] + columns)
        layout.addRow("Altitude (Z):", self.z_field)

        # Combo box for selecting the Precision (M) column, optional field
        self.m_field = QComboBox()
        self.m_field.addItems(["None"] + columns)
        layout.addRow("Precision (M):", self.m_field)

        # Combo box for selecting the Icon type for the CSV layer
        self.icon_field = QComboBox()
        self.icon_field.addItems(["Pin", "Mountain", "Star"])
        layout.addRow("Icon Type:", self.icon_field)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # Retrieve selected options including column mappings and icon type
    def get_selected_options(self):
        return {
            "X": self.x_field.currentText(),
            "Y": self.y_field.currentText(),
            "Z": self.z_field.currentText() if self.z_field.currentText() != "None" else None,
            "M": self.m_field.currentText() if self.m_field.currentText() != "None" else None,
            "Icon": self.icon_field.currentText()
        }

# Dialog for managing layer order (reordering CSV layers)
class LayerManagerDialog(QDialog):
    def __init__(self, layers):
        super().__init__()
        self.setWindowTitle("Manage Layers")
        self.layers = layers  # List of layer dictionaries
        self.layout = QVBoxLayout(self)

        # List widget to display layer names
        self.list_widget = QListWidget()
        self.refresh_list()
        self.layout.addWidget(self.list_widget)

        # Buttons to move layers up or down
        button_layout = QHBoxLayout()
        self.up_button = QPushButton("Move Up")
        self.up_button.clicked.connect(self.move_up)
        button_layout.addWidget(self.up_button)

        self.down_button = QPushButton("Move Down")
        self.down_button.clicked.connect(self.move_down)
        button_layout.addWidget(self.down_button)

        self.layout.addLayout(button_layout)

        # Dialog OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    # Refresh the list widget to show current layer order
    def refresh_list(self):
        self.list_widget.clear()
        for layer in self.layers:
            self.list_widget.addItem(layer["name"])

    # Move selected layer up in the list
    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            self.layers[current_row - 1], self.layers[current_row] = self.layers[current_row], self.layers[current_row - 1]
            self.refresh_list()
            self.list_widget.setCurrentRow(current_row - 1)

    # Move selected layer down in the list
    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < len(self.layers) - 1 and current_row != -1:
            self.layers[current_row + 1], self.layers[current_row] = self.layers[current_row], self.layers[current_row + 1]
            self.refresh_list()
            self.list_widget.setCurrentRow(current_row + 1)

    # Return the new order of layers
    def get_new_order(self):
        return self.layers

# Main application window
class LiveMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Map Viewer")  # Set window title
        self.setGeometry(100, 100, 1200, 800)  # Set window dimensions

        central_widget = QWidget()  # Create central widget
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)  # Set layout for central widget

        self.map_widget = MapWidget()  # Create the map widget
        self.layout.addWidget(self.map_widget)  # Add the map widget to layout

        # Button to load CSV coordinates (adds a new CSV layer)
        self.load_csv_button = QPushButton("Load CSV Coordinates")
        self.load_csv_button.clicked.connect(self.load_csv_data)
        self.layout.addWidget(self.load_csv_button)

        # Button to manage (reorder) layers
        self.manage_layers_button = QPushButton("Manage Layers")
        self.manage_layers_button.clicked.connect(self.manage_layers)
        self.layout.addWidget(self.manage_layers_button)

        # Button to capture the current map view as an image
        self.capture_map_button = QPushButton("Capture Map")
        self.capture_map_button.clicked.connect(self.capture_map)
        self.layout.addWidget(self.capture_map_button)

    # Function to load CSV data and add it as a new layer
    def load_csv_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if not file_path:
            return

        # Read CSV header to get column names using specified encoding
        try:
            df = pd.read_csv(file_path, nrows=1, encoding='latin-1')
            column_names = list(df.columns)
        except Exception as e:
            print(f"Error reading CSV headers: {e}")
            return

        # Show dialog for column and icon selection
        dialog = ColumnSelectorDialog(column_names)
        if dialog.exec_():
            selected_options = dialog.get_selected_options()
            coordinates = load_csv_coordinates(file_path, selected_options)
            icon_type = selected_options["Icon"]
            self.map_widget.add_layer(coordinates, icon_type)

    # Function to open the layer management dialog for reordering layers
    def manage_layers(self):
        if not self.map_widget.layers:
            return
        # Pass a copy of the layers list to avoid modifying original until accepted
        dialog = LayerManagerDialog(self.map_widget.layers.copy())
        if dialog.exec_():
            new_order = dialog.get_new_order()
            self.map_widget.update_layer_order(new_order)

    # Function to capture the current map view as an image
    def capture_map(self):
        self.map_widget.capture_map()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LiveMapApp()
    window.show()
    sys.exit(app.exec_())
