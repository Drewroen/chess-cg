#!/usr/bin/env python3

import asyncio
import obj.chess as chess
from websockets.asyncio.server import serve


DEV_MODE = True


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


async def main():
    print("Server started")
    board = chess.Board()
    board.reset_board()
    board.print_board()
    async with serve(echo, "localhost", 8765):
        try:
            await asyncio.get_running_loop().create_future()  # run forever
        except asyncio.exceptions.CancelledError as e:
            if DEV_MODE:
                print("DEVELOPMENT - Restarting")
            else:
                raise e
        except Exception as e:
            raise e


asyncio.run(main())
