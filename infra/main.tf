provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

# S3: raw source documents (what ingest.py will eventually pull from)
resource "aws_s3_bucket" "docs" {
  bucket = "timess-docs-${data.aws_caller_identity.current.account_id}"
}

# DynamoDB: session/chat logs -- src/dynamo.py already writes here
resource "aws_dynamodb_table" "sessions" {
  name         = "timess-sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"
  range_key    = "turn_id"

  attribute {
    name = "session_id"
    type = "S"
  }
  attribute {
    name = "turn_id"
    type = "S"
  }
}

# Secrets Manager: Mem0 key, readable only by the EC2 instance's role
resource "aws_secretsmanager_secret" "mem0" {
  name = "timess/mem0-api-key"
}

resource "aws_secretsmanager_secret_version" "mem0" {
  secret_id     = aws_secretsmanager_secret.mem0.id
  secret_string = var.mem0_api_key
}

# Security group: only the ports the app actually needs
resource "aws_security_group" "app" {
  name_prefix = "timess-"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # tighten to your IP for real use
  }
  ingress {
    description = "Backend API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Frontend UI"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM: least-privilege permissions for the EC2 instance
resource "aws_iam_role" "app" {
  name = "timess-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "app" {
  name = "timess-app-policy"
  role = aws_iam_role.app.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.docs.arn, "${aws_s3_bucket.docs.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:Query"]
        Resource = aws_dynamodb_table.sessions.arn
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = aws_secretsmanager_secret.mem0.arn
      }
    ]
  })
}

resource "aws_iam_instance_profile" "app" {
  name = "timess-ec2-profile"
  role = aws_iam_role.app.name
}

# EC2: hosts the Docker Compose stack. user_data installs Docker on
# first boot; GitHub Actions' deploy.yml (Part C) copies over your
# docker-compose.yml and starts the containers over SSH.
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.app.name

  user_data = <<-USERDATA
    #!/bin/bash
    dnf install -y docker git
    systemctl enable --now docker
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
      -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
  USERDATA

  tags = {
    Name = "timess-app"
  }
}

