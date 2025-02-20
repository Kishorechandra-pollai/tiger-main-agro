"""Vendor_Site_Code API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import vendor_site_code
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/get_vendor_site_code')
def view_vendor_site_code(db: Session = Depends(get_db)):
    """Function to fetch all records from vendor_site_code table """
    try:
        records = db.query(vendor_site_code).filter(vendor_site_code.status == "ACTIVE").all()
        if not records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No vendor site code found")
        return {"data": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))
