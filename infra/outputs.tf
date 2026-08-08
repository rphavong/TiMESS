# Terraform output variables for TiMESS backend
output "ec2_public_ip" {
  value = aws_instance.app.public_ip
}

output "docs_bucket" {
  value = aws_s3_bucket.docs.bucket
}

output "sessions_table" {
  value = aws_dynamodb_table.sessions.name
}
