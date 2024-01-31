"""Plant_Site_Growing_Area_Mapping API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
import models
from models import PlantSiteGrowingAreaMapping
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/get_plant_site_gowing_area_mapping')
def view_plant_site_growing_area(db: Session = Depends(get_db)):  # pragma: no cover
    """Function to fetch all records from PlantSiteGrowingAreaMapping table """
    try:
        records = db.query(PlantSiteGrowingAreaMapping).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/{growing_area_id}')
def get_plantid(growing_area_id: int, db: Session = Depends(get_db)):
    plants = db.query(models.PlantSiteGrowingAreaMapping).filter(models.PlantSiteGrowingAreaMapping.growing_area_id == growing_area_id).all()
    
    plants_data = [{"plant_name": plant.plant_name,"growing_area": plant.growing_area,"plant_id": plant.plant_id,"growing_area_id": plant.growing_area_id}for plant in plants]
    for i in plants:
        print(i.plant_name)
        print(i.growing_area_id)
    if not plants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No plant with this id: {id} found")
    return {"status": "success", "plant": plants_data}
    