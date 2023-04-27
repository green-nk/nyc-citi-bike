import datetime
import pandas as pd
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator


@dag(
    dag_id="ingest_nyc_citi_bike", 
    schedule_interval="@monthly", 
    start_date=datetime.datetime(2023, 4, 30), 
    catchup=False
)
def ingest_nyc_citi_bike():
    """
    NYC Citi Bike Data Ingestion.
    """
    DATA_FILE = "201907-citibike-tripdata"
    BUCKET_NAME = Variable.get("bucket_name")
    
    src = f"https://s3.amazonaws.com/tripdata/{DATA_FILE}.csv.zip"
    out = f"/opt/airflow/data/raw/{DATA_FILE}.csv.zip"
    
    extract_nyc_citi_bike = BashOperator(
       task_id="extract_nyc_citi_bike", 
       bash_command=f"./scripts/bash/extract.sh {src} {out}"
    )

    rfname = f"raw/{DATA_FILE}.csv.zip"
    nyc_citi_bike_to_raw_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_raw_data_lake", 
        src=out, 
        dst=rfname, 
        bucket=BUCKET_NAME
    )

    @task()
    def transform_raw_nyc_citi_bike(rfname, sfname):
        """
        """
        src_blob_uri = f"{BUCKET_NAME}/{rfname}"
        raw_df = pd.read_csv(src_blob_uri)

        column_names = {c: c.replace(' ', '_') for c in raw_df.columns}
        df = raw_df.rename(columns=column_names)

        schema = {
            "tripduration": "int", 
            "starttime": "datetime64[ns]", 
            "stoptime": "datetime64[ns]", 
            "start_station_id": "int", 
            "start_station_name": "str", 
            "start_station_latitude": "float", 
            "start_station_longitude": "float", 
            "end_station_id": "int", 
            "end_station_name": "str", 
            "end_station_latitude": "float", 
            "end_station_longitude": "float", 
            "bikeid": "int", 
            "usertype": "str", 
            "birth_year": "int", 
            "gender": "int", 
        }

        df = df.astype(schema)

        out = f"data/{sfname}"
        df.to_parquet(out, index=False, compression="gzip")

    sfname = f"staging/{DATA_FILE}.parquet.gz"
    nyc_citi_bike_to_raw_transformation = transform_raw_nyc_citi_bike(rfname, sfname)

    nyc_citi_bike_to_staging_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_staging_data_lake", 
        src=out, 
        dst=sfname, 
        bucket=BUCKET_NAME
    )

    extract_nyc_citi_bike >> nyc_citi_bike_to_raw_data_lake >> nyc_citi_bike_to_raw_transformation >> nyc_citi_bike_to_staging_data_lake

nyc_citi_bike = ingest_nyc_citi_bike()