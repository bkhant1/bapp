output "backend_url" {
  description = "URL of the backend service"
  value       = google_cloud_run_service.backend.status[0].url
}

output "frontend_url" {
  description = "URL of the frontend service"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "database_connection_name" {
  description = "The connection name of the Cloud SQL instance"
  value       = google_sql_database_instance.postgres.connection_name
}

output "database_private_ip" {
  description = "The private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "redis_host" {
  description = "The IP address of the Redis instance"
  value       = google_redis_instance.redis.host
}

output "redis_port" {
  description = "The port number of the Redis instance"
  value       = google_redis_instance.redis.port
}

output "media_bucket_name" {
  description = "Name of the Cloud Storage bucket for media files"
  value       = google_storage_bucket.media.name
}

output "vpc_network" {
  description = "The VPC network"
  value       = google_compute_network.vpc.name
} 