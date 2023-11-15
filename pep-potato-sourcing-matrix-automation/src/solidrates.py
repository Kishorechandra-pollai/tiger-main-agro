from datetime import datetime
from models import growing_area, solids_rates, solid_rate_mapping
from schemas import solidRateMappingSchema, solidRateMappingPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

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
    solid_rate = db.query(solids_rates).filter(solids_rates.solids_rate_id == solids_rate_id).first()
    if not solid_rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No solids_rate_id: {solids_rate_id} found")
    return {"status": "success", "solid_rate": solid_rate}


@router.post("/update_solid_rates/", status_code=status.HTTP_201_CREATED)
async def update_solid_rates( db: Session = Depends(get_db)):
    """Function to update records in solids_rates table."""
    # Fetch all records from the database
    all_records = db.query(growing_area).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    year = 2023
    currency=''
    for record in all_records:
        if record.country=='USA':
            currency = 'USD'
        elif record.country=='Canada':
            currency ='CAD'
        existingRecord = db.query(solids_rates).filter_by(year=year,growing_area_id=record.growing_area_id ).first()

        if existingRecord:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Record already Exists")

        new_record = solids_rates(year = year, growing_area_id=record.growing_area_id, currency=currency, created_by="System", updated_by=None, created_time=datetime.now())
        db.add(new_record)
        db.commit()

    return {"status": "success"}

@router.post("/update_solids_rates_with_default_value/", status_code=status.HTTP_201_CREATED)
async def update_solids_rates_with_default_value( db: Session = Depends(get_db)):
    """Function to update records in potato_rates table."""
    # Fetch all records from the database
    all_records = db.query(solids_rates).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    for record in all_records:
        for period in range(1,14):
            new_record = solid_rate_mapping(solids_rate_id = record.solids_rate_id, period=period, rate=0)
            db.add(new_record)
            db.commit()

    return {"status": "success"}

@router.post('/update_solids_rates_from_previous_year/')
def update_solids_rates_from_previous_year(current_year: int, db: Session = Depends(get_db)):
    previous_year = current_year-1
    previous_year_records = db.query(solids_rates.solids_rate_id,  solid_rate_mapping.rate).join(solids_rates, solids_rates.year == previous_year).all()
    if not previous_year_records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No records with this id: {previous_year} found')

    for record in previous_year_records:
        for period in range(1,14):
            new_record = solid_rate_mapping(solids_rate_id = record.solids_rate_id, period=period, rate=record.rate)
            db.add(new_record)
            db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/update_solid_rates_records/")
def update_solid_rates_records(payload: solidRateMappingPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in solid_rate_mapping table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            db.query(solid_rate_mapping).filter(solid_rate_mapping.solids_rate_id == item.solids_rate_id).update(
                {solid_rate_mapping.rate: item.rate, solid_rate_mapping.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/solid_rate_mapping/{year}')
def get_solid_rate_mapping(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(solid_rate_mapping).join(solids_rates,
                                        solids_rates.solids_rate_id == solid_rate_mapping.solids_rate_id).filter(solids_rates.year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}
