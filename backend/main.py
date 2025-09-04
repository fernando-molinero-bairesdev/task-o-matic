from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.task_router import router as task_router
from routers.user_router import router as user_router
from routers.auth_router import router as auth_router

app = FastAPI(title="Task-O-Matic API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Task-O-Matic API"}

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)
