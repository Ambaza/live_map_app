# Live Map App

## Overview
This application is a PyQT desktop application that displays a live map with multiple mapping options and CSV layer overlays. Users can:
- Load multiple CSV files with coordinate data.
- Select mapping options including:
  - **OpenStreetMap**: Displays an OpenStreetMap view with CSV layer markers.
  - **Google Map**: Displays a map using a custom Google Satellite tile layer.
  - **Sentinel-2 Live Map**: Allows the user to select a date and time to view Sentinel-2 imagery using the Sentinel Hub API with OAuth2 authentication.
- Manage CSV layers by selecting custom icons and reordering them.
- Capture the current map view as an image.
- **Automatic Field Selection**: The app now attempts to auto-select CSV columns for Longitude, Latitude, and Altitude based on header keywords.

## Features
- **Live Map Display**: Renders maps using folium and PyQtWebEngine.
- **Multiple Mapping Modes**: Toggle between OpenStreetMap, Google Map, and Sentinel-2 Live Map.
- **CSV Layer Integration**: Load and display multiple CSV layers with custom icons.
- **Layer Management**: Reorder CSV layers to determine display priority.
- **Map Capture**: Save a snapshot of the current map view.
- **Sentinel Hub Integration**: Uses OAuth2 to authenticate requests for Sentinel-2 imagery.
- **Automatic CSV Field Detection**: Automatically selects appropriate columns for Longitude, Latitude, and Altitude based on header keywords.

## Configuration for Sentinel-2
To use the Sentinel-2 mapping mode:
1. Register an OAuth client in your Sentinel Hub account.
2. Replace the placeholder `<your_client_id>`, `<your_client_secret>`, and `<your_instance_id>` in `map_widget.py` with your actual credentials and instance identifier.
3. Ensure your OAuth client has permissions to access the Sentinel Hub WMS service.

## Running the Application
Start the application with:
```bash
python main.py
