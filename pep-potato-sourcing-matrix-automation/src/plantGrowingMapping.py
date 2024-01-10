import schemas
import models
from schemas import PlantGrowingMappingSchema
from models import plant_growing_area_mapping, growing_area
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_plant_growing(db: Session = Depends(get_db)):  # pragma: no cover
    """Function to get all records from plant_growing_area_mapping."""
    query = db.query(plant_growing_area_mapping).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No plantGrowing  found")
    return {"status": "success", "data": query}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_plant_growing_area_mapping(payload: schemas.PlantGrowingMappingSchema, db: Session = Depends(get_db)):  # pragma: no cover
    existingRecord = db.query(models.plant_growing_area_mapping).filter_by(plant_id=payload.plant_id,
                                                                           growing_area_id=payload.growing_area_id).first()
    if existingRecord:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Record already Exists")
    new_areaMapping = models.plant_growing_area_mapping(**payload.dict())
    db.add(new_areaMapping)


def create_plant_growing_area_mapping(payload: PlantGrowingMappingSchema, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to add new record in plant_growing_area_mapping."""
    existing_record = db.query(plant_growing_area_mapping).filter_by(plant_id=payload.plant_id,
                                                                     growing_area_id=payload.growing_area_id).first()
    if existing_record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Record already Exists")
    new_record = plant_growing_area_mapping(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"status": "success", "plant_mapping_id": new_record.plant_mapping_id}


@router.get('/{plantId}')
def get_plantid(plantId: str, db: Session = Depends(get_db)):  # pragma: no cover
    allGrowingAreasPlantwise = (db.query(models.growing_area, models.plant_growing_area_mapping)
                                .join(models.growing_area,
                                      models.growing_area.growing_area_id == models.plant_growing_area_mapping.growing_area_id)
                                .filter(models.plant_growing_area_mapping.plant_id == plantId)).all()

    if not allGrowingAreasPlantwise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No growing Area with this plant_id: {plantId} found")

    return {"status": "success", "allGrowingAreasPlantwise": allGrowingAreasPlantwise}


@router.get('/{growingAreaId}/pid={plantId}')
def get_plant_(growingAreaId: str, plantId: str, db: Session = Depends(get_db)):  # pragma: no cover
    allGrowingAreasPlantwise = (db.query(models.growing_area, models.plant_growing_area_mapping)
                                .join(models.growing_area,
                                      models.growing_area.growing_area_id == models.plant_growing_area_mapping.growing_area_id)
                                .filter(models.plant_growing_area_mapping.plant_id == plantId)
                                .filter(models.plant_growing_area_mapping.growing_area_id == growingAreaId)).all()

    if not allGrowingAreasPlantwise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No growing Area with this growingAreaId: {growingAreaId} found")

    return {"status": "success", "allGrowingAreasPlantwise": allGrowingAreasPlantwise}


@router.get('/{plant_id}')
def get_post_by_plant_id(plant_id: str, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to get record from plant_growing_area_mapping with plant_id."""
    query = (db.query(growing_area, plant_growing_area_mapping)
             .join(growing_area, growing_area.growing_area_id == plant_growing_area_mapping.growing_area_id)
             .filter(plant_growing_area_mapping.plant_id == plant_id)).all()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No growing Area with this plant_id: {plant_id} found")

    return {"status": "success", "details": query}


@router.get('/{growing_area_id}/pid={plant_id}')
def get_post(growing_area_id: str, plant_id: str, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to get record from plant_growing_area_mapping with plant_id and growing_area_id."""
    query = (db.query(growing_area, plant_growing_area_mapping)
             .join(growing_area, growing_area.growing_area_id == plant_growing_area_mapping.growing_area_id)
             .filter(plant_growing_area_mapping.plant_id == plant_id)
             .filter(plant_growing_area_mapping.growing_area_id == growing_area_id)).all()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No growing Area with this growingAreaId: {growing_area_id} found")

    return {"status": "success", "details": query}


@router.delete('/{plant_mapping_id}')
def delete_post(plant_mapping_id: str, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to delete record from plant_growing_area_mapping."""
    plant_query = db.query(plant_growing_area_mapping).get(plant_mapping_id)
    if plant_query:
        db.delete(plant_query)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No plants  with this id: {id} found')

    return Response(status_code=status.HTTP_204_NO_CONTENT)
