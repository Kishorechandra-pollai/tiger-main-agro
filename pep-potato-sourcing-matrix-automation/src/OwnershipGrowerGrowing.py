import schemas
import models
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_grower_growing(db: Session = Depends(get_db)):
    grower_growing = db.query(models.OwnershipGrowerGrowing).all()
    if not grower_growing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No mapping  found")
    return {"status": "success", "grower_growing": grower_growing}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_grower_growing_area_mapping(payload: schemas.OwnershipGrowerGrowingSchema, db: Session = Depends(get_db)):
    ext_grower_id = payload.grower_id
    ext_growing_area_id = payload.growing_area_id
    ext_year = payload.year
    existing_record = (db.query(models.OwnershipGrowerGrowing).filter(
        models.OwnershipGrowerGrowing.growing_area_id == ext_growing_area_id,
        models.OwnershipGrowerGrowing.grower_id == ext_grower_id,
        models.OwnershipGrowerGrowing.year == ext_year).first())
    if existing_record:
        return {"message": "record exist"}
    else:
        new_GrowerMapping = models.OwnershipGrowerGrowing(**payload.dict())
        db.add(new_GrowerMapping)
    db.commit()
    db.refresh(existing_record if existing_record else new_GrowerMapping)

    return {
        "status": "success",
        "grower_growing_mapping_id": (
            existing_record if existing_record else new_GrowerMapping).growing_area_id_mapper_id
    }


@router.get('/{GrowingAreaId}/{GrowerId}/{year}')
def get_post(GrowingAreaId: str, GrowerId, year, db: Session = Depends(get_db)):
    Growers_GrowingArea_yearWise = (db.query(models.growers, models.OwnershipGrowerGrowing)
                                    .join(models.growers,
                                          models.growers.grower_id == models.OwnershipGrowerGrowing.grower_id)
                                    .filter(models.OwnershipGrowerGrowing.growing_area_id == GrowingAreaId,
                                            models.OwnershipGrowerGrowing.grower_id == GrowerId,
                                            models.OwnershipGrowerGrowing.year == year).all())
    if not Growers_GrowingArea_yearWise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No records found")

    return {"status": "success", "Growers_GrowingAreaWise": Growers_GrowingArea_yearWise}


@router.delete('/{Growing_area_id}/{Grower_id}/{year}')
def delete_post(Growing_area_id: str, Grower_id, year, db: Session = Depends(get_db)):
    grower_growing = (db.query(models.OwnershipGrowerGrowing).filter(
        models.OwnershipGrowerGrowing.growing_area_id == Growing_area_id,
        models.OwnershipGrowerGrowing.grower_id == Grower_id,
        models.OwnershipGrowerGrowing.year == year).first())
    if not grower_growing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No records found')
    db.delete(grower_growing)
    db.commit()
    return {"status": "success",
            "record has been deleted for": f"Grower Id: {Grower_id}, Growing Area Id: {Growing_area_id}"}


# @router.delete('/{year}')
# def delete_post(year: str, db: Session = Depends(get_db)):
#     year_records = (
#         db.query(models.OwnershipGrowerGrowing).filter(models.OwnershipGrowerGrowing.year == year).all())
#     if not year_records:
#         raise HTTPException(status_code=404, detail=f'No records found for year: {year}')
#     for record in year_records:
#         db.delete(record)
#     db.commit()
#     return {"status": "success",
#             "record has been deleted for year": {year}}
#

# @router.post('/updateContractedValue')
# def update_Contracted(payload: schemas.UpdateOwnershipGrowerGrowing, db: Session = Depends(get_db)):
#     data = payload.DataOGG
#     update_count = 0
#     try:
#         for item in data:
#             db.query(models.OwnershipGrowerGrowing).filter(
#                 models.OwnershipGrowerGrowing.grower_id == item.grower_id,
#                 models.OwnershipGrowerGrowing.growing_area_id == item.growing_area_id,
#                 models.OwnershipGrowerGrowing.year == item.year).update(
#                 {models.OwnershipGrowerGrowing.contract: item.contract},
#                 synchronize_session='fetch')
#             update_count += 1
#         db.commit()
#         return {"status": "success", "records_updated": update_count}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post('/updateshrinkage')
# def update_Shrinkage(payload: schemas.UpdateOwnershipGrowerGrowing, db: Session = Depends(get_db)):
#     data = payload.DataOGG
#     update_count = 0
#     try:
#         for item in data:
#             db.query(models.OwnershipGrowerGrowing).filter(
#                 models.OwnershipGrowerGrowing.grower_id == item.grower_id,
#                 models.OwnershipGrowerGrowing.growing_area_id == item.growing_area_id,
#                 models.OwnershipGrowerGrowing.year == item.year).update(
#                 {models.OwnershipGrowerGrowing.shrinkage: item.shrinkage},
#                 synchronize_session='fetch')
#             update_count += 1
#         db.commit()
#         return {"status": "success", "records_updated": update_count}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))



