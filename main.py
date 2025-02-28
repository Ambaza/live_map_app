# main.py
import sys  # Import system module for command line arguments
import os  # For path operations
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QFileDialog, QToolBar, QAction, QDialog, QFormLayout, QComboBox,
    QDateTimeEdit, QDialogButtonBox, QListWidget, QHBoxLayout, QLabel, QMenu
)
import pandas as pd  # For reading CSV headers
from csv_loader import load_csv_coordinates  # For loading CSV coordinates
from vector_loader import load_vector_file  # For loading vector GIS files
from map_widget import MapWidget  # For displaying the map
from icon_selector import IconSelectorDialog  # For selecting custom icons
from vector_layer_selector import VectorLayerSelectorDialog  # For selecting layers from a GeoPackage
from layer_preview import LayerPreviewDialog  # For previewing layer data

# Dialog for selecting date and time (for Sentinel-2)
class DateTimeSelectorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Date and Time for Sentinel-2")
        layout = QFormLayout(self)
        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setCalendarPopup(True)
        layout.addRow("Date & Time:", self.date_time_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def get_date_time(self):
        return self.date_time_edit.dateTime().toString("yyyy-MM-ddTHH:mm")

# Dialog for selecting CSV columns and custom icon with automatic field detection
class ColumnSelectorDialog(QDialog):
    def __init__(self, columns):
        super().__init__()
        self.setWindowTitle("Select CSV Columns and Icon")
        layout = QFormLayout(self)
        self.selected_icon = None
        self.x_field = QComboBox()
        self.x_field.addItems(columns)
        default_index = self.get_default_index(columns, ["lon", "long", "x"])
        if default_index is not None:
            self.x_field.setCurrentIndex(default_index)
        layout.addRow("Longitude (X):", self.x_field)
        self.y_field = QComboBox()
        self.y_field.addItems(columns)
        default_index = self.get_default_index(columns, ["lat", "latitude", "y"])
        if default_index is not None:
            self.y_field.setCurrentIndex(default_index)
        layout.addRow("Latitude (Y):", self.y_field)
        self.z_field = QComboBox()
        self.z_field.addItems(["None"] + columns)
        default_index = self.get_default_index(columns, ["alt", "altitude", "z"])
        if default_index is not None:
            self.z_field.setCurrentIndex(default_index + 1)
        layout.addRow("Altitude (Z):", self.z_field)
        self.m_field = QComboBox()
        self.m_field.addItems(["None"] + columns)
        default_index = self.get_default_index(columns, ["prec", "precision"])
        if default_index is not None:
            self.m_field.setCurrentIndex(default_index + 1)
        layout.addRow("Precision (M):", self.m_field)
        self.icon_button = QPushButton("Select Custom Icon")
        self.icon_button.clicked.connect(self.open_icon_selector)
        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(64, 64)
        self.icon_preview.setStyleSheet("border: 1px solid black;")
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.icon_button)
        icon_layout.addWidget(self.icon_preview)
        layout.addRow("Custom Icon:", icon_layout)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def get_default_index(self, columns, keywords):
        for i, col in enumerate(columns):
            lower = col.lower()
            for keyword in keywords:
                if keyword in lower:
                    return i
        return None
    def open_icon_selector(self):
        folder_path = os.path.join(os.path.dirname(__file__), "QGIS Style")
        dialog = IconSelectorDialog(folder_path)
        if dialog.exec_():
            icon_path = dialog.get_selected_icon()
            if icon_path:
                self.selected_icon = icon_path
                from PyQt5.QtGui import QPixmap
                pixmap = QPixmap(icon_path)
                self.icon_preview.setPixmap(pixmap.scaled(64, 64))
    def get_selected_options(self):
        return {
            "X": self.x_field.currentText(),
            "Y": self.y_field.currentText(),
            "Z": self.z_field.currentText() if self.z_field.currentText() != "None" else None,
            "M": self.m_field.currentText() if self.m_field.currentText() != "None" else None,
            "Icon": self.selected_icon if self.selected_icon is not None else "Pin"
        }

