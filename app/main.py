from fastapi import FastAPI,APIRouter
from fastapi.responses import FileResponse
from database import engine
from models import Base
from schemas.user import UserPostRequest
from routers import user,chat, report, preparation, chatroom
from fastapi.middleware.cors import CORSMiddleware
from database import initialize_database


app = FastAPI(
    title="Example API",
    description="This is an example API of FastAPI",
    contact={
        "name": "Masaki Yoshiiwa",
        "email": "masaki.yoshiiwa@gmail.com",
    },
    
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
)
origin = {"http://localhost:5173"}

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

initialize_database()

@app.get("/")
def serve_html():
    return FileResponse("test.html")
app.include_router(user.router, prefix="/api/users")
app.include_router(report.router, prefix="/api/reports")
app.include_router(preparation.router, prefix="/api/preparations")
app.include_router(chat.router, prefix="/api/chats")
app.include_router(chatroom.router, prefix="/chatrooms", tags=["Chatrooms"])