from incalmo.core.models.attacker.agent import Agent
import traceback

from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import (
    LLMAgentAction,
)

from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from config.attacker_config import AbstractionLevel
from incalmo.core.services.environment_state_service import (
    EnvironmentStateService,
)

from incalmo.core.strategies.llm.llm_response import (
    LLMResponseType,
)
from incalmo.core.strategies.llm.interfaces.llm_interface import (
    LLMInterface,
)

from incalmo.core.actions.LowLevel import RunBashCommand, MD5SumAttackerData
from incalmo.core.actions import HighLevel, LowLevel
from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.events import BashOutputEvent
from config.attacker_config import AttackerConfig

from abc import ABC, abstractmethod

import anthropic
import inspect

client = anthropic.Anthropic()


class LLMStrategy(IncalmoStrategy, ABC):
    def __init__(self, config: AttackerConfig):
        super().__init__(config)
        self.logger = self.logging_service.setup_logger(logger_name="llm")

        # Logging Start
        self.logger.info(
            f"[LLMStrategy] Starting LLM strategy with config: {self.config}"
        )

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
        if self.config.strategy.abstraction != AbstractionLevel.INCALMO:
            for host in self.initial_hosts:
                agent = host.get_agent()
                if agent:
                    await self.low_level_action_orchestrator.run_action(
                        MD5SumAttackerData(agent)
                    )

        # Output preprompt log
        # experiment_log_dir = self.log_creator.logger_dir_path
        pre_prompt = self.llm_interface.pre_prompt

        # if len(self.bash_log) > 0:
        #     with open(f"{experiment_log_dir}/bash_log.log", "w") as f:
        #         f.write(self.bash_log)

        # with open(f"{experiment_log_dir}/pre_prompt.log", "w") as f:
        #     f.write(pre_prompt)

    async def step(self) -> bool:
        # Check if any new agents were created
        agents = self.c2_client.get_agents()
        self.environment_state_service.update_host_agents(agents)

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
            self.logger.error(f"Error getting LLM action: {e}")
            return True

        new_perr_reponse = ""
        if llm_action is None:
            if self.config.strategy.abstraction == AbstractionLevel.SHELL:
                new_perr_reponse = (
                    "No <shell> tag found. Please try again and include a tag."
                )
            else:
                new_perr_reponse = "No <finished> <query> or <action> tag found. Please try again and include a tag."

            self.last_response = new_perr_reponse
            return False

        if llm_action.response_type == LLMResponseType.FINISHED:
            return True

        try:
            current_response = ""
            if llm_action.response_type == LLMResponseType.QUERY:
                query = llm_action.response
                self.logger.info(f"LLM query: \n{query}")
                current_response += "\nThe query result is: \n"
                objects = await dynamic_query_execution(
                    self.environment_state_service, self.attack_graph_service, query
                )
                for obj in objects:
                    # Check if the object is Host
                    current_response += str(obj) + "\n"

                self.logger.info(f"Query response: \n{current_response}")
                self.last_response = current_response
                return False

            if (
                llm_action.response_type == LLMResponseType.ACTION
                or llm_action.response_type == LLMResponseType.MEDIUM_ACTION
            ):
                action = llm_action.response
                self.logger.info(f"LLM action: \n{action}")
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
                    self.environment_state_service, self.config.strategy.abstraction
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
                        self.logger.info(action.get_llm_conversation())

                self.logger.info(f"Action response: \n{current_response}")
                self.last_response = current_response
                return False

            if llm_action.response_type == LLMResponseType.BASH:
                command = llm_action.response
                self.logger.info(f"Bash command: \n{command}")
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

                self.logger.info(f"Command response: \n{object_info}")
                self.last_response = object_info
                return False

        except Exception as e:
            self.last_response = f"Error executing query or action: {e} \n"
            self.last_response += traceback.format_exc()

            self.logger.error(
                f"Error executing query or action: \n{self.last_response}"
            )
            return False

        return False


def get_infection_summary_str(
    env_service: EnvironmentStateService, abstraction: AbstractionLevel
):
    infection_summary = "\n"
    abstractions_with_full_info = [
        AbstractionLevel.AGENT_ALL,
        AbstractionLevel.AGENT_SCAN,
        AbstractionLevel.AGENT_LATERAL_MOVE,
        AbstractionLevel.AGENT_PRIVILEGE_ESCALATION,
        AbstractionLevel.AGENT_EXFILTRATE_DATA,
        AbstractionLevel.AGENT_FIND_INFORMATION,
        AbstractionLevel.INCALMO,
        AbstractionLevel.LOW_LEVEL_ACTIONS,
    ]

    if abstraction in abstractions_with_full_info:
        infection_summary += "Your current infected hosts are:\n"
        for host in env_service.get_hosts_with_agents():
            host_str = (
                f"Host {host.hostname} with IPs {host.ip_addresses} has agents:\n"
            )
            for agent in host.agents:
                host_str += "    "
                host_str += f"Agent id: {agent.paw}, user: {agent.username}\n"
            infection_summary += host_str

    elif abstraction == AbstractionLevel.NO_SERVICES:
        agents = env_service.get_agents()
        infection_summary += "Your current agents are: \n"
        infection_summary += get_agent_string(agents)

    return infection_summary


def get_agent_string(agents: list[Agent]) -> str:
    agent_str = ""
    for agent in agents:
        agent_str += f"host: {agent.paw}, user: {agent.username}, ip: {agent.host_ip_addrs}, paw: {agent.paw}\n"
    return agent_str


def get_all_action_classes():
    """Dynamically discover and return all High and Low level action classes"""
    action_globals = {}

    # Get all classes from HighLevel module
    for name in dir(HighLevel):
        obj = getattr(HighLevel, name)
        if (
            inspect.isclass(obj)
            and issubclass(obj, HighLevelAction)
            and obj != HighLevelAction
        ):
            action_globals[name] = obj

    # Get all classes from LowLevel module
    for name in dir(LowLevel):
        obj = getattr(LowLevel, name)
        if (
            inspect.isclass(obj)
            and issubclass(obj, LowLevelAction)
            and obj != LowLevelAction
        ):
            action_globals[name] = obj

    return action_globals


async def dynamic_query_execution(
    environment_state_service, attack_graph_service, code
):
    # TODO: Make more robust
    exec_globals = get_all_action_classes()
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
    exec_globals = get_all_action_classes()
    exec_locals = {}
    exec(code, exec_globals, exec_locals)

    # Retrieve the defined async function from exec_locals
    action_function = exec_locals["action"]

    # Call the dynamically defined async function with await
    result = await action_function(environment_state_service, attack_graph_service)

    return result


async def dynamic_med_action_execution(code):
    exec_globals = get_all_action_classes()
    exec_locals = {}
    exec(code, exec_globals, exec_locals)

    # Retrieve the defined async function from exec_locals
    action_function = exec_locals["action"]

    # Call the dynamically defined async function with await
    result = await action_function()
    return result
