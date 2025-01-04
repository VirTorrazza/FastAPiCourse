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
    prefix='/user',
    tags=['user']
)

bcrypt_context= CryptContext(schemes=["bcrypt"],deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')
SECRET_KEY="e8f7c2b92a1d81d9fa07cb793b6a8cfdc6dbac54ed2786a1a3bc1d66d989f9d2"
ALGORITHM="HS256"

class PasswordRequest(BaseModel):
    current_password: str
    new_password: str =Field(min_length=8)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    user_info = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user_info


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(passwordrequest: PasswordRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(passwordrequest.current_password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    hashed_new_password = bcrypt_context.hash(passwordrequest.new_password)
    db_user.hashed_password = hashed_new_password
    db.commit()
    db.refresh(db_user)

    return {"message": "Password changed successfully"}
