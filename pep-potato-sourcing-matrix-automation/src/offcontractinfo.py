from datetime import datetime, timedelta
from models import off_contract_info, off_contract_task_mapping
from schemas import OffContractInfoSchema, OffContractTaskMappingSchema, OffContractTaskMappingPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()

@router.get('/')
def get_off_contract_info(db: Session = Depends(get_db)):
    """Function to get all records from off_contract_info."""
    query = db.query(off_contract_info).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_info found")
    return {"status": "success", "data": query}

@router.get('/getByoff_contract_task_id/{off_contract_task_id}')
def getByPotatoRateId(off_contract_task_id: int, db: Session = Depends(get_db)):
    off_contract_task = db.query(off_contract_info).filter(off_contract_info.off_contract_task_id == off_contract_task_id).first()
    if not off_contract_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No off_contract_info_id: {off_contract_task_id} found")
    return {"status": "success", "off_contract_task": off_contract_task}

@router.get('/off_contract_task_mapping/')
def get_off_contract_task_mapping(db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(off_contract_task_mapping).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_task_mapping  found")
    return {"status": "success", "data": query}

@router.get('/off_contract_task_mapping_by_year/{year}')
def off_contract_task_mapping_by_year(year: str, db: Session = Depends(get_db)):
    """Function to get all records from off_contract_task_mapping."""
    query = db.query(off_contract_task_mapping).filter(off_contract_task_mapping.year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}

@router.post("/update_off_contract_task_mapping/", status_code=status.HTTP_201_CREATED)
async def update_off_contract_task_mapping(year: int, db: Session = Depends(get_db)):
    """Function to update records in potato_rates table."""
    # Fetch all records from the database
    all_records = db.query(off_contract_info).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    for record in all_records:
        for period in range(1,14):
            new_record = off_contract_task_mapping(off_contract_task_id = record.off_contract_task_id, period=period, year=year,value=0.0)
            db.add(new_record)
            db.commit()

    return {"status": "success"}

@router.post('/create_freight_task_info', status_code=status.HTTP_201_CREATED)
def create_freight_task_info(payload: OffContractInfoSchema, db: Session = Depends(get_db)):
    new_record = off_contract_info(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "off_contract_task_id": new_record.off_contract_task_id}

@router.post('/create_freight_task_mappings', status_code=status.HTTP_201_CREATED)
def create_freight_task_mappings(payload: OffContractTaskMappingSchema, db: Session = Depends(get_db)):
    new_record = off_contract_task_mapping(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}

@router.post("/update_off_contract_records/{off_contract_task_id}")
def update_off_contract(off_contract_task_id: int, payload: OffContractTaskMappingSchema ,
                   db: Session = Depends(get_db)):
    """Function to update already existing records in off_contract_task_mapping table"""
    existing_records= db.query(off_contract_task_mapping).filter(
        off_contract_task_mapping.off_contract_task_id == off_contract_task_id
    ).first()

    if existing_records is None:
        raise HTTPException(status_code=404, detail="No record found with this f{off_contract_task_id}")

    existing_records.value = payload.value
    existing_records.period = payload.period
    existing_records.year = payload.year

    db.commit()
    db.refresh(existing_records)

    return existing_records

@router.post("/update_off_contract_records/")
def update_off_contract_records(payload: OffContractTaskMappingPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in off_contract_task_mapping table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            db.query(off_contract_task_mapping).filter(off_contract_task_mapping.off_contract_task_id == item.off_contract_task_id).update(
                {off_contract_task_mapping.value: item.value, off_contract_task_mapping.period.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))