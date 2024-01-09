from datetime import datetime, timedelta
from models import freight_task_info, freight_task_mappings, country_division_name
from schemas import FreightTaskInfoSchema, FreightTaskMappingsSchema, FreightTaskMappingsPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()

@router.get('/')
def get_freight_task_info(db: Session = Depends(get_db)):
    """Function to get all records from freight_task_info."""
    query = db.query(freight_task_info).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_info found")
    return {"status": "success", "data": query}

@router.get('/getByfreight_task_id/{freight_task_id}')
def getByfreight__task_id(freight_task_id: int, db: Session = Depends(get_db)):
    freight_task = db.query(freight_task_info).filter(freight_task_info.freight_task_id == freight_task_id).first()
    if not freight_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No freight_task_info_id: {freight_task_id} found")
    return {"status": "success", "freight_task": freight_task}

@router.get('/freight_task_mappings/{year}/{country}')
def get_freight_task_mappings(year: str, country:str,db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(freight_task_mappings).filter(freight_task_mappings.year==year, freight_task_mappings.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_mappings  found")
    return {"status": "success", "data": query}


@router.post("/update_freight_task_mappings/", status_code=status.HTTP_201_CREATED)
async def update_freight_task_mappings(year: int, db: Session = Depends(get_db)):
    """Function to update records in potato_rates table."""
    # Fetch all records from the database
    all_records = db.query(freight_task_info).all()
    countries = db.query(country_division_name).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    existingTaskNames = []
    for record in all_records:
        existingRecord = db.query(freight_task_mappings).filter(freight_task_mappings.year==year,freight_task_mappings.freight_task_id==record.freight_task_id).first()
        if existingRecord:
            existingTaskNames.append(record.task_name)
            continue
        for period in range(1,14):
            for con in countries:
                new_record = freight_task_mappings(freight_task_id = record.freight_task_id, period=period, year=year, value=0.001, company_name=con.task_desc)
                db.add(new_record)
                db.commit()

    return {"status": "success", "Records already exists for ":existingTaskNames, "forYear": year}

@router.post('/create_freight_task_info', status_code=status.HTTP_201_CREATED)
def create_freight_task_info(payload: FreightTaskInfoSchema, db: Session = Depends(get_db)):
    new_record = freight_task_info(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "freight_task_id": new_record.freight_task_id}

@router.post('/create_freight_task_mappings', status_code=status.HTTP_201_CREATED)
def create_freight_task_mappings(payload: FreightTaskMappingsSchema, db: Session = Depends(get_db)):
    new_record = freight_task_mappings(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}

@router.post("/update_freight_task_records/")
def update_freight_task_records(payload: FreightTaskMappingsPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in freight_task_mappings table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.freight_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(freight_task_mappings).filter(freight_task_mappings.freight_task_id == item.freight_task_id, freight_task_mappings.period==item.period, freight_task_mappings.year==item.year).update(
                {freight_task_mappings.value: item.value, freight_task_mappings.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))