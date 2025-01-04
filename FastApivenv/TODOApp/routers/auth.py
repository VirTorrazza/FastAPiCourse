from fastapi import APIRouter, Depends,HTTPException,Path
from starlette import status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import timedelta,datetime,timezone

router= APIRouter(
    prefix='/auth',
    tags=['auth']
)
bcrypt_context= CryptContext(schemes=["bcrypt"],deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')
SECRET_KEY="e8f7c2b92a1d81d9fa07cb793b6a8cfdc6dbac54ed2786a1a3bc1d66d989f9d2"
ALGORITHM="HS256"


class CreateUserRequest(BaseModel): #request model
    username:str
    email:str
    first_name:str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token:str
    token_type:str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username ==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role':role}
    expires = datetime.now(timezone.utc) + expires_delta  # Fixed typo: 'timzone' -> 'timezone'
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str= payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return {"username": username, "id": user_id, "user_role":user_role}

    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")


@router.post("/",status_code=status.HTTP_201_CREATED)
async def get_user(create_user_request: CreateUserRequest,db: Session = Depends(get_db)):
    create_user_model= Users(
        email=create_user_request.email,
        username =create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        role =create_user_request.role
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token=create_access_token(user.username,user.id, user.role,timedelta(minutes=20))
    return {"access_token":token, "token_type":"bearer"}