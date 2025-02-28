# map_widget.py
import os  # For file path operations
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
import folium  # For generating maps

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
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        self.layout.addWidget(self.web_view)
        self.map_file = "map.html"
        self.csv_layers = []  # List of CSV layers
        self.vector_layers = []  # List of vector layers
        self.map_mode = "OSM"
        self.map_mode_data = None
        self.update_map_view()

    def generate_osm_map(self):
        folium_map = folium.Map(location=[0, 0], zoom_start=2)
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
                folium.Marker(location=[lat, lon], popup=popup_text, icon=marker_icon).add_to(folium_map)
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

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
                folium.Marker(location=[lat, lon], popup=popup_text, icon=marker_icon).add_to(folium_map)
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

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
                folium.Marker(location=[lat, lon], popup=popup_text, icon=marker_icon).add_to(folium_map)
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

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

    def set_map_mode(self, mode, data=None):
        self.map_mode = mode
        self.map_mode_data = data
        self.update_map_view()

    def add_layer(self, coordinates, icon):
        layer_name = f"CSV Layer {len(self.csv_layers) + 1}"
        new_layer = {"name": layer_name, "coordinates": coordinates, "icon": icon}
        self.csv_layers.append(new_layer)
        self.update_map_view()

    def add_vector_layer(self, geojson, layer_name):
        new_layer = {"name": layer_name, "geojson": geojson}
        self.vector_layers.append(new_layer)
        self.update_map_view()

    def all_layers(self):
        combined = []
        for layer in self.csv_layers:
            combined.append(layer)
        for layer in self.vector_layers:
            combined.append(layer)
        return combined

    def update_layer_order(self, new_layers):
        self.csv_layers = [layer for layer in new_layers if "coordinates" in layer]
        self.vector_layers = [layer for layer in new_layers if "geojson" in layer]
        self.update_map_view()

    def capture_map(self):
        pixmap = self.web_view.grab()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Map Capture", "", "PNG Files (*.png)")
        if file_path:
            pixmap.save(file_path, "PNG")
