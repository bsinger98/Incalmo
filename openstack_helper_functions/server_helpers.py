import time


def find_server_by_name(conn, name):
    for server in conn.compute.servers():
        if server.name == name:
            return server
    return None


def find_server_by_ip(conn, ip):
    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x["addr"] for x in network_attrs]
            if ip in ip_addresses:
                return server
    return None


def shutdown_server_by_name(conn, name):
    server = find_server_by_name(conn, name)
    if server:
        conn.compute.stop_server(server)
        return True
    return False


def shutdown_server_by_ip(conn, ip):
    server = find_server_by_ip(conn, ip)
    if server:
        conn.compute.stop_server(server)
        return True
    return False


def get_decoy_servers(openstack_conn):
    """Retrieve all decoy servers on OpenStack."""
    decoys = []
    for server in openstack_conn.list_servers():
        # get image
        image = openstack_conn.get_image(server.image.id)
        if "decoy" in image.name:
            decoys.append(server)
    return decoys


def delete_decoy_servers(openstack_conn):
    """Delete all decoy instances on OpenStack and wait until they are deleted with a timeout."""
    decoy_servers = get_decoy_servers(openstack_conn)

    # Initiate deletion of all decoy servers
    for server in decoy_servers:
        print(f"Deleting decoy server: {server.name}")
        openstack_conn.delete_server(server.id)

    # Wait until all decoy servers are deleted, with a 5-minute timeout
    if decoy_servers:
        print("Waiting for all decoy servers to be deleted...")
        start_time = time.time()
        TIMEOUT_300MS = 60 * 5  # 5 minutes

        while True:
            remaining_decoy_servers = get_decoy_servers(openstack_conn)
            if not remaining_decoy_servers:
                print("All decoy servers have been deleted.")
                break

            elapsed_time = time.time() - start_time
            if elapsed_time > TIMEOUT_300MS:
                raise TimeoutError(
                    "Timeout: Not all decoy servers were deleted within the 5-minute limit."
                )

            time.sleep(5)
