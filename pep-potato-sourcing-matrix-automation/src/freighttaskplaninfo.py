from models import freight_task_plan_info, freight_task_plan_mappings, country_division_name
from schemas import FreightTaskPlanInfoSchema, FreightTaskPlanMappingsSchema, FreightTaskPlanMappingsPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_freight_task_plan_info(db: Session = Depends(get_db)): # pragma: no cover
    """Function to get all records from freight_task_plan_info."""
    query = db.query(freight_task_plan_info).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_plan_info found")
    return {"status": "success", "data": query}

@router.get('/get_freight_task_plan_info_byId/{freight_task_plan_id}')
def get_freight_task_plan_info_byId(freight_task_plan_id: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to get a record with freight_task_plan_id."""
    freight_task = db.query(freight_task_plan_info).filter(freight_task_plan_info.freight_task_plan_id == freight_task_plan_id).first()
    if not freight_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No freight_task_plan_info_id: {freight_task_plan_id} found")
    return {"status": "success", "freight_task": freight_task}

@router.get('/get_freight_task_plan_mappings_by_year_and_country/{year}/{country}')
def get_freight_task_plan_mappings_by_year_and_country(year: str, country:str,db: Session = Depends(get_db)):
    """Function to records from freight_task_plan_mappings with year and Country."""
    query = db.query(freight_task_plan_mappings).filter(freight_task_plan_mappings.year==year, freight_task_plan_mappings.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_plan_mappings  found")
    return {"status": "success", "data": query}


@router.post("/create_freight_task_plan_mappings_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_freight_task_plan_mappings_for_next_year(year: int, db: Session = Depends(get_db)):  # pragma : no cover
    """Function to Create freight_task_plan_mappings records for next year."""
    all_records = db.query(freight_task_plan_info).all()
    countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
    update_count = 0
    if all_records.count == 0:
        raise HTTPException(status_code=404, detail="No records found in the database")
    dict_existing_record = []
    existingRecord = db.query(freight_task_plan_mappings)\
        .filter(freight_task_plan_mappings.year == year).all()
    for ex in existingRecord:
        key = str(ex.freight_task_plan_id)+"-"+ex.company_name+"-"+str(ex.period)
        dict_existing_record.append(key)
    for record in all_records: # Iterate over all frieight task info
        for period in range(1,14): # Iterating 1 to 13 periods
            for con in countries: # Iterate through the countries
                isKey = str(record.freight_task_plan_id)+"-"+con.task_desc+"-"+str(period)
                # print(isKey,dict_existing_record)
                if isKey in dict_existing_record:
                    return {"status": "error", "Records already exists for Year": year}
                else:
                    new_record = freight_task_plan_mappings(freight_task_plan_id=record.freight_task_plan_id,
                                                       period=period, year=year,
                                                       value=0, company_name=con.task_desc)
                    db.add(new_record)
                    update_count += 1

    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}


@router.post('/create_freight_task_plan_info', status_code=status.HTTP_201_CREATED)
def create_freight_task_plan_info(payload: FreightTaskPlanInfoSchema, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to add new records in create_freight_task_plan_info table."""
    new_record = freight_task_plan_info(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "freight_task_plan_id": new_record.freight_task_plan_id}

@router.post('/create_freight_task_plan_mappings', status_code=status.HTTP_201_CREATED)
def create_freight_task_plan_mappings(payload: FreightTaskPlanMappingsSchema, db: Session = Depends(get_db)): # pragma: no cover
    """Function to add new records in freight_task_plan_mappings table."""
    new_record = freight_task_plan_mappings(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}

@router.post("/update_freight_task_plan_mapping_records/")
def update_freight_task_plan_mapping_records(payload: FreightTaskPlanMappingsPayload, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update already existing records in freight_task_plan_mappings table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.freight_task_plan_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(freight_task_plan_mappings).filter(freight_task_plan_mappings.freight_task_plan_id == item.freight_task_plan_id, freight_task_plan_mappings.period==item.period, freight_task_plan_mappings.year==item.year, freight_task_plan_mappings.company_name==item.company_name).update(
                {freight_task_plan_mappings.value: item.value, freight_task_plan_mappings.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

