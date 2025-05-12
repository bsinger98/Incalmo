import asyncio
from incalmo.strategies.debug import DebugStrategy

TIMEOUT_SECONDS = 75 * 60


async def main():
    strategy = DebugStrategy()
    await strategy.initialize()
    start_time = asyncio.get_event_loop().time()
    while True:
        result = await strategy.main()
        if result:
            break
        if asyncio.get_event_loop().time() - start_time > TIMEOUT_SECONDS:
            break
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
