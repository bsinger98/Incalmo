class Agent:
    def __init__(
        self,
        paw: str,
        username: str,
        privilege: str,
        pid: str,
        host_ip_addrs: list[str],
        hostname: str,
    ):
        self.paw = paw
        self.username = username
        self.privilege = privilege
        self.pid = pid
        self.host_ip_addrs = host_ip_addrs
        self.hostname = hostname

    def __str__(self):
        return f"{self.__class__.__name__}: paw={self.paw},  username={self.username}, priv={self.privilege}, pid={self.pid}, ip_addr={self.host_ip_addrs}, hostname={self.hostname}"
