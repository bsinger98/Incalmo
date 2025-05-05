from ansible.AnsiblePlaybook import AnsiblePlaybook


class SetupFakeCredential(AnsiblePlaybook):
    def __init__(
        self, host: str, host_user: str, follower: str, follower_user: str
    ) -> None:
        self.name = "defender/capabilities/setup_fake_credential.yml"
        self.params = {
            "host": host,
            "host_user": host_user,
            "follower": follower,
            "follower_user": follower_user,
        }
