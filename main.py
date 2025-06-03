import asyncio
from incalmo.api.server_api import C2ApiClient


async def main():
    C2ApiClient().incalmo_startup(strategy_name="haiku3_5_strategy")

if __name__ == "__main__":
    asyncio.run(main())
