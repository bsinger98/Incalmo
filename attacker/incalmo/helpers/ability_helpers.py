from app.objects.secondclass.c_link import Link
from app.objects.c_agent import Agent
from app.service.planning_svc import PlanningService

import base64
import json
from app.utility.base_service import BaseService
from app.service.file_svc import FileSvc

import asyncio

import logging

plugin_logger = logging.getLogger("deception-plugin")


async def get_link_by_ability_id(
    planning_svc, operation, agent=None, ability_id=None
) -> Link | None:
    """
    Get a link by ability_id
    :param planning_svc:
    :param operation:
    :param agent:
    :param ability_id:
    :return: Link if found or None
    """
    all_agent_links = await planning_svc.get_links(operation=operation, agent=agent)
    if ability_id:
        for link in all_agent_links:
            if link.ability.ability_id == ability_id:
                return link

    return None


file_svc: FileSvc = BaseService.get_service("file_svc")  # type: ignore


async def run_ability(
    planning_svc: PlanningService, operation, agent: Agent, ability_id, timeout_retry=1
) -> dict | None:
    plugin_logger.debug(f"Running ability {ability_id} on {agent.host} ({agent.paw})")
    result_json = None

    for _ in range(timeout_retry):
        link_to_run = await get_link_by_ability_id(
            planning_svc, operation, agent=agent, ability_id=ability_id
        )
        if not link_to_run:
            plugin_logger.debug(
                f"Link not found for {ability_id} on {agent.host} ({agent.paw})"
            )
            return

        # Run the link
        link_id = await operation.apply(link_to_run)
        try:
            # Timeout after 2 minutes
            await asyncio.wait_for(
                operation.wait_for_links_completion([link_id]), timeout=120
            )
        except asyncio.TimeoutError:
            plugin_logger.debug(f"Link {link_id} timed out")
            continue

        plugin_logger.debug(f"Link {link_id} completed")

        # Check status of link
        try:
            if link_to_run.status != link_to_run.states["TIMEOUT"]:
                result = file_svc.read_result_file("%s" % link_id)
                decoded_bytes = base64.b64decode(result)
                result_string = decoded_bytes.decode("utf-8")
                # Load result string as json
                result_json = json.loads(result_string)
                break
        except FileNotFoundError:
            plugin_logger.debug(f"Results not found, link status: {link_to_run.status}")
            result_json = None
            break

    return result_json
