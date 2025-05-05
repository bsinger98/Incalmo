terraform {
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "1.54.1"
    }
  }
}

# No default value
variable "project_name" {
  type        = string
  description = "Openstack project"
}

# No default value
variable "openstack_username" {
  type        = string
  description = "Openstack username"
}

# default value for the variable location
variable "openstack_password" {
  type        = string
  description = "Openstack password"
}

variable "openstack_auth_url" {
  type        = string
  description = "Openstack auth url"
}

variable "openstack_region" {
  type        = string
  description = "Openstack region"
}

variable "perry_key_name" {
  type        = string
  description = "Name of the keypair to use for the Perry instance"
}

# Configure the OpenStack Provider
provider "openstack" {
  user_name   = var.openstack_username
  tenant_name = var.project_name
  password    = var.openstack_password
  auth_url    = var.openstack_auth_url
  region      = var.openstack_region
  insecure    = "true"
}



