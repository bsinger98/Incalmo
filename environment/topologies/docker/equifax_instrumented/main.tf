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

  # For linux hosts, use the host.docker.internal DNS name to access the host
  host {
    host = "host.docker.internal"
    ip   = "host-gateway"
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

  # For linux hosts, use the host.docker.internal DNS name to access the host
  host {
    host = "host.docker.internal"
    ip   = "host-gateway"
  }

  networks_advanced {
    name         = docker_network.db_network.name
    ipv4_address = each.value
  }
}

resource "docker_container" "webserver" {
  name    = "webserver_container"
  image   = docker_image.webserver.name
  restart = "always"

  # For linux hosts, use the host.docker.internal DNS name to access the host
  host {
    host = "host.docker.internal"
    ip   = "host-gateway"
  }

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

# Elasticsearch image (official Elastic distribution)
resource "docker_image" "elasticsearch" {
  name         = "docker.elastic.co/elasticsearch/elasticsearch:8.6.2"
  keep_locally = true
}

# Elasticsearch container (single-node, security disabled for lab purposes)
resource "docker_container" "elasticsearch" {
  name    = "elasticsearch"
  image   = docker_image.elasticsearch.name
  restart = "always"

  env = [
    "discovery.type=single-node",
    "ES_JAVA_OPTS=-Xms512m -Xmx512m",
    "xpack.security.enabled=false",
    "xpack.security.transport.ssl.enabled=false"
  ]

  ports {
    internal = 9200
    external = 9200
  }

  ports {
    internal = 9300
    external = 9300
  }

  networks_advanced {
    name         = docker_network.web_network.name
    ipv4_address = "192.168.200.11"
  }

  healthcheck {
    test     = ["CMD-SHELL", "curl -fs http://localhost:9200 || exit 1"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }
}

# Kibana image (same version as Elasticsearch for compatibility)
resource "docker_image" "kibana" {
  name         = "docker.elastic.co/kibana/kibana:8.6.2"
  keep_locally = true
}

# Kibana container (exposes port 5601, disabled security for simplicity)
resource "docker_container" "kibana" {
  name    = "kibana"
  image   = docker_image.kibana.name
  restart = "always"

  env = [
    "SERVER_NAME=kibana",
    "ELASTICSEARCH_HOSTS=http://elasticsearch:9200",
    "XPACK_SECURITY_ENABLED=false",
    "XPACK_REPORTING_ENABLED=false"
  ]

  ports {
    internal = 5601
    external = 5601
  }

  networks_advanced {
    name         = docker_network.web_network.name
    ipv4_address = "192.168.200.12"
  }

  healthcheck {
    test     = ["CMD-SHELL", "curl -fs http://localhost:5601/api/status || exit 1"]
    interval = "10s"
    timeout  = "10s"
    retries  = 10
  }

  depends_on = [docker_container.elasticsearch]
}

# Elastic Agent image (same version as stack)
resource "docker_image" "elastic_agent" {
  name         = "docker.elastic.co/beats/elastic-agent:8.6.2"
  keep_locally = true
}

# Elastic Agent container
resource "docker_container" "elastic_agent" {
  name       = "elastic_agent"
  image      = docker_image.elastic_agent.name
  restart    = "always"
  privileged = true

  env = [
    "FLEET_ENROLL=0",
    "FLEET_SERVER_ENABLE=0",
    "ELASTICSEARCH_HOST=http://elasticsearch:9200",
    "KIBANA_HOST=http://kibana:5601",
    "ELASTICSEARCH_USERNAME=elastic",
    "ELASTICSEARCH_PASSWORD=changeme",
    "LOGGING_LEVEL=info"
  ]

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  networks_advanced {
    name         = docker_network.web_network.name
    ipv4_address = "192.168.200.13"
  }

  healthcheck {
    test         = ["CMD-SHELL", "pgrep elastic-agent || exit 1"]
    interval     = "20s"
    timeout      = "10s"
    retries      = 5
    start_period = "20s"
  }

  depends_on = [docker_container.elasticsearch, docker_container.kibana]
}

# Trigger local post-deployment provisioning script for data views
resource "null_resource" "provision_stack" {
  depends_on = [
    docker_container.kibana,
    docker_container.elasticsearch,
    docker_container.elastic_agent
  ]

  provisioner "local-exec" {
    command = "${path.module}/provisioning/provision_stack.sh"
  }
}
