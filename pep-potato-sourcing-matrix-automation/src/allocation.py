from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
import schemas
from database import get_db
import models

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
    crop_category_id = db.query(models.category.crop_category).filter(models.category.category_name == category_name).first()
    data = db.query(models.Plant.plant_id).filter(models.Plant.crop_category_id == crop_category_id[0]).all()
    result_list = [t[0] for t in data]
    return result_list


@router.post('/updateAllocation')
def updateAllocation(payload: schemas.AllocationPayload, db: Session = Depends(get_db)):
    data = payload.data
    update_count = 0
    allocation_id_list = {}
    try:
        for item in data:
            allocation_id_list[item.allocation_id] = item.value
            db.query(models.allocation).filter(models.allocation.allocation_id == item.allocation_id).update(
                {models.allocation.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()
        # PcUsage data is updated here
        for allocation_item in allocation_id_list:
            new_index = allocation_id_list[allocation_item]
            data_list = allocation_item.split("#")
            category_value = data_list[0]
            period_value = data_list[1]
            current_year = int(data_list[2])
            print(category_value, period_value, current_year)
            plant_id_list = getAllPlants(category_value, db)
            for plant_id in plant_id_list:
                lastYear_actuals = db.query(models.pcusage.actual_value).filter(models.pcusage.plant_id == plant_id,
                                                                                models.pcusage.year == current_year - 1,
                                                                                models.pcusage.period == period_value).all()
                lastYear_actual_list = [t[0] for t in lastYear_actuals]
                week_value = 1
                while week_value < 5:
                    new_forecast_value = (lastYear_actual_list[week_value - 1] * new_index) / 100
                    db.query(models.pcusage).filter(models.pcusage.plant_id == plant_id,
                                                    models.pcusage.year == current_year,
                                                    models.pcusage.period == period_value,
                                                    models.pcusage.week_no == week_value).update(
                        {models.pcusage.forecasted_value: new_forecast_value}, synchronize_session=False)
                    week_value += 1
            db.commit()

            # requirement: index, lastyear_actual of that period, category

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/createNewAllocation/{year}')
def createAllocation(year: int, db: Session = Depends(get_db)):
    category_table = db.query(models.category.category_name, models.category.country).all()
    for category_item in category_table:
        i = 1
        while i < 14:  # No. of period
            allocation_id = category_item[0] + "#" + str(i) + "#" + str(year)
            payload = {"allocation_id": allocation_id, "category_name": category_item[0], "year": year,
                       "country": trim(category_item[1]), "period": i}
            new_allocation = models.allocation(**payload)
            db.add(new_allocation)
            i += 1
    db.commit()
    return {"Status": "success", "records_inserted": "Next year data are added"}



