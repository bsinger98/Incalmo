# External network is not managed by terraform, need to set as datasource
data "openstack_networking_network_v2" "external_network" {
  name = "external"
}

variable "key_name" {
  description = "The name of the key pair to use for the instance"
}

output "external_network_id" {
  value = data.openstack_networking_network_v2.external_network.id
}

output "talk_to_manage_id" {
  value = openstack_networking_secgroup_v2.talk_to_manage.id
}

output "talk_to_manage_name" {
  value = openstack_networking_secgroup_v2.talk_to_manage.name
}

output "manage_freedom_id" {
  value = openstack_networking_secgroup_v2.manage_freedom.id
}
output "manage_freedom_name" {
  value = openstack_networking_secgroup_v2.manage_freedom.name
}

output "router_external_id" {
  value = openstack_networking_router_v2.router_external.id
}

### Network ###
resource "openstack_networking_network_v2" "manage_network" {
  name           = "manage_network"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "manage" {
  name            = "manage"
  network_id      = openstack_networking_network_v2.manage_network.id
  cidr            = "192.168.198.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_router_v2" "router_external" {
  name                = "router_external"
  admin_state_up      = true
  external_network_id = data.openstack_networking_network_v2.external_network.id
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_external" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.manage.id
}

### Host ###
resource "openstack_compute_instance_v2" "manage_host" {
  name        = "manage_host"
  image_name  = "Ubuntu20"
  flavor_name = "m1.small"
  key_pair    = var.key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.manage_freedom.name
  ]

  network {
    name        = "manage_network"
    fixed_ip_v4 = "192.168.198.14"
  }
  depends_on = [openstack_networking_subnet_v2.manage]
}

resource "openstack_networking_floatingip_v2" "manage_floating_ip" {
  pool = "external"
}

resource "openstack_compute_floatingip_associate_v2" "fip_manage" {
  floating_ip = openstack_networking_floatingip_v2.manage_floating_ip.address
  instance_id = openstack_compute_instance_v2.manage_host.id
}
