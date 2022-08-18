terraform {
  cloud {
    organization = var.organization

    workspaces {
      name = var.workspace
    }
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.5.0"
    }
  }
}

provider "google" {
  project     = var.project_id
  credentials = var.google_credentials
  region      = var.region
  zone        = var.zone
}