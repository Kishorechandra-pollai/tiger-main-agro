"""Plant_Site_Growing_Area_Mapping API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
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
    