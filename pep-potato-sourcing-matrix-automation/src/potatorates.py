"""Potato Rates API for finance"""
# from datetime import datetime
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from models import (growing_area, potato_rate_mapping,
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


# @router.get('/getByPotatoRateId/{potato_rate_id}')
# def getby_potatorateid(potato_rate_id: int, db: Session = Depends(get_db)):
#     """Function to get data by potato_rate_id"""
#     potato_rate = db.query(potato_rates).filter(potato_rates.
#                                                 potato_rate_id == potato_rate_id).first()
#     if not potato_rate:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"No potato_rate_id: {potato_rate_id} found")
#     return {"status": "success", "potato_rates": potato_rate}

@router.get('/getby_growing_areaid/{growing_area_id}')
def getby_growing_areaid(growing_area_id: int, year: int, db: Session = Depends(get_db)):
    """Function to get potato_rate_id for a growing_area_id"""
    try:
        record = db.query(potato_rates).filter(potato_rates.growing_area_id == growing_area_id,
                                               potato_rates.year == year).all()
        result = [
            {
                "potato_rate_id": row.potato_rate_id
            }
            for row in record
        ]
        return {"getbyGrowingAreaId": result}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


# @router.post('/create_potato_rates', status_code=status.HTTP_201_CREATED)
# def create_potato_rates(payload: PotatoRatesSchema, db: Session = Depends(get_db)):
#     new_record = potato_rates(**payload.dict())
#     db.add(new_record)
#     db.commit()
#     db.refresh(new_record)
#     return {"status": "success", "potato_rate_id": new_record.potato_rate_id}

# @router.post('/create_potato_rate_mapping', status_code=status.HTTP_201_CREATED)
# def create_potato_rate_mapping(payload: potatoRateMappingSchema, db: Session = Depends(get_db)):
#     new_record = potato_rate_mapping(**payload.dict())
#     db.add(new_record)
#     db.commit()
#     db.refresh(new_record)
#     return {"status": "success", "row_id": new_record.row_id}

@router.get('/potato_rate_mapping_by_year/{year}')
def get_potato_rate_mapping_data(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(potato_rate_mapping).all()
    query = db.query(potato_rate_mapping).join(potato_rates,
                                               potato_rates.potato_rate_id == potato_rate_mapping
                                               .potato_rate_id).filter(potato_rates.year == year).all()
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
               .join(potato_rates, potato_rates
                     .potato_rate_id == potato_rate_mapping.potato_rate_id)
               .order_by(potato_rate_mapping.potato_rate_id, potato_rate_mapping.period)
               .filter(potato_rates.year == year)
               .all())
    results = [{"potato_rate_id": row.potato_rate_id, "period": row.period,
                "rate": row.rate, "week": 0} for row in records]
    return results


# @router.post("/update_potato_rates/", status_code=status.HTTP_201_CREATED)
# async def update_potato_rates(year:int, db: Session = Depends(get_db)):
#     """Function to update records in potato_rates table."""
#     # Fetch all records from the database
#     all_records = db.query(growing_area).all()
#     # Ensure there are records in the database
#     if all_records.count==0:
#         raise HTTPException(status_code=404, detail="No records found in the database")

#     currency = ''
#     for record in all_records:
#         if record.country=='USA':
#             currency = 'USD'
#         elif record.country=='Canada':
#             currency ='CAD'
#         existing_record = db.query(potato_rates).filter(
#             potato_rates.year==year,
#             potato_rates.growing_area_id==record.growing_area_id).first()

#         if existing_record:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                                 detail="Record already Exists")

#         new_record = potato_rates(year = year, growing_area_id=record.growing_area_id,
#                                   currency=currency, created_by="System", updated_by="System",
#                                   updated_time=datetime.now(), created_time=datetime.now())
#         db.add(new_record)
#         db.commit()

#     return {"status": "success"}

# @router.post("/update_potato_rates_with_default_value/", status_code=status.HTTP_201_CREATED)
# async def update_potato_rates_with_default_value( db: Session = Depends(get_db)):
#     """Function to update records in potato_rates table."""
#     # Fetch all records from the database
#     all_records = db.query(potato_rates).all()
#     # Ensure there are records in the database
#     if all_records.count==0:
#         raise HTTPException(status_code=404, detail="No records found in the database")

#     for record in all_records:
#         for period in range(1,14):
#             for week in range(1,5):
#                 new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id,
#                                                  period=period, week=week, rate=5)
#                 db.add(new_record)
#                 db.commit()
#             return {"status": "success"}

# @router.delete('delete/{year}')
# def delete_post(year:int, db: Session = Depends(get_db)):
#     """ Function to delete records for a particular year"""
#     records_to_delete = db.query(potato_rates).filter(potato_rates.year == year).all()
#     if not records_to_delete:
#         raise HTTPException(status_code=404,
#                             detail=f'No region  with this year: {year} found')
#     for record in records_to_delete:
#         db.delete(record)
#     db.commit()
#     return {"message": f"Records for the year {year} deleted successfully."}

# @router.post('/create_rates_from_previous_year/')
# def create_rates_from_previous_year(current_year: int, db: Session = Depends(get_db)):
#     """Function to create new records from previous year data"""
#     previous_year = current_year-1
#     previous_year_records = db.query(potato_rates.potato_rate_id,
#                                      potato_rate_mapping.rate).join(
#                                          potato_rates, potato_rates.year == previous_year).all()
#     if not previous_year_records:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'No records with this id: {previous_year} found')

#     for record in previous_year_records:
#         for period in range(1,14):
#             for week in range(1,5):
#                 new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id,
#                                                  period=period, week=week, rate=record.rate)
#                 db.add(new_record)
#                 db.commit()

#     return Response(status_code=status.HTTP_204_NO_CONTENT)

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
                "year": row.unload_year,
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
        records = db.query(potato_rate_table_period
                           ).filter(potato_rate_table_period.columns.unload_year == year).all()
        result = [
            {
                "growing_area_id": row.growing_area_id,
                "growing_area_name": row.growing_area_name,
                "period": row.UNL_DATE_PD,
                "actual": row.wgt_avg_potato_price,
                "year": row.unload_year,
                "week": 0,
                "period_with_P": f'P{row.UNL_DATE_PD}'
            }
            for row in records
        ]
        return {"potato_rate_period_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# @router.get('/potato_rate_period_year/{year}/{growing_area_id}')
# def potato_rate_period_year_growing_area_id(year: int,
#                                             growing_area_id: int, db: Session = Depends(get_db)):
#     """Function to fetch all records from potato_rate table
#     for a particular year and growing area id"""
#     try:
#         records = db.query(potato_rate_table_period).filter(
#             and_(
#                 potato_rate_table_period.columns.unload_year == year,
#                 potato_rate_table_period.columns.growing_area_id == growing_area_id
#             )
#         ).all()
#         period_dict = {f'P{period}': 0 for period in range(1, 14)}
#         for row in records:
#             period_dict[f'P{row.UNL_DATE_PD}'] = row.wgt_avg_potato_price
#         result = [
#             {
#                 "growing_area_id": growing_area_id,
#                 "growing_area_name": row.growing_area_name,
#                 "period": period,
#                 "actual": actual,
#                 "year": year,
#                 "week": 0,
#             }
#             for period, actual in period_dict.items()
#         ]
#         return {"potato_rate_period_year": result}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/potato_rate_period_week')
def potato_rate_period_week(db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate_table for period week view"""
    try:
        records = db.query(potato_rate_table_weekly).all()
        result = [
            {
                "growing_area_id": row.growing_area_id,
                "growing_area_name": row.growing_area_name,
                "period": row.period,
                "fcst": row.rate,
                "actual": row.actual_rate,
                "year": row.p_year,
                "week": row.week,
                "period_with_P": f'P{row.period}W{row.week}'
            }
            for row in records
        ]
        return {"potato_rate_period_week": result}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/potato_rate_period_week_year/{year}')
def potato_rate_period_week_year(year: int, db: Session = Depends(get_db)):
    """Function to fetch all records from potato_rate table for a particular year """
    try:
        records = db.query(potato_rate_table_weekly).filter(potato_rate_table_weekly
                                                            .columns.p_year == year).all()
        result = [
            {
                "growing_area_id": row.growing_area_id,
                "growing_area_name": row.growing_area_name,
                "period": row.period,
                "fcst": row.rate,
                "actual": row.actual_rate,
                "year": row.p_year,
                "week": row.week,
                "period_with_P": f'P{row.period}W{row.week}'
            }
            for row in records
        ]
        return {"potato_rate_period_week_year": result}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
