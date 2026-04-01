output "alb_dns_name" {
  value       = aws_lb.app.dns_name
  description = "Public DNS name of the Application Load Balancer."
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.app.repository_url
  description = "ECR repository URL for the app image."
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.address
  description = "RDS hostname/address."
}

output "efs_id" {
  value       = aws_efs_file_system.uploads.id
  description = "EFS file system id for uploads."
}

