from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.db.database import create_db_and_tables
from app.db.session import async_session_maker
from app.routers.report_router import router as report_router
from app.routers.transaction_router import router as transaction_router
from app.routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(report_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7999, reload=True)
