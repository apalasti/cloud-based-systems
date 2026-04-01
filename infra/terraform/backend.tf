terraform {
  backend "s3" {
    # Fill these in after running `infra/terraform/bootstrap`.
    bucket         = "REPLACE_ME"
    key            = "photo-gallery/prod/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "REPLACE_ME"
    encrypt        = true
  }
}

