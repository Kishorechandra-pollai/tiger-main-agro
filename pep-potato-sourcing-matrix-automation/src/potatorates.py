"""Potato Rates API for finance"""
# from datetime import datetime
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from models import (growing_area, potato_rate_mapping,
                    potato_rate_table_period, potato_rate_table_weekly,
                    potato_rates)
from schemas import potatoRateMappingPayload,PotatoRatesSchema
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/')
def get_potato_rates(db: Session = Depends(get_db)):
    """Function to get all records from potato_rates."""
    query = db.query(potato_rates).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rates  found")
    return {"status": "success", "data": query}

@router.get('/potato_rate_mapping_by_year/{year}')
def get_potato_rate_mapping_data(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(potato_rate_mapping).all()
    query = db.query(potato_rate_mapping).join(potato_rates,
                                        potato_rates.potato_rate_id == potato_rate_mapping
                                        .potato_rate_id).filter(potato_rates.year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}

@router.get("/get_potato_rate_mapping/{year}")
def get_potato_rate_mappings(year: str, db: Session = Depends(get_db)):
    """Function to records in potato_rate_mapping table."""
    records = (db.query(potato_rate_mapping.potato_rate_id,
                        potato_rate_mapping.period, potato_rate_mapping.rate, potato_rates)
               .distinct(potato_rate_mapping.period)
               .join(potato_rates,potato_rates
                     .potato_rate_id == potato_rate_mapping.potato_rate_id)
               .order_by(potato_rate_mapping.potato_rate_id, potato_rate_mapping.period)
                                .filter(potato_rates.year==year)
                                .all())
    results = [{"potato_rate_id":row.potato_rate_id, "period":row.period,
                                                "rate":row.rate, "week":0} for row in records]
    return results


@router.post("/update_potato_rates_records/")
def update_potato_rates_records(payload: potatoRateMappingPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in potato_rates table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.potato_rate_id<=0 or item.period<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(potato_rate_mapping
                     ).filter(potato_rate_mapping.potato_rate_id == item.potato_rate_id,
                              potato_rate_mapping.period==item.period,
                              potato_rate_mapping.week==item.week,
                              potato_rate_mapping.p_year==item.p_year).update(
                                  {potato_rate_mapping.rate: item.rate},
                                  synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/potato_rate_period_year/{year}/{region_id}')
def potato_rate_period_year(year:int,region_id:int, db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate table for a particular year """
    try:
        records = db.query(potato_rate_table_period
                           ).filter(potato_rate_table_period.columns.p_year == year,
                                    potato_rate_table_period.columns.region == region_id
                                    ).order_by(potato_rate_table_period.columns.growing_area_id,
                                               potato_rate_table_period.columns.period).all()
        return {"potato_rate_period_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_period_week_year/{year}/{region_id}')
def potato_rate_period_week_year(year:int,region_id:int, db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate table for a particular year """
    try:
        records = db.query(potato_rate_table_weekly).filter(potato_rate_table_weekly
                                                            .columns.p_year == year,
                                                            potato_rate_table_weekly.columns.region_id == region_id).order_by(
                                                                potato_rate_table_weekly.columns.growing_area_id,
                                                                potato_rate_table_weekly.columns.period,
                                                                potato_rate_table_weekly.columns.week
                                                                ).all()
        return {"potato_rate_period_week_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_potato_rate_mapping_for_next_year/{year}", status_code=status.HTTP_201_CREATED)
async def create_potato_rate_mapping_for_next_year(year: int , db: Session = Depends(get_db)):  # pragma: no cover
    """Function to Create potato_rate_mapping records for next year."""
    all_records = db.query(potato_rates).all()
    query_view = db.query(potato_rate_table_weekly).filter(potato_rate_table_weekly.columns.p_year==(year-1)).all() #view which contains actual value by growing_area_id
    update_count = 0
    country = ''
    existingRecord = db.query(potato_rate_mapping)\
                    .filter(potato_rate_mapping.p_year==year).all()
    for ex in existingRecord:
        db.delete(ex)
    db.commit()
    for record in all_records: # Iterate over all potato_rates
        for ele in query_view:  # Iterate through the view
            if ele.potato_rate_id == record.potato_rate_id and ele.growing_area_id == record.growing_area_id:
                if record.currency=='USD':
                    country = 'US'
                elif record.currency=='CAD':
                    country ='Canada'
                new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id, period=ele.period, week=ele.week, p_year=year, rate=ele.actual_rate, country_code=country)
                db.add(new_record)
                update_count += 1
            # else:
            #     for period in range(1,14):
            #         for week in range(1,5):
            #             new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id,
            #                                             period=period, week=week, p_year=year, rate=0,country_code=country)
            #             db.add(new_record)
            #             update_count += 1

    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}

def create_potato_rate_in_db(payload: PotatoRatesSchema, db: Session):
    if isinstance(payload, BaseModel):
        # Convert Pydantic model to dictionary
        payload_dict = payload.dict()
    else:
        # Assume payload is already a dictionary
        payload_dict = payload
    new_record = potato_rates(**payload_dict)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record



@router.post('/create_potato_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: PotatoRatesSchema, db: Session = Depends(get_db)):
    new_record = create_potato_rate_in_db(payload, db)
    return {"status": "success", "potato_rate_id": new_record.potato_rate_id}


def update_potato_rates_default(db: Session, potato_rate_id: int, year: int):
    all_records = db.query(potato_rates).filter(potato_rates.potato_rate_id == potato_rate_id).first()
    if not all_records:
        return None  # Indicate no records found

    for period in range(1, 14):
        for week in range(1, 5):
            new_record = potato_rate_mapping(potato_rate_id=all_records.potato_rate_id,
                                             period=period, week=week, p_year=year, rate=0,country_code="US")
            db.add(new_record)
    db.commit()
    return True


@router.post("/update_potato_rates_with_default_value/{potato_rate_id}/{year}")
async def update_potato_rates_with_default_value(potato_rate_id:int, year:int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update records in potato_rates table."""
    result = update_potato_rates_default(db, potato_rate_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="No records found in the database")
    return {"status": "success"}