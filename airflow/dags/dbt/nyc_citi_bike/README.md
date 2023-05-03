# Data Build Tool (dbt)
How to setup dbt:
* Setup a (new) dbt project
* Run dbt command to build data models.


## Initial Setup
### Setup dbt
1. Create a profile configuration file in profiles folder for initializing a project on BigQuery. Note that you can use `service-account-json` to be an authentication method by using keys as in service account key file instead of `keyfile`.
    ```bash
    mkdir -p ./dags/dbt/profiles
    ```
    ```yml
    <dbt-project-name>:
        target: <target-name>
    outputs:
        <target-name>:
            type: bigquery
            method: service-account
            project: <gcp-project-id>
            dataset: <bq-dataset-name>
            threads: 4
            timeout_seconds: 300
            location: <gcp-region>
            priority: interactive
            keyfile: <path/to/keyfile.json>
        ...
    ```
    Note that `target` can be used to switch between environments such as dev, test and prod. Also, `threads` and `timeout_seconds` etc. might need to be identify for build more efficient data model.

2. In order to run dbt commands, First, you need to enter an `airflow-webserver` container. See [how to execute bash commands in a container](../../../README.md#setup-airflow-services-using-docker-compose) on step 6.

3. Initialize a dbt project, using `dbt init <dbt-project-name>`. After this step, dbt_project.yml file was created in a dbt project folder. you can use this file to config default values such as materialized type for specificed models. Note that running a service in a dbt project folder is more easier or else you have to add `--profiles-dir` and `--project-dir` everytime you're running a dbt command.

4. Create a packages.yml file to identify pacakges needed for running data models. Seel list of [dbt packages](https://hub.getdbt.com/).
    ```yml
    packages:
        - package: <dbt-package-name>
            version: <dbt-package-version>
        ...
    ```

5. Install packages for dbt, using `dbt deps` to install packages specified in packages.yml file.

6. (Optional) To check that we're ready to build a data model, using `dbt debug`. All checks should pass.

> **Note**: In order to run dbt from an existing project. Skip step 3 and 4.


## How to Run dbt commands
* Run a data model. `--full-refresh` flag might needed in order to test things out.
```bash
dbt run --select <path/to/specificed-data-model>
```

* Run a simple test identified in a schema.yml file on a data model.
```bash
dbt test --select <path/to/specified-data-model>
```

Need help? using `dbt --help` as a starting point of reference.

## Reference
* [dbt Quickstart](https://docs.getdbt.com/docs/quickstarts/dbt-core/manual-install)
* [dbt with BigQuery Setup](https://docs.getdbt.com/reference/warehouse-setups/bigquery-setup)