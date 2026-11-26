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

variable "github_oidc_sub" {
  description = "Exact OIDC sub claim allowed to assume the CI role (GitHub includes immutable owner and repo IDs)"
  type        = string
  default     = "repo:sakshi060@74258276/zero-downtime-rollout-platform@1472272200:ref:refs/heads/main"
}
