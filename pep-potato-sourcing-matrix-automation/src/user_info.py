"""User Information API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (user_information,user_page_mapping_table,
                    user_page_mapping,page_information,access_type_information,country_information)
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


router = APIRouter()

@router.get('/get_user_information')
async def get_user_information(db: Session = Depends(get_db)):
    """Function to fetch all records from user_information table """
    try:
        records = db.query(user_information).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/get_user_page_mapping')
async def get_user_page_mapping(db: Session = Depends(get_db)):
    """Function to fetch all records from user_information table """
    try:
        records = db.query(user_page_mapping).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.post('/create_user_information', status_code=status.HTTP_201_CREATED)
async def create_user_information(payload: schemas.UserInfoSchema, db: Session = Depends(get_db)): # pragma: no cover
    user_info= user_information(**payload.dict())
    db.add(user_info)
    db.commit()
    db.refresh(user_info)
    return {"status": "success"}

@router.get('/user_page_mapping_view')
async def user_page_mapping_view(db: Session = Depends(get_db)):
    """Function to fetch records from user_information view table """
    try:
        records = db.query(user_page_mapping_table).all()
        
        response_data = []
        for record in records:
            country_name = "US,Canada" if record.country_name == "All" else record.country_name
            response_data = [
            {
                "user_id": record.user_id,  
                "page_id": record.page_id, 
                "country_id": record.country_id,  
                "access_id": record.access_id, 
                "email": record.email,  
                "country": record.country, 
                "first_name": record.first_name,  
                "last_name": record.last_name, 
                "is_admin": record.is_admin,  
                "user_status": record.user_status, 
                "page_name": record.page_name,  
                "access_name": record.access_name,
                "access_value": record.access_value,
                "country_name": country_name
            }
            for record in records
        ]
        return {"message": "Success", "data": response_data}
    except Exception as e:
        error_detail = str(e)
        raise HTTPException(status_code=400, detail=error_detail) from e

    
@router.post("/update_user_status")
async def update_user_status(user_info: schemas.EditActiveStatusSchema,db: Session = Depends(get_db)): # pragma: no cover
    user_record = db.query(user_information).filter(user_information.email == user_info.email).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    if user_info.user_status is not None:
        user_record.user_status = not user_record.user_status  
    db.commit()
    return {"message": "User status updated successfully"}


def extract_name_from_email(email_id:str):
    try:
        local_part = email_id.split('@')[0]
        names = local_part.split('.')
        first_name = names[0]
        last_name = ''.join(filter(str.isalpha, names[-1]))
        return first_name, last_name
    except Exception as e:
        logger.exception("Error occurred while extracting name from email")
        raise e

def get_or_create_user(user_details: schemas.NewUserInfoSchema, db: Session):
    try:
        # Check if the user already exists based on the email
        user = db.query(user_information).filter(user_information.email == user_details.email).first()
        if user:
            return user
        # Extract first name and last name from the email
        first_name, last_name = extract_name_from_email(user_details.email)
        # If the user does not exist, create a new user
        user = user_information(
            email=user_details.email,
            first_name=first_name,
            last_name=last_name,
            is_admin=user_details.is_admin,
            user_status=user_details.user_status,
            created_by='SYSTEM',
            created_time=datetime.now(),
            updated_by='SYSTEM',
            updated_time=datetime.now(),
            country='US'
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        logger.exception("Error occurred while creating or getting user")
        raise e

def create_page_mapping(user_id: int, page_name: str, country_name: str, access_name: str, db: Session):
    try:
        # Check if the page already exists based on the page_name
        page = db.query(page_information).filter(page_information.page_name == page_name).first()
        if not page:
            raise HTTPException(status_code=404, detail=f"Page with name '{page_name}' not found")

        # Get country_id based on country_name
        country_id = db.execute("SELECT country_id FROM country_information WHERE country_name = :country_name",
                                {"country_name": country_name}).scalar()
        if not country_id:
            raise HTTPException(status_code=404, detail=f"Country with name '{country_name}' not found")

        # Get access_id based on access_name
        access_id = db.execute("SELECT access_id FROM access_type_information WHERE access_name = :access_name",
                               {"access_name": access_name}).scalar()
        if not access_id:
            raise HTTPException(status_code=404, detail=f"Access type with name '{access_name}' not found")

        # Check if the mapping already exists
        mapping = db.query(user_page_mapping).filter(
            user_page_mapping.user_id == user_id,
            user_page_mapping.page_id == page.page_id
        ).first()
        if mapping:
            return mapping

        # Create a new mapping
        new_mapping = user_page_mapping(
            user_id=user_id,
            page_id=page.page_id,
            access_id=access_id,
            country_id=country_id
        )
        db.add(new_mapping)
        db.commit()
        db.refresh(new_mapping)
        return new_mapping
    except Exception as e:
        logger.exception("Error occurred while creating page mapping")
        raise e


@router.post("/create_user_and_mapping/")
async def create_user_and_mapping(user_details: schemas.NewUserInfoSchema, db: Session = Depends(get_db)):# pragma: no cover
    try:
        # Create or get the user
        user = get_or_create_user(user_details, db)
        # Create mapping
        create_page_mapping(
            user_id=user.user_id,
            page_name=user_details.page_name,
            country_name=user_details.country_name,
            access_name=user_details.access_name,
            db=db
        )

        return {"message": "User and mapping created successfully"}
    except Exception as e:
        logger.exception("Error occurred while creating user and mapping")
        raise e
    
@router.post("/update_user_page_mapping")
async def update_user_page_mapping(user_info: schemas.UpdateUserInfoSchema, db: Session = Depends(get_db)):# pragma: no cover

    # Retrieve the user ID based on the provided email from the user_information table
    user_record = db.query(user_information).filter(user_information.email == user_info.email).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user_record.user_id
    # Fetch page_id based on provided page_name from frontend
    page_record = db.query(page_information).filter(page_information.page_name == user_info.page_name).first()
    if not page_record:
        raise HTTPException(status_code=404, detail="Page not found")

    page_id = page_record.page_id

    # Fetch access_id and country_id based on provided access type and country from frontend
    access_record = db.query(access_type_information).filter(access_type_information.access_name == user_info.access_name).first()
    country_record = db.query(country_information).filter(country_information.country_name == user_info.country_name).first()

    if not access_record:
        raise HTTPException(status_code=404, detail="Access type not found")
    if not country_record:
        raise HTTPException(status_code=404, detail="Country not found")

    access_id = access_record.access_id
    country_id = country_record.country_id

    # Update user_page_mapping table for the provided user_id and page_id
    db.query(user_page_mapping).filter(user_page_mapping.user_id == user_id, user_page_mapping.page_id == page_id).update({
        "access_id": access_id,
        "country_id": country_id
    })

    # Update is_admin status in user_information table
    db.query(user_information).filter(user_information.user_id == user_id).update({
        "is_admin": user_info.is_admin
    })

    db.commit()
    return {"message": "User page mapping updated successfully"}