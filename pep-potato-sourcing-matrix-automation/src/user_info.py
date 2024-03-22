"""User Information API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (user_information,user_page_mapping_table,
                    user_page_mapping,page_information,access_type_information,country_information,
                    user_information_mapping_view)
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

@router.get('/get_user_page_mapping_table')
async def get_user_page_mapping_table(email:str,db: Session = Depends(get_db)):
    """Function to fetch records from user_information view table """
    try:
        records = db.query(user_page_mapping_table).filter(user_page_mapping_table.columns.email == email).all()
        return {"message": "Success", "data": records}
    except Exception as e:
        error_detail = str(e)
        raise HTTPException(status_code=400, detail=error_detail) from e

@router.get('/user_information_mapping_view')
async def get_user_information_mapping_view(db: Session = Depends(get_db)):
    """Function to fetch records from view_user_information view table """
    try:
        records = db.query(user_information_mapping_view).all()
        return {"message": "Success", "data": records}
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
    
# @router.post("/update_user_page_mapping")
# async def update_user_page_mapping(payload: schemas.UpdateUserInfoPayload, db: Session = Depends(get_db)):# pragma: no cover
#     for user_info in payload.data:
#         user_record = db.query(user_information).filter(user_information.email == user_info.email).first()
#         if not user_record:
#             raise HTTPException(status_code=404, detail=f"User with email {user_info.email} not found")
#         user_id = user_record.user_id
        
#         # Fetch page_id based on provided page_name from frontend
#         page_record = db.query(page_information).filter(page_information.page_name == user_info.page_name).first()
#         if not page_record:
#             raise HTTPException(status_code=404, detail=f"Page with name {user_info.page_name} not found")
#         page_id = page_record.page_id

#         # Fetch access_id and country_id based on provided access type and country from frontend
#         access_record = db.query(access_type_information).filter(access_type_information.access_name == user_info.access_name).first()
#         country_record = db.query(country_information).filter(country_information.country_name == user_info.country_name).first()

#         if not access_record:
#             raise HTTPException(status_code=404, detail=f"Access type {user_info.access_name} not found")
#         if not country_record:
#             raise HTTPException(status_code=404, detail=f"Country {user_info.country_name} not found")

#         access_id = access_record.access_id
#         country_id = country_record.country_id

#         # Update user_page_mapping table for the provided user_id and page_id
#         db.query(user_page_mapping).filter(user_page_mapping.user_id == user_id, user_page_mapping.page_id == page_id).update({
#             "access_id": access_id,
#             "country_id": country_id
#         })

#         # Update is_admin status in user_information table
#         db.query(user_information).filter(user_information.user_id == user_id).update({
#             "is_admin": user_info.is_admin
#         })

#     db.commit()
#     return {"message": "User page mappings updated successfully"}

@router.post("/update_user_page_mapping")
async def update_user_page_mapping(payload: schemas.UpdateUserInfoPayload, db: Session = Depends(get_db)):# pragma: no cover
    for user_info in payload.data:
        user_record = db.query(user_information).filter(user_information.email == user_info.email).first()
        if not user_record:
            raise HTTPException(status_code=404, detail=f"User with email {user_info.email} not found")
        user_id = user_record.user_id
        
        # Fetch page_id based on provided page_name from frontend
        page_record = db.query(page_information).filter(page_information.page_name == user_info.page_name).first()
        if not page_record:
            raise HTTPException(status_code=404, detail=f"Page with name {user_info.page_name} not found")
        page_id = page_record.page_id

        # Fetch access_id and country_id based on provided access type and country from frontend
        access_record = db.query(access_type_information).filter(access_type_information.access_name == user_info.access_name).first()
        country_record = db.query(country_information).filter(country_information.country_name == user_info.country_name).first()

        if not access_record:
            raise HTTPException(status_code=404, detail=f"Access type {user_info.access_name} not found")
        if not country_record:
            raise HTTPException(status_code=404, detail=f"Country {user_info.country_name} not found")

        access_id = access_record.access_id
        country_id = country_record.country_id

        # Check if the user is an admin and there is more than one admin
        if user_info.is_admin == False:
            admin_count = db.query(user_information).filter(user_information.is_admin == True).count()
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="At least one admin user must exist")

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
    return {"message": "User page mappings updated successfully"}

def extract_name_from_email(email_id: str):
    try:
        local_part = email_id.split('@')[0]
        names = local_part.split('.')
        first_name = names[0]
        last_name = ''.join(filter(str.isalpha, names[-1]))
        return first_name, last_name
    except Exception as e:
        logger.exception("Error occurred while extracting name from email")
        raise e

def get_or_create_user(user_details: schemas.UserCreationPayload, db: Session) :
    try:
        # Check if the user already exists based on the email
        user = db.query(user_information).filter(user_information.email == user_details.email).first()
        if user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Extract first name and last name from the email
        first_name, last_name = extract_name_from_email(user_details.email)
        
        # If the user does not exist, create a new user
        user = user_information(
            email=user_details.email,
            first_name=first_name,
            last_name=last_name,
            is_admin=user_details.is_admin,
            user_status=True,  # setting user_status to True
            created_by='SYSTEM',
            created_time=datetime.now(),
            updated_by='SYSTEM',
            updated_time=datetime.now(),
            country='US'  # setting country to US by default
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        logger.exception("Error occurred while creating or getting user")
        raise e


@router.post("/create_user_and_mapping/")
async def create_user_and_mapping(user_details: schemas.UserCreationPayload, db: Session = Depends(get_db)): # pragma: no cover
    try:
        # Create or get the user
        user = get_or_create_user(user_details, db)
        
        # Fetch all unique page IDs
        unique_page_ids = db.query(page_information.page_id).distinct().all()
        
        # Get access_id for view access
        view_access_id = db.query(access_type_information.access_id).filter(access_type_information.access_name == 'view').scalar()
        if not view_access_id:
            raise HTTPException(status_code=404, detail="Access type with name 'view' not found")
        
        # Get access_id for edit access if user is admin
        edit_access_id = None
        if user_details.is_admin:
            edit_access = db.query(access_type_information).filter(access_type_information.access_name == 'edit').first()
            if not edit_access:
                raise HTTPException(status_code=404, detail="Access type with name 'edit' not found")
            edit_access_id = edit_access.access_id
        
        # Create view only access for all unique page IDs for all countries
        country_id = db.query(country_information.country_id).filter(country_information.country_name == 'All').scalar()
        if not country_id:
            raise HTTPException(status_code=404, detail=f"Country with name 'All' not found")
        
        for page_id_tuple in unique_page_ids:
            page_id = page_id_tuple[0]
            # Check if the mapping already exists
            mapping = db.query(user_page_mapping).filter(
                user_page_mapping.user_id == user.user_id,
                user_page_mapping.page_id == page_id,
                user_page_mapping.country_id == country_id
            ).first()
            if not mapping:
                # Determine access_id based on user's admin status
                if user_details.is_admin:
                    access_id = edit_access_id
                else:
                    access_id = view_access_id
                
                # Create a new mapping
                new_mapping = user_page_mapping(
                    user_id=user.user_id,
                    page_id=page_id,
                    access_id=access_id,
                    country_id=country_id
                )
                db.add(new_mapping)
                db.commit()
                db.refresh(new_mapping)

        return {"message": "User and mappings created successfully"}
    except Exception as e:
        logger.exception("Error occurred while creating user and mappings")
        raise e

@router.post("/update_new_user_page_mapping")
async def update_new_user_page_mapping(user_info_payload: schemas.NewUserInfoPayload, db: Session = Depends(get_db)): # pragma: no cover
    try:
        for user_info in user_info_payload.data:
            email = user_info.email
            # Fetch user information by email
            user = db.query(user_information).filter(user_information.email == email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update user page mapping if page_name provided
            if user_info.page_name:
                # Get page_id for provided page_name
                page = db.query(page_information).filter(page_information.page_name == user_info.page_name).first()
                if not page:
                    raise HTTPException(status_code=404, detail="Page not found")
                page_id = page.page_id
                
                # Delete existing mapping for user_id and page_id
                db.query(user_page_mapping).filter(user_page_mapping.user_id == user.user_id, user_page_mapping.page_id == page_id).delete()
                
                # Get access_id for provided access_name
                access = db.query(access_type_information).filter(access_type_information.access_name == user_info.access_name).first()
                if not access:
                    raise HTTPException(status_code=404, detail="Access type not found")
                access_id = access.access_id
                
                # Get country_id for provided country_name
                country = db.query(country_information).filter(country_information.country_name == user_info.country_name).first()
                if not country:
                    raise HTTPException(status_code=404, detail="Country not found")
                country_id = country.country_id
                
                # Create new user page mapping
                new_mapping = user_page_mapping(
                    user_id=user.user_id,
                    page_id=page_id,
                    access_id=access_id,
                    country_id=country_id
                )
                db.add(new_mapping)
                db.commit()

        return {"message": "User and mapping updated successfully"}
    except Exception as e:
        logger.exception("Error occurred while updating user and mapping")
        raise e