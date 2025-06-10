import asyncio
import json
import ssl
import websockets
from collections import deque
from typing import Callable

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class OBISession:
    def __init__(self, symbol: str, depth_levels: int = 10, trade_window: int = 60, callback: Callable[[str, float, float], None] = None):
        self.symbol = symbol.lower()
        self.depth_levels = depth_levels
        self.trade_window = trade_window
        self.callback = callback

        self.buy_volume = 0.0
        self.sell_volume = 0.0
        self.trade_history = deque()

    def calculate_obi(self, bids, asks):
        bid_volume = sum(float(b[1]) for b in bids[:self.depth_levels])
        ask_volume = sum(float(a[1]) for a in asks[:self.depth_levels])
        if bid_volume + ask_volume == 0:
            return 0.0
        return (bid_volume - ask_volume) / (bid_volume + ask_volume)

    async def obi_stream(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth10@100ms"
        async with websockets.connect(url, ssl=ssl_context) as ws:
            async for message in ws:
                data = json.loads(message)
                bids = data.get('bids', [])
                asks = data.get('asks', [])
                obi = self.calculate_obi(bids, asks)
                delta = self.buy_volume - self.sell_volume
                if self.callback:
                    self.callback(self.symbol.upper(), obi, delta)

    async def trade_stream(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@aggTrade"
        async with websockets.connect(url, ssl=ssl_context) as ws:
            async for message in ws:
                data = json.loads(message)
                qty = float(data['q'])
                is_buyer_maker = data['m']
                now = asyncio.get_event_loop().time()

                if is_buyer_maker:
                    self.sell_volume += qty
                    self.trade_history.append((now, qty, False))
                else:
                    self.buy_volume += qty
                    self.trade_history.append((now, qty, True))

                while self.trade_history and (now - self.trade_history[0][0] > self.trade_window):
                    _, qty_old, is_buy_old = self.trade_history.popleft()
                    if is_buy_old:
                        self.buy_volume -= qty_old
                    else:
                        self.sell_volume -= qty_old

    async def run(self):
        await asyncio.gather(self.obi_stream(), self.trade_stream())