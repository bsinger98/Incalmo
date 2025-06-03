import asyncio
import os
from incalmo.api.server_api import C2ApiClient
from incalmo.core.strategies import llm
from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.services import ConfigService
from incalmo.core.strategies.testers.equifax_test import EquifaxStrategy

TIMEOUT_SECONDS = 75 * 60


async def run_incalmo_strategy(strategy_name=None):
    """Run incalmo with the specified strategy"""

    if not strategy_name:
        # Get strategy from config
        if not strategy_name:
            print("[INFO] No strategy specified, checking config...")
            config = ConfigService().get_config()
            strategy_name = config.strategy

    print(f"[INFO] Starting Incalmo with strategy: {strategy_name}")

    strategy = IncalmoStrategy.build_strategy(strategy_name)
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
