# csv_loader.py
import csv  # Import csv module for CSV file operations

# Function to load coordinates from the CSV file using user-selected options
def load_csv_coordinates(file_path, selected_columns):
    coordinates = []  # Initialize an empty list to store coordinates
    try:
        with open(file_path, newline='', encoding='latin-1') as csvfile:  # Open CSV with latin-1 encoding
            reader = csv.DictReader(csvfile)  # Create a CSV dictionary reader

            # Retrieve user-selected column names
            x_col = selected_columns["X"]
            y_col = selected_columns["Y"]
            z_col = selected_columns["Z"]
            m_col = selected_columns["M"]

            # Iterate over each row in the CSV file
            for row in reader:
                # Skip the row if mandatory fields are empty
                if not row[x_col].strip() or not row[y_col].strip():
                    continue

                try:
                    # Convert mandatory fields to float after stripping whitespace
                    lon = float(row[x_col].strip())
                    lat = float(row[y_col].strip())
                except Exception as e:
                    print(f"Error converting mandatory fields in row: {row}, skipping row")
                    continue

                # Convert optional altitude (Z) field; default to 0 if empty or conversion fails
                alt = 0
                if z_col and row[z_col].strip():
                    try:
                        alt = float(row[z_col].strip())
                    except:
                        alt = 0

                # Convert optional precision (M) field; default to None if empty or conversion fails
                precision = None
                if m_col and row[m_col].strip():
                    try:
                        precision = float(row[m_col].strip())
                    except:
                        precision = None

                # Append the processed coordinate tuple to the list
                coordinates.append((lat, lon, alt, precision))

    except Exception as e:
        print(f"Error reading CSV file: {e}")  # Print error message if any issues occur

    return coordinates  # Return the list of coordinates
