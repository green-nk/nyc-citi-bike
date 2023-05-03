# Setup cloud provider metadata
provider "google" {
  project = var.project_id
  region = var.region
  zone = var.zone
  credentials = file(var.credentials_file)
}

# Setup static IP
resource "google_compute_address" "static_ip" {
  name = "de-project-ip"
}

# Setup VM instance for a compute engine
resource "google_compute_instance" "vm_instance" {
  name = "de-project"
  machine_type = "e2-standard-4"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size = 30
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.static_ip.address
    }
  }

  metadata = {
    "ssh-keys" = local.ssh_connection
  }

  service_account {
    email = var.service_account_email
    scopes = ["cloud-platform"]
  }

  connection {
    type = "ssh"
    host = self.network_interface[0].access_config[0].nat_ip
    user = var.username
    private_key = file(var.ssh_key_filename)
  }

  # Install Miniconda
  provisioner "remote-exec" {
    inline = [
      "wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh", 
      "bash ~/miniconda.sh -b -p $HOME/miniconda", 
      "rm ~/miniconda.sh", 
      "eval \"$(~/miniconda/bin/conda shell.bash hook)\"", 
      "conda init", 
      "conda config --set auto_activate_base false", 
      "source ~/.bashrc", 
      "conda create -y --name ${var.environment_name} python=3.9.7", 
      "conda activate ${var.environment_name}", 
      "conda install -y -c conda-forge numpy=1.22.3 pandas=1.5.3 matplotlib=3.7.1 notebook=6.5.4", 
      "pip install apache-airflow==2.5.3 apache-airflow-providers-google==10.0.0 gcsfs==2023.4.0 dbt-core==1.5.0 dbt-bigquery==1.5.0"
    ]
  }

  # Install Docker
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg", 
      "sudo install -m 0755 -d /etc/apt/keyrings", 
      "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg", 
      "sudo chmod a+r /etc/apt/keyrings/docker.gpg", 
      "echo \"deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \"$(. /etc/os-release && echo \"$VERSION_CODENAME\")\" stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null", 
      "sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin", 
      "sudo usermod -aG docker ${var.username}"
    ]
  }

  # Install Terraform
  provisioner "remote-exec" {
    inline = [
      "wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg", 
      "echo \"deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main\" | sudo tee /etc/apt/sources.list.d/hashicorp.list", 
      "sudo apt-get update && sudo apt-get install -y terraform"
    ]
  }
}

# Setup GCS: Create a bucket
resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_storage_bucket" "data_lake_bucket" {
  name = "${random_id.bucket_prefix.hex}-${var.project_id}"
  location = var.region
  force_destroy = true
  storage_class = "standard"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Setup GCS: Create raw folder in a bucket
locals {
  bucket_name = google_storage_bucket.data_lake_bucket.name
}

resource "google_storage_bucket_object" "data_lake_raw" {
  bucket = local.bucket_name 
  name = "raw/"
  content = "Raw folder to be stored data directly from sources"
}

# Setup GCS: Create staging folder in a bucket
resource "google_storage_bucket_object" "data_lake_staging" {
  bucket = local.bucket_name
  name = "staging/"
  content = "Staging folder to be stored data after some cleaning"
}

# Setup BQ: Create dev dataset
resource "google_bigquery_dataset" "dev_dataset" {
  dataset_id = "development"
  location = var.region
}

# Setup BQ: Create staging dataset
resource "google_bigquery_dataset" "staging_dataset" {
  dataset_id = "staging"
  location = var.region
}

# Setup BQ: Create production dataset
resource "google_bigquery_dataset" "prod_dataset" {
  dataset_id = "production"
  location = var.region
}
