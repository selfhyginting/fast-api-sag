from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from schema.items import Item
import models
from data import Session
from helpers.jwt_token import  AuthJWT

router = APIRouter()   

db=Session()

@router.get('/items',response_model=List[Item],status_code=status.HTTP_200_OK)
def getItems():
    items=db.query(models.Item).all()
    return items

@router.get('/items/{item_id}', status_code=status.HTTP_200_OK)
def getItemById(item_id:int):
    item=db.query(models.Item).filter(models.Item.id==item_id).first()
    return item 

@router.post('/items',status_code=status.HTTP_201_CREATED)
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
    

@router.put('/items/{item_id}', status_code=status.HTTP_200_OK)
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

@router.delete('/items/{item_id}')
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
    