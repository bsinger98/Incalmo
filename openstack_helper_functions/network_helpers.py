import ipaddress


def addr_in_subnet(subnet, addr):
    return ipaddress.ip_address(addr) in ipaddress.ip_network(subnet)


def server_is_on_subnet(subnet, server):
    for network, network_attrs in server.addresses.items():
        ip_addresses = [x["addr"] for x in network_attrs]
        for ip in ip_addresses:
            if addr_in_subnet(subnet, ip):
                return True


def servers_on_subnet(conn, subnet):
    hosts_in_subnet = []
    for server in conn.compute.servers():
        if server_is_on_subnet(subnet, server):
            hosts_in_subnet.append(server)

    return hosts_in_subnet


def servers_ips_on_subnet(conn, subnet):
    ips_in_subnet = []
    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x["addr"] for x in network_attrs]
            for ip in ip_addresses:
                if addr_in_subnet(subnet, ip):
                    ips_in_subnet.append(ip)

    return ips_in_subnet
