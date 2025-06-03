import asyncio
from incalmo.api.server_api import C2ApiClient

async def main():
    # Use full AttackerConfig format
    config = {
        "name": "test_attack",
        "strategy": {"llm": "haiku3_5_strategy", "abstraction": "incalmo"},
        "environment": "EquifaxSmall",
        "c2c_server": "http://localhost:8888",
    }

    C2ApiClient().incalmo_startup(config=config)


if __name__ == "__main__":
    asyncio.run(main())
