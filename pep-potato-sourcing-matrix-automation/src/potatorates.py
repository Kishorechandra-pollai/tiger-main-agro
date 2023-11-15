from datetime import datetime, timedelta
from models import potato_rates, growing_area, potato_rate_mapping
from schemas import potatoRateMappingPayload, potatoRateMappingSchema, PotatoRatesSchema
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()

@router.get('/')
def get_potato_rates(db: Session = Depends(get_db)):
    """Function to get all records from potato_rates."""
    query = db.query(potato_rates).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rates  found")
    return {"status": "success", "data": query}

@router.get('/getByPotatoRateId/{potato_rate_id}')
def getByPotatoRateId(potato_rate_id: int, db: Session = Depends(get_db)):
    potato_rate = db.query(potato_rates).filter(potato_rates.potato_rate_id == potato_rate_id).first()
    if not potato_rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No potato_rate_id: {potato_rate_id} found")
    return {"status": "success", "potato_rates": potato_rate}

@router.post('/create_potato_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: PotatoRatesSchema, db: Session = Depends(get_db)):
    new_record = potato_rates(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "potato_rate_id": new_record.potato_rate_id}

@router.post('/create_potato_rate_mapping', status_code=status.HTTP_201_CREATED)
def create_potato_rate_mapping(payload: potatoRateMappingSchema, db: Session = Depends(get_db)):
    new_record = potato_rate_mapping(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}


@router.get('/potato_rate_mapping_by_year/{year}')
def get_potato_rate_mapping_data(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(potato_rate_mapping).all()
    query = db.query(potato_rate_mapping).join(potato_rates,
                                        potato_rates.potato_rate_id == potato_rate_mapping.potato_rate_id).filter(potato_rates.year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}

@router.get("/get_potato_rate_mapping/{year}")
def get_potato_rate_mappings(year: str, db: Session = Depends(get_db)):
    """Function to records in potato_rate_mapping table."""
    records = (db.query(potato_rate_mapping.potato_rate_id, potato_rate_mapping.period, potato_rate_mapping.rate, potato_rates)
               .distinct(potato_rate_mapping.period)
                                .join(potato_rates,
                                        potato_rates.potato_rate_id == potato_rate_mapping.potato_rate_id)
                                .order_by(potato_rate_mapping.potato_rate_id, potato_rate_mapping.period)
                                .filter(potato_rates.year==year)
                                .all())
    results = [{"potato_rate_id":row.potato_rate_id, "period":row.period,
                                                "rate":row.rate, "week":0} for row in records]
    return results


@router.post("/update_potato_rates/", status_code=status.HTTP_201_CREATED)
async def update_potato_rates(year:int, db: Session = Depends(get_db)):
    """Function to update records in potato_rates table."""
    # Fetch all records from the database
    all_records = db.query(growing_area).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    currency = ''
    for record in all_records:
        if record.country=='USA':
            currency = 'USD'
        elif record.country=='Canada':
            currency ='CAD'
        existingRecord = db.query(potato_rates).filter_by(year=year,growing_area_id=record.growing_area_id ).first()

        if existingRecord:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Record already Exists")

        new_record = potato_rates(year = year, growing_area_id=record.growing_area_id, currency=currency, created_by="System", updated_by="System", updated_time=datetime.now(), created_time=datetime.now())
        db.add(new_record)
        db.commit()

    return {"status": "success"}

@router.post("/update_potato_rates_with_defaul_value/", status_code=status.HTTP_201_CREATED)
async def update_potato_rates_with_defaul_value( db: Session = Depends(get_db)):
    """Function to update records in potato_rates table."""
    # Fetch all records from the database
    all_records = db.query(potato_rates).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    for record in all_records:
        for period in range(1,14):
            for week in range(1,5):
                new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id, period=period, week=week, rate=0)
                db.add(new_record)
                db.commit()

    return {"status": "success"}

@router.delete('/delete/')
def delete_post(potato_rate_id: str, db: Session = Depends(get_db)):
    plant_query = db.query(potato_rates).filter(potato_rates.potato_rate_id == potato_rate_id).first()

    if not plant_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No plants  with this id: {potato_rate_id} found')
    db.delete(plant_query)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post('/update_rates_from_previous_year/')
def update_rates_from_previous_year(current_year: int, db: Session = Depends(get_db)):
    previous_year = current_year-1
    previous_year_records = db.query(potato_rates.potato_rate_id,  potato_rate_mapping.rate).join(potato_rates, potato_rates.year == previous_year).all()
    if not previous_year_records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No records with this id: {previous_year} found')

    for record in previous_year_records:
        for period in range(1,14):
            for week in range(1,5):
                new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id, period=period, week=week, rate=record.rate)
                db.add(new_record)
                db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/update_potato_rates_records/")
def update_potato_rates_records(payload: potatoRateMappingPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in potato_rates table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            db.query(potato_rate_mapping).filter(potato_rate_mapping.potato_rate_id == item.potato_rate_id).update(
                {potato_rate_mapping.rate: item.rate, potato_rate_mapping.week: item.week, potato_rate_mapping.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))