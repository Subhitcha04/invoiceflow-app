terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "cat-2-491109-tfstate"
    prefix = "invoiceflow/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Autopilot Cluster
resource "google_container_cluster" "invoiceflow" {
  name     = "invoiceflow-cluster"
  location = var.region

  enable_autopilot = true

  release_channel {
    channel = "REGULAR"
  }

  addons_config {
    http_load_balancing {
      disabled = false
    }
  }
}