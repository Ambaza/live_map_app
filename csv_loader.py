# csv_loader.py
import csv  # Import csv module to handle CSV file operations

# Function to load coordinates from the CSV file using user-selected columns
from typing import Dict, List, Optional, Tuple

def load_csv_coordinates(
    file_path: str,
    selected_columns: Dict[str, str]
) -> List[Tuple[float, float, float, Optional[float]]]:
    """
    Load coordinates from the CSV file using user-selected columns

    Args:
        file_path: Path to the CSV file
        selected_columns: A dictionary containing the keys 'x', 'y', 'z', and 'm'
            with the corresponding column names in the CSV file

    Returns:
        A list of tuples containing the coordinates in the format (lat, lon, alt, precision)
    """
    coordinates: List[Tuple[float, float, float, Optional[float]]] = []
    try:
        with open(file_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            x_col, y_col, z_col, m_col = selected_columns.values()
            for row in reader:
                try:
                    lat = float(row[y_col])
                    lon = float(row[x_col])
                    alt = float(row[z_col]) if z_col else 0
                    precision = float(row[m_col]) if m_col else None
                    coordinates.append((lat, lon, alt, precision))
                except ValueError:
                    pass
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return coordinates
