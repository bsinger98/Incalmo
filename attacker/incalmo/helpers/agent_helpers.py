import asyncio
from app.objects.c_operation import Operation


def update_trusted_agents(agents, trusted_agents, hosts):
    trusted_agents = list(filter(lambda agent: agent.trusted, agents))
    trusted_agents = list(filter(lambda agent: agent.host in hosts, trusted_agents))

    return trusted_agents


def get_trusted_agents(operation: Operation):
    return list(filter(lambda agent: agent.trusted, operation.agents))


TIMEOUT_PER_LOOP_SEC = 5


async def find_attacker_agents(operation: Operation, timeout_sec=60):
    timeout_time = 0
    while timeout_time < timeout_sec:
        trusted_agents = get_trusted_agents(operation)

        if len(trusted_agents) > 0:
            return trusted_agents

        await asyncio.sleep(TIMEOUT_PER_LOOP_SEC)
        timeout_time += TIMEOUT_PER_LOOP_SEC

    return None
