variable "region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix used for naming and tagging all resources"
  type        = string
  default     = "rollout-platform"
}

variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
}

variable "my_ip" {
  description = "Your public IP, used to restrict access to the EKS API and NodePorts"
  type        = string
}
