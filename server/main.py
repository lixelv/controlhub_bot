from db import MySQL
from time import time
from datetime import datetime
from fastapi import FastAPI, Request, status, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from asyncio import get_event_loop
from cnf import store
from typing import List
import json
import logging

loop = get_event_loop()
app = FastAPI()

logging.basicConfig(filename='app.log', level=logging.INFO, encoding='utf-8')

with open('main.json', 'r') as file:
    tm = json.load(file)["sleep"]

active_connections: List[WebSocket] = []

@app.get("/")
async def read_root(request: Request):
    ip = request.client.host

    try:
        if await sql.pc_exists(ip):
            await sql.add_pc(ip)
    except Exception as e:
        print(e)

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
    try:
        while True:
            data = await websocket.receive_json()
            # ... handle incoming messages ...
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Client disconnected")
    finally:
        if websocket.client_state == 0:  # 0 is CONNECTED state
            await websocket.close()

        if active_connections.count(websocket) != 0:
            active_connections.remove(websocket)


@app.get("/update")
async def update():
    for connection in active_connections:
        ip = connection.client.host

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
@app.get("/sleep")
async def sleep_timing():
    result = {"sleep": tm}
    return result

@app.get("/download/{filename}")
async def download(filename: str):
    return FileResponse(f'{store}/{filename}', media_type="application/octet-stream")


@app.post("/success", status_code=status.HTTP_204_NO_CONTENT)
async def client_success(request: Request, task: dict):
    logging.info(f'{datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")} | {request.client.host} - {task["task"]}')


@app.post("/error", status_code=status.HTTP_204_NO_CONTENT)
async def client_error(request: Request, error: dict):
    logging.error(f'{datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")} | {request.client.host} - {error["error"]}')

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
