"""User Information API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (user_information,user_page_mapping_table,user_page_mapping)
from sqlalchemy.orm import Session



router = APIRouter()

@router.get('/get_user_information')
def get_user_information(db: Session = Depends(get_db)):
    """Function to fetch all records from user_information table """
    try:
        records = db.query(user_information).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/get_user_page_mapping')
def get_user_page_mapping(db: Session = Depends(get_db)):
    """Function to fetch all records from user_information table """
    try:
        records = db.query(user_page_mapping).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.post('/create_user_information', status_code=status.HTTP_201_CREATED)
def create_user_information(payload: schemas.UserInfoSchema, db: Session = Depends(get_db)): # pragma: no cover
    user_info= user_information(**payload.dict())
    db.add(user_info)
    db.commit()
    db.refresh(user_info)
    return {"status": "success"}

@router.get('/user_page_mapping_view')
def user_page_mapping_view(db: Session = Depends(get_db)):
    """Function to fetch all records from user_information view table """
    try:
        records = db.query(user_page_mapping_table).all()
        return {"message": "Success", "data": records}
    except Exception as e:
        error_detail = str(e)
        raise HTTPException(status_code=400, detail=error_detail) from e
    
