
provider "aws" {
  region = var.region
}

module "networking" {
  source = "../../modules/networking"
}

module "kubernetes" {
  source = "../../modules/kubernetes"
  vpc_id = module.networking.vpc_id
}

module "database" {
  source = "../../modules/database"
  vpc_id = module.networking.vpc_id
}
module "registry" {
  source = "../../modules/registry"
}

output "backend_ecr_url" {
  value = module.registry.backend_repository_url
}

output "frontend_ecr_url" {
  value = module.registry.frontend_repository_url
}
