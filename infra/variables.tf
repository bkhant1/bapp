variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "bookexchange"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-west2"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "europe-west2-a"
}

variable "database_name" {
  description = "The name of the database"
  type        = string
  default     = "bookexchange"
}

variable "database_user" {
  description = "The database user name"
  type        = string
  default     = "bookexchange"
}

variable "database_password" {
  description = "The database password"
  type        = string
  sensitive   = true
} 