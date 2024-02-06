from sqlalchemy import func
import models
from models import View_forecast_pcusage, Plant
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from database import get_db
import period_week_calc

router = APIRouter()


def trim(string):
    return string.replace(" ", "")


def total_forcast_volume_func(filter_cond, year, db):
    total_forecast_volume = db.query(func.sum(View_forecast_pcusage.columns.forecasted_value)
                                     .label('total_forecast_volume'), View_forecast_pcusage.columns.year) \
        .filter(View_forecast_pcusage.columns.year == year,
                *filter_cond) \
        .group_by(View_forecast_pcusage.columns.year).all()

    return total_forecast_volume


def total_actual_volume_func(filter_cond, year, db):
    total_actual_volume = db.query(func.sum(View_forecast_pcusage.columns.total_actual_value)
                                   .label('total_actual_volume'), View_forecast_pcusage.columns.year) \
        .filter(View_forecast_pcusage.columns.year == year,
                *filter_cond) \
        .group_by(View_forecast_pcusage.columns.year).all()
    return total_actual_volume


def get_filtered_usage_week_common(db, filter_conditions, year, detail_message=None):
    try:
        result = db.query(View_forecast_pcusage) \
            .filter(View_forecast_pcusage.columns.year == year,
                    *filter_conditions) \
            .order_by(View_forecast_pcusage.columns.period,
                      View_forecast_pcusage.columns.week).all()

        total_forecast_volume = total_forcast_volume_func(filter_conditions, year, db)

        total_actual_volume = total_actual_volume_func(filter_conditions, year, db)

        return {"status": "success", "pcusage": result,
                "total_forecast_volume": total_forecast_volume,
                "total_actual_volume": total_actual_volume}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e) or detail_message or "Error processing request")


@router.get('/company_name/{name}/year/{year}')
def get_filtered_usage_by_company_name(name: str, year: int, db: Session = Depends(get_db)):
    filter_dict = {
        'US': 'US',
        'US-Core': 'US-CORE',
        'Co-Man': 'CO-MAN',
        'Canada-Core': 'Canada'
    }
    if filter_dict[name] == 'CO-MAN' or filter_dict[name] == 'US-CORE':
        filter_conditions = [View_forecast_pcusage.columns.company_name == filter_dict[name]]
    else:
        filter_conditions = [View_forecast_pcusage.columns.country == filter_dict[name]]
    return get_filtered_usage_week_common(db, filter_conditions, year,
                                          f"Plant Mtrx data not found for company name: {name}")


@router.get('/region_id/{region_id}/year/{year}')
def get_filtered_usage_by_region_id(region_id: int, year: int, db: Session = Depends(get_db)):
    filter_conditions = [View_forecast_pcusage.columns.region_id == region_id]
    return get_filtered_usage_week_common(db, filter_conditions, year,
                                          f"Plant Mtrx data not found for region ID: {region_id}")


@router.get('/all_week_data/year/{year}')
def get_week_usage_all_data(year: int, db: Session = Depends(get_db)):
    filter_conditions = []
    return get_filtered_usage_week_common(db, filter_conditions, year,
                                          "Plant Mtrx data not found")


def get_filtered_usage_period_common(db, filter_conditions, year, detail_message=None):
    try:
        result = db.query(View_forecast_pcusage.columns.plant_id,
                          View_forecast_pcusage.columns.plant_name,
                          View_forecast_pcusage.columns.year,
                          View_forecast_pcusage.columns.period,
                          View_forecast_pcusage.columns.Period_with_P,
                          View_forecast_pcusage.columns.year.label("week"),
                          func.sum(View_forecast_pcusage.columns.forecasted_value).label('total_forecast_value'),
                          func.sum(View_forecast_pcusage.columns.total_actual_value).label('total_actual_value')) \
            .filter(View_forecast_pcusage.columns.year == year,
                    *filter_conditions) \
            .group_by(View_forecast_pcusage.columns.year,
                      View_forecast_pcusage.columns.Period_with_P,
                      View_forecast_pcusage.columns.plant_name,
                      View_forecast_pcusage.columns.period, View_forecast_pcusage.columns.plant_id) \
            .order_by(View_forecast_pcusage.columns.period).all()

        total_forecast_volume = total_forcast_volume_func(filter_conditions, year, db)

        total_actual_volume = total_actual_volume_func(filter_conditions, year, db)

        return {"status": "success", "pcusage": result,
                "total_forecast_volume": total_forecast_volume,
                "total_actual_volume": total_actual_volume}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e) or detail_message or "Error processing request")


