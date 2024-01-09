from datetime import date
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
import extensionMapping
import period_week_calc

router = APIRouter()


@router.get('/plant/region_id/{region_id}/year/{year}')
def get_plantMtrx(region_id: int, year: int, db: Session = Depends(get_db)):
    """get plantMtrx data based on region_id input."""
    try:
        data = db.query(models.View_PlantMtrx_table.columns.plant_matrix_id,
                        models.View_PlantMtrx_table.columns.plant_id,
                        models.View_PlantMtrx_table.columns.plant_name,
                        models.View_PlantMtrx_table.columns.period,
                        models.View_PlantMtrx_table.columns.period_with_P,
                        models.View_PlantMtrx_table.columns.week,
                        models.View_PlantMtrx_table.columns.year,
                        models.View_PlantMtrx_table.columns.value,
                        models.View_PlantMtrx_table.columns.growing_area_id,
                        models.View_PlantMtrx_table.columns.growing_area_name) \
            .filter(models.View_PlantMtrx_table.columns.year == year,
                    models.View_PlantMtrx_table.columns.status == 'active',
                    models.View_PlantMtrx_table.columns.region_id == region_id) \
            .order_by(models.View_PlantMtrx_table.columns.plant_id).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Plant Mtrx data not found for region : {region_id}")
        position_data = db.query(models.View_PlantMtrx_position) \
            .filter(models.View_PlantMtrx_position.columns.year == year).all()
        return {"status": "success", "plant_mtrx": data, "position_data": position_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/plant/company_name/{name}/year/{year}')
def get_plantMtrx(name: str, year: int, db: Session = Depends(get_db)):
    """get plantMtrx data based on company_name/country input."""
    filter_dict = {
        'US': 'US',
        'US-Core': 'FLUS',
        'Co-Man': 'Co-Man',
        'Canada-Core': 'Canada'
    }
    try:
        position_data = db.query(models.View_PlantMtrx_position) \
            .filter(models.View_PlantMtrx_position.columns.year == year).all()

        if filter_dict[name] == 'US' or filter_dict[name] == 'Canada':
            data = db.query(models.View_PlantMtrx_table.columns.plant_matrix_id,
                            models.View_PlantMtrx_table.columns.plant_id,
                            models.View_PlantMtrx_table.columns.plant_name,
                            models.View_PlantMtrx_table.columns.period,
                            models.View_PlantMtrx_table.columns.period_with_P,
                            models.View_PlantMtrx_table.columns.week,
                            models.View_PlantMtrx_table.columns.year,
                            models.View_PlantMtrx_table.columns.value,
                            models.View_PlantMtrx_table.columns.growing_area_id,
                            models.View_PlantMtrx_table.columns.growing_area_name) \
                .filter(models.View_PlantMtrx_table.columns.year == year,
                        models.View_PlantMtrx_table.columns.status == 'active',
                        models.View_PlantMtrx_table.columns.country == filter_dict[name]) \
                .order_by(models.View_PlantMtrx_table.columns.plant_id).all()
            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Plant Matrix data not found for : {name}")
        else:
            data = db.query(models.View_PlantMtrx_table.columns.plant_matrix_id,
                            models.View_PlantMtrx_table.columns.plant_id,
                            models.View_PlantMtrx_table.columns.plant_name,
                            models.View_PlantMtrx_table.columns.period,
                            models.View_PlantMtrx_table.columns.period_with_P,
                            models.View_PlantMtrx_table.columns.week,
                            models.View_PlantMtrx_table.columns.year,
                            models.View_PlantMtrx_table.columns.value,
                            models.View_PlantMtrx_table.columns.growing_area_id,
                            models.View_PlantMtrx_table.columns.growing_area_name) \
                .filter(models.View_PlantMtrx_table.columns.year == year,
                        models.View_PlantMtrx_table.columns.status == 'active',
                        models.View_PlantMtrx_table.columns.company_name == filter_dict[name]) \
                .order_by(models.View_PlantMtrx_table.columns.plant_id).all()
            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Plant Mtrx data not found for region : {name}")

        return {"status": "success", "plant_mtrx": data, "position_data": position_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/growing_area/region/{region_id}/year/{year}')
def getplantmtrx_growingarea(region_id: int, year: int, db: Session = Depends(get_db)):
    """get plantMtrx data based on region_id input for growing_area basis."""
    try:
        data = db.query(func.concat(models.View_PlantMtrx_table.columns.growing_area_name, " | ",
                                    models.View_PlantMtrx_table.columns.growing_area_desc)
                        .label("growing_area_name"),
                        models.View_PlantMtrx_table.columns.growing_area_id,
                        models.View_PlantMtrx_table.columns.period,
                        models.View_PlantMtrx_table.columns.period_with_P,
                        models.View_PlantMtrx_table.columns.week,
                        models.View_PlantMtrx_table.columns.year,
                        func.sum(models.View_PlantMtrx_table.columns.value)
                        .label('total_value')) \
            .filter(models.View_PlantMtrx_table.columns.year == year,
                    models.View_PlantMtrx_table.columns.status == 'active',
                    models.View_PlantMtrx_table.columns.ga_region_id == region_id) \
            .group_by(models.View_PlantMtrx_table.columns.year,
                      models.View_PlantMtrx_table.columns.growing_area_desc,
                      models.View_PlantMtrx_table.columns.growing_area_id,
                      models.View_PlantMtrx_table.columns.growing_area_name,
                      models.View_PlantMtrx_table.columns.period_with_P,
                      models.View_PlantMtrx_table.columns.period,
                      models.View_PlantMtrx_table.columns.week).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Plant Mtrx data not found for region : {region_id}")
        return {"status": "success", "plant_mtrx": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/growing_area/country/{name}/year/{year}')
def getplantmtrx_growingarea(name: str, year: int, db: Session = Depends(get_db)):
    """get plantMtrx data based on country input for growing_area basis."""
    try:
        data = db.query(func.concat(models.View_PlantMtrx_table.columns.growing_area_name, " | ",
                                    models.View_PlantMtrx_table.columns.growing_area_desc)
                        .label("growing_area_name"),
                        models.View_PlantMtrx_table.columns.growing_area_id,
                        models.View_PlantMtrx_table.columns.period,
                        models.View_PlantMtrx_table.columns.period_with_P,
                        models.View_PlantMtrx_table.columns.week,
                        models.View_PlantMtrx_table.columns.year,
                        func.sum(models.View_PlantMtrx_table.columns.value)
                        .label('total_value')) \
            .join(models.region,
                  models.View_PlantMtrx_table.columns.ga_region_id == models.region.region_id) \
            .filter(models.View_PlantMtrx_table.columns.year == year,
                    models.View_PlantMtrx_table.columns.status == 'active',
                    models.region.country == name) \
            .group_by(models.View_PlantMtrx_table.columns.year,
                      models.View_PlantMtrx_table.columns.growing_area_desc,
                      models.View_PlantMtrx_table.columns.growing_area_id,
                      models.View_PlantMtrx_table.columns.growing_area_name,
                      models.View_PlantMtrx_table.columns.period_with_P,
                      models.View_PlantMtrx_table.columns.period,
                      models.View_PlantMtrx_table.columns.week).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Plant Mtrx data not found for : {name}")
        return {"status": "success", "plant_mtrx": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/growing_area/all_data/year/{year}')
def getplantmtrx_growingarea_all(year: int, db: Session = Depends(get_db)):
    """get plantMtrx all data for growing_area basis."""
    try:
        data = db.query(func.concat(models.View_PlantMtrx_table.columns.growing_area_name, " | ",
                                    models.View_PlantMtrx_table.columns.growing_area_desc)
                        .label("growing_area_name"),
                        models.View_PlantMtrx_table.columns.growing_area_id,
                        models.View_PlantMtrx_table.columns.period,
                        models.View_PlantMtrx_table.columns.period_with_P,
                        models.View_PlantMtrx_table.columns.week,
                        models.View_PlantMtrx_table.columns.year,
                        func.sum(models.View_PlantMtrx_table.columns.value)
                        .label('total_value')) \
            .filter(models.View_PlantMtrx_table.columns.year == year,
                    models.View_PlantMtrx_table.columns.status == 'active') \
            .group_by(models.View_PlantMtrx_table.columns.year,
                      models.View_PlantMtrx_table.columns.growing_area_desc,
                      models.View_PlantMtrx_table.columns.growing_area_id,
                      models.View_PlantMtrx_table.columns.growing_area_name,
                      models.View_PlantMtrx_table.columns.period_with_P,
                      models.View_PlantMtrx_table.columns.period,
                      models.View_PlantMtrx_table.columns.week).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Plant Mtrx data not found.")
        return {"status": "success", "plant_mtrx": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/only_region_data/year/{year}')
def getplantmtrx_region(year: int, db: Session = Depends(get_db)):
    """get plantMtrx data based on region-wise."""
    try:
        data = db.query(models.View_PlantMtrx_table.columns.region_name,
                        models.View_PlantMtrx_table.columns.period,
                        models.View_PlantMtrx_table.columns.period_with_P,
                        models.View_PlantMtrx_table.columns.week,
                        models.View_PlantMtrx_table.columns.year,
                        func.sum(models.View_PlantMtrx_table.columns.value)
                        .label('totalValue_regionWise')) \
            .filter(models.View_PlantMtrx_table.columns.year == year,
                    models.View_PlantMtrx_table.columns.status == 'active') \
            .group_by(models.View_PlantMtrx_table.columns.year,
                      models.View_PlantMtrx_table.columns.region_id,
                      models.View_PlantMtrx_table.columns.region_name,
                      models.View_PlantMtrx_table.columns.period,
                      models.View_PlantMtrx_table.columns.period_with_P,
                      models.View_PlantMtrx_table.columns.week) \
            .order_by(models.View_PlantMtrx_table.columns.region_id,
                      models.View_PlantMtrx_table.columns.period,
                      models.View_PlantMtrx_table.columns.week).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No data is found for this region:")
        return {"status": "success", "plant_mtrx_regionWise": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def func_getcrop_type(period, week, year, growing_area_id, db: Session = Depends(get_db)):
    fresh_arr = db.query(models.growing_area.fresh_period_start,
                         models.growing_area.fresh_week_start,
                         models.growing_area.fresh_period_end,
                         models.growing_area.fresh_week_end) \
        .filter(models.growing_area.growing_area_id == growing_area_id).first()

    if fresh_arr.fresh_period_start is not None and fresh_arr.fresh_week_start is not None:
        lower_limit = (fresh_arr.fresh_period_start * 4) + fresh_arr.fresh_week_start
        upper_limit = (fresh_arr.fresh_period_end * 4) + fresh_arr.fresh_week_end
    else:
        lower_limit = 22
        upper_limit = 44

    compare_value = (period * 4) + week

    if lower_limit <= compare_value <= upper_limit:
        crop_type = "Fresh"
        crop_year = str(year)
    elif compare_value < lower_limit:
        crop_type = "Storage"
        crop_year = str(year - 1) + "-" + str(year)[-2:]
    else:
        crop_type = "Storage"
        crop_year = str(year) + "-" + str(year + 1)[-2:]

    return crop_type, crop_year


def update_extension(growing_area_id, year, period, week, db: Session = Depends(get_db)):
    """Update the extension value if actual volume is changed."""
    matrix_data = db.query(models.View_Matrix_growingarea.columns.value) \
        .filter(models.View_Matrix_growingarea.columns.growing_area_id == growing_area_id,
                models.View_Matrix_growingarea.columns.year == year,
                models.View_Matrix_growingarea.columns.period == period,
                models.View_Matrix_growingarea.columns.week == week) \
        .first()
    if 6 < period < 9:
        extensionMapping.update_extension_plantMtrx(growing_area_id, year - 1,
                                                    period, week,
                                                    matrix_data[0], db)
    elif 10 < period < 13:
        extensionMapping.update_extension_plantMtrx(growing_area_id, year,
                                                    period, week,
                                                    matrix_data[0], db)


@router.post('/update_plantMtrx')
def update_plantMtrx(payload: schemas.PlantMtrxPayload, db: Session = Depends(get_db)):
    data = payload.data
    update_count = 0
    try:
        for item in data:
            existing_record = db.query(models.plantMtrx).filter(
                models.plantMtrx.plant_matrix_id == item.plant_matrix_id).first()
            if existing_record is None:
                """New record is added to the plantMtrx."""
                region_id = db.query(models.Plant.region_id)\
                    .filter(models.Plant.plant_id == item.plant_id).first()
                crop_type, crop_year = func_getcrop_type(item.period, item.week, item.year,
                                                         item.growing_area_id, db)
                payload = {"plant_matrix_id": item.plant_matrix_id,
                           "plant_id": item.plant_id, "region_id": region_id.region_id,
                           "growing_area_id": item.growing_area_id, "period": item.period,
                           "week": item.week, "year": item.year, "value": item.value,
                           "crop_type": crop_type, "crop_year": crop_year, "status": "active"}
                new_record = models.plantMtrx(**payload)
                db.add(new_record)
            else:
                """Updating growing_area value to the plantMtrx."""
                existing_record.value = item.value
                if item.value == 0:
                    existing_record.status = 'inactive'
                else:
                    existing_record.status = 'active'
            db.commit()
            """Update the extension value if value is changed in extension window."""
            if 6 < item.period < 9:
                update_extension(item.growing_area_id, item.year, item.period, item.week, db)
            elif 10 < item.period < 13:
                update_extension(item.growing_area_id, item.year, item.period, item.week, db)
            update_count += 1
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/createNewMatrix/{year}')
def createnew_plantmatrix(year: int, db: Session = Depends(get_db)):
    """for all plants generate the plant_mtrx from pc_usage data using preferred growing_area"""
    try:
        check_data = db.query(models.plantMtrx.plant_matrix_id).filter(models.plantMtrx.year == year).first()
        record_count = 0
        if check_data is None:
            plant_list = db.query(models.Plant.plant_id, models.Plant.region_id) \
                .filter(models.Plant.status == "ACTIVE").all()
            for plant in plant_list:
                plant_id = plant[0]
                region = plant[1]
                period_value = 1
                while period_value <= 13:
                    week_value = 1
                    if period_week_calc.calculate_week_num(year, int(period_value)):
                        no_of_week = 5
                    else:
                        no_of_week = 4
                    while week_value <= no_of_week:
                        prefered_growingarea = db.query(models.plantMtrx_template.growing_area_id) \
                            .filter(models.plantMtrx_template.plant_id == plant_id,
                                    models.plantMtrx_template.period == period_value,
                                    models.plantMtrx_template.week_no == week_value).first()
                        if prefered_growingarea is not None:
                            total_value = db.query(models.pcusage.forecasted_value) \
                                .filter(models.pcusage.plant_id == plant_id,
                                        models.pcusage.period == period_value,
                                        models.pcusage.week_no == week_value,
                                        models.pcusage.year == year).first()
                            if total_value is None:
                                total_value[0] = 0

                            plantMtrx_id = str(plant_id) + "#" + str(region) + "#" + str(year) + "#" + str(
                                period_value) + "#" + str(week_value) + "#" + str(prefered_growingarea[0])

                            crop_type, crop_year = func_getcrop_type(period_value, week_value, year,
                                                                     prefered_growingarea[0], db)
                            PlantMtrx_payload = {"plant_matrix_id": plantMtrx_id,
                                                 "region_id": region, "plant_id": plant_id,
                                                 "growing_area_id": prefered_growingarea[0],
                                                 "period": period_value, "week": week_value,
                                                 "year": year, "crop_type": crop_type,
                                                 "crop_year": crop_year, "value": total_value[0],
                                                 "status": 'active'}

                            newplantMtrx_record = models.plantMtrx(**PlantMtrx_payload)
                            db.add(newplantMtrx_record)
                            record_count += 1
                            week_value += 1
                        else:
                            week_value += 1
                        db.commit()
                    period_value += 1
        return {"status": "Success", "records create": record_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def update_first_period_data(current_period, current_week, current_year,
                             new_record_count, db: Session = Depends(get_db)):
    """Load actual values in Plant Matrix for first period."""
    records_to_delete = db.query(models.plantMtrx) \
        .filter(models.plantMtrx.period == current_period,
                models.plantMtrx.year == current_year).all()
    for record in records_to_delete:
        db.delete(record)
    db.commit()
    if current_week == -1:
        if period_week_calc.calculate_week_num(current_year, current_period):
            total_week = 5
        else:
            total_week = 4
    else:
        total_week = current_week
    week = 1
    while week <= total_week:
        actual_data_current_week = db.query(models.View_plant_matrix_actual) \
            .filter(models.View_plant_matrix_actual.columns.period_num == current_period,
                    models.View_plant_matrix_actual.columns.week_num == week,
                    models.View_plant_matrix_actual.columns.p_year == current_year) \
            .all()
        if not actual_data_current_week:
            continue
        for item in actual_data_current_week:
            new_record_count += 1
            crop_type, crop_year = func_getcrop_type(item.period_num,
                                                     item.week_num,
                                                     current_year,
                                                     item.growing_area_id, db)
            PlantMtrx_payload = {"plant_matrix_id": item.row_id,
                                 "region_id": item.region_id,
                                 "plant_id": item.Plant_Id,
                                 "growing_area_id": item.growing_area_id,
                                 "period": item.period_num,
                                 "week": item.week_num, "year": item.p_year,
                                 "crop_type": crop_type, "crop_year": crop_year,
                                 "value": item.sumof_rec_potato, "status": 'active'}
            plantMtrx_record = models.plantMtrx(**PlantMtrx_payload)
            db.add(plantMtrx_record)
            db.commit()
            week += 1
    return new_record_count


@router.post('/load_actual_value')
def load_actual_value(db: Session = Depends(get_db)):
    """Load actual values in Plant Matrix."""
    try:
        new_record_count = 0
        today_date = date.today()
        res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
        current_period = int(res['Period'])
        current_week = int(res['week'])
        current_year = int(res['year'])
        if current_period == 1:
            new_record_count = update_first_period_data(13, -1,
                                                        current_year-1,
                                                        new_record_count,
                                                        db)
            new_record_count = update_first_period_data(1, current_week,
                                                        current_year, new_record_count,
                                                        db)
        else:
            lower_limit = (current_period-1)*5+1       #delete all actual value of previous period.
            max_limit = current_period*5+current_week  #current_week value.
            print("lower Limit, max_limit")
            print(lower_limit, max_limit)
            """delete of plant_mtrx_data."""
            records_to_delete = db.query(models.plantMtrx)\
                .filter((models.plantMtrx.period*5)+models.plantMtrx.week >= lower_limit,
                        (models.plantMtrx.period*5)+models.plantMtrx.week <= max_limit,
                        models.plantMtrx.year == today_date.year).all()
            for record in records_to_delete:
                db.delete(record)
            db.commit()
            """Insert new actual volumes in Plant Matrix."""
            period_value = current_period-1
            while period_value <= current_period:
                week_value = 1
                while period_value*5+week_value <= current_period*5+current_week:
                    actual_data_current_week = db.query(models.View_plant_matrix_actual) \
                        .filter(models.View_plant_matrix_actual.columns.period_num == period_value,
                                models.View_plant_matrix_actual.columns.week_num == week_value,
                                models.View_plant_matrix_actual.columns.p_year == today_date.year)\
                        .all()
                    if not actual_data_current_week:
                        continue
                    for item in actual_data_current_week:
                        new_record_count += 1
                        crop_type, crop_year = func_getcrop_type(item.period_num,
                                                                 item.week_num,
                                                                 today_date.year,
                                                                 item.growing_area_id, db)
                        PlantMtrx_payload = {"plant_matrix_id": item.row_id,
                                             "region_id": item.region_id,
                                             "plant_id": item.Plant_Id,
                                             "growing_area_id": item.growing_area_id,
                                             "period": item.period_num,
                                             "week": item.week_num,"year": item.p_year,
                                             "crop_type": crop_type,"crop_year": crop_year,
                                             "value": item.sumof_rec_potato, "status": 'active'}
                        plantMtrx_record = models.plantMtrx(**PlantMtrx_payload)
                        db.add(plantMtrx_record)
                        db.commit()
                        if 6 < item.period_num < 9:
                            update_extension(item.growing_area_id, int(item.p_year),
                                             int(item.period_num), int(item.week_num), db)
                        elif 10 < item.period_num < 13:
                            update_extension(item.growing_area_id, int(item.p_year),
                                             int(item.period_num), int(item.week_num), db)
                    week_value += 1
                period_value += 1
        return {"status": "success", "record_updated": new_record_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.post('/load_previous_data')
# def temp_insert(period: int, year: int, db: Session = Depends(get_db)):
#     try:
#         new_record_count = 0
#         today_date = date.today()
#         res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
#         period_value = period
#         current_week = 1
#         if period_week_calc.calculate_week_num(year, int(period_value)):
#             no_of_week = 5
#         else:
#             no_of_week = 4
#         while current_week <= no_of_week:
#             # delete of forecast data
#             records_to_delete = db.query(models.plantMtrx).filter(models.plantMtrx.period == period_value,
#                                                                   models.plantMtrx.week == current_week,
#                                                                   models.plantMtrx.year == year).all()
#             for record in records_to_delete:
#                 db.delete(record)
#             db.commit()
#             actual_data_current_week = db.query(models.View_plant_matrix_actual) \
#                 .filter(models.View_plant_matrix_actual.columns.period_num == period_value,
#                         models.View_plant_matrix_actual.columns.week_num == current_week,
#                         models.View_plant_matrix_actual.columns.p_year == year).all()
#             for item in actual_data_current_week:
#                 new_record_count += 1
#                 crop_type, crop_year = func_getcrop_type(period_value, current_week, year,
#                                                          item.growing_area_id, db)
#
#                 PlantMtrx_payload = {"plant_matrix_id": item.row_id,
#                                      "region_id": item.region_id, "plant_id": item.Plant_Id,
#                                      "growing_area_id": item.growing_area_id, "period": item.period_num,
#                                      "week": item.week_num, "year": item.p_year, "crop_type": crop_type,
#                                      "crop_year": crop_year, "value": item.sumof_rec_potato, "status": 'active'}
#                 newplantMtrx_record = models.plantMtrx(**PlantMtrx_payload)
#                 db.add(newplantMtrx_record)
#
#             db.commit()
#             current_week += 1
#         return {"status": "success", "record_updated": new_record_count}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


@router.post('/load_previous_data_week_wise')
def temp_insert_week_wise(period: int, week: int, year: int,
                          db: Session = Depends(get_db)):
    """Load previous data based on input week."""
    try:
        new_record_count = 0
        period_value = period
        current_week = week
        records_to_delete = db.query(models.plantMtrx)\
            .filter(models.plantMtrx.period == period_value,
                    models.plantMtrx.week == current_week,
                    models.plantMtrx.year == year).all()
        for record in records_to_delete:
            db.delete(record)
        db.commit()
        actual_data_current_week = db.query(models.View_plant_matrix_actual) \
            .filter(models.View_plant_matrix_actual.columns.period_num == period_value,
                    models.View_plant_matrix_actual.columns.week_num == current_week,
                    models.View_plant_matrix_actual.columns.p_year == year).all()
        for item in actual_data_current_week:
            new_record_count += 1
            crop_type, crop_year = func_getcrop_type(period_value, current_week, year,
                                                     item.growing_area_id, db)

            PlantMtrx_payload = {"plant_matrix_id": item.row_id,
                                 "region_id": item.region_id,
                                 "plant_id": item.Plant_Id,
                                 "growing_area_id": item.growing_area_id,
                                 "period": item.period_num,
                                 "week": item.week_num, "year": item.p_year,
                                 "crop_type": crop_type, "crop_year": crop_year,
                                 "value": item.sumof_rec_potato, "status": 'active'}
            newplantMtrx_record = models.plantMtrx(**PlantMtrx_payload)
            db.add(newplantMtrx_record)
            db.commit()
            if 6 < item.period_num < 9:
                update_extension(item.growing_area_id, int(item.p_year),
                                 int(item.period_num), int(item.week_num), db)
            elif 10 < item.period_num < 13:
                update_extension(item.growing_area_id, int(item.p_year),
                                 int(item.period_num), int(item.week_num), db)
        return {"status": "success", "record_updated": new_record_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/load_previous_2022_year_data')
def prev_year_insert(year: int, db: Session = Depends(get_db)):
    try:
        new_record_count = 0
        today_date = date.today()
        # res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
        period_value = 1
        while period_value <= 13:
            current_week = 1
            if period_week_calc.calculate_week_num(year, int(period_value)):
                no_of_week = 5
            else:
                no_of_week = 4
            while current_week <= no_of_week:
                # delete of forecast data
                records_to_delete = db.query(models.plantMtrx).filter(models.plantMtrx.period == period_value,
                                                                      models.plantMtrx.week == current_week,
                                                                      models.plantMtrx.year == year).all()
                for record in records_to_delete:
                    db.delete(record)
                db.commit()
                actual_data_current_week = db.query(models.View_plant_matrix_actual) \
                    .filter(models.View_plant_matrix_actual.columns.period_num == period_value,
                            models.View_plant_matrix_actual.columns.week_num == current_week,
                            models.View_plant_matrix_actual.columns.p_year == year).all()
                for item in actual_data_current_week:
                    new_record_count += 1
                    crop_type, crop_year = func_getcrop_type(period_value, current_week, year,
                                                             item.growing_area_id, db)

                    PlantMtrx_payload = {"plant_matrix_id": item.row_id,
                                         "region_id": item.region_id, "plant_id": item.Plant_Id,
                                         "growing_area_id": item.growing_area_id, "period": item.period_num,
                                         "week": item.week_num, "year": item.p_year, "crop_type": crop_type,
                                         "crop_year": crop_year, "value": item.sumof_rec_potato, "status": 'active'}
                    newplantMtrx_record = models.plantMtrx(**PlantMtrx_payload)
                    db.add(newplantMtrx_record)

                db.commit()
                current_week += 1
            period_value += 1

        return {"status": "success", "record_updated": new_record_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
