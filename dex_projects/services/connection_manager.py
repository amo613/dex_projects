# services/connection_manager.py
import asyncio
import logging

logger = logging.getLogger("ConnectionManager")

class ConnectionManager:
    def __init__(self, ws_instance, reconnect_delay: int = 5):
        self.ws_instance = ws_instance
        self.reconnect_delay = reconnect_delay

    async def handle_reconnect(self):
        logger.info("Reconnect requested. Warte %s Sekunden...", self.reconnect_delay)
        await asyncio.sleep(self.reconnect_delay)
        try:
            await self.ws_instance.connect()
        except Exception as e:
            logger.error("Reconnect failed: %s", e)
            await self.handle_reconnect()
