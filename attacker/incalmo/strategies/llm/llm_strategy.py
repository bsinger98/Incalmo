from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from app.objects.c_agent import Agent
import traceback

from plugins.deception.app.actions.HighLevel.llm_agents.llm_agent_action import (
    LLMAgentAction,
)
from plugins.deception.app.actions.HighLevelAction import HighLevelAction
from plugins.deception.app.actions.LowLevelAction import LowLevelAction
from plugins.deception.app.actions.HighLevel import *
from plugins.deception.app.actions.LowLevel import *
from plugins.deception.app.actions.EmptyServiceActions import *
from plugins.deception.app.models.network import *
from plugins.deception.app.models.events import *
from plugins.deception.app.strategies.perry_strategy import PerryStrategy
from plugins.deception.app.data.attacker_config import Abstraction
from plugins.deception.app.services.environment_state_service import (
    EnvironmentStateService,
)

from plugins.deception.app.strategies.llm.llm_response import (
    LLMResponseType,
)
from plugins.deception.app.strategies.llm.interfaces.sonnet3_interface import (
    LLMInterface,
)

from abc import ABC, abstractmethod

import anthropic

client = anthropic.Anthropic()


class LLMStrategy(PerryStrategy, ABC):
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        super().__init__(operation, planning_svc, stopping_conditions)

        # Init claude logger
        self.llm_logger = self.log_creator.setup_logger("llm")
        self.llm_logger.info("LLM logger initialized")

        # Initial network assumptions
        self.llm_interface = self.create_llm_interface()

        self.bash_log = ""

        self.cur_step = 0
        self.total_steps = 100
        self.last_response = None

    @abstractmethod
    def create_llm_interface(self) -> LLMInterface:
        pass

    async def finished_cb(self):
        # Log exfiltrated data for non high level abstractions
        if self.config.abstraction != Abstraction.HIGH_LEVEL:
            for host in self.initial_hosts:
                agent = host.get_agent()
                if agent:
                    await self.low_level_action_orchestrator.run_action(
                        MD5SumAttackerData(agent)
                    )

        # Output preprompt log
        experiment_log_dir = self.log_creator.logger_dir_path
        pre_prompt = self.llm_interface.pre_prompt

        if len(self.bash_log) > 0:
            with open(f"{experiment_log_dir}/bash_log.log", "w") as f:
                f.write(self.bash_log)

        with open(f"{experiment_log_dir}/pre_prompt.log", "w") as f:
            f.write(pre_prompt)

    async def step(self) -> bool:
        # Check if any new agents were created
        self.update_trusted_agents()
        self.environment_state_service.update_host_agents(self.trusted_agents)

        finished = await self.llm_request()

        if self.cur_step > self.total_steps or finished:
            await self.finished_cb()
            return True
        else:
            self.cur_step += 1
            return False

    async def llm_request(self) -> bool:
        try:
            llm_action = self.llm_interface.get_llm_action(self.last_response)
        except Exception as e:
            self.llm_logger.error(f"Error getting LLM action: {e}")
            return True

        new_perr_reponse = ""
        if llm_action is None:
            new_perr_reponse = "Perry did not find a <finished> <query> or <action> tag. Please try again and include a tag."
            self.last_response = new_perr_reponse
            return False

        if llm_action.response_type == LLMResponseType.FINISHED:
            return True

        try:
            current_response = ""
            if llm_action.response_type == LLMResponseType.QUERY:
                query = llm_action.response
                self.perry_logger.info(f"LLM query: \n{query}")
                current_response += "\nThe query result is: \n"
                objects = await dynamic_query_execution(
                    self.environment_state_service, self.attack_graph_service, query
                )
                for obj in objects:
                    # Check if the object is Host
                    current_response += str(obj) + "\n"

                self.perry_logger.info(f"Query response: \n{current_response}")
                self.last_response = current_response
                return False

            if (
                llm_action.response_type == LLMResponseType.ACTION
                or llm_action.response_type == LLMResponseType.MEDIUM_ACTION
            ):
                action = llm_action.response
                self.perry_logger.info(f"LLM action: \n{action}")
                if llm_action.response_type == LLMResponseType.MEDIUM_ACTION:
                    med_actions = await dynamic_med_action_execution(
                        llm_action.response
                    )
                    action_obj = []
                    for action in med_actions:
                        action_obj.append(
                            action.convert(self.environment_state_service)
                        )
                else:
                    action_obj = await dynamic_action_execution(
                        self.environment_state_service,
                        self.attack_graph_service,
                        action,
                    )

                current_response += get_infection_summary_str(
                    self.environment_state_service, self.config.abstraction
                )

                current_response += "\nThe actions had the following events: \n"
                if type(action_obj) is not list:
                    action_obj = [action_obj]

                for action in action_obj:
                    events = []
                    if isinstance(action, HighLevelAction):
                        events = await self.high_level_action_orchestrator.run_action(
                            action
                        )
                    elif isinstance(action, LowLevelAction):
                        events = await self.low_level_action_orchestrator.run_action(
                            action
                        )

                    for event in events:
                        current_response += str(event) + "\n"

                    # If action is subclass of LLMAction, log the entire conversation
                    if isinstance(action, LLMAgentAction):
                        self.llm_logger.info(action.get_llm_conversation())

                self.perry_logger.info(f"Action response: \n{current_response}")
                self.last_response = current_response
                return False

            if llm_action.response_type == LLMResponseType.BASH:
                command = llm_action.response
                self.perry_logger.info(f"Bash command: \n{command}")
                self.bash_log += f"Bash command: {command}\n"
                object_info = "The result is: \n"
                attacker_host = self.initial_hosts[0]
                if attacker_host == None or len(attacker_host.agents) == 0:
                    raise Exception("Attacker agent doesn't exist.")
                attacker_agent = attacker_host.agents[0]
                lowlevelbashcommand = RunBashCommand(attacker_agent, command)
                results = await self.low_level_action_orchestrator.run_action(
                    lowlevelbashcommand
                )
                self.bash_log += f"Command response: \n"
                for result in results:
                    if isinstance(result, BashOutputEvent):
                        object_info += result.bash_output
                        self.bash_log += result.bash_output
                        break

                self.perry_logger.info(f"Command response: \n{object_info}")
                self.last_response = object_info
                return False

        except Exception as e:
            self.last_response = f"Error executing query or action: {e} \n"
            self.last_response += traceback.format_exc()

            self.perry_logger.error(
                f"Error executing query or action: \n{self.last_response}"
            )
            return False

        return False


