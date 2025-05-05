from .Host import Host
from .Credential import SSHCredential


class AttackTechnique:
    def __init__(
        self,
        CredentialToUse: SSHCredential | None = None,
        PortToAttack: int | None = None,
    ):
        self.CredentialToUse = CredentialToUse
        self.PortToAttack = PortToAttack

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, AttackTechnique):
            return False
        return (
            self.CredentialToUse == __value.CredentialToUse
            and self.PortToAttack == __value.PortToAttack
        )

    def __str__(self) -> str:
        return f"AttackTechnique: {self.CredentialToUse} {self.PortToAttack}"


class AttackPath:
    def __init__(
        self, attack_host: Host, target_host: Host, attack_technique: AttackTechnique
    ):
        self.attack_host = attack_host
        self.target_host = target_host
        self.attack_technique = attack_technique

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, AttackPath):
            return False
        return (
            self.attack_host == __value.attack_host
            and self.target_host == __value.target_host
            and self.attack_technique == __value.attack_technique
        )

    def __str__(self) -> str:
        return f"AttackPath: {self.attack_host} -> {self.target_host} using {self.attack_technique}"
