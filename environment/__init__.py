from .environment import Environment

from .GoalKeeper import GoalKeeper
from .Result import ExperimentResult, FlagInformation, FlagType, DataExfiltrated

from .specifications.equifax_large import EquifaxLarge
from .specifications.equifax_medium import EquifaxMedium
from .specifications.equifax_small import EquifaxSmall
from .specifications.ics import ICSEnvironment
from .specifications.chain import ChainEnvironment
from .specifications.chain_pe import PEChainEnvironment
from .specifications.star import Star
from .specifications.star_pe import StarPE
from .specifications.dumbbell import Dumbbell
from .specifications.dumbbell_pe import DumbbellPE
from .specifications.enterprise_a import EnterpriseA
from .specifications.enterprise_b import EnterpriseB
from .specifications.chain_2hosts import Chain2Hosts

from .specifications.dev.dev import DevEnvironment
from .specifications.dev.priv_test import DevPrivTestEnvironment
