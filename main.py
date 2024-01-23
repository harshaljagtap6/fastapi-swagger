from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app= FastAPI()
models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int

class UserBase(BaseModel):
    username: str

class IdBase(BaseModel):
    userid: int

class UserIdBase(BaseModel):
    user_id: int
    user_name: str

class UpdateUserData(BaseModel):
    user_id: int
    new_username: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/all_users/")
async def show_all_users(db: db_dependency):
    user = db.query(models.User).all()
    print(user)
    if user == []:
        return JSONResponse({"message": "There are no users in this table."})
    return user

@app.post("/add_users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    return JSONResponse({"message": f"New user with username:{db_user.username} has been added"})


@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        return JSONResponse({"message": f"No users found with this User Id {user_id}"})
    return user
        
@app.post("/users_id/", status_code=status.HTTP_200_OK)
async def fetch_user(userid: IdBase, db: db_dependency):
    print("Received userid:", userid.userid)  # Add this line for debugging
    user = db.query(models.User).filter(models.User.id == userid.userid).first()
    if user is None:
        return JSONResponse({"message": f"No users found with this User Id {userid.userid}"})
    return user    

@app.post("/remove_user/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(userid: IdBase, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == userid.userid).first()
    if user is None:
        return JSONResponse({"message": f"No users found with userid: {userid.userid}. It may have been alreadt removed or never entered."})
    db.delete(user)
    db.commit()
    return JSONResponse({"message": f"User with userid:{userid.userid} username:{user.username} has been removed"})

# @app.post("/update_users_id/", status_code=status.HTTP_200_OK)
# async def fetch_user(userid: UserIdBase, db: db_dependency):
#     user = db.query(models.User).filter(models.User.id == userid.user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User Not Found")
#     db.add(user)
#     db.commit()

@app.post("/update_user_data/", status_code=status.HTTP_200_OK)
async def update_user_data(updated_data: UpdateUserData, db: db_dependency):
    existing_user = db.query(models.User).filter(models.User.id == updated_data.user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    # Update the user data
    existing_user.username = updated_data.new_username
    # Commit the changes to the database
    db.commit()

    return existing_user