from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends , HTTPException, Path
from models import Todos 
from database import SessionLocal
from starlette import status
from pydantic import BaseModel,Field
from .auth import get_current_user

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
    yield db 
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
  title: str  = Field(min_length=3)
  description: str = Field(min_length=3, max_length= 100)
  priority: int = Field(gt=0, lt=6)
  complete: bool

@router.get("/",status_code= status.HTTP_200_OK)
async def read_all(db: db_dependency):
  todos =  db.query(Todos).all()
  return todos

@router.get("/todo/{todo_id}", status_code= status.HTTP_200_OK)
async def read_todo(db : db_dependency, todo_id : int = Path (gt=0)):
  

  todo_model =  db.query(Todos).filter(Todos.id == todo_id).first() #chave unica, logo nao precisa percorrer banco inteiro para achar outros ids 
  if todo_model is not None:
    return todo_model
  
  raise HTTPException ( status_code = 404, detail ='Todo Not found') 

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,db: db_dependency, todo_request: TodoRequest):
  if user is None:
    raise HTTPException(status_code=401, detail='Authetication Failed')
  todo_model = Todos(**todo_request.dict(),owner_id = user.get('id'))
  db.add(todo_model)
  db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency,
                       todo_request : TodoRequest,
                      todo_id: int = Path(gt=0)
                     ):
  todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
  if todo_model is None:
    raise HTTPException(status_code=404, detail = 'Todo not found')
    
  todo_model.title = todo_request.title
  todo_model.description = todo_request.description 
  todo_model.priority = todo_request.complete
  todo_model.complete = todo_request.complete
  db.add(todo_model)
  db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo (db:db_dependency,
                       todo_id: int =  Path(gt = 0)):
  todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
  if todo_model is None:
    raise HTTPException(status_code=404, detail = 'Todo not found')
  db.query(Todos).filter(Todos.id == todo_id).delete()
  db.commit()