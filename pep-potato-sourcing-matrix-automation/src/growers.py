import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_growers(db: Session = Depends(get_db)):
    growers = db.query(models.growers).filter(models.growers.status == "ACTIVE").all()
    if not growers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Growers  found")
    return {"status": "success", "growers": growers}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_growers(payload: schemas.GrowerSchema, db: Session = Depends(get_db)):
    new_growers = models.growers(**payload.dict())
    db.add(new_growers)
    db.commit()
    db.refresh(new_growers)
    return {"status": "success", "growers_id": new_growers.grower_id}


@router.get('/{growerId}')
def get_post(growerId: str, db: Session = Depends(get_db)):
    grower = db.query(models.growers).filter(models.growers.grower_id == growerId).first()
    if not grower:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')
    return {"status": "success", "grower": grower}


@router.delete('/{growerId}')
def delete_post(growerId: str, db: Session = Depends(get_db)):
    grower_query = db.query(models.growers).filter(models.growers.grower_id == growerId).update({'status': 'IN-ACTIVE'})
    if not grower_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
