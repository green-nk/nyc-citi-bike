# NYC Citi Bike
The aim of this project is to ingest data from the NYC Citi Bike website during 2019, process the data, and generate a dashboard displaying metrics related to bike trips. The project uses various workflows and tools to achieve this goal.

## Technologies
This project is hosted on Google Cloud Platform (GCP) and uses the following infrastructure:
* GCE instances for running tasks and scripts.
* GCS as a data lake and staging area.
* BQ as a data warehouse.

The following tools were used in this project:
* Terraform: Infrastructure as code (IaC) tool used to set up Google Compute Engine (GCE) instances, GCS, and BQ.
* Airflow: Orchestration tool used to manage end-to-end workflows.
* Docker: Containerization tool used to package services such as Airflow and dbt as plugins.
* Git: Version control system used to keep track of the project.

## Architecture

## ETL Pipeline
The workflows used in this project are as follows:

1. Extract data from the source website, which is a zip file containing a monthly CSV file of bike trips.
2. Store the raw data in a Google Cloud Storage (GCS) bucket, which serves as a data lake.
3. Perform some raw transformations, such as renaming columns and enforcing a schema, and then save the data as compressed parquet files in a staging area in the same GCS bucket.
4. Load the transformed data into a BigQuery (BQ) data warehouse.
5. Use dbt to create models from the staging area, such as creating new columns based on business logic, and creating a fact table that is partitioned and clustered for efficient querying.
6. Perform basic testing on the data integrity across the data pipeline.
7. Generate a Looker dashboard using the processed data, displaying metrics such as trip counts by hour, day of the week, and station, trip duration on each bike, and the proportion of user types and genders.

## Installation
To run this project locally, you will need to:

1. Clone the project repository from GitHub.
2. Install the necessary tools such as Terraform, Airflow, and Docker.
3. Configure your GCP project and credentials.
4. Configure your environment variables and connections in Airflow.
5. Run the project by executing the DAGs in Airflow.