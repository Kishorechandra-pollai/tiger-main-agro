from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
import schemas
import models
from datetime import datetime

router = APIRouter()


@router.get('/')
def get_extension(db: Session = Depends(get_db)): # pragma: no cover
    """Get the extension value."""
    filtered_ext = db.query(models.ExtensionOwnershipMapping) \
        .filter(models.ExtensionOwnershipMapping.status == "ACTIVE").all()
    if not filtered_ext:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="No extension for this year.")
    return {"status": "success", "extensionMapping": filtered_ext}


@router.get('/year/{year}')
def filtered_extension(year: int, db: Session = Depends(get_db)):
    """Get the extension value based on the input year."""
    compare_year = str(year)[-2:]
    filtered_ext = db.query(models.ExtensionOwnershipMapping) \
        .filter(models.ExtensionOwnershipMapping.status == "ACTIVE",
                models.ExtensionOwnershipMapping.crop_year.contains(compare_year)).all()
    if not filtered_ext:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="No extension is present for this year.")
    return {"status": "success", "extensionMapping": filtered_ext}


def update_ownership_extension_overlap(growing_area_id: int, crop_year, db):  # pragma: no cover
    if '-' in crop_year:
        get_max_period = db.query(func.max(models.ExtensionOwnershipMapping.period)) \
            .filter(models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                    models.ExtensionOwnershipMapping.status == 'ACTIVE',
                    models.ExtensionOwnershipMapping.crop_year == crop_year).scalar()
        if get_max_period:
            get_max_week = db.query(func.max(models.ExtensionOwnershipMapping.week)) \
                .filter(models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                        models.ExtensionOwnershipMapping.status == 'ACTIVE',
                        models.ExtensionOwnershipMapping.crop_year == crop_year,
                        models.ExtensionOwnershipMapping.period == get_max_period).scalar()
            final_extension_limit = get_max_period * 100 + get_max_week
            print("final_extension_limit:", final_extension_limit)
            ga_fresh = db.query(models.growing_area.fresh_period_start,
                                models.growing_area.fresh_week_start) \
                .filter(models.growing_area.growing_area_id == growing_area_id).first()

            fresh_start = ga_fresh[0] * 100 + ga_fresh[1]
            print("fresh_start:", fresh_start)

            if final_extension_limit >= fresh_start:
                """Update the ownership table with final_extension."""
                new_final_extension = db.query(func.sum(models.ExtensionOwnershipMapping.total_value)
                                               .label('total_value_sum')) \
                    .filter(models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                            models.ExtensionOwnershipMapping.crop_year == crop_year,
                            models.ExtensionOwnershipMapping.period * 100 +
                            models.ExtensionOwnershipMapping.week >= fresh_start) \
                    .group_by(models.ExtensionOwnershipMapping.growing_area_id,
                              models.ExtensionOwnershipMapping.crop_year).first()
                if new_final_extension:
                    db.query(models.Ownership).filter(models.Ownership.growing_area_id == growing_area_id,
                                                      models.Ownership.crop_year == crop_year) \
                        .update({models.Ownership.final_extension: new_final_extension[0]}, synchronize_session=False)
                db.commit()
        else:
            db.query(models.Ownership).filter(models.Ownership.growing_area_id == growing_area_id,
                                              models.Ownership.crop_year == crop_year) \
                .update({models.Ownership.final_extension: 0}, synchronize_session=False)
            db.commit()


def update_final_extension_value(input_growing_Area_id, input_crop_year,
                                 db: Session = Depends(get_db)): # pragma: no cover
    """Update the total extension value in Ownership table."""
    final_extension_value = db.query(func.sum(models.ExtensionOwnershipMapping.total_value)
                                     .label('total_value_sum')) \
        .filter(models.ExtensionOwnershipMapping.growing_area_id == input_growing_Area_id,
                models.ExtensionOwnershipMapping.crop_year == input_crop_year) \
        .group_by(models.ExtensionOwnershipMapping.growing_area_id,
                  models.ExtensionOwnershipMapping.crop_year).first()

    db.query(models.Ownership).filter(models.Ownership.growing_area_id == input_growing_Area_id,
                                      models.Ownership.crop_year == input_crop_year) \
        .update({models.Ownership.extension: final_extension_value[0]}, synchronize_session=False)
    db.commit()
    update_ownership_extension_overlap(input_growing_Area_id, input_crop_year, db)


