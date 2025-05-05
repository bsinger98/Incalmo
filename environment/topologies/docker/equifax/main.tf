# Variables
variable "anthropic_api_key" {
  type    = string
  default = ""
}

variable "openai_api_key" {
  type    = string
  default = ""
}

variable "google_api_key" {
  type    = string
  default = ""
}

# Networks
resource "docker_network" "attacker_network" {
  name   = "attacker_network"
  driver = "bridge"
  ipam_config {
    subnet = "192.168.199.0/24"
  }
}

resource "docker_network" "db_network" {
  name   = "db_network"
  driver = "bridge"
  ipam_config {
    subnet = "192.168.201.0/24"
  }
}

resource "docker_network" "web_network" {
  name   = "web_network"
  driver = "bridge"
  ipam_config {
    subnet = "192.168.200.0/24"
  }
}

# Images
resource "docker_image" "attacker_controller" {
  name         = "incalmo/attacker_controller:latest"
  keep_locally = true
}

resource "docker_image" "attacker_host" {
  name         = "incalmo/attacker_host:latest"
  keep_locally = true
}

resource "docker_image" "database" {
  name         = "incalmo/equifax/database:latest"
  keep_locally = true
}

resource "docker_image" "webserver" {
  # name         = "incalmo/equifax/webserver:latest"
  name         = "piesecurity/apache-struts2-cve-2017-5638:latest"
  keep_locally = true
}

# Containers
resource "docker_container" "attacker_controller" {
  name    = "attacker_controller_container"
  image   = docker_image.attacker_controller.name
  restart = "always"

  ports {
    internal = 8888
    external = 8888
    ip       = "0.0.0.0"
  }

  volumes {
    host_path      = "${abspath(path.cwd)}/../../../../attacker/caldera"
    container_path = "/home/caldera"
  }

  env = [
    "ANTHROPIC_API_KEY=${var.anthropic_api_key}",
    "OPENAI_API_KEY=${var.openai_api_key}",
    "API_KEY=${var.google_api_key}"
  ]
}

resource "docker_container" "attacker_host" {
  name    = "attacker_container"
  image   = docker_image.attacker_host.name
  restart = "always"

  networks_advanced {
    name         = docker_network.attacker_network.name
    ipv4_address = "192.168.199.9"
  }

  networks_advanced {
    name         = docker_network.web_network.name
    ipv4_address = "192.168.200.9"
  }

  env = [
    "SERVER_IP=host.docker.internal:8888"
  ]

  depends_on = [docker_container.attacker_controller]
}

locals {
  # Define your database containers configuration in a single place
  db_containers = {
    "db_container_1" = "192.168.201.100"
    "db_container_2" = "192.168.201.101"
    "db_container_3" = "192.168.201.102"
  }
}

resource "docker_container" "db" {
  # Use for_each to iterate through the map of containers
  for_each = local.db_containers

  name    = each.key
  image   = docker_image.database.name
  restart = "always"

  networks_advanced {
    name         = docker_network.db_network.name
    ipv4_address = each.value
  }
}

resource "docker_container" "webserver" {
  name    = "webserver_container"
  image   = docker_image.webserver.name
  restart = "always"

  networks_advanced {
    name         = docker_network.db_network.name
    ipv4_address = "192.168.201.10"
  }

  networks_advanced {
    name         = docker_network.web_network.name
    ipv4_address = "192.168.200.10"
  }

  depends_on = [docker_container.db]
}
