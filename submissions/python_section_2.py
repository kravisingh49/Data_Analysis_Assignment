import pandas as pd
import numpy as np
import datetime

# Filepath for the dataset
filepath = 'datasets/dataset-2.csv'

# Function to calculate a distance matrix based on location IDs
def calculate_distance_matrix():
    # Load the dataset from the given filepath
    df = pd.read_csv(filepath)
    
    # Extract unique location IDs from the dataset
    ids = np.sort(df['ID'].unique())
    
    # Create an empty DataFrame with unique IDs as both rows and columns to store distances
    distance_matrix = pd.DataFrame(np.inf, index=ids, columns=ids)
    
    # Fill the diagonal with zeros since the distance from any location to itself is zero
    np.fill_diagonal(distance_matrix.values, 0)
    
    # Loop through each row in the dataset to populate the distance matrix
    for _, row in df.iterrows():
        id1, id2, distance = row['ID1'], row['ID2'], row['Distance']
        
        # Set the distance between id1 and id2 in both directions (since the matrix is symmetric)
        distance_matrix.loc[id1, id2] = min(distance, distance_matrix.loc[id1, id2])
        distance_matrix.loc[id2, id1] = min(distance, distance_matrix.loc[id2, id1])
    
    # Apply Floyd-Warshall algorithm to calculate the shortest path between all pairs
    for k in ids:
        for i in ids:
            for j in ids:
                # If the direct distance between i and j is longer than going through k, update the distance
                if distance_matrix.loc[i, j] > distance_matrix.loc[i, k] + distance_matrix.loc[k, j]:
                    distance_matrix.loc[i, j] = distance_matrix.loc[i, k] + distance_matrix.loc[k, j]
                    distance_matrix.loc[j, i] = distance_matrix.loc[i, j]  # Ensure symmetry
    
    return distance_matrix

# Usage:
# result_matrix = calculate_distance_matrix()
# print(result_matrix)


# Function to unroll the distance matrix into a long format DataFrame
def unroll_distance_matrix(distance_matrix):
    # Initialize an empty list to store the unrolled data
    records = []
    
    # Iterate over each pair of IDs in the distance matrix
    for id_start in distance_matrix.index:
        for id_end in distance_matrix.columns:
            # Skip diagonal elements where start and end IDs are the same
            if id_start != id_end:
                # Append a record for the current distance pair
                records.append({
                    'id_start': id_start,
                    'id_end': id_end,
                    'distance': distance_matrix.at[id_start, id_end]
                })
    
    # Convert the list of records into a DataFrame
    result_df = pd.DataFrame(records, columns=['id_start', 'id_end', 'distance'])
    
    return result_df

# Usage:
# unrolled_df = unroll_distance_matrix(result_matrix)
# print(unrolled_df)


# Function to find location IDs whose average distance is within 10% of the reference ID's average distance
def find_ids_within_ten_percentage_threshold(df, reference_id):
    # Calculate the average distance for the reference ID (id_start)
    reference_avg_distance = df[df['id_start'] == reference_id]['distance'].mean()
    
    # Define the 10% threshold for comparison
    lower_threshold = reference_avg_distance * 0.9
    upper_threshold = reference_avg_distance * 1.1
    
    # Group the data by id_start and calculate the average distance for all IDs
    avg_distances = df.groupby('id_start')['distance'].mean()
    
    # Filter IDs whose average distances fall within the 10% range of the reference average
    ids_within_threshold = avg_distances[
        (avg_distances >= lower_threshold) & (avg_distances <= upper_threshold)
    ].index.tolist()
    
    # Sort the list of IDs
    ids_within_threshold.sort()
    
    return ids_within_threshold

# Usage:
# For example, to find IDs within 10% of the average distance of ID 1001400:
# id_list = find_ids_within_ten_percentage_threshold(unrolled_df, 1001400)
# print(id_list)


# Function to calculate toll rates for various vehicle types based on distance
def calculate_toll_rate(df):
    # Define the toll rate coefficients for different vehicle types
    rate_coefficients = {
        'moto': 0.8,
        'car': 1.2,
        'rv': 1.5,
        'bus': 2.2,
        'truck': 3.6
    }
    
    # Loop through each vehicle type and calculate the toll rate based on the distance
    for vehicle, coefficient in rate_coefficients.items():
        df[vehicle] = df['distance'] * coefficient
    
    return df

# Usage:
# toll_rates_df = calculate_toll_rate(unrolled_df)
# print(toll_rates_df)


# Function to calculate time-based toll rates with weekday and weekend discounts
def calculate_time_based_toll_rates(df):
    # List of vehicle types to apply time-based toll rates
    vehicle_types = ['moto', 'car', 'rv', 'bus', 'truck']
    
    # Define time ranges and their respective discount factors for weekdays
    weekday_time_discounts = [
        ('00:00:00', '10:00:00', 0.8),  # Early morning discount
        ('10:00:00', '18:00:00', 1.2),  # Peak hour surcharge
        ('18:00:00', '23:59:59', 0.8)   # Evening discount
    ]
    
    # Define a uniform weekend discount factor
    weekend_discount = 0.7
    
    # Create an empty DataFrame to store the expanded results
    expanded_df = pd.DataFrame()
    
    # Loop through each unique combination of id_start and id_end in the dataset
    for (id_start, id_end), group in df.groupby(['id_start', 'id_end']):
        # Apply weekday toll rates
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            for start_time, end_time, factor in weekday_time_discounts:
                # Apply the discount factor to all vehicle types
                for vehicle in vehicle_types:
                    group[vehicle] *= factor
                # Create a new row for the current day and time range
                row = group.iloc[0].copy()
                row[['start_day', 'start_time', 'end_day', 'end_time']] = [
                    day, datetime.time.fromisoformat(start_time), day, datetime.time.fromisoformat(end_time)
                ]
                # Append the row to the expanded DataFrame
                expanded_df = expanded_df.append(row, ignore_index=True)
        
        # Apply weekend toll rates
        for day in ['Saturday', 'Sunday']:
            # Apply the weekend discount to all vehicle types
            for vehicle in vehicle_types:
                group[vehicle] *= weekend_discount
            # Create a new row for the weekend (all day)
            row = group.iloc[0].copy()
            row[['start_day', 'start_time', 'end_day', 'end_time']] = [
                day, datetime.time.min, day, datetime.time.max
            ]
            # Append the row to the expanded DataFrame
            expanded_df = expanded_df.append(row, ignore_index=True)
    
    return expanded_df

# Usage:
# time_based_toll_rates_df = calculate_time_based_toll_rates(toll_rates_df)
# print(time_based_toll_rates_df)
