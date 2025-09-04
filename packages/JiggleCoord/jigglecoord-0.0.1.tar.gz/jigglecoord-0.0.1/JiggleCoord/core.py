import pandas as pd
import math
import collections
import folium
import json
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def generate_snowflake_coordinates(coord_str: str, distance_meters_list: list) -> pd.DataFrame:
    """
    Generates a snowflake-like structure of coordinates by sequentially
    perturbing all points from the previous step and returns a DataFrame.

    Args:
        coord_str (str): The original coordinate pair as a string.
        distance_meters_list (list): A list of distances in meters for sequential perturbations.

    Returns:
        pd.DataFrame: A DataFrame containing 'parent_coord', 'new_coord', 'layer', 'direction', and 'distance'.
    """
    try:
        lat, lon = map(float, coord_str.split(','))
    except ValueError:
        raise ValueError("Input coordinate string must be in 'latitude, longitude' format.")

    R = 6371000.0  # Earth's mean radius in meters
    bearings_deg = [0, 45, 90, 135, 180, 225, 270, 315]
    direction_names = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    points_to_process = collections.deque([(coord_str, 0)])  # (coord_str, layer)
    all_points = {coord_str: 0}
    all_records = []

    distances_to_process = collections.deque(distance_meters_list)
    current_layer = 1

    while distances_to_process:
        current_distance = distances_to_process.popleft()
        num_points_in_level = len(points_to_process)

        for _ in range(num_points_in_level):
            parent_coord_str, parent_layer = points_to_process.popleft()
            parent_lat, parent_lon = map(float, parent_coord_str.split(','))
            parent_lat_rad = math.radians(parent_lat)
            parent_lon_rad = math.radians(parent_lon)

            for i, bearing_deg in enumerate(bearings_deg):
                bearing_rad = math.radians(bearing_deg)
                new_lat_rad = math.asin(
                    math.sin(parent_lat_rad) * math.cos(current_distance / R) +
                    math.cos(parent_lat_rad) * math.sin(current_distance / R) * math.cos(bearing_rad)
                )
                new_lon_rad = parent_lon_rad + math.atan2(
                    math.sin(bearing_rad) * math.sin(current_distance / R) * math.cos(parent_lat_rad),
                    math.cos(current_distance / R) - math.sin(parent_lat_rad) * math.sin(new_lat_rad)
                )
                new_lat = math.degrees(new_lat_rad)
                new_lon = math.degrees(new_lon_rad)
                new_coord_str = f"{new_lat}, {new_lon}"

                if new_coord_str not in all_points or all_points[new_coord_str] > current_layer:
                    all_points[new_coord_str] = current_layer
                    points_to_process.append((new_coord_str, current_layer))

                all_records.append({
                    'parent_coord': parent_coord_str,
                    'new_coord': new_coord_str,
                    'layer': current_layer,
                    'direction': direction_names[i],
                    'distance': current_distance
                })
        current_layer += 1
    return pd.DataFrame(all_records)

def geocode_location(
    coordinates: str,
    retries: int = 3,
    perturb_levels: int = 2,
    perturb_distance: int = 1000
) -> dict:
    """
    Reverse geocodes a coordinate and returns the raw JSON response as a dict.
    If the result is a boundary, it uses a snowflake perturbation strategy.

    Args:
        coordinates (str): A string containing latitude and longitude.
        retries (int): The number of times to retry geocoding.
        perturb_levels (int): The number of perturbation layers to generate.
        perturb_distance (int): The distance in meters for each perturbation.

    Returns:
        dict: The raw JSON geocoding response as a dictionary, or a failure dict.
    """
    geolocator = Nominatim(user_agent="dataviz_prep", timeout=10)
    reverse_geocoder = RateLimiter(
        geolocator.reverse,
        min_delay_seconds=1,
        max_retries=retries,
        error_wait_seconds=2,
        swallow_exceptions=True
    )

    result_dict = {'original_coordinate': coordinates}

    # Attempt 1: Initial reverse geocoding
    initial_location = reverse_geocoder(coordinates, language='en', addressdetails=True, zoom=17)

    if initial_location and initial_location.raw.get('class') != 'boundary':
        print("Initial lookup successful, not a boundary.")
        result_dict.update(initial_location.raw)
        result_dict['perturbation_layer'] = 0
    else:
        print(f"Initial lookup for {coordinates} failed or returned a boundary. Attempting snowflake perturbation...")
        distances = [perturb_distance] * perturb_levels
        snowflake_df = generate_snowflake_coordinates(coordinates, distances)

        best_location = None
        min_layer = float('inf')

        for _, row in snowflake_df.iterrows():
            new_coord_str = row['new_coord']
            print(f"Testing snowflake coordinate: {new_coord_str}")
            try:
                location = reverse_geocoder(new_coord_str, language='en', addressdetails=True, zoom=18)
                if location and location.raw.get('class') != 'boundary':
                    if row['layer'] < min_layer:
                        min_layer = row['layer']
                        best_location = location
            except Exception as e:
                print(f"Geocoding snowflake point {new_coord_str} failed: {e}")
                continue

        if best_location:
            print(f"Found non-boundary location at perturbation layer {min_layer}.")
            result_dict.update(best_location.raw)
            result_dict['perturbation_layer'] = min_layer
        else:
            print(f"Failed to find a suitable location for {coordinates} after all attempts.")
            result_dict['status'] = 'Failed to find a suitable location after all attempts.'
            result_dict['perturbation_layer'] = None
    return result_dict


