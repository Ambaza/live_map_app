from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import os
from PyQt5.QtCore import QUrl  # Import QUrl

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Create a web engine view to display the map
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Generate initial map and load it
        self.map_file = "map.html"
        self.generate_map([])
        self.load_map()
    
    def generate_map(self, coordinates):
        # Create a folium map centered at a default location
        folium_map = folium.Map(location=[0, 0], zoom_start=2)
        
        # Add markers for each coordinate
        for lat, lon, alt in coordinates:
            folium.Marker([lat, lon], popup=f"Altitude: {alt}m").add_to(folium_map)
        
        # Save the map to an HTML file
        folium_map.save(self.map_file)
    

    def load_map(self):
        # Load the generated map file into the web view
        file_path = os.path.abspath(self.map_file)
        self.web_view.setUrl(QUrl.fromLocalFile(file_path))  # Convert string to QUrl

    
    def add_coordinates(self, coordinates):
        # Update the map with new coordinates
        self.generate_map(coordinates)
        self.load_map()
