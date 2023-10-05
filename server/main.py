from db import MySQL
from time import time
from fastapi import FastAPI, Request, status, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from wakeonlan import send_magic_packet
from asyncio import get_event_loop
from cnf import create_hidden_folder, store
from typing import List
from datetime import datetime
import json
import logging

create_hidden_folder(store)

tm = 5

loop = get_event_loop()
sql = MySQL()
app = FastAPI()

logging.basicConfig(filename='app.log', level=logging.INFO, encoding='utf-8')
active_connections: List[WebSocket] = []


def log_error(client, message: str):
    logging.error(f' {datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")} | '
                  f'{client.host}:{client.port} - {message}')

def log_info(client, message: str):
    logging.info(f' {datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")} | '
                 f'{client.host}:{client.port} - {message}')

@app.get("/")
async def read_root(request: Request):
    ip = request.client.host

    try:
        if await sql.pc_exists(ip):
            await sql.add_pc(ip)
    except Exception as e:
        log_error(request.client, e)

    content = await sql.api_read(ip)
    result = {
        "args": content,
        "run": False,
        "sleep": tm - (time() % tm)
    }

    if content is None:
        return result

    else:
        result["run"] = True
        return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    log_info(websocket.client, "Client connected")

    ip = websocket.client.host

    try:
        while True:
            data = await websocket.receive()
            data = json.loads(data["text"])
            
            if await sql.pc_exists(ip):
                await sql.add_pc(ip, data["mac"])
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        log_info(websocket.client, "Client disconnected")
    finally:
        if websocket.client_state == 0:  # 0 is CONNECTED state
            await websocket.close()

        if active_connections.count(websocket) != 0:
            active_connections.remove(websocket)
            
@app.get('/startup')
async def startup(request: Request):
    s = ''
    for ip, mac in await sql.read_mac_pc_for_lunch((await request.json())["data"]):
        send_magic_packet(mac)
        s += f'Был запущен\: `{ip}`\n'
        
    return {
        "data": s
    }
        

@app.post("/update")
async def update(request: Request):
    for connection in active_connections:
        ip = connection.client.host
        data = (await request.json())["data"]

        if ip in data:
            content = await sql.api_read(ip)
            result = {
                "args": content,
                "run": False
            }

            if content is None:
                pass
            else:
                result["run"] = True
                await connection.send_json(json.dumps(result))
    return "ok"

@app.get('/get_cmd')
async def get_cmd(request: Request, id: int):
    content = await sql.get_cmd_from_id(id)
    return {"data": content}

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
                    f"*{i + 1} connection\:*\n"
                    f"host\:  `{active_connections[i].client.host}`\n "
                    f"port\:  `{active_connections[i].client.port}`\n "
                    f"state\: `{active_connections[i].client_state}`\n"
                    for i in range(len(active_connections))
                ]
            )
        }
    else:
        return {"data": None}

@app.get("/ping_ips")
async def ping_ips():
    if active_connections:
        return {
            "data": [
                (active_connections[i].client.host,
                 f'({i + 1}) {active_connections[i].client.host}')
                for i in range(len(active_connections))
            ]
        }
    else:
        return {"data": None}


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
