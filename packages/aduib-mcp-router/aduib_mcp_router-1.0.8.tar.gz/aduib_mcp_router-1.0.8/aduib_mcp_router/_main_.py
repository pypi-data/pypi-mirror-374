import asyncio
from multiprocessing import freeze_support
from aduib_mcp_router.app import main
from aduib_mcp_router.utils import AsyncUtils

if __name__ == '__main__':
    freeze_support()
    AsyncUtils.run_async(main())