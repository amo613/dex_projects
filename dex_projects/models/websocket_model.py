# models/websocket_model.py
import asyncio
import json
import logging
import aiohttp
import websockets
from typing import Any, Optional, Dict 
from services.connection_manager import ConnectionManager
from services.smart_cache import SmartCache

logger = logging.getLogger("WebsocketModel")

class WebsocketModel:
    def __init__(self, koth_model):
        self.uri = "wss://api-rs.dexcelerate.com/ws"
        self.headers = {"Origin": "https://app.dexcelerate.com"}
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.current_koth_data: Optional[Dict[str, Any]] = None
        # active subscriptions speichert für jeden mint den aktuell verwendeten Pair in einem Dict
        self.active_subscriptions: Dict[str, str] = {}
        self.cache = SmartCache(max_size=500)
        self.worker_task: Optional[asyncio.Task] = None
        self.koth_model = koth_model

        self.conn_manager = ConnectionManager(self)

    async def poll_for_raydium_pool(self, mint: str) -> Optional[str]:
        alt_url = f"https://frontend-api.pump.fun/coins/{mint}?sync=true"
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(alt_url, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            raydium_pool = data.get("raydium_pool")
                            if raydium_pool:
                                logger.info("Raydium Pool gefunden: %s", raydium_pool)
                                return raydium_pool
                            else:
                                logger.info("Raydium Pool noch nicht verfügbar für mint %s", mint)
                        else:
                            logger.error("Fehler beim Abrufen des alternativen Endpunkts: Status %s", response.status)
            except Exception as e:
                logger.error("Fehler beim Polling des alternativen Endpunkts: %s", e)
            await asyncio.sleep(20)

    async def subscribe_pair_stats(self, mint: str, pair: str) -> None:
        subscription_data = {
            "event": "subscribe-pair-stats",
            "data": {
                "pair": pair,
                "chain": "SOL",
                "routerType": "RAYDIUM_CLMM",
                "token": mint
            }
        }
        try:
            if self.websocket is not None:
                message = json.dumps(subscription_data)
                await self.websocket.send(message)
                logger.info("Subscribe-Pair-Stats gesendet: mint: %s, pair: %s", mint, pair)
            else:
                logger.error("Kein Websocket vorhanden, um subscribe-pair-stats zu senden.")
        except Exception as e:
            logger.error("Fehler beim Senden der subscribe-pair-stats: %s", e)

    async def track_koth(self) -> None:
        while self.running:
            try:
                token_data = await self.koth_model.fetch_data()
                if not token_data:
                    await asyncio.sleep(20)
                    continue

                mint = token_data.get("mint")
                if not mint:
                    logger.error("Kein mint in den KOTH-Daten gefunden.")
                    await asyncio.sleep(20)
                    continue

                if (self.current_koth_data is None) or (mint != self.current_koth_data.get("mint")):
                    logger.info("Neuer KOTH erkannt: %s", mint)
                    self.current_koth_data = token_data
                    # Zunächst wird die bonding_curve als Pair genutzt, weil wir kein Pair sonst haben
                    pair = token_data.get("bonding_curve")
                    if token_data.get("migrationProgress", 0) == 100:
                        logger.info("MigrationProgress 100 für mint %s, warte 1 Minute und poll dann Raydium Pool...", mint)
                        await asyncio.sleep(60)
                        # Nach dem migraten warten wir zunächst 60 Sekunden bevor wir den Raydium Pool pollen
                        pair = await self.poll_for_raydium_pool(mint)
                    if pair:
                        self.active_subscriptions[mint] = pair
                        await self.subscribe_pair_stats(mint, pair)
                        self.cache.add("subscription_" + mint, {"mint": mint, "pair": pair})
                    else:
                        logger.error("Kein gültiger Pair-Wert für mint %s ermittelt.", mint)
                else:
                    if token_data.get("migrationProgress", 0) == 100:
                        current_pair = self.active_subscriptions.get(mint)
                        if current_pair and current_pair == token_data.get("bonding_curve"):
                            logger.info("Migration abgeschlossen für mint %s. Starte Polling für Raydium Pool...", mint)
                            new_pair = await self.poll_for_raydium_pool(mint)
                            if new_pair and new_pair != current_pair:
                                logger.info("Neuer Raydium Pool für mint %s: %s", mint, new_pair)
                                self.active_subscriptions[mint] = new_pair
                                await self.subscribe_pair_stats(mint, new_pair)
                                self.cache.add("subscription_" + mint, {"mint": mint, "pair": new_pair})
                await asyncio.sleep(20)
            except Exception as e:
                logger.error("KOTH Tracking Error: %s", e)
                await asyncio.sleep(5)

    async def _process_messages(self) -> None:
        try:
            while self.running and self.websocket is not None:
                message = await self.websocket.recv()
                data = json.loads(message)
                logger.debug("Nachricht empfangen: %s", data)
                event = data.get("event")
                if event == "pair-stats":
                    await self._handle_pair_stats_update(data)
                else:
                    await self.on_message(data)
        except websockets.exceptions.ConnectionClosed as e:
            logger.error("Websocket closed: %s", e)
            await self.conn_manager.handle_reconnect()
        except Exception as e:
            logger.error("Error in _process_messages: %s", e)
            await self.conn_manager.handle_reconnect()

    async def _handle_pair_stats_update(self, data: dict) -> None:
        try:
            payload = data.get("data", {})
            pair_data = payload.get("pair", {})
            mint = payload.get("token")
            if not mint or not pair_data:
                logger.error("Ungültige Pair-Stats-Antwort: %s", data)
                return

            price = pair_data.get("pairPrice1Usd")
            marketcap = pair_data.get("pairMarketcapUsd")
            liquidity = pair_data.get("pairReserves0Usd")
            logger.info("Token %s Update: Price: %s, Market Cap: %s, Liquidity: %s",
                        mint, price, marketcap, liquidity)
            self.cache.add("pair_stats_" + mint, pair_data)
        except Exception as e:
            logger.error("Fehler beim Verarbeiten der Pair-Stats: %s", e)

    async def on_message(self, data: dict) -> None:
        logger.info("Processing message (nicht speziell verarbeitet): %s", data)

    async def connect(self) -> None:
        try:
            self.websocket = await websockets.connect(
                self.uri,
                origin=self.headers.get("Origin"),
                ping_interval=20,
                ping_timeout=20
            )
            self.running = True
            logger.info("Websocket-Verbindung aufgebaut.")
            self.worker_task = asyncio.create_task(self._process_messages())
            asyncio.create_task(self.track_koth())
        except Exception as e:
            logger.error("Connection Error: %s", e)
            await self.conn_manager.handle_reconnect()

    async def disconnect(self) -> None:
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Websocket-Verbindung geschlossen.")
            except Exception as e:
                logger.error("Fehler beim Schließen des Websockets: %s", e)
        if self.worker_task:
            self.worker_task.cancel()

    def get_active_data(self) -> Dict[str, Any]:
        data = {}
        for mint in self.active_subscriptions.keys():
            sub = self.cache.get("subscription_" + mint)
            stats = self.cache.get("pair_stats_" + mint)
            data[mint] = {"subscription": sub, "pair_stats": stats}
        return data
