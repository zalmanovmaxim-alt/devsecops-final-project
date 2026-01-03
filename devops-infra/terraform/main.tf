locals {
  env = terraform.workspace

  workspace_config = {
    default = {
      vpc_cidr            = "10.0.0.0/16"
      public_cidrs        = ["10.0.1.0/24", "10.0.2.0/24"]
      private_cidrs       = ["10.0.3.0/24", "10.0.4.0/24"]
      node_desired_size   = 1
      instance_types      = ["t3.small"]
    }
    dev = {
      vpc_cidr            = "10.0.0.0/16"
      public_cidrs        = ["10.0.1.0/24", "10.0.2.0/24"]
      private_cidrs       = ["10.0.3.0/24", "10.0.4.0/24"]
      node_desired_size   = 2
      instance_types      = ["t3.medium"]
    }
    prod = {
      vpc_cidr            = "10.1.0.0/16"
      public_cidrs        = ["10.1.1.0/24", "10.1.2.0/24"]
      private_cidrs       = ["10.1.3.0/24", "10.1.4.0/24"]
      node_desired_size   = 3
      instance_types      = ["t3.large"]
    }
  }

  config = lookup(local.workspace_config, local.env, local.workspace_config["default"])
}

provider "aws" {
  region = var.region
}

module "networking" {
  source               = "./modules/networking"
  environment          = local.env
  vpc_cidr             = local.config.vpc_cidr
  public_subnet_cidrs  = local.config.public_cidrs
  private_subnet_cidrs = local.config.private_cidrs
}

module "iam" {
  source      = "./modules/iam"
  environment = local.env
}

module "kubernetes" {
  source                  = "./modules/kubernetes"
  environment             = local.env
  eks_cluster_role_arn    = module.iam.eks_cluster_role_arn
  eks_node_group_role_arn = module.iam.eks_node_group_role_arn
  subnet_ids              = module.networking.private_subnet_ids
  node_desired_size       = local.config.node_desired_size
  instance_types          = local.config.instance_types
}

module "registry" {
  source      = "./modules/registry"
  environment = local.env
}

output "backend_ecr_url" {
  value = module.registry.backend_repository_url
}

output "frontend_ecr_url" {
  value = module.registry.frontend_repository_url
}

output "eks_cluster_name" {
  value = module.kubernetes.cluster_name
}
