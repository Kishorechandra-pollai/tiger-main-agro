"""Summary SOlid API's"""
# from datetime import datetime, timedelta
from models import solid_task_master, solids_task_mapping, summary_solids
from schemas import SolidTaskMasterSchema, SolidsTaskMappingSchema, SolidsTaskMappingSchemaPayload
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()

@router.get('/')
def get_solid_task_master(db: Session = Depends(get_db)):
    """Function to get all records from solid_task_master."""
    try:
        records = db.query(solid_task_master).all()
        result = [
            {
                "solid_task_id": row.solids_task_id,
                "task_name": row.task_name,
            }
            for row in records
        ]
        return {"details": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/solids_task_mapping_by_year/{year}')
def solids_task_mapping_by_year(year: str, db: Session = Depends(get_db)):
    """Function to get all records from solids_task_mapping based on year."""
    try:
        records = db.query(solids_task_mapping
                           ).filter(solids_task_mapping.year==year).all()
        result = [
            {
                "solid_task_id": row.solids_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
            }
            for row in records
        ]
        return {"details": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/get_total_price_variance')
def get_total_price_variance(db: Session = Depends(get_db)):
    try:
        records = db.query(solids_task_mapping).all()
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


@router.get('/get_solid_task_master/{solids_task_id}')
def get_solid_task_master_byId(solids_task_id: int, db: Session = Depends(get_db)):
    query = db.query(solid_task_master).filter(solid_task_master.solids_task_id == solids_task_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No solids_task_id: {solids_task_id} found")
    return {"status": "success", "details": query}

@router.get('/solid_rate_mappings/')
def get_solids_task_mapping(db: Session = Depends(get_db)):
    """Function to get all records from solids_task_mapping."""
    query = db.query(solids_task_mapping).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solids_task_mapping  found")
    return {"status": "success", "data": query}

@router.get('/solids_task_mapping_by_year/{year}')
def solids_task_mapping_by_year(year: str, db: Session = Depends(get_db)):
    """Function to get all records from solids_task_mapping."""
    query = (db.query(solids_task_mapping.period, func.sum(solids_task_mapping.value).label('prior'),func.sum(solids_task_mapping.value).label('plan'), func.sum(solids_task_mapping.value).label('forcast'))
             .join(solid_task_master, solid_task_master.solids_task_id==solids_task_mapping.solids_task_id)
             .filter(solids_task_mapping.year==year).group_by(solids_task_mapping.year, solids_task_mapping.period).all())

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solids_task_mapping  found")

    return {"status": "success", "data": query}

@router.post("/update_solids_task_mappings/", status_code=status.HTTP_201_CREATED)
async def update_solids_task_mappings(year: int, db: Session = Depends(get_db)):
    """Function to update records in solid_task_master table."""
    # Fetch all records from the database
    all_records = db.query(solid_task_master).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    existingTaskNames = []
    for record in all_records:
        existingRecord = db.query(solids_task_mapping).filter(solids_task_mapping.year==year,solids_task_mapping.solids_task_id==record.solids_task_id ).first()
        if existingRecord:
            existingTaskNames.append(record.task_name)
            continue
        for period in range(1,14):
            new_record = solids_task_mapping(solids_task_id = record.solids_task_id, period=period, year=year, value=0.001)
            db.add(new_record)
            db.commit()

    return {"status": "success", "Records already exists for ":existingTaskNames, "forYear": year}

@router.post('/create_solid_task_master', status_code=status.HTTP_201_CREATED)
def create_solid_task_master(payload: SolidTaskMasterSchema, db: Session = Depends(get_db)):
    new_record = solid_task_master(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "solids_task_id": new_record.solids_task_id}

@router.post('/create_solids_task_mappings', status_code=status.HTTP_201_CREATED)
def create_solid_rate_mappings(payload: SolidsTaskMappingSchema, db: Session = Depends(get_db)):
    new_record = solids_task_mapping(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}

@router.post("/update_solids_task_mapping_records/")
def update_solid_rate_mapping_records(payload: SolidsTaskMappingSchemaPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in solids_task_mapping table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.solids_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(solids_task_mapping).filter(solids_task_mapping.solids_task_id == item.solids_task_id, solids_task_mapping.year==item.year, solids_task_mapping.period==item.period,solids_task_mapping.country_code == item.country_code).update(
                {solids_task_mapping.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/summary_solids_view')
def summary_solids_view(db: Session = Depends(get_db)):
    """Function to fetch all records from summary_solids_view """
    try:
        records = db.query(summary_solids).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "country_code": row.country_code,
                "prior": row.PRIOR,
                "plan": row.PLAN,
                "forecast": row.FORECAST,
                "conversion-factor": row.CF,
                "+/(-) VS PLAN ": row.FORE_PLAN,
                "YAG_Index": row.YAG_Index,
                "M$ IMPACT B/(W) ":row.M_dollar_IMPACT,
                "P*W": f'P{row.period}'
            }
            for row in records
        ]
        return {"summary_solids_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/summary_solids_view/{year}/{country_code}')
def summary_solids_view_year_country_code(year:int,country_code:str,db: Session = Depends(get_db)):
    """Function to fetch all records from summary_solids_view based on year and country_Code filter """
    try:
        records = db.query(summary_solids).filter(
            summary_solids.columns.year == year,
            summary_solids.columns.country_code == country_code).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "country_code": row.country_code,
                "prior": row.PRIOR,
                "plan": row.PLAN,
                "forecast": row.FORECAST,
                "conversion-factor": row.CF,
                "+/(-) VS PLAN ": row.FORE_PLAN,
                "YAG_Index": row.YAG_Index,
                "M$ IMPACT B/(W) ":row.M_dollar_IMPACT,
                "P*W": f'P{row.period}'
            }
            for row in records
        ]
        return {"summary_solids_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e