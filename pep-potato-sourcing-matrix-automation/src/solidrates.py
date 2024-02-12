"""Solid Rates API for finance"""
# from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (growing_area, solid_rate_mapping, solids_rate_table_period,
                    solids_rates)
from schemas import solidRateMappingPayload,SolidRatesSchema
from pydantic import BaseModel

router = APIRouter()

@router.get('/')
def get_solids_rates(db: Session = Depends(get_db)):
    """Function to get all records from solid_rates."""
    query = db.query(solids_rates).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solids_rates  found")
    return {"status": "success", "data": query}

@router.get('/getBySolidsRateId/{solids_rate_id}')
def get_by_solids_rate_id(solids_rate_id: int, db: Session = Depends(get_db)):
    """Function to get records by solids rate id"""
    solid_rate = db.query(solids_rates).filter(solids_rates.solids_rate_id ==
                                               solids_rate_id).first()
    if not solid_rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No solids_rate_id: {solids_rate_id} found")
    return {"status": "success", "solid_rate": solid_rate}

@router.get('/solid_rate_mapping/{year}')
def get_solid_rate_mapping(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(solid_rate_mapping).join(solids_rates,
                                        solids_rates.solids_rate_id ==
                                        solid_rate_mapping.solids_rate_id
                                        ).filter(solids_rates.year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}

@router.post("/update_solid_rates_records/")
def update_solid_rates_records(payload: solidRateMappingPayload,db: Session = Depends(get_db)):
    """Function to update already existing records in solid_rate_mapping table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            db.query(solid_rate_mapping).filter(solid_rate_mapping.solids_rate_id
                                                == item.solids_rate_id,
                                                solid_rate_mapping.period==item.period,
                                                solid_rate_mapping.period_year==item.period_year).update(
                {solid_rate_mapping.rate: item.rate}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/solid_rate_period_year/{year}')
def solid_rate_period_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from solids_rate table for a particular year """
    try:
        records = db.query(solids_rate_table_period).filter(
            solids_rate_table_period.columns.year == year
            ).order_by(solids_rate_table_period.columns.growing_area_id,
                       solids_rate_table_period.columns.period).all()
        return {"solids_rate_period_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/create_solid_rates_mappings_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_solid_rates_mappings_for_next_year(year: int, db: Session = Depends(get_db)): # pragma: no cover
    """Function to Create solid_rate_mapping records for next year."""
    all_records = db.query(solids_rates).all()
    query_view = db.query(solids_rate_table_period).filter(solids_rate_table_period.columns.year==(year-1)).all() #view which contains actual value by growing_area_id
    update_count = 0
    country = ''
    existingRecord = db.query(solid_rate_mapping)\
                    .filter(solid_rate_mapping.period_year==year).all()
    for ex in existingRecord:
        db.delete(ex)
    db.commit()
    for record in all_records: # Iterate over all solids_rates
        if record.currency=='USD':
            country = 'US'
        elif record.currency=='CAD':
            country ='Canada'
        for ele in query_view:  # Iterate through the view
            if ele.growing_area_id == record.growing_area_id:
                new_record = solid_rate_mapping(solids_rate_id = record.solids_rate_id, period=ele.period, period_year=year, rate=ele.actual_rate, country_code=country)
                db.add(new_record)
                update_count += 1
            # else:
            #     for period in range(1,14):
            #         new_record = solid_rate_mapping(solids_rate_id = record.solids_rate_id,
            #                                             period=period, period_year=year, rate=0,country_code=country)
            #         db.add(new_record)
            #         update_count += 1

    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}


def create_solid_rate_in_db(payload: SolidRatesSchema, db: Session):
    if isinstance(payload, BaseModel):
        # Convert Pydantic model to dictionary
        payload_dict = payload.dict()
    else:
        # Assume payload is already a dictionary
        payload_dict = payload
    new_record = solids_rates(**payload_dict)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.post('/create_solids_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: SolidRatesSchema, db: Session = Depends(get_db)):
    new_record = create_solid_rate_in_db(payload, db)
    return {"status": "success", "solids_rate_id": new_record.solids_rate_id}

@router.post("/update_solids_rates_with_default_value/{solids_rate_id}/{year}")
async def update_solids_rates_with_default_value(solids_rate_id:int, year:int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update records in solids_rates table."""
    # Fetch all records from the database
    all_records = db.query(solids_rates).filter(solids_rates.solids_rate_id ==
                                               solids_rate_id).first()
    # Ensure there are records in the database
    if not all_records:
        raise HTTPException(status_code=404, detail="No records found in the database")

    for period in range(1,14):
        new_record = solid_rate_mapping(solids_rate_id = all_records.solids_rate_id,
                                            period=period, period_year=year, rate=0)
        db.add(new_record)
        db.commit()
    return {"status": "success"}
