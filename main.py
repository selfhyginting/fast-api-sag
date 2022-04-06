

from os import remove
from fastapi import FastAPI,status,HTTPException, Depends
from pydantic import BaseModel
from typing import Optional,List
from data import Session
import models
from fastapi_jwt_auth import AuthJWT

app = FastAPI()

class Settings(BaseModel):
    authjwt_secret_key:str='8f585b4ac7a1e1f76af9584e784b67089fe5ad9892876dde9273179d5de06a34'

@AuthJWT.load_config
def get_config():
    return Settings()

class User(BaseModel):
    username:str
    email:str
    password:str

    class Config:
        schema_extra={
            "example":{    
                "username" : "your username",
                "email" : "youremail@gmail.com",
                "password" : "your password"
            }
        }
class UserLogin(BaseModel):
    username:str
    password:str
    
    class Config:
        schema_extra={
            "example" : {
                "username" : "your username",
                "password"  : "your password"
            }
        }
users=[]

class Item(BaseModel):
    id:int 
    name:str
    description:str
    price:int
    on_offer:bool
    
    class Config:
        orm_mode=True

db=Session()

@app.get('/users',response_model=List[User])
def get_users():
    return users

@app.post('/users/signup', status_code=status.HTTP_201_CREATED)
def create_user(user:User):
    new_user={
         "username" : user.username,
        "email" :   user.email,
        "password" : user.password
    }

    users.append(new_user)
    return "user is created"

@app.post('/users/login')
def login(user:UserLogin, jwtToken:AuthJWT=Depends()):
    for us in users:
        if (us["username"]==user.username) and (us["password"]==user.password):
            access_token=jwtToken.create_access_token(subject=user.username)
            refresh_token=jwtToken.create_refresh_token(subject=user.username)
            return {
                "access_token" :access_token,
                "refresh_token" :refresh_token
            }
        raise HTTPException(status_code='401',detail='invalid username or password')

@app.get('/new_token')
def create_NewToken(jwtToken:AuthJWT=Depends()):
    try:
        jwtToken.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Token')

    current_user=jwtToken.get_jwt_subject()
    access_token=jwtToken.create_access_token(subject=current_user)

    return{
        "new_access_token" : access_token 
    }


@app.get('/')
def welcomegreet():
    return "Welcome"
    
@app.get('/items',response_model=List[Item],status_code=status.HTTP_200_OK)
def getItems():
    items=db.query(models.Item).all()
    return items

@app.get('/items/{item_id}',response_model=Item, status_code=status.HTTP_200_OK)
def getItemById(item_id:int):
    item=db.query(models.Item).filter(models.Item.id==item_id).first()
    return item 

@app.post('/items',response_model=Item,status_code=status.HTTP_201_CREATED)
def createItem(item:Item, jwtToken:AuthJWT=Depends()):
    try:
        jwtToken.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Token')
    try:
        current_user=jwtToken.get_jwt_subject()

        db_item=db.query(models.Item).filter(models.Item.name==item.name).first()

        if db_item is not None:
            raise HTTPException(status_code=400,detail="item already exists")
        
        new_item=models.Item(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            on_offer=item.on_offer
        )
        
        db.add(new_item)
        db.commit()

        return {
            "new_item_added" : new_item,
            "created_by" : current_user
        }
    except Exception as e:
        raise e    
    

@app.put('/items/{item_id}',response_model=Item,status_code=status.HTTP_200_OK)
def updateItem(item_id:int,item:Item, jwtToken:AuthJWT=Depends()):
    try:
        jwtToken.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Token')
    try:
        current_user=jwtToken.get_jwt_subject()

        item_update = db.query(models.Item).filter(models.Item.id==item_id).first()
        item_update.name=item.name
        item_update.description=item.description
        item_update.price=item.price
        item_update.on_offer=item.on_offer

        db.commit()
        return {
            "item_updated": item_update,
            "edited_by" : current_user
        }
    except Exception as e :
        raise e

@app.delete('/items/{item_id}')
def deleteItem(item_id:int,jwtToken:AuthJWT=Depends()):
    try:
        jwtToken.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Token')
    
    current_user=jwtToken.get_jwt_subject()

    try:
        item_delete = db.query(models.Item).filter(models.Item.id==item_id).first()

        db.delete(item_delete)
        db.commit()
        
        try:
            remove(models.Item.id)
        except:
            return {
            "item" : "item has been deleted",
            "deleted_by" : current_user
            }
    except:
        return HTTPException
    