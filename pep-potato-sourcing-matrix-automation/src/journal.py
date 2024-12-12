from schemas import JournalEntrySchema, JournalEntryOwnerSchema
from models import journal_all,user_information,page_information,journal_ownership,growing_area,Ownership, region, View_ownership_journal_info
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db
from datetime import datetime
import pytz

router = APIRouter()

# General Journal

@router.post('/post_journal_entry', status_code=status.HTTP_201_CREATED)
async def create_journal(payload: JournalEntrySchema, db: Session = Depends(get_db)):# pragma: no cover
    #Fetching page info
    try:
        user = db.query(user_information).filter(user_information.email == payload.email).first()
    except Exception as e:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    #Fetching page info
    try:
        page = db.query(page_information).filter(page_information.page_name == payload.page_name).first()
    except Exception as e:
        raise HTTPException(status_code = 404, detail = "Page not found")
    
    #Timezone
    cst = pytz.timezone("US/Central")
    cst_time = datetime.now(cst).strftime("%Y-%m-%d %H:%M")
    
    new_journal_entry = journal_all(
                        comments = payload.comments,
                        page_name = page.page_name,
                        page_id = page.page_id,
                        user_first_name = str.title(user.first_name),
                        user_last_name = str.title(user.last_name),
                        email = payload.email,
                        user_id = user.user_id,
                        img_url = payload.img_url,
                        created_time = cst_time
    )
    
    db.add(new_journal_entry)
    db.commit()
    db.refresh(new_journal_entry)
    return {"status":"success"}

@router.get('/get_journal_entry')
async def get_journal_all(db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from journal_entry_all table """
    try:
        records = db.query(journal_all).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
# Ownership Journal

@router.post('/post_journal_entry_owner', status_code=status.HTTP_201_CREATED)
async def create_journal_owner(payload: JournalEntryOwnerSchema, db: Session = Depends(get_db)):# pragma: no cover
    #Fetching page info
    try:
        user = db.query(user_information).filter(user_information.email == payload.email).first()
    except Exception as e:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    #Fetching Ownership info
    try:
        owner = db.query(Ownership).filter(Ownership.ownership_id == payload.ownership_id).first()
    except Exception as e:
        raise HTTPException(status_code = 404, detail = "Ownership data not found")
    
    #Fetching area info
    try:
        if payload.growing_area_desc == None or payload.growing_area_name == None:
            area = db.query(growing_area).filter(growing_area.growing_area_id == owner.growing_area_id).first()
    except Exception as e:
        raise HTTPException(status_code = 404, detail = "GA not found")
    
    #Fetching Region
    try:
        reg = db.query(region).filter(region.region_id==area.region).first()
    except Exception as e:
        raise HTTPException(status_code = 404, detail = "Region not found")
    
    #Timezone
    cst = pytz.timezone("US/Central")
    cst_time = datetime.now(cst).strftime("%Y-%m-%d %H:%M")

    new_journal_entry_owner = journal_ownership(
                                        comments = payload.comments,
                                        user_first_name = user.first_name,
                                        user_last_name = user.last_name,
                                        email = payload.email,
                                        user_id = user.user_id,
                                        ownership_id = payload.ownership_id,
                                        growing_area_name = area.growing_area_name,
                                        growing_area_desc = area.growing_area_desc,
                                        img_url = payload.img_url,
                                        region = reg.region_name,
                                        year = owner.year,
                                        crop_type = owner.crop_type,
                                        crop_year = owner.crop_year,
                                        created_time = cst_time
    )

    db.add(new_journal_entry_owner)
    db.commit()
    db.refresh(new_journal_entry_owner)
    return {"status":"success"}

@router.get('/get_journal_entry_owner/{region}/{year}')
async def get_journal_owner(region:str,year:int ,db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from journal_entry_all table """
    try:
        if region =="US":
            records = db.query(journal_ownership).filter(journal_ownership.region.in_(['East - US','Central - US','West - US']),
                                                     journal_ownership.year == year).all()
            return {"data": records}
        elif region == "All Data":
            records = db.query(journal_ownership).filter(journal_ownership.year == year).all()
            return {"data":records}
        else:
            records = db.query(journal_ownership).filter(journal_ownership.region==region,
                                                     journal_ownership.year == year).all()
            return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

# Jounal Ownership detailed info

@router.get('/get_journal_ownership_detailed_info')
async def get_journal_all(db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from journal_entry_all table """
    try:
        records = db.query(View_ownership_journal_info).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e