@router.get('/period_wise/company_name/{name}/year/{year}')
def getUsage_company_periodWise(name: str, year: int, db: Session = Depends(get_db)):
    filter_dict = {
        'US': 'US',
        'US-Core': 'US-CORE',
        'Co-Man': 'CO-MAN',
        'Canada-Core': 'Canada'
    }
    if filter_dict[name] == 'CO-MAN' or filter_dict[name] == 'US-CORE':
        filter_conditions = [View_forecast_pcusage.columns.company_name == filter_dict[name]]
    else:
        filter_conditions = [View_forecast_pcusage.columns.country == filter_dict[name]]
    return get_filtered_usage_period_common(db, filter_conditions, year,
                                            f"Plant Mtrx data not found for company name: {name}")


@router.get('/period_wise/region_id/{region_id}/year/{year}')
def getUsage_periodWise(region_id: int, year: int, db: Session = Depends(get_db)):
    filter_conditions = [View_forecast_pcusage.columns.region_id == region_id]
    return get_filtered_usage_period_common(db, filter_conditions, year,
                                            f"Plant Mtrx data not found for region ID: {region_id}")


@router.get('/all_period_data/year/{year}')
def get_week_usage_all_data(year: int, db: Session = Depends(get_db)):
    filter_conditions = []
    return get_filtered_usage_period_common(db, filter_conditions, year,
                                            "Plant Mtrx data not found")


@router.post('/createNextYear/{year}')
def create_new_pcusage(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    try:
        previous_year = year - 1

        plants = db.query(Plant.plant_id, Plant.region_id,
                          Plant.crop_category_id) \
            .filter(Plant.status == "ACTIVE").all()
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
                last_year_actual = db.query(View_forecast_pcusage.columns.week,
                                            View_forecast_pcusage.columns.total_actual_value) \
                    .filter(View_forecast_pcusage.columns.year == previous_year,
                            View_forecast_pcusage.columns.plant_id == item[0],
                            View_forecast_pcusage.columns.period == period_value).all()
                previous_actual_dict = {key: value for key, value in last_year_actual}
                # get the last year actual value
                week_value = 1
                if period_week_calc.calculate_week_num(year, int(period_value)):
                    no_of_week = 6
                else:
                    no_of_week = 5
                while week_value < no_of_week:
                    previous_actual_dict.setdefault(week_value, 0)
                    if week_value == 5:
                        forecasted_value = (previous_actual_dict[week_value - 1] * index_dict[period_value]) / 100
                    else:
                        forecasted_value = (previous_actual_dict[week_value] * index_dict[period_value]) / 100
                    # Calculate the forecast value
                    pc_usage_id = str(item[0]) + "#" + str(year) + "#" + str(period_value) + "#" + str(week_value)
                    payload = {"pcusage_id": pc_usage_id, "year": year, "period": period_value, "plant_id": item[0],
                               "forecasted_value": forecasted_value, "country": trim(country[0]), "week_no": week_value}
                    new_forecast_record = models.pcusage(**payload)
                    db.add(new_forecast_record)
                    week_value += 1
                    db.commit()
                period_value += 1
        return {"status": "success", "message": "New forecast records are generated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.post('/update_forecast_actual/{year}')
# def update_forecast_actual(year: int, db: Session = Depends(get_db)):  # pragma: no cover
#     crop_categories = db.query(models.category.category_name) \
#         .filter(models.category.status == 'Active').all()
#     for crop_category in crop_categories:
#         index_values = db.query(models.allocation).filter()
