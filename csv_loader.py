import csv

def load_csv_coordinates(file_path):
    coordinates = []
    try:
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lat = float(row["X"])
                lon = float(row["Y"])
                alt = float(row["Z"])
                coordinates.append((lat, lon, alt))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return coordinates
