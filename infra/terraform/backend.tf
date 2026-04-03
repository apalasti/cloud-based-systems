terraform {
  backend "s3" {
    # Fill these in after running `infra/terraform/bootstrap`.
    bucket         = "cloud-based-sys-prod-tf-state"
    key            = "cloud-based-sys/prod/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "cloud-based-sys-prod-tf-lock"
    encrypt        = true
  }
}

