from sqlalchemy import func
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db
import period_week_calc

router = APIRouter()


def trim(string):
    return string.replace(" ", "")


@router.get('/company_name/{name}')
def get_FilteredUsage(name: str, db: Session = Depends(get_db)):
    filter_dict = {
        'US': 'US',
        'US-Core': 'FLUS',
        'Co-Man': 'Co-Man',
        'Canada-Core': 'Canada'
    }
    if filter_dict[name] == 'US' or filter_dict[name] == 'Canada':

        result = db.query(models.View_forecast_pcusage) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
            .join(models.region, models.region.region_id == models.Plant.region_id) \
            .filter(models.region.country == filter_dict[name])\
            .order_by(models.View_forecast_pcusage.columns.plant_id, models.View_forecast_pcusage.columns.year).all()

        Total_Forecast_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.forecasted_value).label('total_forecast_volume'),
                                         models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
            .join(models.region, models.region.region_id == models.Plant.region_id) \
            .filter(models.region.country == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        Total_Actual_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'), models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
            .join(models.region, models.region.region_id == models.Plant.region_id) \
            .filter(models.region.country == 'US') \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        return {"status": "success", "pcusage": result,
                "Total_forecast_Volume": Total_Forecast_Volume,
                "Total_Actual_Volume": Total_Actual_Volume}
    else:
        result = db.query(models.View_forecast_pcusage) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
            .filter(models.Plant.company_name == filter_dict[name])\
            .order_by(models.View_forecast_pcusage.columns.plant_id, models.View_forecast_pcusage.columns.year).all()

        Total_Forecast_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.forecasted_value)
                                         .label('total_forecast_volume'), models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
            .filter(models.Plant.company_name == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        Total_Actual_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value)
                                       .label('total_actual_volume'), models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
            .filter(models.Plant.company_name == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        return {"status": "success", "pcusage": result,
                "Total_forecast_Volume": Total_Forecast_Volume,
                "Total_Actual_Volume": Total_Actual_Volume}


@router.get('/region_id/{region_id}')
def get_FilteredUsage(region_id: int, db: Session = Depends(get_db)):
    result = db.query(models.View_forecast_pcusage) \
        .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
        .filter(models.Plant.region_id == region_id)\
        .order_by(models.View_forecast_pcusage.columns.plant_id, models.View_forecast_pcusage.columns.year).all()

    Total_Forecast_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.forecasted_value)
                                     .label('total_forecast_volume'), models.View_forecast_pcusage.columns.year) \
        .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
        .filter(models.Plant.region_id == region_id) \
        .group_by(models.View_forecast_pcusage.columns.year).all()

    Total_Actual_Volume = db.query(
        func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'),
        models.View_forecast_pcusage.columns.year) \
        .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
        .filter(models.Plant.region_id == region_id) \
        .group_by(models.View_forecast_pcusage.columns.year).all()

    return {"status": "success", "pcusage": result,
            "Total_forecast_Volume": Total_Forecast_Volume,
            "Total_Actual_Volume": Total_Actual_Volume}


