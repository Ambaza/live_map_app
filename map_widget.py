# map_widget.py
import os
import math
import logging
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
import folium
import ee
import geemap
import json
import requests, datetime
import numpy as np
import rasterio
from rasterio.plot import show
from rasterio.mask import mask
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
from branca.colormap import linear

logging.basicConfig(
    level=logging.ERROR,
    filename="error_log.txt",
    filemode="a",
    format="%(asctime)s %(levelname)s: %(message)s"
)

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

def get_sentinel_token():
    client_id = os.environ.get("PLANET_CLIENT_ID", "")
    client_secret = os.environ.get("PLANET_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise ValueError("Identifiants Planet manquants : définissez PLANET_CLIENT_ID et PLANET_CLIENT_SECRET.")
    auth_url = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(auth_url, client_id=client_id, client_secret=client_secret)
    return token.get("access_token")

def convert_to_float(value):
    try:
        if isinstance(value, str):
            value = value.strip().replace(" ", "").replace(",", ".")
        return float(value)
    except (ValueError, TypeError):
        return None

def validate_coordinates(lat, lon):
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
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        self.layout.addWidget(self.web_view)
        self.map_file = "map.html"
        self.csv_layers = []
        self.vector_layers = []
        self.map_mode = "OSM"
        self.map_mode_data = None
        self.update_map_view()

    def add_marker_if_valid(self, folium_map, lat, lon, popup_text, marker_icon):
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

    def generate_sentinel_ndvi_map(self, date_time, roi=None):
        if roi is None:
            roi = {
                "type": "Polygon",
                "coordinates": [[
                    [-122.6, 37.0],
                    [-121.8, 37.0],
                    [-121.8, 38.0],
                    [-122.6, 38.0],
                    [-122.6, 37.0]
                ]]
            }
        if 'T' in date_time:
            dt = datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        else:
            dt = datetime.datetime.strptime(date_time, "%Y-%m-%d")
        start_date = (dt - datetime.timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z")
        end_date = (dt + datetime.timedelta(days=7)).strftime("%Y-%m-%dT23:59:59Z")
        PLANET_API_KEY = os.environ.get("PLANET_API_KEY", "")
        if not PLANET_API_KEY:
            raise ValueError("Clé Planet manquante : définissez la variable d'environnement PLANET_API_KEY pour afficher les données satellite.")
        search_url = "https://api.planet.com/data/v1/searches"
        search_request = {
            "name": "Sentinel2L2A NDVI Search",
            "item_types": ["Sentinel2L2A"],
            "filter": {
                "type": "AndFilter",
                "config": [
                    {"type": "GeometryFilter", "field_name": "geometry", "config": roi},
                    {"type": "DateRangeFilter", "field_name": "acquired", "config": {"gte": start_date, "lte": end_date}},
                    {"type": "RangeFilter", "field_name": "cloud_cover", "config": {"lt": 10}}
                ]
            }
        }
        response = requests.post(search_url, json=search_request, auth=(PLANET_API_KEY, ""))
        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")
        search_results = response.json()
        features = search_results.get("features", [])
        if not features:
            raise Exception("No Sentinel-2 images found for the given date and region.")
        item_id = features[0]["id"]
        red_band_url = f"https://api.planet.com/data/v1/item-types/Sentinel2L2A/items/{item_id}/assets/B04?api_key={PLANET_API_KEY}"
        nir_band_url = f"https://api.planet.com/data/v1/item-types/Sentinel2L2A/items/{item_id}/assets/B08?api_key={PLANET_API_KEY}"
        def download_band(url):
            band_response = requests.get(url, stream=True)
            if band_response.status_code != 200:
                raise Exception(f"Failed to download band: {url}")
            with rasterio.open(BytesIO(band_response.content)) as dataset:
                return dataset.read(1), dataset.profile
        red_band, profile = download_band(red_band_url)
        nir_band, _ = download_band(nir_band_url)
        ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band + red_band + 1e-10)
        ndvi_norm = (ndvi - ndvi.min()) / (ndvi.max() - ndvi.min())
        cmap = plt.get_cmap('RdYlGn')
        ndvi_colored = (cmap(ndvi_norm)[:, :, :3] * 255).astype(np.uint8)
        ndvi_image = Image.fromarray(ndvi_colored)
        temp_ndvi_path = "ndvi_image.png"
        ndvi_image.save(temp_ndvi_path)
        lat, lon = roi["coordinates"][0][0][1], roi["coordinates"][0][0][0]
        folium_map = folium.Map(location=[lat, lon], zoom_start=12)
        folium.raster_layers.ImageOverlay(
            image=temp_ndvi_path,
            bounds=[[roi["coordinates"][0][1][1], roi["coordinates"][0][1][0]],
                    [roi["coordinates"][0][3][1], roi["coordinates"][0][3][0]]],
            colormap=lambda x: (1 - x, x, 0, 1),
            opacity=0.6
        ).add_to(folium_map)
        colormap_obj = linear.RdYlGn_09.scale(-1, 1).to_step(10)
        colormap_obj.caption = "NDVI Index"
        folium_map.add_child(colormap_obj)
        return folium_map

    def generate_cropland_map(self):
        try:
            ee.Initialize(project="npa-base-line-2023")
        except Exception as e:
            logging.error(f"EE initialization error: {e}")
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
        import datetime
        try:
            ee.Initialize(project="npa-base-line-2023")
        except Exception as e:
            logging.error("EE initialization error: %s", e)
            ee.Initialize(project="npa-base-line-2023")
        roi = ee.Geometry.Rectangle([-122.6, 37.0, -121.8, 38.0])
        if date_time:
            try:
                dt = datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
                start_date = (dt - datetime.timedelta(days=15)).strftime("%Y-%m-%d")
                end_date = (dt + datetime.timedelta(days=15)).strftime("%Y-%m-%d")
            except Exception as e:
                logging.error("Error parsing date_time: %s", e)
                start_date = '2021-06-01'
                end_date = '2021-09-30'
        else:
            start_date = '2021-06-01'
            end_date = '2021-09-30'
        collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                      .filterBounds(roi)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)))
        composite = collection.median().clip(roi)
        ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI')
        cropland_class = ndvi.gt(0.4).rename('Cropland')
        Map = geemap.Map(center=[37.5, -122.2], zoom=10)
        Map.addLayer(composite, {"bands": ["B4", "B3", "B2"], "max": 3000}, "Sentinel-2 Composite")
        Map.addLayer(cropland_class, {"min": 0, "max": 1, "palette": ["white", "green"]}, "Cropland Classification")
        for layer in self.csv_layers:
            for coordinate in layer["coordinates"]:
                lat, lon, alt, precision = coordinate
                popup_text = f"Altitude: {alt} m"
                if precision is not None:
                    popup_text += f", Precision: {precision} m"
                lat_conv = convert_to_float(lat)
                lon_conv = convert_to_float(lon)
                if (lat_conv is None or lon_conv is None or math.isnan(lat_conv) or math.isnan(lon_conv)):
                    logging.error(f"Invalid coordinates for geemap marker: ({lat}, {lon})")
                    continue
                Map.add_marker(location=[lat_conv, lon_conv], popup=popup_text)
        for layer in self.vector_layers:
            try:
                geojson_data = json.loads(layer["geojson"]) if isinstance(layer["geojson"], str) else layer["geojson"]
                Map.add_geojson(geojson_data, layer_name=layer["name"])
            except Exception as e:
                logging.error(f"Error adding vector layer {layer['name']}: {e}")
        Map.addLayerControl()
        return Map

    def update_map_view(self):
        folium_map = None
        if self.map_mode == "OSM":
            folium_map = self.generate_osm_map()
        elif self.map_mode == "Google":
            folium_map = self.generate_google_map()
        elif self.map_mode == "Sentinel":
            date_time = self.map_mode_data if self.map_mode_data else "2023-01-01T00:00"
            try:
                folium_map = self.generate_sentinel_ndvi_map(date_time)
            except ValueError as e:
                logging.error(f"Données Planet indisponibles : {e}")
                self.web_view.setHtml(f"<h3>Données Planet indisponibles</h3><p>{e}</p>")
                return
        elif self.map_mode == "Cropland":
            folium_map = self.generate_cropland_map()
        elif self.map_mode == "GeemapCropland":
            date_time = self.map_mode_data if self.map_mode_data else "2023-01-01T00:00"
            geemap_map = self.generate_geemap_cropland_map(date_time)
            geemap_map.to_html(self.map_file)
            self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(self.map_file)))
            return
        if folium_map is None:
            folium_map = folium.Map(location=[0, 0], zoom_start=2)
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
