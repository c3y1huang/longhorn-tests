variable "aws_access_key" {
  type        = string
  description = "AWS ACCESS_KEY"
}

variable "aws_secret_key" {
  type        = string
  description = "AWS SECRET_KEY"
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
}

variable "os_distro_version" {
  type        = string
  default     = "20.04"
}

variable "aws_ami_ubuntu_account_number" {
  type        = string
  default     = "099720109477"
}

variable "registry_aws_instance_type" {
  type        = string
  description = "Recommended instance types t2.micro"
  default     = "t2.micro"
}

variable "docker_hub_username" {
  type = string
  sensitive = true
}

variable "docker_hub_password" {
  type = string
  sensitive = true
}

variable "longhorn_version" {
  type = string
  default = "master"
}

variable "aws_ssh_public_key_file_path" {
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "aws_ssh_private_key_file_path" {
  type        = string
  default     = "~/.ssh/id_rsa"
}

variable "appco_test" {
  type = string
  default = "false"
}

variable "arch" {
  type        = string
  description = "available values (amd64, arm64)"
  default     = "amd64"
}
