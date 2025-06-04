import asyncio
from incalmo.api.server_api import C2ApiClient
from incalmo.incalmo_runner import run_incalmo_strategy
from incalmo.core.services.config_service import ConfigService


async def main():
    print("Starting Incalmo C2 server using configservice")
    config = ConfigService().get_config()
    await run_incalmo_strategy(strategy_name=config.strategy.llm)


if __name__ == "__main__":
    asyncio.run(main())
