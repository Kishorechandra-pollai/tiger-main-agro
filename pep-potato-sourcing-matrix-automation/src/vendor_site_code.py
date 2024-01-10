"""Vendor_Site_Code API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import vendor_site_code
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/get_vendor_site_code')
def view_vendor_site_code(db: Session = Depends(get_db)):
    """Function to fetch all records from vendor_site_code table """
    try:
        records = db.query(vendor_site_code).all()
        return {"data": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))
