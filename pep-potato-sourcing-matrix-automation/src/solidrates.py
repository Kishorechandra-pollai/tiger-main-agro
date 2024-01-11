"""Solid Rates API for finance"""
# from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (growing_area, solid_rate_mapping, solids_rate_table_period,
                    solids_rates)
from schemas import solidRateMappingPayload

router = APIRouter()

@router.get('/')
def get_solids_rates(db: Session = Depends(get_db)):
    """Function to get all records from potato_rates."""
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
            solids_rate_table_period.columns.year == year).all()
        return {"solids_rate_period_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