@router.post('/extension_mapping')
def update_extension_mapping(payload: schemas.ExtensionOwnershipPayload,
                             db: Session = Depends(get_db)):
    """Update the extension value in extension mapping table by user directly."""
    update_extension = payload.ExtensionData
    input_growing_Area_id = update_extension[0].growing_area_id
    input_crop_year = update_extension[0].crop_year
    update_count = 0
    try:
        max_period_week = max(item.period * 100 + item.week for item in update_extension)
        for item in update_extension:
            if item.period < 0:
                (db.query(models.ExtensionOwnershipMapping)
                 .filter(
                    models.ExtensionOwnershipMapping.growing_area_id == item.growing_area_id,
                    models.ExtensionOwnershipMapping.crop_year == item.crop_year)
                 .update({models.ExtensionOwnershipMapping.status: "INACTIVE",
                          models.ExtensionOwnershipMapping.total_value: 0,
                          models.ExtensionOwnershipMapping.split: "false"},
                         synchronize_session='fetch'))
                db.commit()
            else:
                print("--------positive input--------")
                record_to_check = db.query(models.ExtensionOwnershipMapping) \
                    .filter(models.ExtensionOwnershipMapping.extension_id == item.extension_id) \
                    .first()
                print(record_to_check)
                if record_to_check is not None:
                    db.query(models.ExtensionOwnershipMapping).filter(
                        models.ExtensionOwnershipMapping.extension_id == item.extension_id) \
                        .update({models.ExtensionOwnershipMapping.total_value: item.total_value,
                                 models.ExtensionOwnershipMapping.status: 'ACTIVE',
                                 models.ExtensionOwnershipMapping.split: item.split},
                                synchronize_session=False)
                else:  # pragma: no cover
                    payload = {
                        "extension_id": item.extension_id,
                        "growing_area_id": item.growing_area_id,
                        "crop_year": item.crop_year,
                        "crop_type": item.crop_type,
                        "period": item.period,
                        "week": item.week,
                        "total_value": item.total_value,
                        "split": item.split,
                        "year": item.year,
                        "status": "ACTIVE",
                        "updated_time": datetime.now()}
                    new_records = models.ExtensionOwnershipMapping(**payload)
                    db.add(new_records)
                db.commit()
        # Setting status based on the maximum period and week combined value
        db.query(models.ExtensionOwnershipMapping) \
            .filter(models.ExtensionOwnershipMapping.growing_area_id == input_growing_Area_id,
                    models.ExtensionOwnershipMapping.crop_year == input_crop_year,
                    models.ExtensionOwnershipMapping.period * 100 +
                    models.ExtensionOwnershipMapping.week > max_period_week) \
            .update({models.ExtensionOwnershipMapping.total_value: 0,
                     models.ExtensionOwnershipMapping.status: "INACTIVE",
                     models.ExtensionOwnershipMapping.split: "false"},
                    synchronize_session='fetch')
        db.commit()
        update_final_extension_value(input_growing_Area_id, input_crop_year, db)
        return {"status": "success",
                "message": f"Extension updated Successfully for growing_area_id {input_growing_Area_id}"}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


def update_extension_plantMtrx(growing_area_id, year, period, week,
                               value, db: Session = Depends(get_db)): # pragma: no cover
    """Update Extension if PlantMtrx value is changed."""
    ext_record = db.query(models.ExtensionOwnershipMapping) \
        .filter(models.ExtensionOwnershipMapping.status == 'ACTIVE',
                models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                models.ExtensionOwnershipMapping.year == year,
                models.ExtensionOwnershipMapping.period == period,
                models.ExtensionOwnershipMapping.week == week).first()
    if ext_record is None:
        return "No extension"
    if ext_record.split == 'false':
        ext_record.total_value = value
    else:
        if ext_record.total_value > value:
            ext_record.total_value = value
    db.commit()
    update_final_extension_value(growing_area_id, ext_record.crop_year, db)
    return "updated"
