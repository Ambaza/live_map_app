# csv_loader.py
import csv  # Import csv module to handle CSV file operations

# Function to load coordinates from the CSV file using user-selected columns
def load_csv_coordinates(file_path, selected_columns):
    coordinates = []  # Initialize an empty list to store coordinates
    try:
        with open(file_path, newline='', encoding='latin-1') as csvfile:  # Open the CSV file with latin-1 encoding
            reader = csv.DictReader(csvfile)  # Create a CSV dictionary reader

            # Retrieve the user-selected column names
            x_col = selected_columns["X"]
            y_col = selected_columns["Y"]
            z_col = selected_columns["Z"]
            m_col = selected_columns["M"]

            # Iterate through each row in the CSV
            for row in reader:
                lat = float(row[y_col])  # Convert latitude value to float
                lon = float(row[x_col])  # Convert longitude value to float
                alt = float(row[z_col]) if z_col and row[z_col] else 0  # Convert altitude or default to 0
                precision = float(row[m_col]) if m_col and row[m_col] else None  # Convert precision if available
                coordinates.append((lat, lon, alt, precision))  # Append the coordinate tuple to the list

    except Exception as e:
        print(f"Error reading CSV file: {e}")  # Print error if encountered

    return coordinates  # Return the list of coordinates
