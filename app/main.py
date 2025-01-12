from fastapi import FastAPI,APIRouter
from database import engine
from models import Base
from schemas.user import UserPostRequest, UserInDB
from routers import user
app = FastAPI(
    title="Example API",
    description="This is an example API of FastAPI",
    contact={
        "name": "Masaki Yoshiiwa",
        "email": "masaki.yoshiiwa@gmail.com",
    },
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
)
Base.metadata.create_all(bind=engine)

router = APIRouter()

app.include_router(user.router, prefix="/api/users")
