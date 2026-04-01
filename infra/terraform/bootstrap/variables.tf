variable "aws_region" {
  type        = string
  description = "AWS region to deploy into."
  default     = "eu-north-1"
}

variable "project_name" {
  type        = string
  description = "Project name prefix for resource naming."
  default     = "cloud-based-sys"
}

variable "environment" {
  type        = string
  description = "Environment name (single env by default)."
  default     = "prod"
}

