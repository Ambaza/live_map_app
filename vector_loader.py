# vector_loader.py
import geopandas as gpd

def load_vector_file(file_path, layer=None):
    try:
        if layer is not None:
            gdf = gpd.read_file(file_path, layer=layer)
        else:
            gdf = gpd.read_file(file_path)
        return gdf.to_json()
    except Exception as e:
        print(f"Error reading vector file: {e}")
        return None
