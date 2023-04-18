import datetime
from airflow.decorators import dag
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator

@dag(
    dag_id="extract_nyc_citi_bike", 
    schedule_interval="@monthly", 
    start_date=datetime.datetime(2023, 4, 30), 
    catchup=False
)
def extract_nyc_citi_bike():
    """
    """
    DATA_FILE = "201907-citibike-tripdata"
    SOURCE = f"https://s3.amazonaws.com/tripdata/{DATA_FILE}.csv.zip"
    OUTPUT = f"/opt/airflow/data/raw/{DATA_FILE}.csv.zip"
    
    UPLOAD_FILE_PATH= f"data/raw/{DATA_FILE}.csv.zip"
    FILE_NAME = f"raw/{DATA_FILE}.csv.zip"
    BUCKET_NAME = Variable.get("bucket_name")

    get_nyc_citi_bike = BashOperator(
       task_id="download_nyc_citi_bike", 
       bash_command=f"curl -o {OUTPUT} {SOURCE}"
    )

    load_nyc_citi_bike = LocalFilesystemToGCSOperator(
        task_id="upload_nyc_citi_bike", 
        src=UPLOAD_FILE_PATH, 
        dst=FILE_NAME, 
        bucket=BUCKET_NAME
    )

    get_nyc_citi_bike >> load_nyc_citi_bike

nyc_citi_bike = extract_nyc_citi_bike()