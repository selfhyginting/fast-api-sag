from pydantic import BaseModel

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
    