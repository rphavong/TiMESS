# Terraform configuration for TiMESS backend
## Tells terraform to use the S3 backend for storing state files and specifies the required AWS provider version.
terraform {
  backend "s3" {
    bucket = "timess-tfstate"
    key    = "timess/terraform.tfstate"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
