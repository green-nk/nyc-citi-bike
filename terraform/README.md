# Project Infrastructure
How to setup infrastructure for this project using terraform:
* Google Compute Engine (GCE)
* Google Cloud Storage (GCS)
* BigQuery (BQ)


## Initial Setup
### Setup SSH Access on Local Machine
1. Create ssh key connection
    ```bash
    ssh-keygen -f <ssh-private-keyfile> -C <vms-username>
    ```
2. Build a `config` file to be easier to access to GCE instances (optional)
    ```bash
    Host <ssh-connection-name>
        HostName <host-ip-address>
        User <vms-username>
        IdentityFile <path/to/ssh-private-keyfile>
    ```


### Setup GCP Project
1. Setup [GCP account](https://cloud.google.com/free)
2. Setup your [GCP project](https://console.cloud.google.com/)
    * e.g. Using "dtc-de" as a project name and GCP will generate a unique project ID to be used later.
3. Setup a [service account](https://cloud.google.com/docs/authentication/getting-started)
    * Grant `BigQuery Admin`, `Compute Admin`, `Service Account User`, `Storage Admin`, `Storage Object Admin` and `Viewer` roles to get a service account email to be used later.
    * Download a service account key json file for authentication to be used later.


### Setup Infrastructure with terraform
1. Setup a terraform input variable file. See list of [regions and zones](https://cloud.google.com/compute/docs/regions-zones)
    ```tfvars
    project_id = <gcp-project-id>
    region = <gcp-region>
    zone = <gcp-zone>
    username = <vms-username>
    environment_name = <python-environment>
    ```

2. Using `terraform init` to initializes or configures the backend, installs plugins/providers, and checks out an existing configuration from a version control. Note that initialization step should be done in a terraform directory.

3. Using `terraform plan` to matches or previews local changes against a remote state, and proposes an execution plan. Note that you can add all input variables specified here at run time to files as well.
    ```bash
    terraform plan \
        -var-file=<tf-input-variable-file> \
        -var="credentials_file=<path/to/keyfile.json>" \
        -var="ssh_key_filename=<path/to/ssh-private-keyfile>" \
        -var="service_account_email=<service-account-email>"
    ```
4. Using `terraform apply` to ask for an approval to the proposed plan, and applies changes to the cloud resources.
    ```bash
    terraform apply \
        -var-file=<tf-input-variable-file> \
        -var="credentials_file=<path/to/keyfile.json>" \
        -var="ssh_key_filename=<path/to/ssh-private-keyfile>" \
        -var="service_account_email=<service-account-email>"
    ```

5. (Optional) Test a connection to VMs from a local machine
    ```bash
    # Using ssh connection
    ssh -i <path/to/ssh-private-keyfile> <vms-username>@<host-ip-address>

    # Or using a config file
    ssh <ssh-connection-name>
    ```

6. (Optional) In case you want to restart the project from scratch, using `terrafrom destroy` to removes your stack from the cloud.
    ```bash
    terraform destroy \
        -var-file=<tf-input-variable-file> \
        -var="credentials_file=<path/to/keyfile.json>" \
        -var="ssh_key_filename=<path/to/ssh-private-keyfile>" \
        -var="service_account_email=<service-account-email>"
    ```

### (Optional) Setup GitHub access
GitHub is a web-based platform for software development projects that uses the Git version control system. It provides features like code management, collaboration tools, issue tracking, and project management capabilities. Developers can use GitHub to host and review code, manage projects and build software with other developers.

For GCE to connect to GitHub with a specific ssh file, Add known host and a specific ssh file to prevent `Host key verification failed` and `Permission denied (publickey)` respectively.
```bash
# Add known host manually
ssh-keyscan -t rsa github.com > <path/to/ssh-known-host>

# Create ssh key connection
ssh-keygen -f <ssh-private-keyfile> -C <vms-username>

# Add an existing ssh key connection
eval "$(ssh-agent -s)"
ssh-add <path/to/ssh-private-keyfile>

# (Optional) Test ssh connection to GitHub
ssh -T git@github.com
```
(Optional) In case you don't want to add an existing ssh key manually everytime you logging into GCE, Configure a `.bashrc` file to add this step autmatically.


## Reference
[Setup Resources with Terraform on GCP](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started)
[Setup SSH Connection to GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
