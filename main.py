import asyncio
from incalmo.incalmo_runner import run_incalmo_strategy
from incalmo.core.services.config_service import ConfigService
from incalmo.c2server.state_store import StateStore
from config.attacker_config import StateMachineStrategy


async def main():
    print("Starting Incalmo C2 server using configservice")
    StateStore.initialize()  # Initialize the state store (reset the database)
    config = ConfigService().get_config()
    task_id = (
        config.strategy.name
        if isinstance(config.strategy, StateMachineStrategy)
        else config.strategy.planning_llm
    )
    await run_incalmo_strategy(config, task_id=task_id)


if __name__ == "__main__":
    asyncio.run(main())
