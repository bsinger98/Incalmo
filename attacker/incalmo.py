import asyncio
from incalmo.strategies.debug import DebugStrategy


async def main():
    strategy = DebugStrategy()
    await strategy.initialize()
    result = await strategy.main()
    print(f"DebugStrategy returned: {result}")


if __name__ == "__main__":
    asyncio.run(main())
