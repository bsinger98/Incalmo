import asyncio
from incalmo.api.server_api import C2ApiClient
from incalmo.core.services.config_service import ConfigService


async def main():
    print("Starting Incalmo C2 server using configservice")
    config = ConfigService().get_config()
    C2ApiClient().incalmo_startup(config=config)


if __name__ == "__main__":
    asyncio.run(main())
