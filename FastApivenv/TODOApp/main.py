from fastapi import FastAPI, Depends,HTTPException,Path
from starlette import status
from sqlalchemy.orm import Session
import models
from models import Todos
from database import engine, SessionLocal
from pydantic import BaseModel,Field

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

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

@app.get("/",status_code=status.HTTP_200_OK)
async def read_all(db: Session = Depends(get_db)):
    return db.query(Todos).all()  # Fetch all records from Todos table



@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(todo_id: int =Path (gt=0), db: Session = Depends(get_db)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request:TodoRequest, db: Session = Depends(get_db)):
    todo_model=Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()

@app.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(todo_request: TodoRequest, todo_id: int =Path(gt=0), db: Session = Depends(get_db)):
    todo_model= db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")
    todo_model.title=todo_request.title
    todo_model.description=todo_request.description
    todo_model.priority=todo_request.priority
    todo_model.complete=todo_request.complete

    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id:int =Path(gt=0),db: Session = Depends(get_db)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