@router.get('/period_wise/company_name/{name}')
def getUsage_company_periodWise(name: str, db: Session = Depends(get_db)):
    filter_dict = {
        'US': 'US',
        'US-Core': 'FLUS',
        'Co-Man': 'Co-Man',
        'Canada-Core': 'Canada'
    }
    if filter_dict[name] == 'US' or filter_dict[name] == 'Canada':
        data = db.query(models.View_forecast_pcusage.columns.plant_id,
                        models.View_forecast_pcusage.columns.year,
                        models.View_forecast_pcusage.columns.period,
                        models.View_forecast_pcusage.columns.Period_with_P,
                        models.View_forecast_pcusage.columns.year.label("week"),
                        func.sum(models.View_forecast_pcusage.columns.forecasted_value).label('total_forecast_value'),
                        func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_value')) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
            .join(models.region, models.region.region_id == models.Plant.region_id) \
            .filter(models.region.country == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year, models.View_forecast_pcusage.columns.Period_with_P,
                      models.View_forecast_pcusage.columns.period, models.View_forecast_pcusage.columns.plant_id) \
            .order_by(models.View_forecast_pcusage.columns.plant_id, models.View_forecast_pcusage.columns.year,
                      models.View_forecast_pcusage.columns.Period_with_P).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No Plant found for this category: {name}")

        Total_Forecast_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.forecasted_value).label('total_forecast_volume'),
                                         models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id)\
            .join(models.region, models.region.region_id == models.Plant.region_id) \
            .filter(models.region.country == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        Total_Actual_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'), models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id)\
            .join(models.region, models.region.region_id == models.Plant.region_id) \
            .filter(models.region.country == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        return {"status": "success", "pcusage_period": data,
                "Total_forecast_Volume": Total_Forecast_Volume,
                "Total_Actual_Volume": Total_Actual_Volume}
    else:
        data = db.query(models.View_forecast_pcusage.columns.plant_id,
                        models.View_forecast_pcusage.columns.year,
                        models.View_forecast_pcusage.columns.period,
                        models.View_forecast_pcusage.columns.Period_with_P,
                        models.View_forecast_pcusage.columns.year.label("week"),
                        func.sum(models.View_forecast_pcusage.columns.forecasted_value).label('total_forecast_value'),
                        func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_value')) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id)  \
            .filter(models.Plant.company_name == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year, models.View_forecast_pcusage.columns.Period_with_P,
                      models.View_forecast_pcusage.columns.period, models.View_forecast_pcusage.columns.plant_id) \
            .order_by(models.View_forecast_pcusage.columns.plant_id, models.View_forecast_pcusage.columns.year,
                      models.View_forecast_pcusage.columns.Period_with_P).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No Plant found for this category: {name}")

        Total_Forecast_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.forecasted_value).label('total_forecast_volume'),
                                         models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id)\
            .filter(models.Plant.company_name == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        Total_Actual_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'),
                                       models.View_forecast_pcusage.columns.year) \
            .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id)\
            .filter(models.Plant.company_name == filter_dict[name]) \
            .group_by(models.View_forecast_pcusage.columns.year).all()

        return {"status": "success", "pcusage_period": data,
                "Total_forecast_Volume": Total_Forecast_Volume,
                "Total_Actual_Volume": Total_Actual_Volume}


