# Live Map App

## Overview
This application is a PyQT desktop application that displays a live map using Sentinel-2 imagery and allows users to load CSV files with coordinate data as an overlay. Users can manually select the CSV columns corresponding to:
- **X**: Longitude
- **Y**: Latitude
- **Z**: Altitude (optional for 3D mapping)
- **M**: Precision in meters (optional)

## Features
- **Live Map Display:** Utilizes folium and PyQtWebEngine to render a live map.
- **CSV Layer Integration:** Supports adding coordinate layers from CSV files with manual column selection.
- **Flexible CSV Compatibility:** Works with various CSV encodings (recommended: `latin-1`) and custom column headers.

## Installation
1. **Python Version:** Ensure Python 3.7 or higher is installed.
2. **Dependencies:** Install required libraries using the provided `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
