"""Home - Dashboard API"""
from schemas import planVolumeUsagePayload
from sqlalchemy import func
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
import models
from models import pc_plan_volume_usage
import period_week_calc
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/dashboard_pc_plan_volume_usage/{year}')
def dashboard_pc_plan_volume_usage_year(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to fetch all records from pc_plan_volume_usage table for a particular year."""
    try:
        records = db.query(pc_plan_volume_usage.plan_volume_id,
                           pc_plan_volume_usage.crop_type,
                           models.category.category_name,
                           pc_plan_volume_usage.period,
                           func.concat('P', pc_plan_volume_usage.period).label("period_with_P"),
                           func.concat('p', pc_plan_volume_usage.period, "W",
                                       pc_plan_volume_usage.week).label("PxW"),
                           pc_plan_volume_usage.week,
                           pc_plan_volume_usage.volume)\
            .join(models.category, models.category.crop_category == pc_plan_volume_usage.crop_type)\
            .filter(pc_plan_volume_usage.year == year)\
            .order_by(pc_plan_volume_usage.crop_type,
                      pc_plan_volume_usage.period,
                      pc_plan_volume_usage.week).all()
        return {"status": "success", "pc_plan_volume_usage_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/update_plan_volume_usage")
def update_plan_volume_usage(payload: planVolumeUsagePayload, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update already existing records in dashboard_pc_plan_volume_usage table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            result = db.query(pc_plan_volume_usage) \
                .filter(pc_plan_volume_usage.crop_type == item.crop_type,
                        pc_plan_volume_usage.period == item.period,
                        pc_plan_volume_usage.week == item.week,
                        pc_plan_volume_usage.year == item.year) \
                .update({pc_plan_volume_usage.volume: item.volume}, synchronize_session='fetch')
            if result == 0:
                raise HTTPException(status_code=404, detail=f"No records found: {item}")
            update_count += 1
        db.commit()
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/create_new_plan_volume_usage/year/{year}")
def update_plan_volume_usage(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to next year data from previous year values."""
    new_records = 0
    try:
        check_pre_data = db.query(pc_plan_volume_usage).filter(pc_plan_volume_usage.year == year).first()
        if check_pre_data is None:
            category_table = db.query(models.category.crop_category, models.category.country).all()
            for crop_category in category_table:
                period = 1
                while period <= 13:  # No. of period
                    week = 1
                    if period_week_calc.calculate_week_num(year, int(period)):
                        total_week = 5
                    else:
                        total_week = 4
                    while week <= total_week:
                        if week == 5:
                            compare_week = week - 1
                        last_year_volume = db.query(pc_plan_volume_usage.volume) \
                            .filter(pc_plan_volume_usage.year == year - 1,
                                    pc_plan_volume_usage.crop_type == crop_category[0],
                                    pc_plan_volume_usage.period == period,
                                    pc_plan_volume_usage.week == compare_week).first()
                        plan_volume_id = str(crop_category[0]) + "#" + str(period) + "#" + str(week) \
                                         + "#" + str(year)
                        payload = {"plan_volume_id": plan_volume_id, "year": year,
                                   "crop_type": crop_category[0], "period": period, "week": week,
                                   "volume": last_year_volume[0]}
                        new_pc_volume = pc_plan_volume_usage(**payload)
                        db.add(new_pc_volume)
                        new_records += 1
                        week += 1
                    period += 1
                    db.commit()
        return {"status": "success", "new_records_created": new_records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

