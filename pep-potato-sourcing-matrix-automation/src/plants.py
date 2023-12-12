from datetime import date
import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db
import period_week_calc

router = APIRouter()


@router.get('/')
def get_plant(db: Session = Depends(get_db)):
    plant = db.query(models.Plant).filter(models.Plant.status == "ACTIVE").all()
    today_date = date.today()
    res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
    current_period = res['Period']
    current_week = res['week']
    year_data = res['year']
    print(current_period, current_week)
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No plant  found")
    return {"status": "success", "plant": plant,
            "current_period": current_period, "current_week": current_week, "year": year_data}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_plant(payload: schemas.PlantSchema, db: Session = Depends(get_db)):
    new_plant = models.Plant(**payload.dict())
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)
    return {"status": "success", "plants_id": new_plant.plant_id}


@router.get('/{plantId}')
def get_post(plantId: str, db: Session = Depends(get_db)):
    plant = db.query(models.Plant).filter(models.Plant.plant_id == plantId).first()
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No plant with this id: {id} found")
    return {"status": "success", "plant": plant}


@router.delete('/{plantId}')
def delete_post(plantId: str, db: Session = Depends(get_db)):
    plant_query = db.query(models.Plant).filter(models.Plant.plant_id == plantId)
    plant = plant.status = 'IN-ACTIVE'
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No plants  with this id: {id} found')
    db.delete(plant)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
