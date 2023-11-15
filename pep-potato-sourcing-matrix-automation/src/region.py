import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_region(db: Session = Depends(get_db)):
    region = db.query(models.region).filter(models.region.status == "ACTIVE").all()
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No region found")
    return {"status": "success", "regions": region}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_region(payload: schemas.Region, db: Session = Depends(get_db)):
    new_region = models.region(**payload.dict())
    db.add(new_region)
    db.commit()
    db.refresh(new_region)
    return {"status": "success", "region_id": new_region.region_id}


@router.get('/{regionId}')
def get_post(regionId: str, db: Session = Depends(get_db)):
    region = db.query(models.region).filter(models.region.region_id == regionId).first()
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No region  with this id: {id} found')
    return {"status": "success", "region": region}


@router.delete('/{regionId}')
def delete_post(regionId: str, db: Session = Depends(get_db)):
    region_query = db.query(models.region).filter(models.region.region_id == regionId).update({'status': 'IN-ACTIVE'})
    if not region_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No region  with this id: {id} found')

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/{name}')
def get_region_id(region_name: str, db: Session = Depends(get_db)):
    region = db.query(models.region.region_id).filter(models.region.region_name == region_name,
                                                      models.region.status == "ACTIVE").first()
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No region with this id: {id} found')
    return {"status": "success", "region": region}
