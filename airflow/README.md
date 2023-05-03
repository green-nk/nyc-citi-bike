# Workflow Orchestration
How to setup Airflow as a workflow orchestration tool:
* Build a custom image to include other dependecies such as dbt and wget.
* Run Airflow services using Docker Compose.
* Setup Airflow environment variables and connection.
* Run Airflow commands to manipulate a data pipeline.


## Initial Setup
### Setup Airflow Services using Docker Compose
1. Initialize environment
    ```bash
    mkdir -p ./logs ./plugins ./data/raw ./data/staging ./dags/scripts/variables/
    echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
    ```

2. Build a custom Airflow image. Note that an airflow directory should be the place that easier to run services with docker.
    ```bash
    # Build an image explicitly
    docker compose build

    # Build an image on-the-fly with running services
    docker compose up --build -d
    ```
    Note that step 3 should be done before running other Airflow services. Building an image on-the-fly might cause an error.

3. Initialize the database using `docker compose up -d airflow-init`. Note that in case you want to see logs when building containers neglect `-d` to not running docker in detached mode. 

4. Run Airflow services using `docker compose up -d`.

5. Create an environment variable json file in a variables folder.
    ```json
    {
        "project_id": <gcp-project-id>, 
        "gcs_bucket": <gcs-bucket-name>, 
        "bq_dataset": <bq-dataset-name>, 
        "bq_dst_table_name": <bq-dst-table-name>, 
        "dbt_project": <dbt-project-name>
    }
    ```

6. In order to setup environment variables and connection on Airflow, First, you need to enter an `airflow-webserver` container.
    ```bash
    # Check container id or container name
    docker ps

    # Enter bash terminal on that container
    docker exec -it <container-id-or-container-name> bash
    ```
    (Optional) You can setup VSCode for attaching a running container, using dev containers extension.

7. In an `airflow-webserver` container, Use Airflow commands to finish setting up services as necessary. Note that Airflow uses `google_cloud_default` as a default connection ID for GCP.
    ```bash
    # Add environment variables
    airflow variables import <path/to/environment-variables-file.json>

    # Delete existing connection if necessary
    airflow connections delete google_cloud_default

    # Add GCP connection to Airflow
    airflow connections add google_cloud_default \
        --conn-type google_cloud_platform \
        --conn-extra '{"extra__google_cloud_platform__project": <gcp-project-id>, "extra__google_cloud_platform__key_path": <path/to/keyfile.json>}'
    ```
    Airflow provides web UI on `localhost:8080` which you can setup environment variables and connection there as well.

8. (Optional) Stop Airflow services using `docker compose down`.

> **Note**: After first-time setup, Run only step 4 to start services.

> **Caution**: Please check mounted volume before running Docker Compose. In case some required files are missing.


## How to Run Airflow DAGs
* Run Airflow DAG manually on the specific execution date
    ```bash
    airflow dags trigger <dag-id> -e <execution-date>
    ```
* Test Airflow DAG. Note that `airflow dags test` and `airflow dags trigger` is difference in that the former doesn't include running tasks in DAG history.
    ```bash
    airflow dags test <dag-id> <execution-date>
    ```
* Backfill data by running DAGs on different execution dates despite of setting `catchup` to False. Note that using `--reset-dagruns` just to start backfilling it from scratch only.
    ```bash
    airflow dags backfill <dag-id> --reset-dagruns -s <start-date> -e <end-date>
    ```

Need help? using `airflow cheat-sheet` as a starting point of reference. Note that Airflow also provide web UI on `localhost:8080` which you can trigger DAGs interactively there as well.


## Troubleshooting
* Restart services from scratch.
    ```bash
    # Reset PG database that stored meta data, doing this in an airflow-webserver container
    airflow db reset
    ```
    ```bash
    # Stop services and remove mounted volume to start fresh, doing this in GCE instances
    docker compose down --volumes --remove-orphans
    ```

> **Note**: Exception on uploading compressed parquet file might occur. as the following `Error while reading data, error message: Input file is not in Parquet format` or `Can not reuploading to GCS`. If so, delete existing files before reuploading or try not to compress a parquet file store it as is.

> **Note**: `psycopg2.errors.DeadlockDetected: deadlock detected` Exception might occur from time to time. though, this doesn't affect the data pipeline.


## Reference
* [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/)
* [Building Custom Image](https://airflow.apache.org/docs/docker-stack/build.html)
* [Basic on How to Run Airflow DAGs](https://airflow.apache.org/docs/apache-airflow/2.5.3/core-concepts/dag-run.html)