from fastapi import FastAPI, Depends,HTTPException,Path
from starlette import status
from sqlalchemy.orm import Session
import models
from models import Todos
from database import engine
from pydantic import BaseModel,Field
from routers import  auth,todos,admin,users

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
