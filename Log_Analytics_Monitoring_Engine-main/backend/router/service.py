from backend.config.sql_config import get_connection
from mysql.connector import Error
from fastapi import APIRouter
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


router = APIRouter()


@router.post("/create/user")  # API end point
def create_user(User: UserCreate):
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        query = "insert into credentials (password,email) values(%s,%s)"
        cursor.execute(query, (User.password, User.email))
        db.commit()
        cursor.close()
        db.close()
        return {"Message": "User added to database succesfully"}
    except Error as e:
        print("Error : ", e)


@router.get("/get/user/info")
def get_user(id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    query = "select password,email from credentials where id = %s "
    cursor.execute(query, (id,))
    user = cursor.fetchone()
    db.close()
    cursor.close()
    return {"message": "USer found!!", "data": user}


@router.put("/update/user")
def update_user(new_user: create_user):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    query = "update credentials set password=%s,email=%s where id=%s"
    cursor.execute(query, (new_user.password, new_user.email))
    db.commit()
    db.close()
    cursor.close()
    return {"Message": "User updated seccesfully!!"}


@router.delete("/delete/user/info")
def delete_user(id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    query = "delete from  credentials where id=%s"
    cursor.execute(query, (id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "user deleted succesfully!!"}
