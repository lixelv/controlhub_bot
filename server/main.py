from db import SQLite
from time import time
from fastapi import FastAPI, Request, status
import json
import logging

logging.basicConfig(level=logging.ERROR, filename='app.log')
sql = SQLite('db.db')
app = FastAPI()

app.add_event_handler('startup', sql.init)
app.add_event_handler('shutdown', sql.close)

with open('main.json', 'r') as file:
    default = json.load(file)

@app.get("/")
async def read_root(request: Request):
    tm = default["sleep"]

    ip = request.client.host

    if await sql.pc_exists(ip):
        await sql.add_pc(ip)

    content = await sql.api_read(ip)

    result = {"args": content}
    result.update(default)
    result["sleep"] = tm - (time() % tm)

    if content is None:
        return result

    else:
        result["run"] = True

        return result

@app.get("/sleep")
async def sleep_timing():
    tm = default["sleep"]
    result = default.copy()
    result["sleep"] = tm - (time() % tm)
    return result


@app.get("/success", status_code=status.HTTP_204_NO_CONTENT)
async def client_success(request: Request, task: str):
    logging.info(f'SUCCESS:     {request.client.host} - {task}')


@app.post("/error", status_code=status.HTTP_204_NO_CONTENT)
async def client_error(request: Request, error: str):
    logging.error(f'ERROR:     {request.client.host} - {error}')
