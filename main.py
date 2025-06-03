import asyncio
from incalmo.core.strategies.llm.haiku3_5 import Haiku3_5Strategy
from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.services import ConfigService
from incalmo.core.strategies.testers.equifax_test import EquifaxStrategy

TIMEOUT_SECONDS = 75 * 60


async def main():
    config = ConfigService().get_config()
    llm_strategy = config.strategy
    strategy = IncalmoStrategy.build_strategy(llm_strategy.llm)
    await strategy.initialize()
    start_time = asyncio.get_event_loop().time()
    while True:
        print(f"[DEBUG] Running strategy: {strategy.__class__.__name__}")
        result = await strategy.main()
        if result:
            break
        if asyncio.get_event_loop().time() - start_time > TIMEOUT_SECONDS:
            break
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
