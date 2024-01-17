from models import off_contract_info, off_contract_task_mapping, country_division_name
from schemas import OffContractInfoSchema, OffContractTaskMappingSchema, OffContractTaskMappingPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()

@router.get('/')
def get_off_contract_info(db: Session = Depends(get_db)):
    """Function to get all records from off_contract_info."""
    query = db.query(off_contract_info).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_info found")
    return {"status": "success", "data": query}

@router.get('/get_off_contract_task_by_id/{off_contract_task_id}')
def get_off_contract_task_by_id(off_contract_task_id: int, db: Session = Depends(get_db)):
    """Function to get a record with off_contract_task_id."""
    query = db.query(off_contract_info).filter(off_contract_info.off_contract_task_id == off_contract_task_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No off_contract_info_id: {off_contract_task_id} found")
    return {"status": "success", "off_contract_task": query}

@router.get('/off_contract_task_mapping/')
def get_off_contract_task_mapping(db: Session = Depends(get_db)):
    """Function to get all records from off_contract_task_mapping."""
    query = db.query(off_contract_task_mapping).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_task_mapping  found")
    return {"status": "success", "data": query}

@router.get('/off_contract_task_mapping_by_year_and_country/{year}/{country}')
def off_contract_task_mapping_by_year_and_country(year: str, country:str, db: Session = Depends(get_db)):
    """Function to get records with year and country"""
    query = db.query(off_contract_task_mapping).filter(off_contract_task_mapping.year==year, off_contract_task_mapping.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}


@router.post("/create_off_contract_task_mapping_for_year/")
async def create_off_contract_task_mapping_for_year(year: int, db: Session = Depends(get_db)):   # pragma: no cover
    """Function to create records in potato_rates table for future records."""
    # Fetch all records from the database
    all_records = db.query(off_contract_info).all()
    countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
    if all_records.count == 0:
        raise HTTPException(status_code=404, detail="No off-contract-info found in the database")
    update_count = 0
    for record in all_records:
        is_exists = db.query(off_contract_task_mapping)\
            .filter(off_contract_task_mapping.year == year,
                    off_contract_task_mapping.off_contract_task_id == record.off_contract_task_id)\
            .first()
        if is_exists:
            return {"status": "error", "Records already exists for Year": year}
        for period in range(1, 14):
            for con in countries:
                new_record = off_contract_task_mapping(off_contract_task_id=record.off_contract_task_id,
                                                       period=period, year=year,
                                                       value=0.001, company_name=con.task_desc)
                db.add(new_record)
                update_count += 1
                db.commit()

    return {"status": "success", "Records added": update_count, "for Year": year}

@router.post('/create_off_contract_info', status_code=status.HTTP_201_CREATED)
def create_off_contract_info(payload: OffContractInfoSchema, db: Session = Depends(get_db)):
    """Function to add new record for create_off_contract_info table"""
    new_record = off_contract_info(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "off_contract_task_id": new_record.off_contract_task_id}

@router.post('/create_off_contract_task_mapping', status_code=status.HTTP_201_CREATED)
def create_off_contract_task_mapping(payload: OffContractTaskMappingSchema, db: Session = Depends(get_db)):
    """Function to add new record for off_contract_task_mapping table"""
    new_record = off_contract_task_mapping(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "row_id": new_record.row_id}

@router.post("/update_off_contract_records/{off_contract_task_id}")
def update_off_contract(off_contract_task_id: int, payload: OffContractTaskMappingSchema,
                        db: Session = Depends(get_db)):
    """Function to update already existing records in off_contract_task_mapping table"""
    existing_records= db.query(off_contract_task_mapping).filter(
        off_contract_task_mapping.off_contract_task_id == off_contract_task_id
    ).first()

    if existing_records is None:
        raise HTTPException(status_code=404, detail="No record found with this f{off_contract_task_id}")

    existing_records.value = payload.value
    existing_records.period = payload.period
    existing_records.year = payload.year

    db.commit()
    db.refresh(existing_records)

    return existing_records

@router.post("/update_off_contract_records/")
def update_off_contract_records(payload: OffContractTaskMappingPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in off_contract_task_mapping table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.off_contract_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(off_contract_task_mapping)\
                .filter(off_contract_task_mapping.off_contract_task_id == item.off_contract_task_id,
                        off_contract_task_mapping.period == item.period,
                        off_contract_task_mapping.year == item.year,
                        off_contract_task_mapping.company_name==item.company_name)\
                .update({off_contract_task_mapping.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

