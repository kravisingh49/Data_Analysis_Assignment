from typing import Dict, List
import pandas as pd
import re
import numpy as np
import polyline

def reverse_by_n_elements(lst: List[int], n: int) -> List[int]:
    """ Reverse every group of n elements in the list. """

    result = []  # Initialize the result list to store the final reversed list
    i = 0  # Start index for the first chunk
    while i < len(lst):
        chunk = []  # Temporary list to hold the current chunk before reversing
        for j in range(i, min(i + n, len(lst))):  # Loop over the current chunk
            chunk.insert(0, lst[j])  # Insert each element at the beginning to reverse the order
        result.extend(chunk)  # Add the reversed chunk to the result list
        i += n  # Move to the start of the next chunk
    return result


def group_by_length(lst: List[str]) -> Dict[int, List[str]]:
    """ Group strings by their length in a dictionary. """

    result = {}  # Dictionary to hold the grouped strings
    for string in lst:
        length = len(string)  # Calculate the length of each string
        if length not in result:
            result[length] = []  # Create a new list for this length if it doesn't exist
        result[length].append(string)  # Add the string to the appropriate list
    return dict(sorted(result.items()))  # Return the dictionary sorted by key (string length)



def flatten_dict(nested_dict, sep='.') -> Dict:
    """ Flatten a nested dictionary, concatenating keys. """

    flattened = {}  # Dictionary to store the flattened results
    
    def flatten(item, parent_key=''):
        if isinstance(item, dict):  # Check if the current item is a dictionary
            for key, value in item.items():
                new_key = parent_key + sep + key if parent_key else key  # Form a new key
                flatten(value, new_key)  # Recursively flatten further
        else:
            flattened[parent_key] = item  # Add the non-dictionary item to the flattened dictionary
    
    flatten(nested_dict)  # Start the flattening process from the root
    return flattened



def unique_permutations(nums: List[int]) -> List[List[int]]:
    """ Generate all unique permutations of a list of numbers that may contain duplicates. """

    result = set()  # Use a set to avoid duplicate permutations
    
    def backtrack(start, end):
        if start == end:
            result.add(tuple(nums[:]))  # Add the current permutation as a tuple to the set
        for i in range(start, end):
            if i != start and nums[i] == nums[start]:
                continue  # Skip duplicates
            nums[start], nums[i] = nums[i], nums[start]  # Swap the elements
            backtrack(start + 1, end)  # Recurse with the next element
            nums[start], nums[i] = nums[i], nums[start]  # Swap back to backtrack
    
    nums.sort()  # Sort numbers to help identify duplicates
    backtrack(0, len(nums))  # Start the recursion
    return [list(x) for x in result]  # Convert each tuple back to a list



def find_all_dates(text: str) -> List[str]:
    """ Find all dates in specified formats within a text using regular expressions. """

    date_pattern = r'\b(?:\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4}|\d{4}\.\d{2}\.\d{2})\b'
    return re.findall(date_pattern, text)  # Return all matches found



def polyline_to_dataframe(polyline_str: str) -> pd.DataFrame:
    """ Decode polyline string to coordinates and calculate distances using Haversine formula. """

    coordinates = polyline.decode(polyline_str)  # Decode the polyline to get coordinates
    df = pd.DataFrame(coordinates, columns=['latitude', 'longitude'])  # Create DataFrame from coordinates
    
    def haversine(lat1, lon1, lat2, lon2):
        """ Calculate the Haversine distance between two points. """

        R = 6371000  # Radius of the Earth in meters
        phi1, phi2 = np.radians([lat1, lat2])  # Convert latitude to radians
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)
        a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c

    df['distance'] = [0] + [haversine(df.iloc[i - 1]['latitude'], df.iloc[i - 1]['longitude'], lat, lon) for i, (lat, lon) in enumerate(df.iloc[1:].values, 1)]
    return df



def rotate_and_multiply_matrix(matrix: List[List[int]]) -> List[List[int]]:
    """ Rotate a matrix 90 degrees clockwise and replace each element with the sum of row and column elements. """

    n = len(matrix)  # Determine the size of the matrix
    rotated = [[matrix[n - 1 - j][i] for j in range(n)] for i in range(n)]  # Rotate the matrix 90 degrees
    transformed = [[sum(rotated[i]) + sum(rotated[k][j] for k in range(n)) - rotated[i][j] * 2 for j in range(n)] for i in range(n)]
    return transformed


def time_check() -> pd.Series:
    """
    Read a dataset from a CSV file and verify the completeness of the data by checking whether the timestamps
    for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period.

    Returns:
        pd.Series: Returns a boolean series indexed by (id, id_2) where True indicates incomplete timestamps.
    """
    # Specify the CSV file path directly in the function
    file_path = 'templates/python_section_1.py'

    # Load the dataset from the specified CSV file
    df = pd.read_csv(file_path)

    # Define the complete set of days for easy comparison
    all_days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}

    def is_incomplete(group):
        # Check day completeness
        days_covered = set(group['startDay']).union(set(group['endDay']))
        days_complete = days_covered == all_days

        # Check time completeness
        full_day_start = pd.to_datetime('00:00:00', format='%H:%M:%S').time()
        full_day_end = pd.to_datetime('23:59:59', format='%H:%M:%S').time()
        time_complete = all(pd.to_datetime(group['startTime'], format='%H:%M:%S').dt.time.min() <= full_day_start and
                            pd.to_datetime(group['endTime'], format='%H:%M:%S').dt.time.max() >= full_day_end for group in [group])
        
        # Return True if either days or times are not completely covered
        return not (days_complete and time_complete)

    # Apply the check function to each (id, id_2) group and invert the results (True for incomplete)
    results = df.groupby(['id', 'id_2']).apply(is_incomplete)

    return results

# Example usage:
# Call the function directly without passing any arguments
results = time_check()
print(results)
