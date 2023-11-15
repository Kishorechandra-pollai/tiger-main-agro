import schemas
import models
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, func
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/plant/region_id/{region_id}')
def get_plantMtrx(region_id: int, db: Session = Depends(get_db)):
    try:
        data = db.query(models.plantMtrx, func.concat("P", models.plantMtrx.period).label("period_with_P"))\
            .join(models.Plant, models.plantMtrx.plant_id == models.Plant.plant_id)\
            .filter(models.Plant.region_id == region_id).all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Plant Mtrx data not found for region : {region_id}")

        # Extract the results as dictionaries and build the response
        result = [
            {
                "plant_matrix_id": row.plantMtrx.plant_matrix_id,
                "period": row.plantMtrx.period,
                "value": row.plantMtrx.value,
                "week": row.plantMtrx.week,
                "plant_id": row.plantMtrx.plant_id,
                "year": row.plantMtrx.year,
                "growing_area_id": row.plantMtrx.growing_area_id,
                "period_with_P": row.period_with_P
            }
            for row in data
        ]
        return {"status": "success", "plant_mtrx": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/plant/company_name/{name}')
def get_plantMtrx(name: str, db: Session = Depends(get_db)):
    filter_dict = {
        'US': 'US',
        'US-Core': 'Frito',
        'Co-Man': 'Co-Man'
    }
    try:
        if filter_dict[name] == 'US':
            data = db.query(models.plantMtrx, func.concat("P", models.plantMtrx.period).label("period_with_P"))\
                .join(models.Plant, models.plantMtrx.plant_id == models.Plant.plant_id)\
                .join(models.region, models.Plant.region_id == models.region.region_id)\
                .filter(models.region.country == filter_dict[name]).all()
            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Plant Matrix data not found for : {name}")

            # Extract the results as dictionaries and build the response
            result = [
                {
                    "plant_matrix_id": row.plantMtrx.plant_matrix_id,
                    "period": row.plantMtrx.period,
                    "value": row.plantMtrx.value,
                    "week": row.plantMtrx.week,
                    "plant_id": row.plantMtrx.plant_id,
                    "year": row.plantMtrx.year,
                    "growing_area_id": row.plantMtrx.growing_area_id,
                    "period_with_P": row.period_with_P
                }
                for row in data
            ]
            return {"status": "success", "plant_mtrx": result}
        else:
            data = db.query(models.plantMtrx, func.concat("P", models.plantMtrx.period).label("period_with_P")) \
                .join(models.Plant, models.plantMtrx.plant_id == models.Plant.plant_id)  \
                .filter(models.Plant.company_name == filter_dict[name]).all()
            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Plant Mtrx data not found for region : {name}")

            # Extract the results as dictionaries and build the response
            result = [
                {
                    "plant_matrix_id": row.plantMtrx.plant_matrix_id,
                    "period": row.plantMtrx.period,
                    "value": row.plantMtrx.value,
                    "week": row.plantMtrx.week,
                    "plant_id": row.plantMtrx.plant_id,
                    "year": row.plantMtrx.year,
                    "growing_area_id": row.plantMtrx.growing_area_id,
                    "period_with_P": row.period_with_P
                }
                for row in data
            ]
            return {"status": "success", "plant_mtrx": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/growing_area/region/{region_id}')
def getPlantMtrx_growingArea(region_id: int, db: Session = Depends(get_db)):
    try:
        data = db.query(
            models.plantMtrx.growing_area_id,
            models.plantMtrx.year,
            models.plantMtrx.week,
            models.plantMtrx.period,
            func.concat("P", models.plantMtrx.period).label("period_with_P"),
            func.sum(models.plantMtrx.value).label('total_value'))\
            .join(models.growing_area, models.plantMtrx.growing_area_id == models.growing_area.growing_area_id)\
            .filter(models.growing_area.region == region_id) \
            .group_by(models.plantMtrx.year, models.plantMtrx.growing_area_id, models.plantMtrx.period, models.plantMtrx.week) \
            .order_by(models.plantMtrx.growing_area_id, models.plantMtrx.period, models.plantMtrx.week).all()

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Plant Mtrx data not found for region : {region_id}")
        return {"status": "success", "plant_mtrx": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/growing_area/country/{name}')
def getPlantMtrx_growingArea(name: str, db: Session = Depends(get_db)):
    try:
        data = db.query(
            models.plantMtrx.growing_area_id,
            models.plantMtrx.year,
            models.plantMtrx.week,
            models.plantMtrx.period,
            func.concat("P", models.plantMtrx.period).label("period_with_P"),
            func.sum(models.plantMtrx.value).label('total_value'))\
            .join(models.growing_area, models.plantMtrx.growing_area_id == models.growing_area.growing_area_id)\
            .join(models.region, models.growing_area.region == models.region.region_id)\
            .filter(models.region.country == name) \
            .group_by(models.plantMtrx.year, models.plantMtrx.growing_area_id, models.plantMtrx.period, models.plantMtrx.week) \
            .order_by(models.plantMtrx.growing_area_id, models.plantMtrx.period, models.plantMtrx.week).all()

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Plant Mtrx data not found for region : {region_id}")
        return {"status": "success", "plant_mtrx": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/only_region_data')
def getPlantMtrx_region(db: Session = Depends(get_db)):
    try:
        data = db.query(models.plantMtrx.region_id,
                        models.plantMtrx.year,
                        models.plantMtrx.period,
                        func.concat("P", models.plantMtrx.period).label("period_with_P"),
                        models.plantMtrx.week,
                        func.sum(models.plantMtrx.value).label('totalValue_regionWise')) \
            .group_by(models.plantMtrx.year, models.plantMtrx.region_id, models.plantMtrx.period, models.plantMtrx.week) \
            .order_by(models.plantMtrx.region_id, models.plantMtrx.period, models.plantMtrx.week) \
            .all()

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No data is found for this region:")
        return {"status": "success", "plant_mtrx_regionWise": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/update_plantMtrx')
def update_plantMtrx(payload: schemas.PlantMtrxPayload, db: Session = Depends(get_db)):
    data = payload.data
    update_count = 0
    try:
        for item in data:
            existing_record = db.query(models.plantMtrx).filter(
                models.plantMtrx.plant_matrix_id == item.plant_matrix_id).first()
            if existing_record is None:
                print(item)
                payload = {"plant_matrix_id": item.plant_matrix_id, "plant_id": item.plant_id, "region_id": item.region_id,
                           "growing_area_id": item.growing_area_id, "period": item.period, "week": item.week,
                           "year": item.year, "value": item.value}
                new_record = models.plantMtrx(**payload)
                db.add(new_record)
            else:
                for key, value in item.dict().items():
                    setattr(existing_record, key, value)

            db.commit()
            update_count += 1
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/createNewMatrix')
async def createNew_plantMatrix(year: int, db: Session = Depends(get_db)):
    try:
        check_data = db.query(models.plantMtrx.plant_matrix_id).filter(models.plantMtrx.year == year).first()
        newrecord_count = 0
        if check_data is None:
            plant_list = db.query(models.Plant.plant_id, models.Plant.region_id).filter(models.Plant.status == "ACTIVE").all()
            for plant in plant_list:
                plant_id = plant[0]
                region = plant[1]
                period_value = 1
                while period_value < 14:
                    week_value = 1
                    while week_value < 5:
                        total_value = db.query(models.pcusage.forecasted_value).filter(models.pcusage.plant_id == plant_id,
                                                                                       models.pcusage.period == period_value,
                                                                                       models.pcusage.week_no == week_value,
                                                                                       models.pcusage.year == year).first()
                        prefered_growingarea = db.query(models.plantMtrx_template.growing_area_id).filter(
                            models.plantMtrx_template.plant_id == plant_id,
                            models.plantMtrx_template.period == period_value,
                            models.plantMtrx_template.week_no == week_value).first()

                        plantMtrx_id = str(plant_id) + "#" + str(region) + "#" + str(year) + "#" + str(
                            period_value) + "#" + str(week_value) + "#" + str(prefered_growingarea[0])

                        PlantMtrx_payload = {"plant_matrix_id": plantMtrx_id,
                                             "region_id": region, "plant_id": plant_id,
                                             "growing_area_id": prefered_growingarea[0], "period": period_value,
                                             "week": week_value, "year": year, "value": total_value[0]}

                        newplantMtrx_record = models.plantMtrx(**PlantMtrx_payload)
                        db.add(newplantMtrx_record)
                        newrecord_count += 1
                        week_value += 1
                        db.commit()
                    period_value += 1
        # for all plants generate the plant_mtrx from pc_usage data using preferred growing_area->
        return {"status": "Success", "records create": newrecord_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

