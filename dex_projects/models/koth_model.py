# models/koth_model.py
import aiohttp
import logging

logger = logging.getLogger("KOTHModel")

class KOTHModel:
    def __init__(self):
        self.url = "https://frontend-api-v3.pump.fun/coins/king-of-the-hill?includeNsfw=True"

    async def fetch_data(self) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug("Fetched KOTH Data: %s", data)
                        return data
                    else:
                        logger.error("Fehler beim Abrufen des KOTH: Statuscode %s", response.status)
                        return {}
        except Exception as e:
            logger.error("KOTH Fetch Exception: %s", e)
            return {}
