# map_widget.py
import os  # For file path operations
import math  # For math.isnan
import logging  # For logging errors
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog  # For widget layout and file dialogs
from PyQt5.QtWebEngineWidgets import QWebEngineView  # To display web content
from PyQt5.QtCore import QUrl  # For handling URLs
from PyQt5.QtGui import QPixmap  # For capturing the map view
import folium  # For generating maps

# Configure logging to file
logging.basicConfig(
    level=logging.ERROR,
    filename="error_log.txt",
    filemode="a",
    format="%(asctime)s %(levelname)s: %(message)s"
)

# Import for Sentinel OAuth token retrieval
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

def get_sentinel_token():
    """
    Fetch Sentinel Hub OAuth token.
    """
    client_id = "850b83f6-ae06-47de-b0d1-2b1d34171b57"
    client_secret = "WtYF5yWvIq8VLZPZn5NcIXZe46jP7Unk"
    token_url = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
    return token.get("access_token")

def convert_to_float(value):
    """
    Convert a coordinate value to float.
    Handles string values that may use commas as decimal separators.
    Returns a float, or None if conversion fails.
    """
    try:
        if isinstance(value, str):
            # Remove any thousand separators (e.g., spaces or periods) if needed,
            # then replace comma with dot for decimal conversion.
            value = value.strip().replace(" ", "").replace(",", ".")
        num = float(value)
        return num
    except (ValueError, TypeError):
        return None

def validate_coordinates(lat, lon):
    """
    Validate latitude and longitude values.
    Converts values using convert_to_float.
    Returns True if both are valid numbers within acceptable ranges.
    """
    lat_conv = convert_to_float(lat)
    lon_conv = convert_to_float(lon)
    if lat_conv is None or lon_conv is None:
        return False
    if math.isnan(lat_conv) or math.isnan(lon_conv):
        return False
    if not (-90 <= lat_conv <= 90 and -180 <= lon_conv <= 180):
        return False
    return True

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)  # Set widget layout

        # Create a QWebEngineView to display the generated map
        self.web_view = QWebEngineView()
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        self.layout.addWidget(self.web_view)

        self.map_file = "map.html"  # HTML file to store the generated map
        self.csv_layers = []      # List of CSV layers
        self.vector_layers = []   # List of vector layers

        self.map_mode = "OSM"     # Default mapping mode is OpenStreetMap
        self.map_mode_data = None # Additional data (e.g., date/time for Sentinel)

        self.update_map_view()    # Render the initial map

    def add_marker_if_valid(self, folium_map, lat, lon, popup_text, marker_icon):
        """
        Convert and validate lat/lon, and add marker if valid.
        """
        lat_conv = convert_to_float(lat)
        lon_conv = convert_to_float(lon)
        if validate_coordinates(lat_conv, lon_conv):
            folium.Marker(location=[lat_conv, lon_conv], popup=popup_text, icon=marker_icon).add_to(folium_map)
        else:
            logging.error(f"Invalid coordinates skipped: ({lat}, {lon}) with popup '{popup_text}'")

    def generate_osm_map(self):
        folium_map = folium.Map(location=[0, 0], zoom_start=2)
        icon_mapping = {"Pin": "map-marker", "Mountain": "tree-conifer", "Star": "star"}
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
                self.add_marker_if_valid(folium_map, lat, lon, popup_text, marker_icon)
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
        icon_mapping = {"Pin": "map-marker", "Mountain": "tree-conifer", "Star": "star"}
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
                self.add_marker_if_valid(folium_map, lat, lon, popup_text, marker_icon)
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
            extra_params={"token": token, "datetime": date_time, "MAXCC": 20}
        )
        wms.add_to(folium_map)
        icon_mapping = {"Pin": "map-marker", "Mountain": "tree-conifer", "Star": "star"}
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
                self.add_marker_if_valid(folium_map, lat, lon, popup_text, marker_icon)
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

    def generate_cropland_map(self):
        # Using Earth Engine to display the USGS cropland dataset (1000m resolution)
        import ee
        try:
            ee.Initialize(project="npa-base-line-2023")
        except Exception as e:
            logging.error(f"Earth Engine initialization error: {e}")
            raise e
        dataset = ee.Image("USGS/GFSAD1000_V1")
        visParams = {'min': 0, 'max': 100, 'palette': ['ffffff', 'ffff00', 'ff0000']}
        mapid = dataset.getMapId(visParams)
        tile_url = mapid['tile_fetcher'].url_format
        folium_map = folium.Map(location=[0, 0], zoom_start=2, tiles=tile_url, attr="Cropland Classification")
        icon_mapping = {"Pin": "map-marker", "Mountain": "tree-conifer", "Star": "star"}
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
                self.add_marker_if_valid(folium_map, lat, lon, popup_text, marker_icon)
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(folium_map)
        return folium_map

    def generate_geemap_cropland_map(self, date_time):
        # Use geemap for high quality interactive visualization
        import ee
        import geemap
        try:
            ee.Initialize(project="npa-base-line-2023")
        except Exception as e:
            logging.error(f"Earth Engine initialization error with geemap: {e}")
            ee.Authenticate()  # This will prompt for authentication if needed
            ee.Initialize(project="npa-base-line-2023")
        dataset = ee.Image("USGS/GFSAD1000_V1")
        visParams = {'min': 0, 'max': 100, 'palette': ['ffffff', 'ffff00', 'ff0000']}
        Map = geemap.Map(center=[0, 0], zoom=2)
        Map.add_ee_layer(dataset, visParams, "Cropland Classification")
        for layer in self.csv_layers:
            for coordinate in layer["coordinates"]:
                lat, lon, alt, precision = coordinate
                popup_text = f"Altitude: {alt} m"
                if precision is not None:
                    popup_text += f", Precision: {precision} m"
                if validate_coordinates(lat, lon):
                    import folium
                    folium.Marker(location=[convert_to_float(lat), convert_to_float(lon)], popup=popup_text).add_to(Map)
                else:
                    logging.error(f"Invalid coordinates in geemap layer: ({lat}, {lon})")
        for layer in self.vector_layers:
            folium.GeoJson(layer["geojson"], name=layer["name"]).add_to(Map)
        return Map

    def update_map_view(self):
        if self.map_mode == "OSM":
            folium_map = self.generate_osm_map()
        elif self.map_mode == "Google":
            folium_map = self.generate_google_map()
        elif self.map_mode == "Sentinel":
            date_time = self.map_mode_data if self.map_mode_data else "2023-01-01T00:00"
            folium_map = self.generate_sentinel_map(date_time)
        elif self.map_mode == "Cropland":
            folium_map = self.generate_cropland_map()
        elif self.map_mode == "GeemapCropland":
            date_time = self.map_mode_data if self.map_mode_data else "2023-01-01T00:00"
            geemap_map = self.generate_geemap_cropland_map(date_time)
            geemap_map.to_html(self.map_file)
            self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(self.map_file)))
            return
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
