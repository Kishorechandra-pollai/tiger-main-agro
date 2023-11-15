import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_category(db: Session = Depends(get_db)):
    category = db.query(models.category).filter(models.category.status == "ACTIVE").all()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Category  found")
    return {"status": "success", "category": category}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_category(payload: schemas.Category, db: Session = Depends(get_db)):
    new_category = models.category(**payload.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"status": "success", "category": new_category.crop_category}


@router.get('/{categoryId}')
def get_post(categoryId: str, db: Session = Depends(get_db)):
    category_id = db.query(models.category).filter(models.category.crop_category == categoryId).first()
    if not category_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No category  with this id: {id} found')
    return {"status": "success", "category": category_id}


@router.delete('/{categoryId}')
def delete_post(categoryId: str, db: Session = Depends(get_db)):
    category_query = db.query(models.category).filter(models.category.crop_category == categoryId).update({'status': 'IN-ACTIVE'})
    if not category_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Category  with this id: {id} found')

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
