### Webserver Network Rules ###
resource "openstack_networking_secgroup_v2" "webserver_secgroup" {
  name        = "webserver"
  description = "Webserver security group"
}

# Webservers can talk to anything
resource "openstack_networking_secgroup_rule_v2" "webserver_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.webserver_secgroup.id
}
resource "openstack_networking_secgroup_rule_v2" "webserver_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.webserver_secgroup.id
}


### Employee A Rules ###
resource "openstack_networking_secgroup_v2" "employee_a_secgroup" {
  name        = "employee_a_secgroup"
  description = "Employee A security group"
}

resource "openstack_networking_secgroup_rule_v2" "employee_a_ingress_rules" {
  for_each          = toset(["192.168.200.0/24", "192.168.201.0/24", "192.168.203.0/24"])
  direction         = "ingress"
  ethertype         = "IPv4"
  remote_ip_prefix  = each.value
  security_group_id = openstack_networking_secgroup_v2.employee_a_secgroup.id
}

resource "openstack_networking_secgroup_rule_v2" "employee_a_egress_rules" {
  for_each          = toset(["192.168.200.0/24", "192.168.201.0/24", "192.168.203.0/24"])
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = each.value
  security_group_id = openstack_networking_secgroup_v2.employee_a_secgroup.id
}

### Employee B Rules ###
resource "openstack_networking_secgroup_v2" "employee_b_secgroup" {
  name        = "employee_b_secgroup"
  description = "Employee B security group"
}

resource "openstack_networking_secgroup_rule_v2" "employee_b_ingress_rules" {
  for_each          = toset(["192.168.200.0/24", "192.168.204.0/24", "192.168.203.0/24"])
  direction         = "ingress"
  ethertype         = "IPv4"
  remote_ip_prefix  = each.value
  security_group_id = openstack_networking_secgroup_v2.employee_b_secgroup.id
}

resource "openstack_networking_secgroup_rule_v2" "employee_b_egress_rules" {
  for_each          = toset(["192.168.200.0/24", "192.168.204.0/24", "192.168.203.0/24"])
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = each.value
  security_group_id = openstack_networking_secgroup_v2.employee_b_secgroup.id
}

### Database Rules ###
resource "openstack_networking_secgroup_v2" "database_secgroup" {
  name        = "database_secgroup"
  description = "Database security group"
}

resource "openstack_networking_secgroup_rule_v2" "database_ingress_rules" {
  for_each          = toset(["192.168.200.0/24", "192.168.201.0/24", "192.168.203.0/24", "192.168.204.0/24"])
  direction         = "ingress"
  ethertype         = "IPv4"
  remote_ip_prefix  = each.value
  security_group_id = openstack_networking_secgroup_v2.database_secgroup.id
}

resource "openstack_networking_secgroup_rule_v2" "database_egress_rules" {
  for_each          = toset(["192.168.200.0/24", "192.168.201.0/24", "192.168.203.0/24", "192.168.204.0/24"])
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = each.value
  security_group_id = openstack_networking_secgroup_v2.database_secgroup.id
}

