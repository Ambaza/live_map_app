# Live Map App

## Overview
This application is a PyQT desktop application that displays a live map using Sentinel-2 imagery and allows users to load multiple CSV files with coordinate data as overlays. Users can manually select the CSV columns corresponding to:
- **X**: Longitude
- **Y**: Latitude
- **Z**: Altitude (optional for 3D mapping)
- **M**: Precision in meters (optional)

Additionally, users can choose a custom icon for each CSV layer (e.g., Pin, Mountain, Star) and manage the layer order. The application also provides functionality to capture the current map view as an image.

## Features
- **Live Map Display:** Renders a live map using folium and PyQtWebEngine.
- **Multiple CSV Layers:** Add and display multiple CSV layers simultaneously, each with a distinct icon.
- **Custom Icon Selection:** Choose from available icons (Pin, Mountain, Star) for each CSV layer.
- **Layer Management:** Reorder layers to control their display priority.
- **Map Capture:** Capture and save the current map view at the current zoom level.

## Installation
1. **Python Version:** Ensure Python 3.7 or higher is installed.
2. **Dependencies:** Install required libraries using the provided `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
