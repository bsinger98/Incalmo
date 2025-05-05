from plugins.deception.app.models.events import Event


class FlagFound(Event):
    def __init__(self, host_ip: str, flag: str, flag_path: str):
        self.host_ip = host_ip
        self.flag = flag
        self.flag_path = flag_path
