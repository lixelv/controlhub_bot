import fastapi

app = fastapi.FastAPI()

@app.get('/')
async def read_root():
    return {"Hello": "World"}

@app.post('/')
async def post_root(request: fastapi.Request):
    return await request.json()
