"""Potato Rates API for finance"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (potato_rate_mapping,
                    potato_rate_table_period, potato_rate_table_weekly,
                    potato_rates)
from schemas import potatoRateMappingPayload
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


@router.get('/getby_growing_areaid/{growing_area_id}')
def getby_growing_areaid(growing_area_id: int, year: int, db: Session = Depends(get_db)):
    """Function to get potato_rate_id for a growing_area_id"""
    try:
        record = db.query(potato_rates)\
            .filter(potato_rates.growing_area_id == growing_area_id,
                    potato_rates.year == year)\
            .all()
        return {"getbyGrowingAreaId": record}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_mapping_by_year/{year}')
def get_potato_rate_mapping_data(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(potato_rate_mapping)\
        .join(potato_rates,
              potato_rates.potato_rate_id == potato_rate_mapping.potato_rate_id)\
        .filter(potato_rates.year == year).all()
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
               .join(potato_rates, potato_rates.potato_rate_id ==
                     potato_rate_mapping.potato_rate_id)
               .order_by(potato_rate_mapping.potato_rate_id, potato_rate_mapping.period)
               .filter(potato_rates.year == year).all())
    results = [{"potato_rate_id": row.potato_rate_id, "period": row.period,
                "rate": row.rate, "week": 0} for row in records]
    return results


@router.post("/update_potato_rates_records/")
def update_potato_rates_records(payload: potatoRateMappingPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in potato_rates table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.potato_rate_id <= 0 or item.period <= 0:
                return {"status": "error", "message": "Please check details"}
            db.query(potato_rate_mapping
                     ).filter(potato_rate_mapping.potato_rate_id == item.potato_rate_id,
                              potato_rate_mapping.period == item.period,
                              potato_rate_mapping.week == item.week).update(
                {potato_rate_mapping.rate: item.rate},
                synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_period')
def potato_rate_period(db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate_table for period week view"""
    try:
        records = db.query(potato_rate_table_period).all()
        result = [
            {
                "growing_area_id": row.growing_area_id,
                "growing_area_name": row.growing_area_name,
                "period": row.UNL_DATE_PD,
                "actual": row.wgt_avg_potato_price,
                "year": row.UNLOAD_YEAR,
                "week": 0,
                "period_with_P": f'P{row.UNL_DATE_PD}'
            }
            for row in records
        ]
        return {"potato_rate_period": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_period_year/{year}')
def potato_rate_period_year(year: int, db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate table for a particular year """
    try:
        records = db.query(potato_rate_table_period)\
            .filter(potato_rate_table_period.columns.UNLOAD_YEAR == year)\
            .all()
        result = [
            {
                "growing_area_id": row.growing_area_id,
                "growing_area_name": row.growing_area_name,
                "period": row.UNL_DATE_PD,
                "actual": row.wgt_avg_potato_price,
                "year": row.UNLOAD_YEAR,
                "week": 0,
                "period_with_P": f'P{row.UNL_DATE_PD}'
            }
            for row in records
        ]
        return {"potato_rate_period_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_period_year/{year}/{growing_area_id}')
def potato_rate_period_year_growing_area_id(year: int,
                                            growing_area_id: int, db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate table
    for a particular year and growing area id"""
    try:
        records = db.query(potato_rate_table_period).filter(
            and_(
                potato_rate_table_period.columns.UNLOAD_YEAR == year,
                potato_rate_table_period.columns.growing_area_id == growing_area_id
            )
        ).all()
        period_dict = {f'P{period}': 0 for period in range(1, 14)}
        for row in records:
            period_dict[f'P{row.UNL_DATE_PD}'] = row.wgt_avg_potato_price
        result = [
            {
                "growing_area_id": growing_area_id,
                "growing_area_name": row.growing_area_name,
                "period": period,
                "actual": actual,
                "year": year,
                "week": 0,
            }
            for period, actual in period_dict.items()
        ]
        return {"potato_rate_period_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_period_week')
def potato_rate_period_week(db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate_table for period week view"""
    try:
        records = db.query(potato_rate_table_weekly).all()
        return {"potato_rate_period_week": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_period_week_year/{year}')
def potato_rate_period_week_year(year: int, db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate table for a particular year """
    try:
        records = db.query(potato_rate_table_weekly)\
            .filter(potato_rate_table_weekly.columns.p_year == year)\
            .all()
        return {"potato_rate_period_week_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
