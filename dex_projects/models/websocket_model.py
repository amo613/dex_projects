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
                                print(f"Raydium Pool gefunden: {raydium_pool}")
                                return raydium_pool
                            else:
                                logger.info("Raydium Pool noch nicht verfügbar für mint %s", mint)
                                print(f"Raydium Pool noch nicht verfügbar für mint {mint}")
                        else:
                            logger.error("Fehler beim Abrufen des alternativen Endpunkts: Status %s", response.status)
                            print(f"Fehler beim Abrufen des alternativen Endpunkts: Status {response.status}")
            except Exception as e:
                logger.error("Fehler beim Polling des alternativen Endpunkts: %s", e)
                print(f"Fehler beim Polling des alternativen Endpunkts: {e}")
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
                print(f"Subscribe-Pair-Stats gesendet: mint: {mint}, pair: {pair}")
            else:
                logger.error("Kein Websocket vorhanden, um subscribe-pair-stats zu senden.")
                print("Kein Websocket vorhanden, um subscribe-pair-stats zu senden.")
        except Exception as e:
            logger.error("Fehler beim Senden der subscribe-pair-stats: %s", e)
            print(f"Fehler beim Senden der subscribe-pair-stats: {e}")

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
                    print("Kein mint in den KOTH-Daten gefunden.")
                    await asyncio.sleep(20)
                    continue

                if (self.current_koth_data is None) or (mint != self.current_koth_data.get("mint")):
                    logger.info("Neuer KOTH erkannt: %s", mint)
                    print(f"Neuer KOTH erkannt: {mint}")
                    self.current_koth_data = token_data
                    # Zunächst wird die bonding_curve als Pair genutzt, weil wir sonst kein Pair haben
                    pair = token_data.get("bonding_curve")
                    if token_data.get("migrationProgress", 0) == 100:
                        logger.info("MigrationProgress 100 für mint %s, warte 1 Minute und poll dann Raydium Pool...", mint)
                        print(f"MigrationProgress 100 für mint {mint}, warte 1 Minute und poll dann Raydium Pool...")
                        await asyncio.sleep(60)
                        # Nach dem Migrieren warten wir 60 Sekunden, bevor wir den Raydium Pool pollen
                        pair = await self.poll_for_raydium_pool(mint)
                    if pair:
                        self.active_subscriptions[mint] = pair
                        await self.subscribe_pair_stats(mint, pair)
                        self.cache.add("subscription_" + mint, {"mint": mint, "pair": pair})
                    else:
                        logger.error("Kein gültiger Pair-Wert für mint %s ermittelt.", mint)
                        print(f"Kein gültiger Pair-Wert für mint {mint} ermittelt.")
                else:
                    if token_data.get("migrationProgress", 0) == 100:
                        current_pair = self.active_subscriptions.get(mint)
                        if current_pair and current_pair == token_data.get("bonding_curve"):
                            logger.info("Migration abgeschlossen für mint %s. Starte Polling für Raydium Pool...", mint)
                            print(f"Migration abgeschlossen für mint {mint}. Starte Polling für Raydium Pool...")
                            new_pair = await self.poll_for_raydium_pool(mint)
                            if new_pair and new_pair != current_pair:
                                logger.info("Neuer Raydium Pool für mint %s: %s", mint, new_pair)
                                print(f"Neuer Raydium Pool für mint {mint}: {new_pair}")
                                self.active_subscriptions[mint] = new_pair
                                await self.subscribe_pair_stats(mint, new_pair)
                                self.cache.add("subscription_" + mint, {"mint": mint, "pair": new_pair})
                await asyncio.sleep(20)
            except Exception as e:
                logger.error("KOTH Tracking Error: %s", e)
                print(f"KOTH Tracking Error: {e}")
                await asyncio.sleep(5)

    async def _process_messages(self) -> None:
        try:
            while self.running and self.websocket is not None:
                message = await self.websocket.recv()
                data = json.loads(message)
                logger.debug("Nachricht empfangen: %s", data)
                print(f"Nachricht empfangen: {data}")
                event = data.get("event")
                if event == "pair-stats":
                    await self._handle_pair_stats_update(data)
                else:
                    await self.on_message(data)
        except websockets.exceptions.ConnectionClosed as e:
            logger.error("Websocket closed: %s", e)
            print(f"Websocket closed: {e}")
            await self.conn_manager.handle_reconnect()
        except Exception as e:
            logger.error("Error in _process_messages: %s", e)
            print(f"Error in _process_messages: {e}")
            await self.conn_manager.handle_reconnect()

    async def _handle_pair_stats_update(self, data: dict) -> None:
        try:
            payload = data.get("data", {})
            pair_info = payload.get("pair", {})
            stats_info = payload.get("pairStats", {})
            pair_address = pair_info.get("pairAddress")
            found_mint = None
            for mint, subscribed_pair in self.active_subscriptions.items():
                if subscribed_pair == pair_address:
                    found_mint = mint
                    break
            if not found_mint:
                logger.error("Kein passender Token für Pair-Stats gefunden: %s", data)
                print(f"Kein passender Token für Pair-Stats gefunden: {data}")
                return

            logger.info("Token %s Update: Price: %s, Market Cap: %s, Liquidity: %s",
                        found_mint, pair_info.get("pairPrice1Usd"), pair_info.get("pairMarketcapUsd"), pair_info.get("pairReserves0Usd"))
            print(f"Token {found_mint} Update: Price: {pair_info.get('pairPrice1Usd')}, Market Cap: {pair_info.get('pairMarketcapUsd')}, Liquidity: {pair_info.get('pairReserves0Usd')}")
            combined_data = {"pair": pair_info, "pairStats": stats_info}
            self.cache.add("pair_stats_" + found_mint, combined_data)
        except Exception as e:
            logger.error("Fehler beim Verarbeiten der Pair-Stats: %s", e)
            print(f"Fehler beim Verarbeiten der Pair-Stats: {e}")

    async def on_message(self, data: dict) -> None:
        logger.info("Processing message (nicht speziell verarbeitet): %s", data)
        print(f"Processing message (nicht speziell verarbeitet): {data}")

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
            print("Websocket-Verbindung aufgebaut.")
            self.worker_task = asyncio.create_task(self._process_messages())
            asyncio.create_task(self.track_koth())
        except Exception as e:
            logger.error("Connection Error: %s", e)
            print(f"Connection Error: {e}")
            await self.conn_manager.handle_reconnect()

    async def disconnect(self) -> None:
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Websocket-Verbindung geschlossen.")
                print("Websocket-Verbindung geschlossen.")
            except Exception as e:
                logger.error("Fehler beim Schließen des Websockets: %s", e)
                print(f"Fehler beim Schließen des Websockets: {e}")
        if self.worker_task:
            self.worker_task.cancel()

    def get_active_data(self) -> Dict[str, Any]:
        data = {}
        for mint in self.active_subscriptions.keys():
            stats = self.cache.get("pair_stats_" + mint)
            if stats is None:
                stats = {}
            data[mint] = stats
        return data
