from datetime import date
from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
from database import get_db
import schemas
import models
import period_week_calc

router = APIRouter()


def trim(string):
    return string.replace(" ", "")


@router.get('/get_all')
def get_allocation(db: Session = Depends(get_db)):
    try:
        data = db.query(models.allocation).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No Category  found")
        return {"status": "success", "category": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/filter/{year}')
def get_FilteredAllocation(year: int, db: Session = Depends(get_db)):
    try:
        data = db.query(models.allocation).filter(models.allocation.year == year).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No Allocation is found for year {year}")
        return {"status": "success", "category": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def getAllPlants(category_name: str, db: Session = Depends(get_db)):
    """Get the Plants List of that category."""
    crop_category_id = db.query(models.category.crop_category) \
        .filter(models.category.category_name == category_name) \
        .first()
    data = db.query(models.Plant.plant_id) \
        .filter(models.Plant.crop_category_id == crop_category_id[0]) \
        .all()
    result_list = [t[0] for t in data]
    return result_list


@router.post('/updateAllocation')
def updateAllocation(payload: schemas.AllocationPayload, db: Session = Depends(get_db)):
    today_date = date.today()
    res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
    current_period = int(res['Period'])
    current_week = int(res['week'])
    year_data = int(res['year'])
    data = payload.data
    update_count = 0
    allocation_id_list = {}
    try:
        for item in data:
            if int(item.year) > year_data:
                allocation_id_list[item.allocation_id] = item.value
                db.query(models.allocation) \
                    .filter(models.allocation.allocation_id == item.allocation_id) \
                    .update({models.allocation.value: int(item.value)},
                            synchronize_session='fetch')
                update_count += 1
                db.commit()

                new_index = int(item.value)
                category_value = item.category_name
                period_value = int(item.period)
                current_year = int(item.year)
                plant_id_list = getAllPlants(category_value, db)
                print(plant_id_list)
                for plant_id in plant_id_list:
                    lastYear_actual_list = {}
                    lastYear_actuals = db.query(models.View_forecast_pcusage.columns.week,
                                                models.View_forecast_pcusage.columns.total_actual_value)\
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

                        db.query(models.pcusage).filter(models.pcusage.plant_id == plant_id,
                                                        models.pcusage.year == current_year,
                                                        models.pcusage.period == period_value,
                                                        models.pcusage.week_no == week_value)\
                            .update({models.pcusage.forecasted_value: new_forecast_value},
                                    synchronize_session=False)
                        db.query(models.plantMtrx)\
                            .filter(models.plantMtrx.plant_id == plant_id,
                                    models.plantMtrx.year == current_year,
                                    models.plantMtrx.period == period_value,
                                    models.plantMtrx.week == week_value)\
                            .update({models.plantMtrx.value: new_forecast_value},
                                    synchronize_session=False)
                        week_value += 1
                        db.commit()
            elif year_data == int(item.year) and current_period < item.period:
                allocation_id_list[item.allocation_id] = item.value
                db.query(models.allocation) \
                    .filter(models.allocation.allocation_id == item.allocation_id) \
                    .update({models.allocation.value: int(item.value)},
                            synchronize_session='fetch')
                update_count += 1
                db.commit()

                new_index = int(item.value)
                category_value = item.category_name
                period_value = int(item.period)
                current_year = int(item.year)
                plant_id_list = getAllPlants(category_value, db)
                print(plant_id_list)
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

                        db.query(models.pcusage).filter(models.pcusage.plant_id == plant_id,
                                                        models.pcusage.year == current_year,
                                                        models.pcusage.period == period_value,
                                                        models.pcusage.week_no == week_value) \
                            .update({models.pcusage.forecasted_value: new_forecast_value},
                                    synchronize_session=False)
                        db.query(models.plantMtrx) \
                            .filter(models.plantMtrx.plant_id == plant_id,
                                    models.plantMtrx.year == current_year,
                                    models.plantMtrx.period == period_value,
                                    models.plantMtrx.week == week_value) \
                            .update({models.plantMtrx.value: new_forecast_value},
                                    synchronize_session=False)
                        week_value += 1
                        db.commit()
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/createNewAllocation/{year}')
def createAllocation(year: int, db: Session = Depends(get_db)):
    category_table = db.query(models.category.category_name, models.category.country).all()
    for category_item in category_table:
        i = 1
        while i <= 13:  # No. of period
            allocation_id = category_item[0] + "#" + str(i) + "#" + str(year)
            payload = {"allocation_id": allocation_id, "category_name": category_item[0], "year": year,
                       "country": trim(category_item[1]), "period": i, "value": 0}
            new_allocation = models.allocation(**payload)
            db.add(new_allocation)
            i += 1
    db.commit()
    return {"Status": "success", "records_inserted": "Next year data are added"}
