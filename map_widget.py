# map_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout  # Import necessary PyQt5 widgets
from PyQt5.QtWebEngineWidgets import QWebEngineView  # Import QWebEngineView to display web content
from PyQt5.QtCore import QUrl  # Import QUrl to handle URLs
import folium  # Import folium to generate maps
import os  # Import os for file path operations

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)  # Set layout for the widget

        # Create a web view to display the generated map
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # File name for the generated HTML map
        self.map_file = "map.html"
        self.generate_map([])  # Generate an initial empty map
        self.load_map()  # Load the generated map into the web view

    # Function to generate the map with provided coordinates
    def generate_map(self, coordinates):
        # Create a folium map centered at [0, 0] with a default zoom level
        folium_map = folium.Map(location=[0, 0], zoom_start=2)
        # Iterate over coordinates and add markers
        for coordinate in coordinates:
            if len(coordinate) == 4:
                # Unpack if coordinate includes precision (M)
                lat, lon, alt, precision = coordinate
                popup_text = f"Altitude: {alt} m"
                if precision is not None:
                    popup_text += f", Precision: {precision} m"
                folium.Marker([lat, lon], popup=popup_text).add_to(folium_map)
            else:
                # Fallback for coordinates with only 3 values
                lat, lon, alt = coordinate
                folium.Marker([lat, lon], popup=f"Altitude: {alt} m").add_to(folium_map)
        # Save the map to an HTML file
        folium_map.save(self.map_file)

    # Function to load the HTML map into the web view
    def load_map(self):
        file_path = os.path.abspath(self.map_file)  # Get absolute path of the map file
        self.web_view.setUrl(QUrl.fromLocalFile(file_path))  # Convert file path to QUrl and set it

    # Function to update the map with new coordinates
    def add_coordinates(self, coordinates):
        self.generate_map(coordinates)
        self.load_map()
