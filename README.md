# NYC Citi Bike 🚴🏽
The aim of this project is to ingest data from [NYC Citi Bike](https://citibikenyc.com/system-data) and generate [NYC Citi Bike Trips Dashboard](https://lookerstudio.google.com/reporting/94e4c68c-cfa4-440c-9502-c9a40b83e002) displaying metrics like the number of trips and total trip duration among various categories. The project mainly focuses on data during 2019 and updates data in a batch manner on monthly-basis.

![Example NYC Citi Bike Trips Dashboard](/images/nyc-citi-bike-trips-dashboard.png)


## Technologies 💻
This project is hosted on Google Cloud Platform (GCP) and uses the following infrastructure:
* Google Compute Engine (GCE): instances for running tasks and scripts.
* Google Cloud Storage (GCS): a data lake to store data on both raw and staging area.
* BigQuery (BQ): a data warehouse to do analytic queries.

The following tools were used in this project:
* Terraform: Infrastructure as code (IaC) tool used to set up GCE instances, GCS, and BQ.
* Airflow: Orchestration tool used to manage end-to-end workflows.
* Data Build Tool (dbt): Data transformation tool used to do batch processing in a data warehouse.
* Docker: Containerization tool used to package services such as Airflow and dbt.
* Looker Studio: Data visualization tool used to generate a dashboard.


## Architecture 🏗️
![Project Architecture](/images/architecture.png)


## Data Pipeline 👷🏽‍♂️
1. Extract data from the source website, which is a zip file containing a monthly CSV file of bike trips using a Bash command line tool.
2. Store the raw data as is in a GCS bucket, which serves as a data lake.
3. Perform some raw transformations using a Python script, such as renaming columns and enforcing a schema, and then save the data as compressed parquet files in a staging area in the same GCS bucket.
4. Load the transformed data into a BigQuery data warehouse.
5. Use dbt to create data models from the staging data, such as creating new columns based on business logics, and creating a fact table that is partitioned and clustered for efficient querying.
6. Perform basic testing to ensure good data quality before data are going to be used by the end user.
7. Generate a NYC Citi Bike Trips dashboard using Looker Studio, displaying metrics such as trip counts by hour, day of the week, and station, trip duration on each bike, and the proportion of user types and genders.


## Installation 🧱
To run this project you will need to:

1. Clone the project repository from GitHub.
2. Setup [SSH connection](terraform/README.md#setup-ssh-access-on-local-machine) on a local machine.
3. Setup your [GCP project](terraform/README.md#setup-gcp-project).
4. Setup the necessary services: [Terraform](terraform/README.md#setup-infrastructure-with-terraform) and [Airflow](airflow/README.md).
5. Setup your [dbt project](airflow/dags/dbt/nyc_citi_bike/README.md).
6. Run the project by executing the DAGs in Airflow.


## Possible Improvement 💡
* Expand the dashboard to include additional metrics, such as average trip duration by station, average trip duration on each bike on each month and popular possible routes.
* Improve readability of the dashboard of categorical data like gender and birth year.
* Expand the project to cover data from multiple years or cities and try to handle a changing schema across time.
* Implement automated data quality checks to ensure data consistency and accuracy throughout the pipeline using [Great Expectations](https://www.youtube.com/watch?v=9iN6iw7Lamo&t=932s).
* Implement data privacy and security measures, such as data masking, encryption, or access controls, to protect sensitive data.
* Add CI/CD to the pipeline to make it more rigid using [GitHub Actions](https://www.youtube.com/watch?v=R8_veQiYBjI&t=1710s).
* Use this [Makefile](https://github.com/josephmachado/beginner_de_project/blob/master/Makefile) as a starting point to create one for running this project.
