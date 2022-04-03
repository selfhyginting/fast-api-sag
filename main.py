
from fastapi import FastAPI,status,HTTPException
from pydantic import BaseModel
from typing import Optional,List
from data import Session
import models
app = FastAPI()

class Item(BaseModel):
    id:int 
    name:str
    description:str
    price:int
    on_offer:bool
    
    class Config:
        orm_mode=True

db=Session()


@app.get('/items',response_model=List[Item],status_code=status.HTTP_200_OK)
def getItems():
    items=db.query(models.Item).all()
    return items

@app.get('/items/{item_id}',response_model=Item, status_code=status.HTTP_200_OK)
def getItemById(item_id:int):
    item=db.query(models.Item).filter(models.Item.id==item_id).first()
    return item 
@app.post('/items',response_model=Item,status_code=status.HTTP_201_CREATED)
def createItem(item:Item):
    db_item=db.query(models.Item).filter(models.Item.name==item.name).first()

    if db_item is not None:
        raise HTTPException(status_code=400,detail="item already exists")
    
    new_item=models.Item(
        name=item.name,
        description=item.description,
        price=item.price,
        on_offer=item.on_offer
    )
    
    db.add(new_item)
    db.commit()

    return new_item

@app.put('/items/{item_id}',response_model=Item,status_code=status.HTTP_200_OK)
def updateItem(item_id:int,item:Item):
    item_update = db.query(models.Item).filter(models.Item.id==item_id).first()
    item_update.name=item.name
    item_update.description=item.description
    item_update.price=item.price
    item_update.on_offer=item.on_offer

    db.commit()
    return item_update

@app.delete('/items/{item_id}')
def deleteItem(item_id:int):
    try:
        item_delete = db.query(models.Item).filter(models.Item.id==item_id).first()
        db.delete(item_delete)
        db.commit()
        return "item has been deleted"
    except:
        return HTTPException
    