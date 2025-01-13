from fastapi import FastAPI,APIRouter
from fastapi.responses import FileResponse
from database import engine
from models import Base
from schemas.user import UserPostRequest
from routers import user,chat, ai
from fastapi.middleware.cors import CORSMiddleware

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
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],  
    allow_headers=["*"],  
)
router = APIRouter()
@app.get("/")
def serve_html():
    return FileResponse("test.html")
app.include_router(user.router, prefix="/api/users")
app.include_router(chat.router, prefix="/api/chats")
app.include_router(ai.router, prefix="/api/ai")  # AI 라우터 등록
