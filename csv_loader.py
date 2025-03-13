# csv_loader.py
import csv
import math  # Import math to check for NaN

def load_csv_coordinates(file_path, selected_columns):
    coordinates = []
    try:
        with open(file_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            x_col = selected_columns["X"]
            y_col = selected_columns["Y"]
            z_col = selected_columns["Z"]
            m_col = selected_columns["M"]
            for row in reader:
                x_val = row[x_col].strip()
                y_val = row[y_col].strip()
                if not x_val or not y_val:
                    continue
                try:
                    lon = float(x_val)
                    lat = float(y_val)
                    # Skip the row if conversion yields NaN
                    if math.isnan(lat) or math.isnan(lon):
                        continue
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

# New helper function to preview the first 10 lines
def get_csv_preview(file_path, n=10):
    preview_lines = []
    try:
        with open(file_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                preview_lines.append(row)
                if i >= n - 1:
                    break
    except Exception as e:
        print(f"Error previewing CSV file: {e}")
    return preview_lines
