from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional 
app = FastAPI()

class Item(BaseModel):
    id:int 
    name:str
    description:str
    price:int
    on_offer:bool

@app.get('/')
def index():
    return {
        "message": "Welcome to selfhy's API"
    }

@app.get('/greet/{name}')
def greetName(name:str):
    return {
        "greeting" : f"Hello {name}"
    }

@app.get('/optional-name')
def optionalName(name:Optional[str]='user'):
    return {
        "optonal_name" : name
    }


@app.put('/item/{item_id}')
def updateItem(item_id:int,items:Item):
    return {
        "name" : items.name,
        "description" : items.description,
        "price" : items.price,
        "on_offer" : items.on_offer

    }