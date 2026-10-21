from fastapi import FastAPI

app = FastAPI(title="Trading Platform API")


@app.get("/")
async def root():
    return {"message": "Trading Platform API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
