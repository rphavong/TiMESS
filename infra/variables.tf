# Terraform input variables for TiMESS backend
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  description = "EC2 size. t3.xlarge (4 vCPU/16GB) gives Ollama enough headroom for an 8B model on CPU."
  type        = string
  default     = "t3.xlarge"
}

variable "mem0_api_key" {
  description = "Passed in via TF_VAR_mem0_api_key -- never hardcoded"
  type        = string
  sensitive   = true
}

variable "key_pair_name" {
  description = "The EC2 key pair name -- 'rob-key', matching what you created in Part A (no .pem extension)"
  type        = string
}
