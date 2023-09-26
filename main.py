import aiofiles
import json
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    async with aiofiles.open('main.json', mode='r', encoding='utf-8') as file:
        content = await file.read()
        return json.loads(content)
