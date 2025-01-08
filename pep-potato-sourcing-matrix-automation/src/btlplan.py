from models import btl_plan_task_info,btl_plan_task_mapping, country_division_name
from schemas import BTLPlanInfoSchema,BTLPlanTaskMappingPayload,BTLPlanTaskMappingSchema
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_btl_plan_task_info(db: Session = Depends(get_db)): # pragma: no cover
    """Function to get all records from btl_plan_task_info."""
    query = db.query(btl_plan_task_info).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No btl_plan_task_info found")
    return {"status": "success", "data": query}


@router.get('/get_btl_plan_task_mapping_by_year_and_country/{year}/{country}')
def get_btl_plan_task_mapping_by_year_and_country(year: str, country:str,db: Session = Depends(get_db)): # pragma : no cover
    """Function to records from btl_plan_task_mapping with year and Country."""
    query = db.query(btl_plan_task_mapping).filter(btl_plan_task_mapping.year==year, btl_plan_task_mapping.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No btl_plan_task_mapping  found")
    return {"status": "success", "data": query}


@router.post("/create_btl_plan_task_mapping_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_btl_plan_task_mapping_for_next_year(year: int, db: Session = Depends(get_db)):  # pragma : no cover
    """Function to Create btl_plan_task_mapping records for next year."""
    all_records = db.query(btl_plan_task_info).all()
    countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
    update_count = 0
    if all_records.count == 0:
        raise HTTPException(status_code=404, detail="No records found in the database")
    dict_existing_record = []
    existingRecord = db.query(btl_plan_task_mapping)\
        .filter(btl_plan_task_mapping.year == year).all()
    for ex in existingRecord:
        key = str(ex.btl_plan_task_id)+"-"+ex.company_name+"-"+str(ex.period)
        dict_existing_record.append(key)
    for record in all_records: # Iterate over all frieight task info
        for period in range(1,14): # Iterating 1 to 13 periods
            for con in countries: # Iterate through the countries
                isKey = str(record.btl_plan_task_id)+"-"+con.task_desc+"-"+str(period)
                # print(isKey,dict_existing_record)
                if isKey in dict_existing_record:
                    return {"status": "error", "Records already exists for Year": year}
                else:
                    new_record = btl_plan_task_mapping(btl_plan_task_id=record.btl_plan_task_id,
                                                       period=period, year=year,
                                                       value=0, company_name=con.task_desc)
                    db.add(new_record)
                    update_count += 1

    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}


@router.post('/create_btl_plan_task_info', status_code=status.HTTP_201_CREATED)
def create_btl_plan_task_info(payload: BTLPlanInfoSchema, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to add new records in create_btl_plan_task_info table."""
    new_record = btl_plan_task_info(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "btl_plan_task_id": new_record.btl_plan_task_id}

@router.post('/create_btl_plan_task_mapping', status_code=status.HTTP_201_CREATED)
def create_btl_plan_task_mapping(payload: BTLPlanTaskMappingSchema, db: Session = Depends(get_db)): # pragma: no cover
    """Function to add new records in btl_plan_task_mapping table."""
    new_record = btl_plan_task_mapping(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}

@router.post("/update_btl_plan_mapping_records/")
def update_btl_plan_mapping_records(payload: BTLPlanTaskMappingPayload, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update already existing records in btl_plan_task_mapping table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.btl_plan_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(btl_plan_task_mapping).filter(btl_plan_task_mapping.btl_plan_task_id == item.btl_plan_task_id, btl_plan_task_mapping.period==item.period, btl_plan_task_mapping.year==item.year, btl_plan_task_mapping.company_name==item.company_name).update(
                {btl_plan_task_mapping.value: item.value, btl_plan_task_mapping.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))