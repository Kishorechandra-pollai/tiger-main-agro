"""Inflation-Deflation API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import inflation_deflation_task_mappings,country_division_name,inflation_deflation_task
from schemas import InflationDeflationMappingSchema,InflationDeflationMappingPayload
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/inflation_deflation_task_mapping')
def get_inflation_deflation_task_mappings(db: Session = Depends(get_db)):
    """Function to get all records from inflation_deflation_task_mappings"""
    try:
        records = db.query(inflation_deflation_task_mappings).all()
        result = [
            {
                "inflation_deflation_task_id": row.inflation_deflation_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"inflation_deflation_task_mapping": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@router.get('/inflation_deflation_task')
def get_inflation_deflation_task(db: Session = Depends(get_db)):
    """Function to get all records frominflation_deflation_task."""
    try:
        records = db.query(inflation_deflation_task).all()
        result = [
            {
                "inflation_deflation_task_id": row.inflation_deflation_task_id,
                "task_name": row.task_name,
            }
            for row in records
        ]
        return {"inflation_deflation_task": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/inflation_deflation_task_mappings_by_year/{year}/{company_name}')
def inflation_deflation_task_mappings_by_year(year: int,company_name :str, db: Session = Depends(get_db)):
    """Function to get all records from inflation_deflation_task_mappings based on year."""
    try:
        records = db.query(inflation_deflation_task_mappings
                           ).filter(inflation_deflation_task_mappings.year==year,
                                    inflation_deflation_task_mappings.company_name == company_name).all()
        result = [
            {
                "inflation_deflation_task_id": row.inflation_deflation_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"inflation_deflation_task_mappings_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/create_inflation_deflation_task_mappings")
async def create_inflation_deflation_task_mappings(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update records in inflation_deflation_task_mapping table."""
    # Fetch all records from the database
    all_records = db.query(inflation_deflation_task).all()
    countries = db.query(country_division_name).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    existingTaskNames = []
    for record in all_records:
        existingRecord = db.query(inflation_deflation_task_mappings).filter(inflation_deflation_task_mappings.year==year
                                                                            ,inflation_deflation_task_mappings.inflation_deflation_task_id==record.inflation_deflation_task_id ).first()
        if existingRecord:
            existingTaskNames.append(record.task_name)
            continue
        for period in range(1,14):
            for con in countries:
                new_record =inflation_deflation_task_mappings(inflation_deflation_task_id = record.inflation_deflation_task_id, 
                                                              period=period, year=year, value=0.0, company_name=con.division_name)
                db.add(new_record)
                db.commit()

    return {"status": "success", "Records already exists for ":existingTaskNames, "forYear": year}


@router.post("/update_inflation_deflation_task_mappings_records/")
def update_inflation_deflation_task_mappings_records(payload: InflationDeflationMappingPayload, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update already existing records in 
    update_inflation_deflation_task_mappings_records table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.price_variance_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(inflation_deflation_task_mappings).filter(
                inflation_deflation_task_mappings.inflation_deflation_task_id== item.inflation_deflation_task_id,
                inflation_deflation_task_mappings.year==item.year, 
                inflation_deflation_task_mappings.period==item.period).update(
                    {inflation_deflation_task_mappings.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))