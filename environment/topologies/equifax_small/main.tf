######### Setup Networking #########
module "perry_manager" {
  source   = "../modules/perry_manager"
  key_name = var.perry_key_name
}

module "attacker" {
  source             = "../modules/attacker"
  router_external_id = module.perry_manager.router_external_id
  key_name           = var.perry_key_name
}

resource "openstack_networking_network_v2" "webserver_network" {
  name           = "webserver_network"
  admin_state_up = "true"
  description    = "The external webserver network"
}

resource "openstack_networking_network_v2" "critical_company_network" {
  name           = "critical_company_network"
  admin_state_up = "true"
  description    = "The corporate network with critical data"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "webserver_subnet" {
  name            = "webserver_network"
  network_id      = openstack_networking_network_v2.webserver_network.id
  cidr            = "192.168.200.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "critical_company_subnet" {
  name            = "critical_company_network"
  network_id      = openstack_networking_network_v2.critical_company_network.id
  cidr            = "192.168.201.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

### Routers ###
# Connect subnets
resource "openstack_networking_router_interface_v2" "router_interface_manage_company" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.webserver_subnet.id
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_datacenter" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.critical_company_subnet.id
}

######### Setup Compute #########
### Webserver Subnet Hosts ###
resource "openstack_compute_instance_v2" "webserver" {
  count       = 2
  name        = "webserver_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.webserver.name
  ]

  network {
    name = "webserver_network"
    // sequential ips
    fixed_ip_v4 = "192.168.200.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.webserver_subnet]
}

### Corporate Subnet Hosts ###
resource "openstack_compute_instance_v2" "database" {
  count       = 12
  name        = "database_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "critical_company_network"
    fixed_ip_v4 = "192.168.201.${count.index + 50}"
  }

  depends_on = [openstack_networking_subnet_v2.critical_company_subnet]
}


