output "ecr_repository_urls" {
  value = { for k, r in aws_ecr_repository.apps : k => r.repository_url }
}

output "gha_role_arn" {
  value = aws_iam_role.gha.arn
}
