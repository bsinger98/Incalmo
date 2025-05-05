### Webserver Network Rules ###
resource "openstack_networking_secgroup_v2" "dev_hosts" {
  name        = "Dev hosts group"
  description = ""
}

# Open security rules for hosts
resource "openstack_networking_secgroup_rule_v2" "dev_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.dev_hosts.id
}
resource "openstack_networking_secgroup_rule_v2" "dev_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.dev_hosts.id
}

# All ICMP traffic is allowed
resource "openstack_networking_secgroup_rule_v2" "dev_icmp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.dev_hosts.id
}
resource "openstack_networking_secgroup_rule_v2" "dev_icmp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.dev_hosts.id
}
