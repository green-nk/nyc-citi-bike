import datetime
from airflow.decorators import dag
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator


@dag(
    dag_id="ingest_nyc_citi_bike", 
    schedule_interval="@monthly", 
    start_date=datetime.datetime(2022, 1, 31), 
    catchup=False, 
)
def ingest_nyc_citi_bike():
    """
    NYC Citi Bike Data Ingestion.
    """
    DATA_FILE = "201907-citibike-tripdata"
    BUCKET_NAME = Variable.get("gcs_bucket")

    src = f"https://s3.amazonaws.com/tripdata/{DATA_FILE}.csv.zip"
    out = f"/opt/airflow/data/raw/{DATA_FILE}.csv.zip"
    extract_nyc_citi_bike = BashOperator(
        task_id="extract_nyc_citi_bike", 
        bash_command=f"/opt/airflow/dags/scripts/bash/extract.sh {src} {out}"
    )

    raw_destination_blob = f"raw/{DATA_FILE}.csv.zip"
    nyc_citi_bike_to_raw_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_raw_data_lake", 
        src=out, 
        dst=raw_destination_blob, 
        bucket=BUCKET_NAME
    )

    extract_nyc_citi_bike >> nyc_citi_bike_to_raw_data_lake

nyc_citi_bike = ingest_nyc_citi_bike()