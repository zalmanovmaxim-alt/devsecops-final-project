output "eks_cluster_role_arn" {
  value       = aws_iam_role.eks_cluster.arn
  description = "The ARN of the IAM role for the EKS cluster"
}

output "eks_node_group_role_arn" {
  value       = aws_iam_role.eks_nodes.arn
  description = "The ARN of the IAM role for the EKS node group"
}
