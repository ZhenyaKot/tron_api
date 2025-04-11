from fastapi import FastAPI

from database import create_tables
from handlers import router as tasks_router

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await create_tables()

app.include_router(tasks_router)