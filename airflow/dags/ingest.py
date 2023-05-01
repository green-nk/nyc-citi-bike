import datetime
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from utils import get_config, read_csv_from_zip, raw_transfrom


@dag(
    dag_id="ingest_nyc_citi_bike", 
    schedule_interval="@monthly", 
    start_date=datetime.datetime(2019, 2, 1), 
    end_date=datetime.datetime(2020, 1, 1), 
    catchup=False
)
def ingest_nyc_citi_bike():
    """
    NYC Citi Bike Data Ingestion.
    """
    # Get an execution date for templating Jinja
    @task()
    def get_data_file(date):
        """
        Get data file to be identified a downloadable source.
        """
        # Get data interval end date: the last day of each scheduled date
        data_date = (datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Get data month period to idenfity data source
        data_month_period = ''.join(data_date.split('-')[:2])
        data_file = f"{data_month_period}-citibike-tripdata"

        return data_file
    
    date = "{{ ds }}"
    data_file = get_data_file(date)

    # Get config variables
    config = get_config()
    airflow_home = config["airflow_home"]

    project_id = config["project_id"]
    bucket_name = config["bucket_name"]
    bq_dataset = config["bq_dataset"]
    bq_dst_table_name = config["bq_dst_table_name"]

    dbt_project = config["dbt_project"]

    # Get script file path
    script_filepath = f"{airflow_home}/dags/scripts/bash"

    # Get data file path
    raw_dst_blob = f"raw/{data_file}.csv.zip"
    staging_dst_blob = f"staging/{data_file}.parquet.snappy"

    # Extract data from a source
    src = f"https://s3.amazonaws.com/tripdata/{data_file}.csv.zip"
    out = f"{airflow_home}/data/{raw_dst_blob}"
    extract_nyc_citi_bike = BashOperator(
        task_id="extract_nyc_citi_bike", 
        bash_command=f"{script_filepath}/extract.sh {src} {out}"
    )

    # Load raw data into a data lake
    nyc_citi_bike_to_raw_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_raw_data_lake", 
        src=out, 
        dst=raw_dst_blob, 
        bucket=bucket_name
    )

    # Preprocess raw data into staging data
    @task()
    def apply_raw_transformation(src, out, data_file, schema_file):
        """
        Raw transformation into staging area.
        """
        print(f"Loading file from {src}...")
        raw_df = read_csv_from_zip(src, data_file)
        
        print(f"Applying transformation to {src}...")
        df = raw_transfrom(raw_df, schema_file)
        
        print(f"Saving file to {out}...")
        df.to_parquet(out, index=False, compression="snappy")
    
    src = out
    out = f"{airflow_home}/data/{staging_dst_blob}"
    schema_file = f"{airflow_home}/dags/scripts/schema/schema.json"
    transform_raw_nyc_citi_bike = apply_raw_transformation(src, out, data_file, schema_file)

    # Load preprocessed data back into staging area in a data lake
    nyc_citi_bike_to_staging_data_lake = LocalFilesystemToGCSOperator(
        task_id="nyc_citi_bike_to_staging_data_lake", 
        src=out, 
        dst=staging_dst_blob, 
        bucket=bucket_name
    )
    
    # Load preprocessed data from a data lake to a data warehouse
    dst_table = f"{project_id}.{bq_dataset}.{bq_dst_table_name}"
    nyc_citi_bike_to_data_warehouse = GCSToBigQueryOperator(
        task_id="nyc_citi_bike_to_data_warehouse", 
        bucket=bucket_name, 
        source_objects=[staging_dst_blob], 
        destination_project_dataset_table=dst_table, 
        source_format="PARQUET", 
        create_disposition="CREATE_IF_NEEDED", 
        write_disposition="WRITE_APPEND", 
        autodetect=True
    )

    # Connection checking for transformation on a data warehouse
    profiles_dir = f"{airflow_home}/dags/dbt/profiles"
    project_dir = f"{airflow_home}/dags/dbt/{dbt_project}"
    connection_to_data_warehouse = BashOperator(
        task_id="connection_to_data_warehouse", 
        bash_command=f"{script_filepath}/connect.sh {profiles_dir} {project_dir}"
    )

    # Model staging data in a data warehouse
    stg_model_file = "models/staging/stg_bike_trips.sql"
    model_stg_bike_trips = BashOperator(
        task_id="model_stg_bike_trips", 
        bash_command=f"{script_filepath}/model.sh {stg_model_file} {profiles_dir} {project_dir}"
    )

    # Test staging data in a data warehouse
    test_stg_bike_trips = BashOperator(
        task_id="test_stg_bike_trips", 
        bash_command=f"{script_filepath}/test_model.sh {stg_model_file} {profiles_dir} {project_dir}"
    )

    # Model fact data in a data warehouse
    fact_model_file = "models/core/fact_bike_trips.sql"
    model_fact_bike_trips = BashOperator(
        task_id="model_fact_bike_trips", 
        bash_command=f"{script_filepath}/model.sh {fact_model_file} {profiles_dir} {project_dir}"
    )

    data_file >> extract_nyc_citi_bike >> nyc_citi_bike_to_raw_data_lake >> \
    transform_raw_nyc_citi_bike >> nyc_citi_bike_to_staging_data_lake >> \
    nyc_citi_bike_to_data_warehouse >> connection_to_data_warehouse >> \
    model_stg_bike_trips >> test_stg_bike_trips >> model_fact_bike_trips

nyc_citi_bike = ingest_nyc_citi_bike()
