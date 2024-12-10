from schemas import JournalEntrySchema, JournalEntryOwnerSchema
from models import journal_all,user_information,page_information,journal_ownership,growing_area,Ownership
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

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

	new_journal_entry = journal_all(
						comments = payload.comments,
						page_name = page.page_name,
						page_id = page.page_id,
						user_first_name = str.title(user.first_name),
						user_last_name = str.title(user.last_name),
						email = payload.email,
						user_id = user.user_id,
						img_url = payload.img_url
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
	
	#Fetching area info
	try:
		if payload.growing_area_desc == None or payload.growing_area_name == None:
			owner = db.query(Ownership).filter(Ownership.ownership_id == payload.ownership_id).first()
			area = db.query(growing_area).filter(growing_area.growing_area_id == owner.growing_area_id).first()
	except Exception as e:
		raise HTTPException(status_code = 404, detail = "OwnershipID/GA not found")

	new_journal_entry_owner = journal_ownership(
										comments = payload.comments,
										user_first_name = user.first_name,
										user_last_name = user.last_name,
										email = payload.email,
										user_id = user.user_id,
										ownership_id = payload.ownership_id,
										growing_area_name = area.growing_area_name,
										growing_area_desc = area.growing_area_desc,
										img_url = payload.img_url
	)
	
	db.add(new_journal_entry_owner)
	db.commit()
	db.refresh(new_journal_entry_owner)
	return {"status":"success"}

@router.get('/get_journal_entry_owner')
async def get_journal_owner(db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from journal_entry_all table """
    try:
        records = db.query(journal_ownership).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e