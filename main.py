import bcrypt
from fastapi import FastAPI,status,HTTPException, Depends
from pydantic import BaseModel
from typing import Optional,List
from data import Session
import models
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder

app = FastAPI()

#hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tokenization
class Settings(BaseModel):
    authjwt_secret_key:str='8f585b4ac7a1e1f76af9584e784b67089fe5ad9892876dde9273179d5de06a34'

@AuthJWT.load_config
def get_config():
    return Settings()

class User(BaseModel):
    username:str
    password:str

    class Config:
        orm_mode=True
        schema_extra={
            "example":{    
                "username" : "your username",
                "password" : "your password"
            }
        }
    

class UserLogin(BaseModel):
    username:str
    password:str
    
    class Config:
        orm_mode=True
        schema_extra={
            "example" : {
                "username" : "your username",
                "password"  : "your password"
            }
        }

class Item(BaseModel):
    id:int 
    name:str
    description:str
    price:int
    on_offer:bool
    
    class Config:
        orm_mode=True
        schema_extra={
            "example":{    
                "username" : "your username",
                "password" : "your password"
            }
        }
    
db=Session()

@app.get('/users',response_model=List[User],status_code=status.HTTP_200_OK)
def get_users():
    users=db.query(models.User).all()
    return users

@app.get('/users/{username}',response_model=List[User], status_code=status.HTTP_200_OK)
def getItemByUsername(username:str):
    user=db.query(models.User).filter(models.User.username==username).first()
    return user

@app.post('/users/signup', status_code=status.HTTP_201_CREATED)
def create_user(user:User):
    db_item=db.query(models.User).filter(models.User.username==user.username).first()
    if db_item is not None:
        raise HTTPException(status_code=400,detail="Item already exists")
    #hash_password =codecs.encode(user.password)
    #encpassword = (user.password).encode('utf-8')
    #hash_password = bcrypt.hashpw(encpassword,bcrypt.gensalt(10)) 
    hash_password=pwd_context.hash(user.password)
    new_user=models.User(
        username=user.username,
        password=hash_password
    )
    db.add(new_user)
    db.commit()

    return hash_password

def verify_password(plain_password, hashed_password):
    if (pwd_context.verify(plain_password, hashed_password)):
        return True
        
@app.post('/users/login')
def login(user:UserLogin, jwtToken:AuthJWT=Depends()):
    userlogin=db.query(models.User).filter(models.User.username==user.username).first()
    #decpassword= (user.password).encode('utf-8')
    """ tespass=List[User[user.username]]
    selfhy= UserInDB(**tespass) """""" 
    res=verify_password(user.password,tespass) """
    
    #temp= bcrypt.checkpw(decpassword, (userlogin.password).encode('utf-8')) 

    #json_compatible_item_data = jsonable_encoder(temp)
    #tespass=bcrypt.checkpw(decpassword,temp.encode('utf-8'))
    
    if userlogin is not None: 
        if verify_password(user.password, userlogin.password):
            access_token=jwtToken.create_access_token(subject=user.username)
            refresh_token=jwtToken.create_refresh_token(subject=user.username)
            return {
                "access_token" :access_token,
                "refresh_token" :refresh_token
            } 
        raise HTTPException(status_code=401,detail="Invalid username or password")
    raise HTTPException(status_code=401,detail="Invalid username or password")

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

@app.get('/items/{item_id}',response_model=List[Item], status_code=status.HTTP_200_OK)
def getItemById(item_id:int):
    item=db.query(models.Item).filter(models.Item.id==item_id).first()
    return item 

@app.post('/items',status_code=status.HTTP_201_CREATED)
def createItem(item:Item, jwtToken:AuthJWT=Depends()):
    try:
        jwtToken.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Token')
    try:
        current_user=jwtToken.get_jwt_subject()

        db_item=db.query(models.Item).filter(models.Item.name==item.name).first()

        if db_item is not None:
            raise HTTPException(status_code=400,detail="Item already exists")
        
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
            "new_item_added" : {
                "id" : new_item.id,
                "name" : new_item.name,
                "description" : new_item.description,
                "price" : new_item.price,
                "on_offer" : new_item.on_offer,
            },
            "created_by" : current_user
        }
    except Exception as e:
        raise e    
    

@app.put('/items/{item_id}', status_code=status.HTTP_200_OK)
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
            "update_item" : {
                "name" : item_update.name,
                "description" : item_update.description,
                "price" : item_update.price,
                "on_offer" : item_update.on_offer,
            },
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
        
        return {
            "item" : "item has been deleted",
            "deleted_by" : current_user
            }
            
    except:
        return HTTPException
    