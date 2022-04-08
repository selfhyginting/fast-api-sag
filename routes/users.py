
from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from schema.users import User, UserLogin
import models
from data import Session
from passlib.context import CryptContext
from helpers.jwt_token import  AuthJWT


router = APIRouter()

#hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db=Session()

# 

@router.get('/users',response_model=List[User],status_code=status.HTTP_200_OK)
def get_users():
    users=db.query(models.User).all()
    return users

@router.get('/users/{username}',response_model=List[User], status_code=status.HTTP_200_OK)
def getItemByUsername(username:str):
    user=db.query(models.User).filter(models.User.username==username).first()
    return user

@router.post('/users/signup', status_code=status.HTTP_201_CREATED)
def create_user(user:User):
    db_item=db.query(models.User).filter(models.User.username==user.username).first()
    if db_item is not None:
        raise HTTPException(status_code=400,detail="Item already exists")
   
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
        
@router.post('/users/login')
def login(user:UserLogin, jwtToken:AuthJWT=Depends()):
    userlogin=db.query(models.User).filter(models.User.username==user.username).first()
    
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

@router.get('/new_token')
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