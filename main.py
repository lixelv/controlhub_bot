from fastapi import FastAPI
from db import SQLite
import json

sql = SQLite('db.db')
app = FastAPI()


with open('main.json', 'r') as file:
    default = json.load(file)

@app.get("/")
async def read_root():
    content = sql.api_read()
    if content is None:
        return default

    else:
        result = {"args": content}
        result.update(default)
        result["run"] = True
        return result
