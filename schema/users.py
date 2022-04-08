from pydantic import BaseModel

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