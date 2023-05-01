import json
import os
import pandas as pd
import zipfile
from airflow.models import Variable

def get_config():
    """
    Get airflow configuration variables.
    """
    config = {
        "airflow_home": os.getenv("AIRFLOW_HOME"), 
        "project_id": Variable.get("project_id"), 
        "bucket_name": Variable.get("gcs_bucket"), 
        "bq_dataset": Variable.get("bq_dataset"), 
        "bq_dst_table_name": Variable.get("bq_dst_table_name"), 
        "dbt_project": Variable.get("dbt_project"), 
    }
    
    return config


def read_csv_from_zip(src, data_file):
    """
    Read spcificed csv file from zip.
    """
    with zipfile.ZipFile(src, 'r') as fzip:
        with fzip.open(f"{data_file}.csv") as f:
            df = pd.read_csv(f)

    return df


def raw_transfrom(raw_df, schema_file):
    """
    Transform raw data
    - Rename column names
    - Enforce a schema
    """
    df = rename_columns(raw_df)
    
    # trip_duration, start_station_id, end_station_id, bike_id, birth_year and gender can be an int
    # a float is acceptable for now as to preserve null value
    schema = load_json(schema_file)
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