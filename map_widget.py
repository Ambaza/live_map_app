# map_widget.py
import os  # For file path operations
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog  # For widget layout and file dialogs
from PyQt5.QtWebEngineWidgets import QWebEngineView  # To display web content
from PyQt5.QtCore import QUrl  # For handling URLs
from PyQt5.QtGui import QPixmap  # For capturing the map view
import folium  # For generating maps

# Import for Sentinel OAuth token retrieval
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Function to fetch Sentinel Hub OAuth token
def get_sentinel_token():
    client_id = "850b83f6-ae06-47de-b0d1-2b1d34171b57"
    client_secret = "WtYF5yWvIq8VLZPZn5NcIXZe46jP7Unk"
    token_url = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
    return token.get("access_token")

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)  # Set the widget layout

        # Create a web view to display the generated map
        self.web_view = QWebEngineView()
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        self.layout.addWidget(self.web_view)

        self.map_file = "map.html"  # File to store the generated HTML map
        self.csv_layers = []  # List to store CSV layers
        self.vector_layers = []  # List to store vector layers

        self.map_mode = "OSM"  # Default mapping mode is OpenStreetMap
        self.map_mode_data = None  # Additional data (e.g., date/time for Sentinel)

        self.update_map_view()  # Load the initial map view

    # Generate an OpenStreetMap using folium and add CSV and vector layers
    def generate_osm_map(self):
        folium_map = folium.Map(location=[0, 0], zoom_start=2)
        icon_mapping = {
            "Pin": "map-marker",
            "Mountain": "tree-conifer",
            "Star": "star"
        }
        # Add CSV layers
        for layer in self.csv_layers:
            icon_type = layer.get("icon", "Pin")
            for coordinate in layer["coordinates"]:
                lat, lon, alt, precision = coordinate
                popup_text = f"Altitude: {alt} m"
                if precision is not None:
                    popup_text += f", Precision: {precision} m"
                if os.path.exists(icon_type):
                    marker_icon = folium.features.CustomIcon(icon_type, icon_size=(32, 32))
                else:
                    marker_icon = folium.Icon(icon=icon_mapping.get(icon_type, "map-marker"), prefix='fa')
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    icon=marker_icon
                ).add_to(folium_map)
        # Add vector layers
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

    # Generate a Google Map using a custom TileLayer with crossOrigin attribute
    def generate_google_map(self):
        folium_map = folium.Map(location=[0, 0], zoom_start=2, tiles=None)
        folium.TileLayer(
            tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite',
            name='Google Satellite',
            overlay=False,
            control=True,
            **{'crossOrigin': 'anonymous'}
        ).add_to(folium_map)
        icon_mapping = {
            "Pin": "map-marker",
            "Mountain": "tree-conifer",
            "Star": "star"
        }
        for layer in self.csv_layers:
            icon_type = layer.get("icon", "Pin")
            for coordinate in layer["coordinates"]:
                lat, lon, alt, precision = coordinate
                popup_text = f"Altitude: {alt} m"
                if precision is not None:
                    popup_text += f", Precision: {precision} m"
                if os.path.exists(icon_type):
                    marker_icon = folium.features.CustomIcon(icon_type, icon_size=(32, 32))
                else:
                    marker_icon = folium.Icon(icon=icon_mapping.get(icon_type, "map-marker"), prefix='fa')
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    icon=marker_icon
                ).add_to(folium_map)
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

    # Generate a Sentinel-2 map using a WMS tile layer with proper parameters
    def generate_sentinel_map(self, date_time):
        token = get_sentinel_token()
        instance_id = "<your_instance_id>"  # Replace with your actual instance ID
        folium_map = folium.Map(location=[0, 0], zoom_start=2, tiles=None)
        wms = folium.raster_layers.WmsTileLayer(
            url=f"https://services.sentinel-hub.com/ogc/wms/{instance_id}",
            layers="TRUE_COLOR",
            fmt="image/png",
            transparent=True,
            version="1.3.0",
            attr="Sentinel-2 Imagery",
            extra_params={
                "token": token,
                "datetime": date_time,
                "MAXCC": 20
            }
        )
        wms.add_to(folium_map)
        icon_mapping = {
            "Pin": "map-marker",
            "Mountain": "tree-conifer",
            "Star": "star"
        }
        for layer in self.csv_layers:
            icon_type = layer.get("icon", "Pin")
            for coordinate in layer["coordinates"]:
                lat, lon, alt, precision = coordinate
                popup_text = f"Altitude: {alt} m"
                if precision is not None:
                    popup_text += f", Precision: {precision} m"
                if os.path.exists(icon_type):
                    marker_icon = folium.features.CustomIcon(icon_type, icon_size=(32, 32))
                else:
                    marker_icon = folium.Icon(icon=icon_mapping.get(icon_type, "map-marker"), prefix='fa')
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    icon=marker_icon
                ).add_to(folium_map)
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

    # Update the map view based on the selected mapping mode
    def update_map_view(self):
        if self.map_mode == "OSM":
            folium_map = self.generate_osm_map()
        elif self.map_mode == "Google":
            folium_map = self.generate_google_map()
        elif self.map_mode == "Sentinel":
            date_time = self.map_mode_data if self.map_mode_data else "2023-01-01T00:00"
            folium_map = self.generate_sentinel_map(date_time)
        folium.LayerControl().add_to(folium_map)
        folium_map.save(self.map_file)
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(self.map_file)))

    # Set the mapping mode and update the view
    def set_map_mode(self, mode, data=None):
        self.map_mode = mode
        self.map_mode_data = data
        self.update_map_view()

    # Add a new CSV layer with its coordinates and chosen icon
    def add_layer(self, coordinates, icon):
        layer_name = f"CSV Layer {len(self.csv_layers) + 1}"
        new_layer = {"name": layer_name, "coordinates": coordinates, "icon": icon}
        self.csv_layers.append(new_layer)
        self.update_map_view()

    # Add a new vector layer using GeoJSON data and layer name
    def add_vector_layer(self, geojson, layer_name):
        new_layer = {"name": layer_name, "geojson": geojson}
        self.vector_layers.append(new_layer)
        self.update_map_view()

    # Combine all layers (CSV and vector) for management
    def all_layers(self):
        combined = []
        for layer in self.csv_layers:
            combined.append(layer)
        for layer in self.vector_layers:
            combined.append(layer)
        return combined

    # Update layer order based on a new order list (combined CSV and vector layers)
    def update_layer_order(self, new_layers):
        # For simplicity, assign CSV layers first if they are in new order, then vector layers.
        self.csv_layers = [layer for layer in new_layers if "coordinates" in layer]
        self.vector_layers = [layer for layer in new_layers if "geojson" in layer]
        self.update_map_view()

    # Capture the current map view as an image and allow the user to save it
    def capture_map(self):
        pixmap = self.web_view.grab()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Map Capture", "", "PNG Files (*.png)")
        if file_path:
            pixmap.save(file_path, "PNG")
