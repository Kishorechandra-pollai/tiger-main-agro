from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
import models
from database import get_db



router = APIRouter()

@router.get('/{period}')
def get_plantid(period: int, db: Session = Depends(get_db)):
    plants = db.query(models.plantMtrx_template).filter(models.plantMtrx_template.period == period).all()
    
    plants_data = [{"plant_id": plant.plant_id,"period": plant.period,"week_no": plant.week_no,"growing_area_id": plant.growing_area_id}for plant in plants]
    for i in plants:
        print(i.period)
        print(i.week_no)
    if not plants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No plant with this id: {id} found")
    return {"status": "success", "plant": plants_data}