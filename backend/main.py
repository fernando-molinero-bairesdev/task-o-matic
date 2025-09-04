
from fastapi import FastAPI

from routers.task_router import router as task_router
from routers.user_router import router as user_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to Task-O-Matic backend!"}

app.include_router(task_router)
app.include_router(user_router)
