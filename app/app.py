from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def hello() -> dict[str, str]:
    return {"message": "Hello World"}
