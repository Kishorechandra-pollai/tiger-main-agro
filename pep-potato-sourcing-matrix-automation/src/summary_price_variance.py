"""Summary Price Variance API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import (country_division_name, price_variance_task,
                    price_variance_task_mapping,summary_price_variance)
from schemas import PriceVarianceMappingPayload
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/price_variance_task_mapping')
def get_price_variance_task_mapping(db: Session = Depends(get_db)):
    """Function to get all records from price_variance_task_mapping."""
    try:
        records = db.query(price_variance_task_mapping).all()
        result = [
            {
                "price_variance_task_id": row.price_variance_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"price_variance_task_mapping": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@router.get('/price_variance_task')
def get_price_variance_task(db: Session = Depends(get_db)):
    """Function to get all records from price_variance_task."""
    try:
        records = db.query(price_variance_task).all()
        result = [
            {
                "price_variance_task_id": row.price_variance_task_id,
                "task_name": row.task_name,
            }
            for row in records
        ]
        return {"price_variance_task": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/price_variance_task_mapping_by_year/{year}/{company_name}')
def price_variance_task_mapping_by_year(year: int,company_name :str, db: Session = Depends(get_db)):
    """Function to get all records from price_variance_task_mapping based on year."""
    try:
        records = db.query(price_variance_task_mapping
                           ).filter(price_variance_task_mapping.year==year,
                                    price_variance_task_mapping.company_name == company_name).all()
        result = [
            {
                "price_variance_task_id": row.price_variance_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"price_variance_task_mapping_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_total_price_variance/{year}/{company_name}')
def get_total_price_variance(year:int, company_name: str,db: Session = Depends(get_db)):
    try:
        records = db.query(price_variance_task_mapping).filter(price_variance_task_mapping.year==year,
                                                               price_variance_task_mapping.company_name == company_name).all()
        total = {}
        for record in records:
            period = record.period
            if period in total:
                total[period] += record.value
            else:
                total[period] = record.value
        result = [
            {"period": period, "Total": total[period]}
            for period in sorted(total.keys())
        ]
        for item in result:
            item["period_with_P"] = f'P{item["period"]}'
        return {"task": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_price_variance_task_mapping")
async def create_price_variance_task_mapping(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update records in price_variance_task_mapping table."""
    # Fetch all records from the database
    all_records = db.query(price_variance_task).all()
    countries = db.query(country_division_name).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    existingTaskNames = []
    for record in all_records:
        existingRecord = db.query(price_variance_task_mapping).filter(price_variance_task_mapping.year==year
                                                                            ,price_variance_task_mapping.price_variance_task_id==record.price_variance_task_id ).first()
        if existingRecord:
            existingTaskNames.append(record.task_name)
            continue
        for period in range(1,14):
            for con in countries:
                new_record =price_variance_task_mapping(price_variance_task_id = record.price_variance_task_id, 
                                                              period=period, year=year, value=0.0, company_name=con.task_desc)
                db.add(new_record)
                db.commit()

    return {"status": "success", "Records already exists for ":existingTaskNames, "forYear": year}

@router.delete('delete_all')
def delete_all_post(db: Session = Depends(get_db)):  # pragma: no cover
    records_to_delete = db.query(price_variance_task_mapping).all()
    if not records_to_delete:
        raise HTTPException(status_code=404,
                            detail=f'No records found')
    for record in records_to_delete:
            db.delete(record)
    db.commit()
    return {"message": f"Records for the  deleted successfully."}

@router.post("/update_price_variance_mappings_records/")
def update_price_variance_mappings_records(payload: PriceVarianceMappingPayload, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update already existing records in update_price_variance_mappings_records table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.price_variance_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(price_variance_task_mapping).filter(price_variance_task_mapping.price_variance_task_id == item.price_variance_task_id,
                                                         price_variance_task_mapping.year==item.year, 
                                                         price_variance_task_mapping.period==item.period,
                                                         price_variance_task_mapping.company_name == item.company_name).update(
                {price_variance_task_mapping.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/summary_price_variance_view/{year}/{country_code}')
def summary_price_variance_year_country_code(year:int,country_code:str,db: Session = Depends(get_db)):
    """Function to fetch all records from summary_price_variance view based on year and country_Code filter """
    try:
        records = db.query(summary_price_variance).filter(
            summary_price_variance.columns.year == year,
            summary_price_variance.columns.country_code == country_code).all()
        return {"summary_solids_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e