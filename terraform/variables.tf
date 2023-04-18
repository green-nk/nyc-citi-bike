variable "project_id" {
  description = "The ID of the GCP project"
}

variable "region" {
  description = "The GCP region to deploy resources"
  type = string
  default = "us-east1"
}

variable "zone" {
  description = "The GCP zone to deploy resources"
  type = string
  default = "us-east1-b"
}

variable "credentials_file" {
  description = "GCP service account key file location"
}

variable "username" {
  description = "Username for GCP VM instances"
  type = string
  default = "ubuntu"
}

variable "ssh_key_filename" {
  description = "SSH key filename to be used to connect to VM instances"
}

locals {
  ssh_connection = "${var.username}:${file("${var.ssh_key_filename}.pub")}"
}

variable "service_account" {
  description = "Service account email to be set to VM instances"
}

variable "environment_name" {
  description = "Development environment to be created"
}
