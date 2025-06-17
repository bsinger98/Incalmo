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
        raise Exception("No strategy specified")

    print(f"[INFO] Starting Incalmo with strategy: {strategy_name}")

    print(f"[DEBUG] Building strategy...")
    strategy = IncalmoStrategy.build_strategy(strategy_name)

    print(f"[DEBUG] Initializing strategy...")
    await strategy.initialize()

    print(f"[DEBUG] Strategy initialized, starting main loop...")
    start_time = asyncio.get_event_loop().time()

    while True:
        print(
            f"[DEBUG] Running strategy: {strategy.__class__.__name__}"
        )  # Regular print
        result = await strategy.main()
        if result:
            print(f"[DEBUG] Strategy completed with result: {result}")
            break
        if asyncio.get_event_loop().time() - start_time > TIMEOUT_SECONDS:
            print(f"[DEBUG] Strategy timed out after {TIMEOUT_SECONDS} seconds")
            break
        await asyncio.sleep(0.5)

    print(f"[INFO] Strategy {strategy_name} completed")
