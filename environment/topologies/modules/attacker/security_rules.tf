### Attacker Network Rules ###
resource "openstack_networking_secgroup_v2" "attacker" {
  name        = "attacker"
  description = "attacker security group"
}

# Attackers can talk to anything
resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.attacker.id
}

resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.attacker.id
}
