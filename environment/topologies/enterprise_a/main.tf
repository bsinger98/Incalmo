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

resource "openstack_networking_network_v2" "employee_a_network" {
  name           = "employee_a_network"
  admin_state_up = "true"
  description    = "Employee a network"
}

resource "openstack_networking_network_v2" "database_network" {
  name           = "database_network"
  admin_state_up = "true"
  description    = "Database network"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "webserver_subnet" {
  name            = "webserver_network"
  network_id      = openstack_networking_network_v2.webserver_network.id
  cidr            = "192.168.200.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "employee_a_subnet" {
  name            = "employee_a_network"
  network_id      = openstack_networking_network_v2.employee_a_network.id
  cidr            = "192.168.201.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "database_subnet" {
  name            = "database_network"
  network_id      = openstack_networking_network_v2.database_network.id
  cidr            = "192.168.203.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

### Routers ###
# Connect subnets
resource "openstack_networking_router_interface_v2" "webserver_router_interface" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.webserver_subnet.id
}

resource "openstack_networking_router_interface_v2" "employee_a_router_interface" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.employee_a_subnet.id
}

resource "openstack_networking_router_interface_v2" "database_router_interface" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.database_subnet.id
}

######### Setup Compute #########
### Webserver Subnet Hosts ###
resource "openstack_compute_instance_v2" "webserver" {
  count       = 10
  name        = "webserver_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.webserver_secgroup.name
  ]

  network {
    name = "webserver_network"
    // sequential ips
    fixed_ip_v4 = "192.168.200.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.webserver_subnet]
}

### Employee A hosts ###
resource "openstack_compute_instance_v2" "employee_a_host" {
  count       = 10
  name        = "employee_a_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.employee_a_secgroup.name
  ]

  network {
    name        = "employee_a_network"
    fixed_ip_v4 = "192.168.201.${count.index + 50}"
  }

  depends_on = [openstack_networking_subnet_v2.employee_a_subnet]
}

### Database hosts ###
resource "openstack_compute_instance_v2" "database" {
  count       = 10
  name        = "database_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.database_secgroup.name
  ]

  network {
    name        = "database_network"
    fixed_ip_v4 = "192.168.203.${count.index + 50}"
  }

  depends_on = [openstack_networking_subnet_v2.database_subnet]
}


