from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy import func
from fastapi import Depends, HTTPException, status, APIRouter
import schemas
import models
from database import get_db

router = APIRouter()


@router.get('/')
def filtered_extension(db: Session = Depends(get_db)):
    filtered_ext = db.query(models.ExtensionOwnershipMapping).filter(
        or_(
            and_(
                models.ExtensionOwnershipMapping.crop_type == 'Fresh',
                models.ExtensionOwnershipMapping.period >= 11),
            and_(
                models.ExtensionOwnershipMapping.crop_type == 'Storage',
                models.ExtensionOwnershipMapping.period >= 7,
                models.ExtensionOwnershipMapping.period <= 8))).filter(
        models.ExtensionOwnershipMapping.status == "ACTIVE").all()
    if not filtered_ext:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mapping found based on the specified conditions")
    return {"status": "success", "extensionMapping": filtered_ext}


@router.post('/extension_mapping')
def update_extension_mapping(payload: schemas.ExtensionOwnershipPayload,
                             db: Session = Depends(get_db)):
    updateextension = payload.ExtensionData
    input_growing_Area_id = updateextension[0].growing_area_id
    input_crop_year = updateextension[0].crop_year
    update_count = 0
    try:
        max_period_week = max(item.period * 100 + item.week for item in updateextension)
        # print(max_period_week)
        for item in updateextension:
            if item.period < 0:
                (db.query(models.ExtensionOwnershipMapping)
                 .filter(
                    models.ExtensionOwnershipMapping.growing_area_id == item.growing_area_id,
                    models.ExtensionOwnershipMapping.crop_year == item.crop_year)
                 .update({models.ExtensionOwnershipMapping.status: "INACTIVE",
                          models.ExtensionOwnershipMapping.total_value: 0},
                         synchronize_session='fetch'))
                db.commit()
            else:
                print("--------positive input--------")
                record_to_check = db.query(models.ExtensionOwnershipMapping)\
                    .filter(models.ExtensionOwnershipMapping.extension_id == item.extension_id).first()
                print(record_to_check)
                if record_to_check is not None:
                    db.query(models.ExtensionOwnershipMapping).filter(
                        models.ExtensionOwnershipMapping.extension_id == item.extension_id).update(
                        {models.ExtensionOwnershipMapping.total_value: item.total_value,
                         models.ExtensionOwnershipMapping.status: 'ACTIVE'}, synchronize_session=False)
                else:
                    print("--------new input--------")
                    payload = {
                        "extension_id": item.extension_id,
                        "growing_area_id": item.growing_area_id,
                        "crop_year": item.crop_year,
                        "crop_type": item.crop_type,
                        "period": item.period,
                        "week": item.week,
                        "total_value": item.total_value,
                        "status": "ACTIVE"}
                    print(payload)
                    new_records = models.ExtensionOwnershipMapping(**payload)
                    db.add(new_records)
                db.commit()
                print("--------items added --------")
        # Setting status based on the maximum period and week combined value
        db.query(models.ExtensionOwnershipMapping).filter(
            models.ExtensionOwnershipMapping.growing_area_id == input_growing_Area_id,
            models.ExtensionOwnershipMapping.crop_year == input_crop_year,
            models.ExtensionOwnershipMapping.period * 100 + models.ExtensionOwnershipMapping.week > max_period_week
        ).update(
            {models.ExtensionOwnershipMapping.total_value: 0, models.ExtensionOwnershipMapping.status: "INACTIVE"},
            synchronize_session='fetch')

        db.commit()

        final_extension_value = db.query(func.sum(models.ExtensionOwnershipMapping.total_value)
                                         .label('total_value_sum')) \
            .filter(models.ExtensionOwnershipMapping.growing_area_id == input_growing_Area_id,
                    models.ExtensionOwnershipMapping.crop_year == input_crop_year) \
            .group_by(models.ExtensionOwnershipMapping.growing_area_id,
                      models.ExtensionOwnershipMapping.crop_year).first()

        db.query(models.Ownership).filter(models.Ownership.growing_area_id == input_growing_Area_id,
                                          models.Ownership.crop_year == input_crop_year)\
            .update({models.Ownership.extension: final_extension_value[0]}, synchronize_session=False)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

