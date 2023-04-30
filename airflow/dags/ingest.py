import datetime
import pandas as pd
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from utils import raw_transfrom


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
    PROJECT_ID = Variable.get("project_id")

    # Extract data from a source
    src = f"https://s3.amazonaws.com/tripdata/{DATA_FILE}.csv.zip"
    out = f"/opt/airflow/data/raw/{DATA_FILE}.csv.zip"
    extract_nyc_citi_bike = BashOperator(
        task_id="extract_nyc_citi_bike", 
        bash_command=f"/opt/airflow/dags/scripts/bash/extract.sh {src} {out}"
    )

    # Load raw data into a data lake
    raw_dst_blob = f"raw/{DATA_FILE}.csv.zip"
    nyc_citi_bike_to_raw_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_raw_data_lake", 
        src=out, 
        dst=raw_dst_blob, 
        bucket=BUCKET_NAME
    )

    # Preprocess raw data into staging data
    @task()
    def apply_raw_transformation(src, out, schema_filepath):
        """
        Raw transformation into staging area.
        """
        print(f"Loading file from {src}...")
        raw_df = pd.read_csv(src)
        
        print(f"Applying transformation to {src}...")
        df = raw_transfrom(raw_df, schema_filepath)
        
        print(f"Saving file to {out}...")
        df.to_parquet(out, index=False, compression="gzip")
    
    src = f"gs://{BUCKET_NAME}/{raw_dst_blob}"
    out = f"/opt/airflow/data/staging/{DATA_FILE}.parquet.gz"
    schema_filepath = "/opt/airflow/dags/scripts/schema/schema.json"
    transform_raw_nyc_citi_bike = apply_raw_transformation(src, out, schema_filepath)

    # Load preprocessed data back into staging area in a data lake
    staging_dst_blob = f"staging/{DATA_FILE}.parquet.gz"
    nyc_citi_bike_to_staging_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_staging_data_lake", 
        src=out, 
        dst=staging_dst_blob, 
        bucket=BUCKET_NAME
    )
    
    # Load preprocessed data from a data lake to a data warehouse
    dataset = "development"
    table_name = "bike_trips"
    dst_table = f"{PROJECT_ID}.{dataset}.{table_name}"
    nyc_citi_bike_to_data_warehouse = GCSToBigQueryOperator(
        task_id="nyc_citi_bike_to_data_warehouse", 
        bucket=BUCKET_NAME, 
        source_objects=[staging_dst_blob], 
        destination_project_dataset_table=dst_table, 
        source_format="PARQUET", 
        create_disposition="CREATE_IF_NEEDED", 
        write_disposition="WRITE_TRUNCATE", 
        autodetect=True, 
        time_partitioning={
            "field": "start_time", 
            "type": "DAY"
        }, 
        cluster_fields=["bike_id", "user_type"]
    )

    extract_nyc_citi_bike >> nyc_citi_bike_to_raw_data_lake >> transform_raw_nyc_citi_bike >> nyc_citi_bike_to_staging_data_lake >> nyc_citi_bike_to_data_warehouse

nyc_citi_bike = ingest_nyc_citi_bike()
