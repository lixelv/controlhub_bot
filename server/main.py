from db import SQLite
import json
from fastapi import FastAPI, Request, status
import logging

logging.basicConfig(level=logging.ERROR, filename='app.log')
sql = SQLite('db.db')
app = FastAPI()
app.add_event_handler('startup', sql.init)

with open('main.json', 'r') as file:
    default = json.load(file)

@app.get("/")
async def read_root(request: Request):
    ip = request.client.host

    if await sql.pc_exists(ip):
        await sql.add_pc(ip)

    content = await sql.api_read(ip)

    if content is None:
        return default

    else:
        result = {"args": content}
        result.update(default)
        result["run"] = True
        return result

@app.get("/success", status_code=status.HTTP_204_NO_CONTENT)
async def client_success(request: Request, task: str):
    logging.info(f'SUCCESS:     {request.client.host} - {task}')


@app.post("/error", status_code=status.HTTP_204_NO_CONTENT)
async def client_error(request: Request, error: str):
    logging.error(f'ERROR:     {request.client.host} - {error}')

@app.on_event("shutdown")
async def shutdown_event():
    if sql is not None:
        await sql.close()