def geopy_df_geocoder(
    df: pd.DataFrame,
    latitude_col: str,
    longitude_col: str,
    geocode_on: str = None,
    perturb_levels: int = 2,
    perturb_distance: int = 1000,
    **kwargs
) -> pd.DataFrame:
    """
    Geocodes coordinates from a DataFrame, with optional perturbation based on a condition.

    Args:
        df (pd.DataFrame): The input DataFrame.
        latitude_col (str): The name of the column containing latitude values.
        longitude_col (str): The name of the column containing longitude values.
        geocode_on (str, optional): A boolean expression string to select rows for re-geocoding/perturbation.
                                    E.g., "class == 'boundary' and type == 'administrative'".
                                    If None, all rows are geocoded. Defaults to None.
        perturb_levels (int): The number of perturbation layers to generate.
        perturb_distance (int): The distance in meters for each perturbation.
        **kwargs: Additional keyword arguments to pass to the geocode_location function.

    Returns:
        pd.DataFrame: The original DataFrame with geocoding results merged in as new columns.
    """
    # 1. Select the rows to process
    if geocode_on:
        try:
            # Create a boolean mask to filter the DataFrame
            rows_to_process = df.query(geocode_on).copy()
        except pd.core.computation.ops.UndefinedVariableError:
            print(f"Warning: The column(s) used in 'geocode_on' are not in the DataFrame. Geocoding all rows.")
            rows_to_process = df.copy()
    else:
        rows_to_process = df.copy()

    if rows_to_process.empty:
        print("No rows match the geocode_on condition. Returning the original DataFrame.")
        return df

    # 2. Prepare coordinates for processing
    rows_to_process['_original_index'] = rows_to_process.index
    rows_to_process['coord_str'] = rows_to_process.apply(
        lambda row: f"{row[latitude_col]}, {row[longitude_col]}", axis=1
    )
    coords_to_process = rows_to_process['coord_str'].tolist()

    # 3. Geocode the selected coordinates
    all_data = []
    for coord in coords_to_process:
        try:
            result_dict = geocode_location(
                coord,
                perturb_levels=perturb_levels,
                perturb_distance=perturb_distance,
                **kwargs
            )
            # Add a status field for clarity
            if 'status' not in result_dict:
                result_dict['status'] = 'Success'

            all_data.append(result_dict)
        except Exception as e:
            print(f"An unexpected error occurred while processing {coord}: {e}")
            all_data.append({
                'original_coordinate': coord,
                'status': f'Processing failed due to an error: {e}',
                'perturbation_layer': None
            })

    # 4. Flatten the geocoding results into a DataFrame
    if not all_data:
        print("No geocoding results were produced.")
        return df

    results_df = pd.json_normalize(all_data)

    # 5. Merge the results back into the original DataFrame
    # Use the original coordinate to merge
    results_df.set_index('original_coordinate', inplace=True)
    df['_original_coord_key'] = df.apply(
        lambda row: f"{row[latitude_col]}, {row[longitude_col]}", axis=1
    )

    # Perform a left merge to keep all original rows
    final_df = df.merge(
        results_df,
        left_on='_original_coord_key',
        right_index=True,
        how='left'
    )

    # Clean up the temporary column
    final_df.drop(columns=['_original_coord_key'], inplace=True)

    # Fill any NaN values from the merge for clarity
    for col in results_df.columns:
        if col not in final_df.columns:
            # Handle the case where all rows were not processed
            final_df[col] = None

    print("Geocoding complete. The original DataFrame has been updated with new geocoded columns.")
    return final_df