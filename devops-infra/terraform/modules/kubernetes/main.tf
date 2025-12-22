
resource "aws_eks_cluster" "main" {
  name     = "devsecops-cluster"
  role_arn = var.eks_role_arn
  vpc_config {
    subnet_ids = var.subnet_ids
  }
}
