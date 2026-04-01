variable "aws_region" {
  type        = string
  description = "AWS region to deploy into."
  default     = "eu-north-1"
}

variable "project_name" {
  type        = string
  description = "Project name prefix for resource naming."
  default     = "photo-gallery"
}

variable "environment" {
  type        = string
  description = "Environment name."
  default     = "prod"
}

variable "app_port" {
  type        = number
  description = "Container port the app listens on."
  default     = 5000
}

variable "desired_count" {
  type        = number
  description = "Number of ECS tasks."
  default     = 1
}

variable "task_cpu" {
  type        = number
  description = "Fargate task CPU units."
  default     = 512
}

variable "task_memory" {
  type        = number
  description = "Fargate task memory (MiB)."
  default     = 1024
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class."
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  type        = number
  description = "RDS allocated storage (GiB)."
  default     = 20
}

variable "db_name" {
  type        = string
  description = "Database name."
  default     = "appdb"
}

variable "db_username" {
  type        = string
  description = "Database master username."
  default     = "app"
}

variable "uvicorn_workers" {
  type        = number
  description = "Number of Uvicorn workers (passed as UVICORN_WORKERS)."
  default     = 2
}

