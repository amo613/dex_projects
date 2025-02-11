import asyncio
import logging
import aiohttp
from models.koth_model import KOTHModel
from models.websocket_model import WebsocketModel

logger = logging.getLogger("DexViewModel")

class DexcelerateViewModel:
    def __init__(self):
        self.koth_model = KOTHModel()
        self.service = WebsocketModel(self.koth_model)
        self.tokens = {}
        self.top_holders = []             
        self.selected_token = None        
        self.selected_token_creator = None 
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

    async def fetch_top_holders(self, mint: str) -> list:
        rpc_url = "https://rpc.shyft.to?api_key=MXDr4p_jJq0eikqs"
        print(f"Fetching largest accounts for mint: {mint}") 

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenLargestAccounts",
            "params": [mint]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(rpc_url, json=payload) as resp:
                result = await resp.json()
                print("getTokenLargestAccounts result:", result)  
                if "error" in result:
                    print("Error in getTokenLargestAccounts:", result["error"])
                    return []
                largest = result["result"]["value"]

        payload_supply = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenSupply",
            "params": [mint]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(rpc_url, json=payload_supply) as resp:
                supply_result = await resp.json()
                print("getTokenSupply result:", supply_result)  
                if "error" in supply_result:
                    print("Error in getTokenSupply:", supply_result["error"])
                    return []
                supply_info = supply_result["result"]["value"]
                supply = supply_info["amount"]
                decimals = supply_info["decimals"]

        total_supply = float(supply) / (10 ** decimals) if float(supply) != 0 else 0
        holders = []
        for account in largest:
            amount = float(account["amount"]) / (10 ** decimals)
            percentage = (amount / total_supply * 100) if total_supply != 0 else 0
            holders.append({
                "address": account["address"],
                "amount": amount,
                "percentage": f"{percentage:.2f}%"
            })
        holders.sort(key=lambda x: float(x["percentage"].replace('%','')), reverse=True)
        return holders[:20]


    async def load_top_holders(self, mint: str):
        """
        Lädt die Top-20-Halter und alle relevanten Adressen
        """
        holders = await self.fetch_top_holders(mint)
        self.top_holders = holders
        self.selected_token = mint
        
        token_data = self.tokens.get(mint, {})
        # Neue Attribute für Rollen wie Dev, Bonding curve etc.
        self.selected_token_creator = token_data.get("creator")
        self.bonding_curve = token_data.get("bonding_curve")
        self.associated_bonding_curve = token_data.get("associated_bonding_curve")


