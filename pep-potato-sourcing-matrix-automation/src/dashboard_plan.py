"""Home - Dashboard Plan API"""
from schemas import pcVolumePlanUsagePayload
from sqlalchemy import func
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
import models
from models import pc_volume_usage_plan
import period_week_calc
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/dashboard_pc_volume_usage_plan/{year}')
def dashboard_pc_volume_usage_plan_year(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to fetch all records from pc_volume_usage_plan table for a particular year."""
    try:
        records = db.query(pc_volume_usage_plan.pc_volume_plan_id,
                           pc_volume_usage_plan.crop_type,
                           models.category.category_name,
                           pc_volume_usage_plan.period,
                           func.concat('P', pc_volume_usage_plan.period).label("period_with_P"),
                           func.concat('p', pc_volume_usage_plan.period, "W",
                                       pc_volume_usage_plan.week).label("PxW"),
                           pc_volume_usage_plan.week,
                           pc_volume_usage_plan.year,
                           pc_volume_usage_plan.volume) \
            .join(models.category, models.category.crop_category == pc_volume_usage_plan.crop_type) \
            .filter(pc_volume_usage_plan.year == year) \
            .order_by(pc_volume_usage_plan.crop_type,
                      pc_volume_usage_plan.period,
                      pc_volume_usage_plan.week).all()
        return {"status": "success", "pc_volume_usage_plan_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/update_plan_volume_usage")
def update_plan_volume_usage(payload: pcVolumePlanUsagePayload, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update already existing records in dashboard_pc_volume_usage_plan table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            result = db.query(pc_volume_usage_plan) \
                .filter(pc_volume_usage_plan.pc_volume_plan_id == item.pc_volume_plan_id) \
                .update({pc_volume_usage_plan.volume: item.volume}, synchronize_session=False)
            if result == 0:
                raise HTTPException(status_code=404, detail=f"No records found: {item.pc_volume_plan_id}")
            update_count += 1
        db.commit()
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/create_new_plan_volume_usage/year/{year}")
def create_new_plan_volume_usage(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to next year data from previous year values."""
    new_records = 0
    try:
        existing_records = db.query(pc_volume_usage_plan).filter(pc_volume_usage_plan.year == year).all()
        if len(existing_records) != 0:
            for record in existing_records:
                db.delete(record)
            db.commit()
        category_table = db.query(models.category.crop_category,
                                  models.category.country,
                                  models.category.category_name).all()
        for crop_category in category_table:
            period = 1
            while period <= 13:  # No. of period
                index = db.query(models.allocation.value) \
                    .filter(models.allocation.category_name == crop_category.category_name,
                            models.allocation.year == year, models.allocation.period == period) \
                    .first()
                # getting index for current year active_allocation table.
                week = 1
                if period_week_calc.calculate_week_num(year, int(period)):
                    total_week = 5
                else:
                    total_week = 4
                while week <= total_week:
                    compare_week = week
                    if week == 5:
                        compare_week = week - 1
                    last_year_volume = db.query(pc_volume_usage_plan.volume) \
                        .filter(pc_volume_usage_plan.year == year - 1,
                                pc_volume_usage_plan.crop_type == crop_category[0],
                                pc_volume_usage_plan.period == period,
                                pc_volume_usage_plan.week == compare_week).first()
                    # Creating next year indexed plan volume
                    new_volume = (last_year_volume[0] * index.value) / 100

                    pc_volume_plan_id = str(crop_category[0]) + "#" + str(period) + "#" + str(week) \
                                     + "#" + str(year)
                    payload = {"pc_volume_plan_id": pc_volume_plan_id, "year": year,
                               "crop_type": crop_category[0],
                               "period": period, "week": week,
                               "volume": new_volume}
                    new_pc_volume = pc_volume_usage_plan(**payload)
                    db.add(new_pc_volume)
                    new_records += 1
                    week += 1
                period += 1
                db.commit()
        return {"status": "success", "new_records_created": new_records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


