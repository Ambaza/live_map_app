# map_widget.py
import os  # Import os for file path operations
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog  # Import necessary PyQt5 widgets
from PyQt5.QtWebEngineWidgets import QWebEngineView  # Import QWebEngineView to display web content
from PyQt5.QtCore import QUrl  # Import QUrl to handle URLs
from PyQt5.QtGui import QPixmap  # Import QPixmap for capturing the map view
import folium  # Import folium to generate maps

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)  # Set layout for the widget

        # Create a web view to display the generated map
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        # File name for the generated HTML map
        self.map_file = "map.html"
        self.layers = []  # List to store multiple CSV layers

        self.generate_map()  # Generate initial empty map
        self.load_map()  # Load the generated map into the web view

    # Function to generate the map with current layers
    def generate_map(self):
        # Create a folium map centered at a default location [0, 0]
        folium_map = folium.Map(location=[0, 0], zoom_start=2)
        # Define mapping from icon names to folium icon identifiers
        icon_mapping = {
            "Pin": "map-marker",
            "Mountain": "tree-conifer",  # Using tree-conifer as a placeholder for mountain
            "Star": "star"
        }
        # Iterate over each layer and add its markers to the map
        for layer in self.layers:
            icon_type = layer.get("icon", "Pin")
            for coordinate in layer["coordinates"]:
                # Unpack coordinate tuple: (lat, lon, alt, precision)
                lat, lon, alt, precision = coordinate
                popup_text = f"Altitude: {alt} m"
                if precision is not None:
                    popup_text += f", Precision: {precision} m"
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    icon=folium.Icon(icon=icon_mapping.get(icon_type, "map-marker"), prefix='fa')
                ).add_to(folium_map)
        # Save the generated map to an HTML file
        folium_map.save(self.map_file)

    # Function to load the generated map into the web view
    def load_map(self):
        file_path = os.path.abspath(self.map_file)  # Get absolute file path
        self.web_view.setUrl(QUrl.fromLocalFile(file_path))  # Load map using QUrl

    # Add a new CSV layer with its coordinates and chosen icon
    def add_layer(self, coordinates, icon):
        layer_name = f"Layer {len(self.layers) + 1}"  # Generate a layer name
        new_layer = {"name": layer_name, "coordinates": coordinates, "icon": icon}
        self.layers.append(new_layer)
        self.generate_map()
        self.load_map()

    # Update the order of layers and refresh the map
    def update_layer_order(self, new_layers):
        self.layers = new_layers
        self.generate_map()
        self.load_map()

    # Capture the current map view as an image and allow the user to save it
    def capture_map(self):
        # Grab the current view of the web engine
        pixmap = self.web_view.grab()
        # Open a file dialog to save the captured image
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Map Capture", "", "PNG Files (*.png)")
        if file_path:
            pixmap.save(file_path, "PNG")
