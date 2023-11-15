from models import Plant, region, growing_area
import models
import schemas
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import Depends, HTTPException, status, APIRouter, Response, Query
from database import get_db
from typing import List, Dict, Union, Any, Optional
from datetime import datetime, timedelta
from pydantic import ValidationError
from fastapi.responses import JSONResponse
import time

router = APIRouter()


@router.get('/')
def view(db: Session = Depends(get_db)):
    try:
        records = db.query(models.erp_raw_data_us).all()
        return {"data": records}
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


def cal_spend(item: models.erp_raw_data_us):
    Spend_Column = item.UNIT_PRICE * item.QUANTITY_BILLED
    RecQty_CWT = item.RECEIPT_QUANTITY / 100
    RecQty_MCWT = RecQty_CWT / 1000
    return schemas.ErpRawDataUsSchema(UNIT_PRICE=item.UNIT_PRICE, QUANTITY_BILLED=item.QUANTITY_BILLED,
                                      Spend=Spend_Column, Rec_Qty_CWT=RecQty_CWT, Rec_Qty_MCWT=RecQty_MCWT)


# FastAPI endpoint to get calculated results
@router.get("/get_spend/", response_model=list[schemas.ErpRawDataUsSchema])
async def get_spend(db: Session = Depends(get_db)):
    query = select(models.erp_raw_data_us.UNIT_PRICE, models.erp_raw_data_us.QUANTITY_BILLED,
                   models.erp_raw_data_us.RECEIPT_QUANTITY).all()
    records = db.execute(query).all()
    results = [cal_spend(models.erp_raw_data_us(UNIT_PRICE=row.UNIT_PRICE, QUANTITY_BILLED=row.QUANTITY_BILLED,
                                                RECEIPT_QUANTITY=row.RECEIPT_QUANTITY, RECEIPT_NUM=row.RECEIPT_NUM)) for
               row in records]
    return results


def cal_spend_by_value(UNIT_PRICE, QUANTITY_BILLED):
    Spend_Column = UNIT_PRICE * QUANTITY_BILLED
    return Spend_Column


# FastAPI endpoint to update spend value
@router.post("/update_spend/", status_code=status.HTTP_201_CREATED)
async def update_spend(db: Session = Depends(get_db)):
    records = db.query(models.erp_raw_data_us).all()
    for row in records:
        spend = cal_spend_by_value(row.UNIT_PRICE, row.QUANTITY_BILLED)
        row.spend = spend
    db.commit()

    return {"status": "success"}


def calculate_period_week_combinations(unload_date: datetime):
    start_date = datetime(unload_date.year, 1, 1)
    while start_date.weekday() != 6:
        start_date -= timedelta(days=1)

    week = 1
    period = 1
    result = []
    loop_count = 1
    current_date = start_date
    while current_date <= unload_date:
        result.append((f"P{period}W{week}", loop_count))
        loop_count += 1
        week += 1

        if week > 4:
            period += 1
            week = 1
        if period > 13:
            break

        current_date += timedelta(days=7)

        if current_date.month != start_date.month:
            start_date = current_date

    return result


