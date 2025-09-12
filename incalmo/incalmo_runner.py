import asyncio
from incalmo.core.strategies.strategy_factory import StrategyFactory
from config.attacker_config import AttackerConfig

TIMEOUT_SECONDS = 75 * 60

strategy_factory = StrategyFactory()


async def run_incalmo_strategy(config: AttackerConfig, task_id: str):
    """Run incalmo with the specified strategy"""
    strategy = strategy_factory.build_strategy(config, task_id)

    await strategy.initialize()

    start_time = asyncio.get_event_loop().time()

    while True:
        result = await strategy.main()
        if result:
            break
        if asyncio.get_event_loop().time() - start_time > TIMEOUT_SECONDS:
            break
        await asyncio.sleep(0.5)
