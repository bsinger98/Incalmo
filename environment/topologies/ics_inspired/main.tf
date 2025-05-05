######### Setup Networking #########
# External network is not managed by terraform, need to set as datasource
module "perry_manager" {
  source   = "../modules/perry_manager"
  key_name = var.perry_key_name
}

module "attacker" {
  source             = "../modules/attacker"
  router_external_id = module.perry_manager.router_external_id
  key_name           = var.perry_key_name
}

resource "openstack_networking_network_v2" "employee_one_network" {
  name           = "employee_one_network"
  admin_state_up = "true"
  description    = "Employee network one"
}

resource "openstack_networking_network_v2" "employee_two_network" {
  name           = "employee_two_network"
  admin_state_up = "true"
  description    = "Employee network two"
}

resource "openstack_networking_network_v2" "OT_network" {
  name           = "OT_network"
  admin_state_up = "true"
  description    = "The corporate network with critical data"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "employee_one_subnet" {
  name            = "employee_one_subnet"
  network_id      = openstack_networking_network_v2.employee_one_network.id
  cidr            = "192.168.200.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "employee_two_subnet" {
  name            = "employee_two_subnet"
  network_id      = openstack_networking_network_v2.employee_two_network.id
  cidr            = "192.168.201.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "OT_subnet" {
  name            = "OT_subnet"
  network_id      = openstack_networking_network_v2.OT_network.id
  cidr            = "192.168.203.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

### Routers ###
# Connect subnets
resource "openstack_networking_router_interface_v2" "router_interface_manage_company" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.employee_one_subnet.id
}

resource "openstack_networking_router_interface_v2" "router_interface_employee_two" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.employee_two_subnet.id
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_datacenter" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.OT_subnet.id
}

######### Setup Compute #########
### Employee 1 Subnet Hosts ###
resource "openstack_compute_instance_v2" "employee_one" {
  count       = 10
  name        = "employee_A_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.employee_one_group.name
  ]

  network {
    name = "employee_one_network"
    // sequential ips
    fixed_ip_v4 = "192.168.200.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.employee_one_subnet]
}

resource "openstack_compute_instance_v2" "manage_employee_one" {
  count       = 1
  name        = "manage_A_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.employee_one_group.name
  ]

  network {
    name = "employee_one_network"
  }

  depends_on = [openstack_networking_subnet_v2.employee_one_subnet]
}

### Corporate Subnet Hosts ###
resource "openstack_compute_instance_v2" "employee_two" {
  count       = 10
  name        = "employee_B_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.employee_two_group.name
  ]

  network {
    name        = "employee_two_network"
    fixed_ip_v4 = "192.168.201.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.employee_two_subnet]
}

resource "openstack_compute_instance_v2" "manage_employee_two" {
  count       = 1
  name        = "manage_B_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.employee_two_group.name
  ]

  network {
    name = "employee_two_network"
  }

  depends_on = [openstack_networking_subnet_v2.employee_two_subnet]
}

resource "openstack_compute_instance_v2" "ot_sensors" {
  count       = 20
  name        = "sensor_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.ot_group.name
  ]

  network {
    name        = "ot_network"
    fixed_ip_v4 = "192.168.203.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.OT_subnet]
}

resource "openstack_compute_instance_v2" "ot_hosts" {
  count       = 5
  name        = "control_host_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.ot_group.name
  ]

  network {
    name        = "ot_network"
    fixed_ip_v4 = "192.168.203.${count.index + 50}"
  }

  depends_on = [openstack_networking_subnet_v2.OT_subnet]
}
