from fastapi import FastAPI
from fastapi.responses import FileResponse
from os import path
import os

app = FastAPI()

@app.get("/favicon.ico")
async def read_favicon():
    return FileResponse('icon.ico')

@app.get("/download/{filename}")
async def download(filename: str):
    return FileResponse(f'files/{filename}', media_type="application/octet-stream")