@router.get('/period_wise/region_id/{region_id}')
def getUsage_periodWise(region_id: int, db: Session = Depends(get_db)):
    data = db.query(models.View_forecast_pcusage.columns.plant_id,
                    models.View_forecast_pcusage.columns.year,
                    models.View_forecast_pcusage.columns.period,
                    models.View_forecast_pcusage.columns.Period_with_P,
                    models.View_forecast_pcusage.columns.year.label("week"),
                    func.sum(models.View_forecast_pcusage.columns.forecasted_value).label('total_forecast_value'),
                    func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_value')) \
        .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
        .filter(models.Plant.region_id == region_id) \
        .group_by(models.View_forecast_pcusage.columns.year, models.View_forecast_pcusage.columns.Period_with_P,
                  models.View_forecast_pcusage.columns.period, models.View_forecast_pcusage.columns.plant_id) \
        .order_by(models.View_forecast_pcusage.columns.plant_id, models.View_forecast_pcusage.columns.year,
                  models.View_forecast_pcusage.columns.Period_with_P).all()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Plant found for this region: {region_id}")

    Total_Forecast_Volume = db.query(func.sum(models.View_forecast_pcusage.columns.forecasted_value).label('total_forecast_volume'),
                                     models.View_forecast_pcusage.columns.year) \
        .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
        .filter(models.Plant.region_id == region_id) \
        .group_by(models.View_forecast_pcusage.columns.year).all()

    Total_Actual_Volume = db.query(
        func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'),
        models.View_forecast_pcusage.columns.year) \
        .join(models.Plant, models.View_forecast_pcusage.columns.plant_id == models.Plant.plant_id) \
        .filter(models.Plant.region_id == region_id) \
        .group_by(models.View_forecast_pcusage.columns.year).all()

    return {"status": "success", "pcusage_period": data,
            "Total_forecast_Volume": Total_Forecast_Volume,
            "Total_Actual_Volume": Total_Actual_Volume}


@router.post('/createNextYear/{year}')
def create_new_pcusage(year: int, db: Session = Depends(get_db)):
    try:
        previous_year = year - 1

        plants = db.query(models.Plant.plant_id, models.Plant.region_id, models.Plant.crop_category_id) \
            .filter(models.Plant.status == "ACTIVE").all()
        # Get all the Plants
        for item in plants:
            category_id = item[2]
            category_name = db.query(models.category.category_name).filter(
                models.category.crop_category == category_id).first()
            # get the category of selected plant
            country = db.query(models.region.country).filter(models.region.region_id == item[1]).first()

            index_value = db.query(models.allocation.period, models.allocation.value).filter(
                models.allocation.category_name == category_name[0], models.allocation.year == year).all()
            # get the index value for that category for all periods

            index_dict = {key: value for key, value in index_value}
            period_value = 1
            while period_value < 14:  # Period_Value
                last_year_actual = db.query(models.View_forecast_pcusage.columns.week,
                                            models.View_forecast_pcusage.columns.total_actual_value) \
                    .filter(models.View_forecast_pcusage.columns.year == previous_year,
                            models.View_forecast_pcusage.columns.plant_id == item[0],
                            models.View_forecast_pcusage.columns.period == period_value).all()
                previous_actual_dict = {key: value for key, value in last_year_actual}
                # get the last year actual value
                week_value = 1
                if period_week_calc.calculate_week_num(year, int(period_value)):
                    no_of_week = 6
                else:
                    no_of_week = 5
                while week_value < no_of_week:
                    prefered_growingarea = db.query(models.plantMtrx_template.growing_area_id) \
                        .filter(models.plantMtrx_template.plant_id == item[0],
                                models.plantMtrx_template.period == period_value,
                                models.plantMtrx_template.week_no == week_value).first()
                    if prefered_growingarea is not None:
                        previous_actual_dict.setdefault(week_value, 0)
                        if week_value == 5:
                            forecasted_value = (previous_actual_dict[week_value-1] * index_dict[period_value]) / 100
                        else:
                            forecasted_value = (previous_actual_dict[week_value] * index_dict[period_value]) / 100
                        # Calculate the forecast value
                        pc_usage_id = str(item[0]) + "#" + str(year) + "#" + str(period_value) + "#" + str(week_value)
                        payload = {"pcusage_id": pc_usage_id, "year": year, "period": period_value, "plant_id": item[0],
                                   "forecasted_value": forecasted_value, "country": trim(country[0]), "week_no": week_value}
                        new_forecast_record = models.pcusage(**payload)
                        db.add(new_forecast_record)
                        week_value += 1
                period_value += 1
            db.commit()

        return {"status": "success", "message": "New forecast records are generated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/temp_insert')
def temp_insert(db: Session = Depends(get_db)):
    try:
        year = 2022

        plants = db.query(models.Plant.plant_id, models.Plant.region_id, models.Plant.crop_category_id) \
            .filter(models.Plant.status == "ACTIVE").all()
        # Get all the Plants
        for item in plants:
            category_id = item[2]
            category_name = db.query(models.category.category_name).filter(
                models.category.crop_category == category_id).first()
            # get the category of selected plant
            country = db.query(models.region.country).filter(models.region.region_id == item[1]).first()

            index_value = db.query(models.allocation.period, models.allocation.value).filter(
                models.allocation.category_name == category_name[0], models.allocation.year == year).all()
            # get the index value for that category for all periods

            index_dict = {key: value for key, value in index_value}

            period_value = 1
            while period_value < 14:  # Period_Value
                # get the last year actual value

                week_value = 1
                limit_week = 4
                if period_value == 13:
                    limit_week = 5
                while week_value <= limit_week:
                    forecasted_value = (40 * 100) / 100
                    # Calculate the forecast value
                    pc_usage_id = str(item[0]) + "#" + str(year) + "#" + str(period_value) + "#" + str(week_value)
                    payload = {"pcusage_id": pc_usage_id, "year": year, "period": period_value, "plant_id": item[0],
                               "forecasted_value": forecasted_value, "country": trim(country[0]), "week_no": week_value}

                    new_forecast_record = models.pcusage(**payload)
                    db.add(new_forecast_record)
                    week_value += 1
                period_value += 1
            db.commit()

        return {"status": "success", "message": "New forecast records are generated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
