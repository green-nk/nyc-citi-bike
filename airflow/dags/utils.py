import json


def raw_transfrom(raw_df, schema_filepath):
    """
    Transform raw data
    - Rename column names
    - Enforce a schema
    """
    df = rename_columns(raw_df)
    
    # trip_duration, start_station_id, end_station_id, bike_id, birth_year and gender can be an int
    # a float is acceptable for now as to preserve null value
    schema = load_json(schema_filepath)
    df = df.astype(schema)

    return df


def rename_columns(df):
    """
    Rename column names.
    """
    # Split words with underscores and replace spaces with underscores
    column_names = {
        "tripduration": "trip_duration", 
        "starttime": "start_time", 
        "stoptime": "end_time", 
        "start station id": "start_station_id", 
        "start station name": "start_station_name", 
        "start station latitude": "start_station_latitude", 
        "start station longitude": "start_station_longitude", 
        "end station id": "end_station_id", 
        "end station name": "end_station_name", 
        "end station latitude": "end_station_latitude", 
        "end station longitude": "end_station_longitude", 
        "bikeid": "bike_id", 
        "usertype": "user_type", 
        "birth year": "birth_year", 
        "gender": "gender" 
    }
    processed_df = df.rename(columns=column_names)

    return processed_df


def load_json(filepath):
    """
    Load json config into Python dictionary.
    """
    with open(filepath, 'r') as f:
        d = json.load(f)

    return d