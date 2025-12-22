
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
