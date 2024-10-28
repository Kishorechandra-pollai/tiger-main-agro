from datetime import date
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from database import get_db
import schemas
import models
import period_week_calc
import plant_mtrx

router = APIRouter()


def trim(string): # pragma: no cover
    """trim function"""
    return string.replace(" ", "")


@router.get('/year/{year}')
def get_filtered_allocation(year: int, db: Session = Depends(get_db)): # pragma: no cover
    """get api for allocation index based on input year."""
    try:
        data = db.query(models.allocation).filter(models.allocation.year == year).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No Allocation is found for year {year}")
        return {"status": "success", "category": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_all_plants(category_name: str, db: Session = Depends(get_db)):  # pragma: no cover
    """Get the Plants List of that category."""
    crop_category_id = db.query(models.category.crop_category) \
        .filter(models.category.category_name == category_name) \
        .first()
    data = db.query(models.Plant.plant_id) \
        .filter(models.Plant.crop_category_id == crop_category_id[0],
                models.Plant.status == 'ACTIVE') \
        .all()
    result_list = [t[0] for t in data]
    return result_list


def update_only_allocation(allocation_id, index, db: Session = Depends(get_db)):  # pragma: no cover
    """function to update index values in active_allocation table."""
    db.query(models.allocation) \
        .filter(models.allocation.allocation_id == allocation_id) \
        .update({models.allocation.value: float(index)},
                synchronize_session='fetch')
    db.commit()


def update_volume(is_actual_update, item, db: Session = Depends(get_db)):  # pragma: no cover
    """Function updates forecast and plantMtrx volume."""
    new_index = float(item.value)
    category_value = item.category_name
    period_value = int(item.period)
    current_year = int(item.year)
    plant_id_list = get_all_plants(category_value, db)
    for plant_id in plant_id_list:
        lastYear_actual_list = {}
        lastYear_actuals = db.query(models.View_forecast_pcusage.columns.week,
                                    models.View_forecast_pcusage.columns.total_actual_value) \
            .filter(models.View_forecast_pcusage.columns.plant_id == plant_id,
                    models.View_forecast_pcusage.columns.year == current_year - 1,
                    models.View_forecast_pcusage.columns.period == period_value).all()
        if not lastYear_actuals:
            continue
        lastYear_actual_list = {key: value for key, value in lastYear_actuals}
        week_value = 1
        if period_week_calc.calculate_week_num(current_year, int(period_value)):
            no_of_week = 6
        else:
            no_of_week = 5
        while week_value < no_of_week:
            lastYear_actual_list.setdefault(week_value, 0)
            if week_value == 5:
                new_forecast_value = (lastYear_actual_list[week_value - 1] * new_index) / 100
            else:
                new_forecast_value = (lastYear_actual_list[week_value] * new_index) / 100
            forecast_record = db.query(models.pcusage) \
                .filter(models.pcusage.plant_id == plant_id,
                        models.pcusage.year == current_year,
                        models.pcusage.period == period_value,
                        models.pcusage.week_no == week_value).first()
            if forecast_record is None:
                week_value += 1
                continue
            forecast_record.forecasted_value = new_forecast_value
            db.commit()
            if is_actual_update:
                plant_matrix = db.query(models.plantMtrx) \
                    .filter(models.plantMtrx.plant_id == plant_id,
                            models.plantMtrx.year == current_year,
                            models.plantMtrx.period == period_value,
                            models.plantMtrx.week == week_value).first()
                if plant_matrix is None:
                    week_value += 1
                    continue
                plant_matrix.value = new_forecast_value
                db.commit()
                """Update Extension values if present."""
                if 6 < period_value < 9:
                    plant_mtrx.update_extension(plant_matrix.growing_area_id,
                                                current_year, period_value,
                                                week_value, db)
                elif 10 < period_value < 13:
                    plant_mtrx.update_extension(plant_matrix.growing_area_id,
                                                current_year, period_value,
                                                week_value, db)
            week_value += 1


@router.post('/updateAllocation')
def update_allocation(payload: schemas.AllocationPayload, db: Session = Depends(get_db)):  # pragma: no cover
    """Main function when index value is changed."""
    today_date = date.today()
    res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
    current_period = int(res['Period'])
    year_data = int(res['year'])
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if int(item.year) > year_data:
                update_only_allocation(item.allocation_id, item.value, db)
                update_count += 1
                """Below function updates forecast and plantMtrx volume."""
                update_volume(False, item, db)
            elif year_data == int(item.year) and current_period < item.period:
                update_only_allocation(item.allocation_id, item.value, db)
                update_count += 1
                update_volume(False, item, db)
            else:
                update_only_allocation(item.allocation_id, item.value, db)
                update_count += 1
                update_volume(False, item, db)
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/createNewAllocation/{year}')
def create_allocation(year: int, db: Session = Depends(get_db)):
    """Create next year allocation table with index as zero."""
    records_count = 0
    category_table = db.query(models.category.category_name, models.category.country)\
        .filter(models.category.status == 'Active').all()
    for category_item in category_table:
        i = 1
        while i <= 13:  # No. of period
            allocation_id = category_item[0] + "#" + str(i) + "#" + str(year)
            payload = {"allocation_id": allocation_id, "category_name": category_item[0], "year": year,
                       "country": trim(category_item[1]), "period": i, "value": 100}
            new_allocation = models.allocation(**payload)
            db.add(new_allocation)
            i += 1
            records_count += 1
    db.commit()
    return {"Status": "success", "new_records": records_count}
