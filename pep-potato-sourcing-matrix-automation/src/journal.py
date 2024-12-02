from schemas import JournalEntrySchema, JournalEntryOwnerSchema
from models import journal_entry, user_information,page_information, journal_entry_owner
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
	if payload.is_parent == True:
		try:
			page = db.query(page_information).filter(page_information.page_name == payload.page_name).first()
		except Exception as e:
			raise HTTPException(status_code = 404, detail = "Page not found")
	else:
		try:
			page = db.query(journal_entry).filter(journal_entry.journal_id == payload.parent_id).first()
		except Exception as e:
			raise HTTPException(status_code = 404, detail = "Journal not found")

	new_journal_entry = journal_entry(
						comments = payload.comments,
						page_name = page.page_name,
						page_id = page.page_id,
						user_first_name = user.first_name,
						user_last_name = user.last_name,
						email = payload.email,
						user_id = user.user_id,
						is_parent = payload.is_parent,
						parent_id = payload.parent_id
	)
	
	db.add(new_journal_entry)
	db.commit()
	db.refresh(new_journal_entry)
	return {"status":"success"}

@router.get('/get_journal_entry')
async def get_journal_all(db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from journal_entry_all table """
    try:
        records = db.query(journal_entry).all()
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

	new_journal_entry_owner = journal_entry_owner(
										comments = payload.comments,
										user_first_name = user.first_name,
										user_last_name = user.last_name,
										email = payload.email,
										user_id = user.user_id,
										ownership_id = payload.ownership_id,
										is_parent = payload.is_parent,
										parent_id = payload.parent_id
	)
	
	db.add(new_journal_entry_owner)
	db.commit()
	db.refresh(new_journal_entry_owner)
	return {"status":"success"}

@router.get('/get_journal_entry_owner')
async def get_journal_owner(db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from journal_entry_all table """
    try:
        records = db.query(journal_entry_owner).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e