@router.post("/update_erp_raw_data/", status_code=status.HTTP_201_CREATED)
async def update_erp_raw_data(db: Session = Depends(get_db)):
    # Fetch all records from the database
    all_records = db.query(models.erp_raw_data_us).all()
    # Ensure there are records in the database
    if all_records.count == 0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    # List to store the result in tabular format
    result_table = []
    i = 1
    # Calculate P*W values for each record
    for record in all_records:
        record_dict = {}
        print('records', i)
        i += 1
        record_dict = {"BPA_Number": record.BPA_Number}
        spend = cal_spend_by_value(record.UNIT_PRICE, record.QUANTITY_BILLED)
        Plant_Id = update_Plant_by_Name(record.Ship_To_Organization, db)
        site_Id = update_site_Id_by_Vendor_Name(record.VENDOR_SITE_CODE, db)
        grower_id = update_grower_id_By_Vendor_Name(record.VENDOR_NAME, db)
        growignarea_id = get_growing_area_id_by_vendor_name(record.VENDOR_NAME, db)
        region_id = update_Region_by_Name(record.Ship_To_Organization, db)

        if record.UNLOAD_DATE and isinstance(record.UNLOAD_DATE, str):
            unload_date = datetime.strptime(record.UNLOAD_DATE, '%d-%b-%Y %H:%M:%S')
            result = calculate_period_week_combinations(unload_date)
            for Unl_Date_PxW, loop_count in result:
                record.Unl_Date_PxW = Unl_Date_PxW
                record.Unl_Date_Wk_Num = loop_count

        if record.RECEIPT_DATE:
            receipt = str(record.RECEIPT_DATE)

            receDate = datetime.strptime(receipt, '%Y-%m-%d %H:%M:%S')
            formatedDate = receDate.strftime('%d-%b-%Y %H:%M:%S')
            receipt_date = datetime.strptime(formatedDate, '%d-%b-%Y %H:%M:%S')

            result = calculate_period_week_combinations(receipt_date)

            for Rec_Date_PxW, loop_count in result:
                record.Rec_Date_PxW = Rec_Date_PxW
                record.Rec_Date_wk_num = loop_count

        record.status = 'Success'
        record.spend = spend
        record.Region_id = region_id
        record.Plant_Id = Plant_Id
        record.growignarea_id = growignarea_id
        record.Site_Id = site_Id
        record.grower_Id = grower_id
        record.PROCESS_TIME = datetime.now()
        result_table.append(record_dict)
        db.commit()

    return {"status": "success", "result_table": result_table}


def getCropYear(dt):
    original_year = dt.year
    year = str(dt.year)[-2:]
    prev_year = int(year) - 1
    next_year = int(year) + 1

    for month in range(1, 12):
        if month <= 4:
            return (f"{month}=>{prev_year}{year} Storage")
        elif month >= 11:
            return (f"{month} => {year}{next_year} Fresh")
        else:
            return (f"{month}=>{original_year} Storage")


getCropYear(datetime.now());


# @router.get('/update_Plant_by_Name')
def update_Plant_by_Name(plantName, db: Session = Depends(get_db)):
    plant_query = (db.query(models.View_site_plant_growing_area_mapping.columns.plant_id)
                   .where(models.View_site_plant_growing_area_mapping.columns.plant_name == plantName).first())

    if not plant_query:
        plant_Id = None
        return plant_Id

    plant_Id = plant_query.plant_id

    return plant_Id


# @router.get('/update_site_Id_by_Vendor_Name')
def update_site_Id_by_Vendor_Name(VENDOR_SITE_CODE, db: Session = Depends(get_db)):
    site_query = (db.query(models.View_site_plant_growing_area_mapping.columns.VENDOR_SITE_ID)
                  .where(
        models.View_site_plant_growing_area_mapping.columns.VENDOR_SITE_CODE == VENDOR_SITE_CODE).first())
    if not site_query:
        site_Id = None
        return site_Id

    site_Id = site_query.VENDOR_SITE_ID
    return site_Id


# @router.get('/update_grower_id_By_Vendor_Name')
def update_grower_id_By_Vendor_Name(venderName, db: Session = Depends(get_db)):
    grower_query = (db.query(models.view_growing_area_mapping_Alice.columns.grower_id)
                    .where(models.view_growing_area_mapping_Alice.columns.grower_name == venderName).first())

    if not grower_query:
        grower_id = None
        return grower_id

    grower_id = grower_query.grower_id
    return grower_id


# @router.get('/get_growing_area_id_by_vendor_name')
def get_growing_area_id_by_vendor_name(vendor_name, db: Session = Depends(get_db)):
    site_query = (db.query(models.view_growing_area_mapping_Alice.columns.growing_area_id)
                  .where(models.view_growing_area_mapping_Alice.columns.grower_name == vendor_name).first())
    if not site_query:
        growing_area_id = None

    growing_area_id = site_query.growing_area_id

    return growing_area_id


# @router.get('/update_Region_by_Name')
def update_Region_by_Name(plantName, db: Session = Depends(get_db)):
    region_query = (db.query(models.view_plant_growing_area_Alice.columns.region,
                             models.view_plant_growing_area_Alice.columns.growing_area_id)
                    .where(models.view_plant_growing_area_Alice.columns.plant_name == plantName).first())

    if not region_query:
        region_Id = None
        return region_Id

    region_Id = region_query.region

    return region_Id
