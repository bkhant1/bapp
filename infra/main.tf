# Configure the Google Cloud Provider
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "bookexchange-terraform-state"
    prefix = "terraform/state"
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "vpcaccess.googleapis.com",
    "redis.googleapis.com",
    "servicenetworking.googleapis.com",
    "artifactregistry.googleapis.com"
  ])

  service = each.value
  project = var.project_id

  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false

  depends_on = [google_project_service.apis]
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.project_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Reserve IP range for private services
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.project_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

# Create private service connection
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "postgres" {
  name             = "${var.project_name}-db"
  database_version = "POSTGRES_17"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc.id
      ssl_mode        = "ALLOW_UNENCRYPTED_AND_ENCRYPTED"
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
    }

    maintenance_window {
      day  = 7
      hour = 3
    }
  }

  deletion_protection = false

  depends_on = [
    google_project_service.apis,
    google_service_networking_connection.private_vpc_connection
  ]
}

# Database
resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.postgres.name
}

# Database User
resource "google_sql_user" "user" {
  name     = var.database_user
  instance = google_sql_database_instance.postgres.name
  password = var.database_password
}

# Cloud Storage Bucket for media files
resource "google_storage_bucket" "media" {
  name     = "${var.project_name}-media-${random_id.bucket_suffix.hex}"
  location = var.region

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  depends_on = [google_project_service.apis]
}

# Random suffix for bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# Artifact Registry Repository for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  repository_id = "${var.project_name}-repo"
  location      = var.region
  format        = "DOCKER"
  
  description = "Docker repository for ${var.project_name} container images"

  depends_on = [google_project_service.apis]
}

# Cloud Run Service for Backend
resource "google_cloud_run_service" "backend" {
  name     = "${var.project_name}-backend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/${var.project_name}-backend:latest"
        
        ports {
          container_port = 8000
        }

        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.database.name}"
        }

        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.redis.host}:${google_redis_instance.redis.port}/0"
        }

        env {
          name  = "GCS_BUCKET_NAME"
          value = google_storage_bucket.media.name
        }

        env {
          name  = "DEBUG"
          value = "False"
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres.connection_name
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.apis]
}

# Cloud Run Service for Frontend
resource "google_cloud_run_service" "frontend" {
  name     = "${var.project_name}-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/${var.project_name}-frontend:latest"
        
        ports {
          container_port = 80
        }

        env {
          name  = "REACT_APP_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.apis]
}

# IAM policy for Cloud Run services to be publicly accessible
resource "google_cloud_run_service_iam_member" "backend_public" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Grant Artifact Registry Reader permission to default Compute Engine service account
resource "google_project_iam_member" "artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:1036566880412-compute@developer.gserviceaccount.com"
}

# VPC Access Connector for Cloud Run to access Cloud SQL
resource "google_vpc_access_connector" "connector" {
  name          = "${var.project_name}-connector"
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.vpc.name
  region        = var.region

  depends_on = [google_project_service.apis]
} 

# Redis Memorystore Instance
resource "google_redis_instance" "redis" {
  name           = "${var.project_name}-redis"
  memory_size_gb = 1
  region         = var.region
  redis_version  = "REDIS_7_2"
  tier           = "STANDARD_HA"
  
  authorized_network = google_compute_network.vpc.id
  
  depends_on = [google_project_service.apis]
} 