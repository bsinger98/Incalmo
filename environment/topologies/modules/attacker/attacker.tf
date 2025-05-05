# input variables
variable "router_external_id" {
  description = "The external router"
}
variable "key_name" {
  description = "The key name to use for the instances"
}

resource "openstack_networking_network_v2" "attacker_network" {
  name           = "attacker_network"
  admin_state_up = "true"
  description    = "The attacker network"
}

resource "openstack_networking_subnet_v2" "attacker_subnet" {
  name            = "attacker_subnet"
  network_id      = openstack_networking_network_v2.attacker_network.id
  cidr            = "192.168.202.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_attacker" {
  router_id = var.router_external_id
  subnet_id = openstack_networking_subnet_v2.attacker_subnet.id
}

### Attacker Subnet Hosts ###
resource "openstack_compute_instance_v2" "attacker" {
  name        = "attacker"
  image_name  = "Kali"
  flavor_name = "m1.small"
  key_pair    = var.key_name
  security_groups = [
    openstack_networking_secgroup_v2.attacker.name
  ]
  network {
    name        = "attacker_network"
    fixed_ip_v4 = "192.168.202.100"
  }

  depends_on = [openstack_networking_subnet_v2.attacker_subnet]
}
