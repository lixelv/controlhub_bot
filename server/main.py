from db import MySQL
from time import time
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse
from asyncio import get_event_loop
from cnf import store
import json
import logging

logging.basicConfig(filename='app.log', level=logging.INFO, encoding='utf-8')

loop = get_event_loop()

app = FastAPI()

with open('main.json', 'r') as file:
    tm = json.load(file)["sleep"]

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
