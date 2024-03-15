"""Page Information API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (page_information,country_information,access_type_information)
#from sqlalchemy import func, and_
from sqlalchemy.orm import Session


router = APIRouter()

@router.get('/get_page_information')
def view_page_information(db: Session = Depends(get_db)):
    """Function to fetch all records from page_information table """
    try:
        records = db.query(page_information).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/get_country_information')
def view_country_information(db: Session = Depends(get_db)):
    """Function to fetch all records from country_information table """
    try:
        records = db.query(country_information).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/get_access_information')
def view_country_information(db: Session = Depends(get_db)):
    """Function to fetch all records from country_information table """
    try:
        records = db.query(access_type_information).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post('/create_page_information', status_code=status.HTTP_201_CREATED)
def create_page_information(payload: schemas.PageInfoSchema, db: Session = Depends(get_db)):# pragma: no cover
    page_info= page_information(**payload.dict())
    db.add(page_info)
    db.commit()
    db.refresh(page_info)
    return {"status": "success"}
    
@router.post('/create_country_information', status_code=status.HTTP_201_CREATED)
def create_country_information(payload: schemas.CountryInfoSchema, db: Session = Depends(get_db)):# pragma: no cover
    new_country= country_information(**payload.dict())
    db.add(new_country)
    db.commit()
    db.refresh(new_country)
    return {"status": "success"}

@router.post('/create_access_type_information', status_code=status.HTTP_201_CREATED)
def create_access_type_information(payload: schemas.AccessInfoSchema, db: Session = Depends(get_db)):# pragma: no cover
    access_details= access_type_information(**payload.dict())
    db.add(access_details)
    db.commit()
    db.refresh(access_details)
    return {"status": "success"}