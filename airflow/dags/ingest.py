import datetime
from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator


@dag(
    dag_id="ingest_nyc_citi_bike", 
    schedule_interval="@monthly", 
    start_date=datetime.datetime(2022, 1, 31), 
    catchup=False
)
def ingest_nyc_citi_bike():
    """
    NYC Citi Bike Data Ingestion.
    """
    src = "https://s3.amazonaws.com/tripdata/201907-citibike-tripdata.csv.zip"
    out = "/opt/airflow/data/raw/201907-citibike-tripdata.csv.zip"
    
    extract_nyc_citi_bike = BashOperator(
        task_id="extract_nyc_citi_bike", 
        bash_command=f"wget -O {out} {src}"
    )

    bucket_name = "89c4cf55ff5c1b59-hopeful-vim-384700"
    raw_destination_blob_name = "raw/201907-citibike-tripdata.csv.zip"
    nyc_citi_bike_to_raw_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_raw_data_lake", 
        src=out, 
        dst=raw_destination_blob_name, 
        bucket=bucket_name
    )

    extract_nyc_citi_bike >> nyc_citi_bike_to_raw_data_lake

nyc_citi_bike = ingest_nyc_citi_bike()