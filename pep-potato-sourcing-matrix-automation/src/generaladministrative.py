from models import general_administrative_task, general_administrative_mappings, country_division_name
from schemas import GeneralAdministrativeTaskSchema, GeneralAdministrativeMappingsPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_general_administrative_task_info(db: Session = Depends(get_db)):
    """Function to get all records from freight_task_info."""
    query = db.query(general_administrative_task).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_info found")
    return {"status": "success", "data": query}


# @router.get('/getBygeneral_administrative_id/{general_administrative_id}')
# def getBygeneral_administrative_id(general_administrative_id: int, db: Session = Depends(get_db)):
#     general_administrative = db.query(general_administrative_task).filter(general_administrative_task.general_administrative_id == general_administrative_id).first()
#     if not general_administrative:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"No general_administrative_id: {general_administrative_id} found")
#     return {"status": "success", "general_administrative": general_administrative}

# @router.get('/general_administrative_mappings/')
# def get_general_administrative_mappings(db: Session = Depends(get_db)):
#     """Function to get all records from potato_rate_mapping."""
#     query = db.query(general_administrative_mappings).all()
#     if not query:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail="No general_administrative_mappings  found")
#     return {"status": "success", "data": query}

@router.get('/general_administrative_mappings_by_year/{year}/{country}')
def general_administrative_mappings_by_year(year: str, country: str, db: Session = Depends(get_db)):
    """Function to get all records from general_administrative_mappings."""
    query = db.query(general_administrative_mappings).filter(general_administrative_mappings.year == year,
                                                             general_administrative_mappings.company_name == country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}


@router.post("/update_general_administrative_mappings/", status_code=status.HTTP_201_CREATED)
async def update_general_administrative_mappings(year: int, db: Session = Depends(get_db)):# pragma: no cover
    """Function to update records in potato_rates table."""
    # Fetch all records from the database
    all_records = db.query(general_administrative_task).all()
    countries = db.query(country_division_name).all()
    # Ensure there are records in the database
    if all_records.count == 0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    existingTaskNames = []
    for record in all_records:
        existingRecord = db.query(general_administrative_mappings).filter(general_administrative_mappings.year == year,
                                                                          general_administrative_mappings.general_administrative_id == record.general_administrative_id).first()
        if existingRecord:
            existingTaskNames.append(record.task_name)
            continue
        for period in range(1, 14):
            for con in countries:
                new_record = general_administrative_mappings(general_administrative_id=record.general_administrative_id,
                                                             period=period, year=year, value=0.001,
                                                             company_name=con.task_desc)
                db.add(new_record)
                db.commit()

    return {"status": "success", "Records already exists for ": existingTaskNames, "forYear": year}


@router.post('/create_general_administrative_task', status_code=status.HTTP_201_CREATED)
def create_general_administrative_task(payload: GeneralAdministrativeTaskSchema, db: Session = Depends(get_db)): # pragma: no cover
    new_record = general_administrative_task(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "general_administrative_id": new_record.general_administrative_id}


@router.post("/update_general_administrative_records/")
def update_general_administrative_records(payload: GeneralAdministrativeMappingsPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in update_general_administrative_records table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.general_administrative_id <= 0 or item.period <= 0 or item.year <= 0:
                return {"status": "error", "message": "Please check details"}
            db.query(general_administrative_mappings).filter(
                general_administrative_mappings.general_administrative_id == item.general_administrative_id,
                general_administrative_mappings.period == item.period,
                general_administrative_mappings.year == item.year,
                general_administrative_mappings.company_name == item.company_name).update(
                {general_administrative_mappings.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_general_administrative_mappings_for_next_year/{year}")
async def create_g_and_a_mappings_for_next_year(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to create records with given year for each country and general_administrative_task and add into
    general_administrative_mappings table."""

    all_records = db.query(general_administrative_task).all()
    countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
    update_count = 0
    if all_records.count == 0:
        raise HTTPException(status_code=404, detail="No records found in the database")
    dict_existing_record = []
    existingRecord = db.query(general_administrative_mappings) \
        .filter(general_administrative_mappings.year == year).all()
    for ex in existingRecord:
        key = str(ex.general_administrative_id) + "-" + ex.company_name + "-" + str(ex.period)
        dict_existing_record.append(key)
    for record in all_records:  # Iterate over all frieight task info
        for period in range(1, 14):  # Iterating 1 to 13 periods
            for con in countries:  # Iterate through the countries
                isKey = str(record.general_administrative_id) + "-" + con.task_desc + "-" + str(period)
                # print(isKey,dict_existing_record)
                if isKey in dict_existing_record:
                    return {"status": "error", "Records already exists for Year": year}
                else:
                    new_record = general_administrative_mappings(
                        general_administrative_id=record.general_administrative_id,
                        period=period, year=year, value=0,
                        company_name=con.task_desc)
                    db.add(new_record)
                    update_count += 1

    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}
