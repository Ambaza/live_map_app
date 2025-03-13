# Live Map App

## Project Overview
The **Live Map App** is a Python-based application designed to visualize geospatial data interactively. It allows users to load various geographic data formats (CSV, vector files) and display them on an interactive map with dynamic layers and icons.

## Installation & Setup
### Prerequisites
- Python 3.10+
- Required dependencies (listed in `requirements.txt`)

### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/Ambaza/live_map_app.git
   cd live_map_app
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   python main.py
   ```

## Project Structure
```
live_map_app/
├── main.py                   # Entry point of the application
├── map_widget.py             # Manages interactive map display using Leaflet.js (via Python bindings)
├── csv_loader.py             # Handles loading and parsing of CSV files containing geospatial data
├── vector_loader.py          # Loads and processes vector data (Shapefiles, GeoJSON, etc.)
├── icon_selector.py          # Dynamically selects and applies icons to map markers
├── vector_layer_selector.py  # Allows users to choose different vector layers to display
├── layer_preview.py          # Provides a preview of selected map layers before rendering
├── spss_viewer.py            # Handles display and analysis of SPSS (.sav) files
├── requirements.txt          # Lists dependencies required for the project
└── README.md                 # Project documentation
```

## How It Works
1. **Loading Data**:
   - Users can upload **CSV files** (longitude, latitude columns are automatically detected).
   - Users can load **vector files** (Shapefiles, GeoJSON, etc.).
2. **Map Interaction**:
   - Data is rendered on an **interactive map**.
   - Users can select layers and adjust visibility dynamically.
3. **Icon Customization**:
   - Icons are chosen based on data properties using `icon_selector.py`.
4. **SPSS Data Integration**:
   - Users can load SPSS files (`.sav`) to visualize statistical data geographically.

## Current Development Status
- [x] CSV loading and parsing
- [x] Basic map rendering
- [x] Vector file support
- [ ] Advanced filtering options (in progress)
- [ ] Real-time updates (planned)
- [ ] Improved error handling (planned)

## Common Errors & Debugging
### `Invalid LatLng object: (X, NaN)`
- This occurs when **latitude or longitude values are missing or not properly converted to numbers**.
- **Solution:**
  - Ensure the CSV or vector data is correctly formatted.
  - Check for missing values before passing coordinates to the map.
  - Implement better error handling when parsing numbers.

## Future Features & Roadmap
- **Real-time data updates** from external APIs
- **User-defined styles** for map layers
- **Offline map support**
- **Mobile-friendly UI improvements**

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Description of changes"`).
4. Push to your branch (`git push origin feature-name`).
5. Open a Pull Request.

## License
[MIT License](LICENSE)
