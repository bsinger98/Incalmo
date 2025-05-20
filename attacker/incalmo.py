import asyncio
from incalmo.strategies.debug import DebugStrategy
from incalmo.strategies.struts_strategy import StrutsStrategy
from incalmo.strategies.llm.gemini_2_flash import Gemini2FlashStrategy
from incalmo.strategies.llm.llm_strategy import LLMStrategy
from incalmo.services import ConfigService

TIMEOUT_SECONDS = 75 * 60


async def main():
    config = ConfigService().get_config()
    strategy_name = config.strategy
    strategy = LLMStrategy.build_llm_strategy(strategy_name)
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
