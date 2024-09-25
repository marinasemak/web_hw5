import asyncio
import logging

import aiohttp
import names
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from functions import main as extended_command

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects")

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} disconnects")

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    @staticmethod
    async def handle_command():
        """
        handle command "exchange" from input field
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5",
                ssl=False,
            ) as response:
                result = await response.json()
            return result

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            try:
                if message == "exchange":
                    result = await self.handle_command()
                    for el in result:
                        await self.send_to_clients(f"{el}\n")
                elif message.split()[0] == "exchange" and message.split()[1].isdigit():
                    result = await extended_command(
                        int(message.split()[1]), currencies=None
                    )
                    for el in result:
                        await self.send_to_clients(f"{el}\n")
                else:
                    await self.send_to_clients(f"{ws.name}: {message}")
            except IndexError:
                await self.send_to_clients(f"Enter some text or command")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, "localhost", 8080):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
