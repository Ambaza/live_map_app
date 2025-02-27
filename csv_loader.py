
# csv_loader.py
import csv  # For CSV file operations

# Load coordinates from the CSV file using user-selected options
def load_csv_coordinates(file_path, selected_columns):
    coordinates = []  # Initialize list to store coordinates
    try:
        with open(file_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            x_col = selected_columns["X"]
            y_col = selected_columns["Y"]
            z_col = selected_columns["Z"]
            m_col = selected_columns["M"]
            for row in reader:
                if not row[x_col].strip() or not row[y_col].strip():
                    continue
                try:
                    lon = float(row[x_col].strip())
                    lat = float(row[y_col].strip())
                except Exception as e:
                    print(f"Error converting mandatory fields in row: {row}, skipping row")
                    continue
                alt = 0
                if z_col and row[z_col].strip():
                    try:
                        alt = float(row[z_col].strip())
                    except:
                        alt = 0
                precision = None
                if m_col and row[m_col].strip():
                    try:
                        precision = float(row[m_col].strip())
                    except:
                        precision = None
                coordinates.append((lat, lon, alt, precision))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return coordinates
