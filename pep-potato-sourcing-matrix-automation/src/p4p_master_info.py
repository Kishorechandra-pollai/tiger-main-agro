# from datetime import datetime, timedelta
from models import p4p_master_info, p4p_task_mappings, View_p4p_result_table, country_division_name, \
    View_p4p_result_update
from schemas import p4pMasterInfoSchema, p4pTaskMappingsSchema, p4pTaskMappingsPayload, TaskItemPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db
from typing import List

router = APIRouter()


@router.get('/')
def get_p4p_master_info(db: Session = Depends(get_db)):
    """Function to get all records from p4p_master_info."""
    query = db.query(p4p_master_info).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No p4p_master_info found")
    return {"status": "success", "data": query}


@router.get('/get_p4p_master_info/{p4p_id}')
def get_p4p_master_info_byId(p4p_id: int, db: Session = Depends(get_db)):
    query = db.query(p4p_master_info).filter(p4p_master_info.p4p_id == p4p_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No p4p_id: {p4p_id} found")
    return {"status": "success", "details": query}


@router.get('/p4p_task_mappings/')
def get_p4p_task_mappings(db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(p4p_task_mappings).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No p4p_task_mappings  found")
    return {"status": "success", "data": query}


@router.get('/p4p_task_mappings_by_year/{year}/{country}')
def p4p_task_mappings_by_year(year: str, country: str, db: Session = Depends(get_db)):
    """Function to get all records from p4p_task_mappings."""
    # query = (db.query(p4p_task_mappings.p4p_id, p4p_task_mappings.period, p4p_task_mappings.value, p4p_master_info.p4p_name).join(p4p_master_info, p4p_master_info.p4p_id==p4p_task_mappings.p4p_id).filter(p4p_task_mappings.year==year).all())
    query = (db.query(View_p4p_result_table).filter(View_p4p_result_table.columns.p_year == year,
                                                    View_p4p_result_table.columns.company_name == country).all())
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No p4p_task_mappings  found")

    return {"status": "success", "data": query}


@router.post("/update_p4p_task_mappings/", status_code=status.HTTP_201_CREATED)
async def update_p4p_task_mappings(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update records in p4p_master_info table."""
    # Fetch all records from the database
    all_records = db.query(p4p_master_info).all()
    countries = db.query(country_division_name).all()
    # Ensure there are records in the database
    if all_records.count == 0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    existingTaskNames = []
    for record in all_records:
        existingRecord = db.query(p4p_task_mappings).filter(p4p_task_mappings.year == year,
                                                            p4p_task_mappings.p4p_id == record.p4p_id).first()
        if existingRecord:
            existingTaskNames.append(record.p4p_name)
            continue
        for period in range(1, 14):
            for con in countries:
                new_record = p4p_task_mappings(p4p_id=record.p4p_id, period=period, year=year, value=0.001,
                                               company_name=con.task_desc)
                db.add(new_record)
                db.commit()

    return {"status": "success", "Records already exists for ": existingTaskNames, "forYear": year}


@router.post('/create_p4p_task_mappings_info', status_code=status.HTTP_201_CREATED)
def create_p4p_task_mappings_info(payload: p4pMasterInfoSchema, db: Session = Depends(get_db)):
    new_record = p4p_task_mappings(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "p4p_id": new_record.p4p_name}


@router.post('/create_p4p_task_mappings', status_code=status.HTTP_201_CREATED)
def create_p4p_task_mappings(payload: p4pTaskMappingsSchema, db: Session = Depends(get_db)):
    new_record = p4p_task_mappings(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}


@router.post("/update_p4p_task_mappings_records/")
def update_p4p_task_mappings_records(payload: p4pTaskMappingsPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in update_p4p_task_mappings_records table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.p4p_id <= 0 or item.period <= 0 or item.year <= 0:
                return {"status": "error", "message": "Please check details"}
            db.query(p4p_task_mappings).filter(p4p_task_mappings.p4p_id == item.p4p_id,
                                               p4p_task_mappings.year == item.year,
                                               p4p_task_mappings.period == item.period,
                                               p4p_task_mappings.company_name == item.company_name).update(
                {p4p_task_mappings.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))
