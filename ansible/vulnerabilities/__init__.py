from .ssh.equifax_ssh_config.EquifaxSSHConfig import EquifaxSSHConfig
from .ssh.SSHEnablePasswordLogin import SSHEnablePasswordLogin

from .apacheStruts.SetupStrutsVulnerability import SetupStrutsVulnerability
from .SetupNetcatShell import SetupNetcatShell

from .privledge_escalation.sudobaron.sudobaron import SetupSudoBaron
from .privledge_escalation.sudoedit.sudoedit import SetupSudoEdit
from .privledge_escalation.sudobypass.sudobypass import SetupSudoBypass
from .privledge_escalation.writeablePasswd.writeable_passwd import SetupWriteablePasswd
from .privledge_escalation.writeableSudoers.writeable_sudoers import (
    SetupWriteableSudoers,
)
