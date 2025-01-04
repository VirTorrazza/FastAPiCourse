from fastapi import FastAPI, Depends,HTTPException,Path,APIRouter
from starlette import status
from sqlalchemy.orm import Session
import models
from models import Todos
from database import engine, SessionLocal
from pydantic import BaseModel,Field
from .auth import get_current_user

router = APIRouter()
models.Base.metadata.create_all(bind=engine)
user_dependency = Depends(get_current_user)

class TodoRequest(BaseModel):
    title:str= Field(min_length=3)
    description:str=Field(min_length=3,max_length=100)
    priority:int=Field(gt=0,lt=6)
    complete:bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(db: Session = Depends(get_db),user: dict = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Todos).filter(Todos.owner_id== user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(todo_id: int =Path (gt=0),user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request: TodoRequest, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = Todos(**todo_request.dict(), owner_id=user['id'])

    try:
        db.add(todo_model)
        db.commit()
        db.refresh(todo_model)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create Todo item")

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(todo_request: TodoRequest, user: dict = Depends(get_current_user),todo_id: int =Path(gt=0), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model= db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id==user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")
    todo_model.title=todo_request.title
    todo_model.description=todo_request.description
    todo_model.priority=todo_request.priority
    todo_model.complete=todo_request.complete


    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id:int =Path(gt=0),user: dict = Depends(get_current_user),db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get('id')).delete()
    db.commit()
