import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_growing_area(db: Session = Depends(get_db)):
    growing_area = db.query(models.growing_area).filter(models.growing_area.status == "ACTIVE").all()
    if not growing_area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No growing area  found")
    return {"status": "success", "growing_area": growing_area}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_growing_area(payload: schemas.GrowingAreaSchema, db: Session = Depends(get_db)):
    new_area = models.growing_area(**payload.dict())
    db.add(new_area)
    db.commit()
    db.refresh(new_area)
    return {"status": "success", "growing_area_id": new_area.growing_area_id}


@router.get('/{growing_areaId}')
def get_post(growing_areaId: str, db: Session = Depends(get_db)):
    growing_area = db.query(models.growing_area).filter(
        models.growing_area.growing_area_id == growing_areaId).first()
    if not growing_area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Growing area  with this id: {id} found")
    return {"status": "success", "growing-area":  growing_area}


@router.delete('/{growing_areaId}')
def delete_post(growing_areaId: str, db: Session = Depends(get_db)):
    growing_area_query = db.query(models.growing_area).filter(models.growing_area.growing_area_id == growing_areaId).update({'status': 'IN-ACTIVE'})
    if not growing_area_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growing area  with this id: {id} found')

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
