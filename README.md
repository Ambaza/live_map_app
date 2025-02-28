# Live Map App

## Overview
This application is a PyQT desktop app that displays a live map with multiple mapping options and layered GIS data. Users can:
- Load CSV files with coordinate data.
- Load vector GIS files (e.g., SHP, SHX, GeoJSON, GPKG).
- Select mapping options including:
  - **OpenStreetMap**: Displays an OpenStreetMap view.
  - **Google Map**: Displays a Google Satellite view using custom tiles.
  - **Sentinel-2 Live Map**: Displays Sentinel-2 imagery using the Sentinel Hub API with OAuth2.
- Manage layers by reordering them.
- Capture the current map view as an image.
- Automatically detect CSV columns and select custom icons.

## New Features: GIS Data Import
A new button, **"Load GIS Data"**, lets you import vector files such as:
- Shapefiles (.shp, .shx)
- GeoJSON files
- GeoPackage files (.gpkg)

The app uses GeoPandas to read these files and adds them as vector layers on the map.

## Configuration for Sentinel-2
1. Register an OAuth client in your Sentinel Hub account.
2. Replace `<your_client_id>`, `<your_client_secret>`, and `<your_instance_id>` in `map_widget.py` with your actual credentials.
3. Ensure your OAuth client has permissions to access the Sentinel Hub WMS service.

## Installation
Install dependencies:
```bash
pip install -r requirements.txt


File Structure

live_map_app/
├── main.py
├── map_widget.py
├── csv_loader.py
├── vector_loader.py
├── icon_selector.py
├── vector_layer_selector.py
├── layer_preview.py
├── requirements.txt
└── README.md
