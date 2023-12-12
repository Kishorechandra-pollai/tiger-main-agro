from models import erp_raw_data_us
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db


router = APIRouter()


@router.get("/pagination_range")
async def pagination_range(page:int, items_per_page:int, vendor_name:str, BPA_no:int, db: Session = Depends(get_db)):
    try:
        offset = (page-1)*items_per_page
        all_records = all_records = db.query(erp_raw_data_us).filter(erp_raw_data_us.VENDOR_NAME == vendor_name).filter(erp_raw_data_us.BPA_Number==BPA_no).order_by(erp_raw_data_us.row_id).limit(items_per_page).offset(offset).all()
        if not all_records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No erp_raw_data found")
        print(all_records.count)
        return all_records

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/read_file")
# async def read_file(db: Session = Depends(get_db)):

#     return ""