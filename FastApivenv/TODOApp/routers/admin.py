from fastapi import FastAPI, Depends, HTTPException, status, APIRouter,Path
from sqlalchemy.orm import Session
from models import Todos
from database import engine, SessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user
from fastapi import APIRouter, Depends,HTTPException
from starlette import status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import timedelta,datetime,timezone

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

bcrypt_context= CryptContext(schemes=["bcrypt"],deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')
SECRET_KEY="e8f7c2b92a1d81d9fa07cb793b6a8cfdc6dbac54ed2786a1a3bc1d66d989f9d2"
ALGORITHM="HS256"

class PasswordRequest(BaseModel):
    current_password: str
    new_password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication failed")

    todos = db.query(Todos).all()
    return todos

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id:int=Path(gt=0), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None and user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail="Authentication failed")
    todo_model= db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
