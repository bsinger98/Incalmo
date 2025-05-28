import asyncio
from incalmo.core.strategies.llm.haiku3_5 import Haiku3_5Strategy
from incalmo.core.strategies.llm.llm_strategy import LLMStrategy
from incalmo.core.services import ConfigService
from incalmo.core.strategies.testers.equifax_test import EquifaxStrategy

TIMEOUT_SECONDS = 75 * 60


async def main():
    config = ConfigService().get_config()
    # strategy_name = config.strategy
    # strategy = LLMStrategy.build_llm_strategy(strategy_name)
    strategy = EquifaxStrategy()
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
