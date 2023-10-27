import json
import logging

from fastapi import FastAPI, Request, status, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from cnf import create_hidden_folder, store
from wakeonlan import send_magic_packet
from asyncio import get_event_loop
from datetime import datetime
from typing import Dict
from time import time
from db import MySQL

create_hidden_folder(store)

tm = 5

loop = get_event_loop()
sql = MySQL()
app = FastAPI()

logging.basicConfig(filename='app.log', level=logging.INFO, encoding='utf-8')
active_connections: Dict[str, WebSocket] = {}


def log_error(client, message: str):
    logging.error(f' {datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")} | '
                  f'{client.host}:{client.port} - {message}')

def log_info(client, message: str):
    logging.info(f' {datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")} | '
                 f'{client.host}:{client.port} - {message}')

@app.get("/")
async def read_root(request: Request):
    ip = request.client.host
    return {"data": {"ip": ip}}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    mac = ''

    try:
        while True:
            data = await websocket.receive()
            print(data)
            if data.get('text') is not None:
                data = json.loads(data["text"])

                mac = data["mac"]

                active_connections.update({mac: websocket})
                log_info(websocket.client, "Client connected")
                
                new_pc = await sql.pc_exists(mac)

                if new_pc:
                    await sql.add_pc(mac)
            
            else:
                pass


    except WebSocketDisconnect:
        del active_connections[mac]
        log_info(websocket.client, "Client disconnected")
        
    except Exception as e:
        log_info(websocket.client, str(e))

    finally:
        if websocket.client_state == 0:  # 0 is CONNECTED state
            await websocket.close()

        if active_connections.get(mac) is not None:
            del active_connections[mac]
        

@app.post("/update")
async def update(request: Request):
    data = await request.json()
    print(active_connections)
    if data.get("data"):
        for mac in await sql.read_mac_pc_for_lunch(data.get("mac")):
            print(f"Запущен: {mac[0].replace(':', '-').upper()}")
            send_magic_packet(mac[0].replace(':', '-').upper())
    else:       
        for mac in active_connections.keys() if data.get('mac') == 'all' else [data.get('mac')]:
            
            content = await sql.api_read(mac)
            
        
            result = {
                "args": content,
                "run": False
            }
            if content is None or mac not in active_connections.keys():
                pass
            
            else:
                result["run"] = True
                websocket = active_connections[mac]
                await websocket.send_json(json.dumps(result))
    return "ok"

@app.get("/sleep")
async def sleep_timing():
    result = {"sleep": tm}
    return result


@app.get("/download/{filename}")
async def download(filename: str):
    return FileResponse(f'{store}/{filename}', media_type="application/octet-stream")


@app.get("/ping_websockets")
async def ping_websockets():
    if active_connections:
        return {
            "data": "\n".join(
                [
                    f"*connection\:*\n"
                    f"mac\: {mac}\n"
                    f"host\:  `{active_connections[mac].client.host}`\n"
                    f"port\:  `{active_connections[mac].client.port}`\n"
                    f"state\: `{active_connections[mac].client_state}`\n"
                    for mac in active_connections.keys()
                ]
            )
        }
    else:
        return {"data": None}

@app.get("/ping_macs")
async def ping_macs(request: Request):
    request_data = (await request.json()).get("data")
    if request_data == "startup":
        return {
            "data": [
                (mac[0], mac[0]) for mac in await sql.read_mac_pc_for_lunch('all')
            ]
        }
    
    elif active_connections:
        return {
            "data": [
                (mac, mac) for mac in active_connections.keys()
            ]
        }
    else:
        return {"data": None}

@app.get('/check')
async def check_websockets():
    return {"data": {mac: websocket.client.host for mac, websocket in active_connections.items()}}  # active_connections

@app.post("/success", status_code=status.HTTP_204_NO_CONTENT)
async def client_success(request: Request, task: dict):
    log_info(request.client, task["task"])


@app.post("/error", status_code=status.HTTP_204_NO_CONTENT)
async def client_error(request: Request, error: dict):
    log_error(request.client, error["error"])


@app.on_event("startup")
async def startup():
    global sql
    sql = await MySQL.create(loop=loop)


@app.on_event("shutdown")
async def shutdown():
    await sql.close()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=True, loop=loop)
