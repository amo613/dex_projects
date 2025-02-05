# viewmodels/dex_vm.py
import asyncio
import logging
from models.koth_model import KOTHModel
from models.websocket_model import WebsocketModel

logger = logging.getLogger("DexViewModel")

class DexcelerateViewModel:
    def __init__(self):
        self.koth_model = KOTHModel()
        self.service = WebsocketModel(self.koth_model)
        self.tokens = {}

    async def start(self):
        await self.service.connect()
        asyncio.create_task(self.update_data_periodically())

    async def update_data_periodically(self):
        while self.service.running:
            self.tokens = self.service.get_active_data()
            logger.debug("Aktuelle Tokens: %s", self.tokens)
            await asyncio.sleep(10)

    async def stop(self): 
        await self.service.disconnect()
