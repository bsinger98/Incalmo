### Webserver Network Rules ###
resource "openstack_networking_secgroup_v2" "webserver" {
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
  security_group_id = openstack_networking_secgroup_v2.webserver.id
}
resource "openstack_networking_secgroup_rule_v2" "webserver_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.webserver.id
}


### Critical Company Network Rules ###
resource "openstack_networking_secgroup_v2" "critical_company" {
  name        = "critical_company"
  description = "critical company security group"
}

# Everyone in critical company can talk to each other
resource "openstack_networking_secgroup_rule_v2" "intra_critical_company_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
}

resource "openstack_networking_secgroup_rule_v2" "intra_critical_company_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
}

resource "openstack_networking_secgroup_rule_v2" "critical_company_webserver_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
}

resource "openstack_networking_secgroup_rule_v2" "critical_company_webserver_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
}


