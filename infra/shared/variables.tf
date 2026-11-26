variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "rollout-platform"
}

variable "github_repo" {
  description = "owner/repo allowed to assume the CI role"
  type        = string
  default     = "sakshi060/zero-downtime-rollout-platform"
}

variable "app_names" {
  type    = list(string)
  default = ["orders-api", "gateway"]
}