# Dialog for managing layer order with right-click preview
class LayerManagerDialog(QDialog):
    def __init__(self, layers):
        super().__init__()
        self.setWindowTitle("Manage Layers")
        self.layers = layers
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.refresh_list()
        self.layout.addWidget(self.list_widget)
        button_layout = QHBoxLayout()
        self.up_button = QPushButton("Move Up")
        self.up_button.clicked.connect(self.move_up)
        button_layout.addWidget(self.up_button)
        self.down_button = QPushButton("Move Down")
        self.down_button.clicked.connect(self.move_down)
        button_layout.addWidget(self.down_button)
        self.layout.addLayout(button_layout)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
    def refresh_list(self):
        self.list_widget.clear()
        for layer in self.layers:
            self.list_widget.addItem(layer["name"])
    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            self.layers[current_row - 1], self.layers[current_row] = self.layers[current_row], self.layers[current_row - 1]
            self.refresh_list()
            self.list_widget.setCurrentRow(current_row - 1)
    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < len(self.layers) - 1 and current_row != -1:
            self.layers[current_row + 1], self.layers[current_row] = self.layers[current_row], self.layers[current_row + 1]
            self.refresh_list()
            self.list_widget.setCurrentRow(current_row + 1)
    def contextMenuEvent(self, event):
        item = self.list_widget.itemAt(event.pos())
        if item:
            menu = QMenu(self)
            preview_action = menu.addAction("Preview Layer")
            action = menu.exec_(event.globalPos())
            if action == preview_action:
                index = self.list_widget.row(item)
                layer = self.layers[index]
                if "geojson" in layer:
                    preview_text = layer["geojson"]
                elif "coordinates" in layer:
                    preview_text = f"CSV Layer with {len(layer['coordinates'])} points."
                else:
                    preview_text = "No preview available."
                dlg = LayerPreviewDialog(preview_text, layer["name"])
                dlg.exec_()
    def get_new_order(self):
        return self.layers

# Main application window
class LiveMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Map Viewer")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.map_widget = MapWidget()
        self.layout.addWidget(self.map_widget)
        self.load_csv_button = QPushButton("Load CSV Coordinates")
        self.load_csv_button.clicked.connect(self.load_csv_data)
        self.layout.addWidget(self.load_csv_button)
        self.load_vector_button = QPushButton("Load GIS Data")
        self.load_vector_button.clicked.connect(self.load_vector_data)
        self.layout.addWidget(self.load_vector_button)
        self.manage_layers_button = QPushButton("Manage Layers")
        self.manage_layers_button.clicked.connect(self.manage_layers)
        self.layout.addWidget(self.manage_layers_button)
        self.capture_map_button = QPushButton("Capture Map")
        self.capture_map_button.clicked.connect(self.capture_map)
        self.layout.addWidget(self.capture_map_button)
        self.mapping_toolbar = QToolBar("Mapping Options")
        self.addToolBar(self.mapping_toolbar)
        self.action_osm = QAction("OpenStreetMap", self)
        self.action_osm.triggered.connect(lambda: self.map_widget.set_map_mode("OSM"))
        self.mapping_toolbar.addAction(self.action_osm)
        self.action_google = QAction("Google Map", self)
        self.action_google.triggered.connect(lambda: self.map_widget.set_map_mode("Google"))
        self.mapping_toolbar.addAction(self.action_google)
        self.action_sentinel = QAction("Sentinel-2", self)
        self.action_sentinel.triggered.connect(self.select_sentinel_date_time)
        self.mapping_toolbar.addAction(self.action_sentinel)
    def select_sentinel_date_time(self):
        dialog = DateTimeSelectorDialog()
        if dialog.exec_():
            date_time = dialog.get_date_time()
            self.map_widget.set_map_mode("Sentinel", date_time)
    def load_csv_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if not file_path:
            return
        try:
            df = pd.read_csv(file_path, nrows=1, encoding='latin-1')
            column_names = list(df.columns)
        except Exception as e:
            print(f"Error reading CSV headers: {e}")
            return
        dialog = ColumnSelectorDialog(column_names)
        if dialog.exec_():
            selected_options = dialog.get_selected_options()
            coordinates = load_csv_coordinates(file_path, selected_options)
            icon_type = selected_options["Icon"]
            self.map_widget.add_layer(coordinates, icon_type)
    def load_vector_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open GIS File",
            "",
            "GIS Files (*.shp *.shx *.geojson *.gpkg)"
        )
        if not file_path:
            return
        ext = os.path.splitext(file_path)[1].lower()
        from vector_loader import load_vector_file
        if ext == ".gpkg":
            from vector_layer_selector import VectorLayerSelectorDialog
            dlg = VectorLayerSelectorDialog(file_path)
            if dlg.exec_():
                selected_layers = dlg.get_selected_layers()
                for layer_name in selected_layers:
                    geojson = load_vector_file(file_path, layer=layer_name)
                    if geojson is not None:
                        self.map_widget.add_vector_layer(geojson, layer_name)
        else:
            geojson = load_vector_file(file_path)
            if geojson is not None:
                layer_name = os.path.basename(file_path)
                self.map_widget.add_vector_layer(geojson, layer_name)
    def manage_layers(self):
        all_layers = self.map_widget.all_layers()
        if not all_layers:
            return
        dialog = LayerManagerDialog(all_layers.copy())
        if dialog.exec_():
            new_order = dialog.get_new_order()
            self.map_widget.update_layer_order(new_order)
    def capture_map(self):
        self.map_widget.capture_map()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LiveMapApp()
    window.show()
    sys.exit(app.exec_())