def get_infection_summary_str(
    env_service: EnvironmentStateService, abstraction: Abstraction
):
    infection_summary = "\n"
    abstractions_with_full_info = [
        Abstraction.AGENT_ALL,
        Abstraction.AGENT_SCAN,
        Abstraction.AGENT_LATERAL_MOVE,
        Abstraction.AGENT_PRIVILEGE_ESCALATION,
        Abstraction.AGENT_EXFILTRATE_DATA,
        Abstraction.AGENT_FIND_INFORMATION,
        Abstraction.HIGH_LEVEL,
        Abstraction.LOW_LEVEL,
    ]

    if abstraction in abstractions_with_full_info:
        infection_summary += "Your current infected hosts are:\n"
        for host in env_service.get_hosts_with_agents():
            host_str = f"Host {host.hostname} with IP {host.ip_address} has agents:\n"
            for agent in host.agents:
                host_str += "    "
                host_str += f"Agent id: {agent.paw}, user: {agent.username}\n"
            infection_summary += host_str

    elif abstraction == Abstraction.NO_SERVICES:
        agents = env_service.get_agents()
        infection_summary += "Your current agents are: \n"
        infection_summary += get_agent_string(agents)

    return infection_summary


def get_agent_string(agents: list[Agent]) -> str:
    agent_str = ""
    for agent in agents:
        agent_str += f"host: {agent.host}, user: {agent.username}, ip: {agent.host_ip_addrs}, paw: {agent.paw}\n"
    return agent_str


async def dynamic_query_execution(
    environment_state_service, attack_graph_service, code
):
    exec_globals = {}
    exec_locals = {}
    exec(code, exec_globals, exec_locals)

    # Retrieve the defined async function from exec_locals
    query_function = exec_locals["query"]

    # Call the dynamically defined async function with await
    result = await query_function(environment_state_service, attack_graph_service)

    return result


async def dynamic_action_execution(
    environment_state_service, attack_graph_service, code
):
    exec_globals = globals()
    exec_locals = {}
    exec(code, exec_globals, exec_locals)

    # Retrieve the defined async function from exec_locals
    action_function = exec_locals["action"]

    # Call the dynamically defined async function with await
    result = await action_function(environment_state_service, attack_graph_service)

    return result


async def dynamic_med_action_execution(code):
    exec_globals = globals()
    exec_locals = {}
    exec(code, exec_globals, exec_locals)

    # Retrieve the defined async function from exec_locals
    action_function = exec_locals["action"]

    # Call the dynamically defined async function with await
    result = await action_function()
    return result
