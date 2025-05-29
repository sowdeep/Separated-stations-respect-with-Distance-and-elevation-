import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Haversine formula to calculate distance between two points (in km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# Load station data from CSV
def load_station_data(file_path):
    try:
        # Use comma as delimiter for the .csv file
        stations = pd.read_csv(file_path, sep=',')
        required_columns = ['station_name', 'latitude', 'longitude', 'elevation']
        if not all(col in stations.columns for col in required_columns):
            raise ValueError("CSV file must contain columns: station_name, latitude, longitude, elevation")
        # Ensure numeric columns
        stations['latitude'] = pd.to_numeric(stations['latitude'], errors='coerce')
        stations['longitude'] = pd.to_numeric(stations['longitude'], errors='coerce')
        stations['elevation'] = pd.to_numeric(stations['elevation'], errors='coerce')
        if stations.isnull().any().any():
            print("Warning: Missing or invalid values detected in the data. Please check the input file.")
        return stations
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

# Compute pairwise distances between all stations
def compute_pairwise_distances(stations):
    n = len(stations)
    distances = pd.DataFrame(index=stations['station_name'], columns=stations['station_name'], dtype=float)
    for i, row1 in stations.iterrows():
        for j, row2 in stations.iterrows():
            if i != j:
                distances.loc[row1['station_name'], row2['station_name']] = haversine(
                    row1['latitude'], row1['longitude'], row2['latitude'], row2['longitude']
                )
    return distances

# Find stations within ±100 m elevation
def find_elevation_matches(stations, elevation_tolerance=100):
    elevation_matches = {}
    for i, row in stations.iterrows():
        station_name = row['station_name']
        elevation = row['elevation']
        matches = stations[
            (stations['elevation'] >= elevation - elevation_tolerance) &
            (stations['elevation'] <= elevation + elevation_tolerance) &
            (stations['station_name'] != station_name)
        ]['station_name'].tolist()
        elevation_matches[station_name] = matches
    return elevation_matches

# Create the station-based table
def create_station_table(stations, distances, elevation_matches, max_distance=100):
    table = stations[['station_name', 'latitude', 'longitude', 'elevation']].copy()
    table['Range'] = ''
    table['Elevation'] = ''
    
    for station in table['station_name']:
        # All stations within 100 km
        nearby = distances[station][distances[station] <= max_distance].index.tolist()
        nearby = [s for s in nearby if s != station]  # Exclude the station itself
        table.loc[table['station_name'] == station, 'Range'] = '; '.join(nearby)
        
        # All stations within ±100 m elevation
        table.loc[table['station_name'] == station, 'Elevation'] = '; '.join(elevation_matches[station])
    
    return table

# Main function
def main(file_path):
    # Load data
    stations = load_station_data(file_path)
    if stations is None:
        return
    
    # Compute distances and elevation matches
    distances = compute_pairwise_distances(stations)
    elevation_matches = find_elevation_matches(stations)
    
    # Create and save the table
    table = create_station_table(stations, distances, elevation_matches)
    output_file = 'station_proximity_table.csv'
    table.to_csv(output_file, index=False)
    print(f"Station proximity table saved to {output_file}")

# Run the program
if __name__ == "__main__":
    file_path = 'C:\\Users\\aaa\\Desktop\\stations works\\stations.csv'  # Updated to .csv file
    main(file_path)