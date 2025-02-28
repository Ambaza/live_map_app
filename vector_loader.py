# vector_loader.py
import geopandas as gpd  # Import geopandas to handle vector GIS files

def load_vector_file(file_path):
    try:
        gdf = gpd.read_file(file_path)  # Read the vector file
        return gdf.to_json()  # Convert to GeoJSON string
    except Exception as e:
        print(f"Error reading vector file: {e}")
        return None
