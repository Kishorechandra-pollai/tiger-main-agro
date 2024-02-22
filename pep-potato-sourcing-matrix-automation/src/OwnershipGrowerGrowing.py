from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
import schemas
import models

router = APIRouter()


@router.get('/year/{year}')
def get_ownershipMapping(year: int, db: Session = Depends(get_db)):
    grower_growing = db.query(models.OwnershipGrowerGrowing.row_id,
                              models.OwnershipGrowerGrowing.ownership_id,
                              models.OwnershipGrowerGrowing.growing_area_id,
                              models.growers.grower_name,
                              models.OwnershipGrowerGrowing.shrinkage,
                              models.OwnershipGrowerGrowing.contract_erp,
                              models.OwnershipGrowerGrowing.contract,
                              models.OwnershipGrowerGrowing.year,
                              models.OwnershipGrowerGrowing.crop_year)\
        .join(models.growers,
              models.OwnershipGrowerGrowing.grower_id == models.growers.grower_id)\
        .filter(models.OwnershipGrowerGrowing.status == "ACTIVE",
                or_(models.OwnershipGrowerGrowing.year == year,
                    models.OwnershipGrowerGrowing.year == year - 1)).all()
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


@router.delete('/{Growing_area_id}/{Grower_id}/{year}')
def delete_post(Growing_area_id: str, Grower_id, year, db: Session = Depends(get_db)):
    grower_growing = (db.query(models.OwnershipGrowerGrowing).filter(
        models.OwnershipGrowerGrowing.growing_area_id == Growing_area_id,
        models.OwnershipGrowerGrowing.grower_id == Grower_id,
        models.OwnershipGrowerGrowing.year == year, models.OwnershipGrowerGrowing.status == "ACTIVE").first())
    if not grower_growing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No records found')
    db.delete(grower_growing)
    db.commit()
    return {"status": "success",
            "record has been deleted for": f"Grower Id: {Grower_id}, Growing Area Id: {Growing_area_id}"}


@router.post("/update_contract_erp/{crop_year}")
def update_contract_erp(crop_year: str, db: Session = Depends(get_db)):
    try:
        min_crop_year = db.query(func.min(models.View_growing_area_contract_erp.columns.crop_year))\
            .filter(models.View_growing_area_contract_erp.columns.STORAGE_period == crop_year).scalar()
        view_data = (db.query(models.View_growing_area_contract_erp)
                     .filter(models.View_growing_area_contract_erp.columns.STORAGE_period == crop_year,
                             models.View_growing_area_contract_erp.columns.crop_year == min_crop_year)
                     .all())
        if len(view_data) > 0:
            for data in view_data:
                row_id = f"{data.growignarea_id}#{data.grower_id}#{data.STORAGE_period}"
                ownershipId = f"{data.growignarea_id}#{data.STORAGE_period}"
                existing_record = (db.query(models.OwnershipGrowerGrowing)
                                   .filter(
                    models.OwnershipGrowerGrowing.growing_area_id == data.growignarea_id,
                    models.OwnershipGrowerGrowing.grower_id == data.grower_id,
                    models.OwnershipGrowerGrowing.crop_year == crop_year
                ).first())
                if existing_record is not None:
                    db.query(models.OwnershipGrowerGrowing).filter(
                        models.OwnershipGrowerGrowing.growing_area_id == data.growignarea_id,
                        models.OwnershipGrowerGrowing.grower_id == data.grower_id,
                        models.OwnershipGrowerGrowing.crop_year == crop_year
                    ).update({models.OwnershipGrowerGrowing.contract_erp: data.sum_contract,
                              models.OwnershipGrowerGrowing.status: "ACTIVE"})
                else:
                    payload = {"row_id": row_id,
                               "growing_area_id": data.growignarea_id,
                               "grower_id": data.grower_id,
                               "contract": 0,
                               "contract_erp": data.sum_contract,
                               "shrinkage": 0,
                               "year": data.STORAGE_period[:4],
                               "crop_type": data.CROP_TYPE,
                               "crop_year": data.STORAGE_period,
                               "ownership_id": ownershipId,
                               "status": "ACTIVE"}
                    new_record = models.OwnershipGrowerGrowing(**payload)
                    db.add(new_record)
                db.commit()
            return {"message": f"Contract ERP updated for {crop_year}"}
        else:
            return {"message": f"Contract grower level ERP is not available for {crop_year}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")
