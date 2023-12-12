"""Freight Cost Management API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import (FreightCostMapping, FreightCostRate,
                    PlantSiteGrowingAreaMapping, freight_cost_period_table,
                    freight_cost_period_week_table, rate_growing_area_table)
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/get_freight_cost_rate')
def view_freight_cost(db: Session = Depends(get_db)):
    """Function to fetch all records from freight_cost_rate table """
    try:
        records = db.query(FreightCostRate).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_freight_cost_records")
def create_freight_cost(payload: schemas.FreightCostRateSchema, db: Session = Depends(get_db)):
    """Function to create records for freight_cost_rate table """
    mapping_values = db.query(PlantSiteGrowingAreaMapping.plant_id
                              ,PlantSiteGrowingAreaMapping.vendor_site_id
                              ,PlantSiteGrowingAreaMapping.growing_area_id).all()

    if not mapping_values:
        raise HTTPException(status_code=404 ,
                            detail="No records found in plant_site_growing_area_mapping table")
    freight_records = []
    for mapping in mapping_values:
        freight_record = FreightCostRate(
            currency=payload.currency,
            comment=payload.comment,
            plant_id=mapping.plant_id,
            vendor_site_id=mapping.vendor_site_id,
            growing_area_id=mapping.growing_area_id,
            year=payload.year,
            created_by=payload.created_by,
            created_time=payload.created_time,
            updated_time=payload.updated_time,
            updated_by=payload.updated_by
        )
        db.add(freight_record)
    db.commit()
    db.refresh(freight_record)

    freight_records.append(freight_record)
    return freight_records

@router.post("/update_freight_cost_records/{freight_cost_id}")
def update_freight(freight_cost_id: int, payload: schemas.FreightCostRateSchema ,
                   db: Session = Depends(get_db)):
    """Function to update already existing records in freight_cost_rate table by
    filtering through freight cost id """
    existing_freight_records= db.query(FreightCostRate).filter(
        FreightCostRate.freight_cost_id == freight_cost_id
    ).first()

    if existing_freight_records is None:
        raise HTTPException(status_code=404, detail="No record found with this f{freight_cost_id}")

    existing_freight_records.rate = payload.currency
    existing_freight_records.comment = payload.comment
    existing_freight_records.year = payload.year
    existing_freight_records.created_by = payload.created_by
    existing_freight_records.updated_by = payload.updated_by

    db.commit()
    db.refresh(existing_freight_records)

    return existing_freight_records

@router.get('/get_freight_cost_mapping')
def view_freight_mapping(db: Session = Depends(get_db)):
    """Function to fetch all records from freight_cost_mapping table """
    try:
        records = db.query(FreightCostMapping, func.concat("P", FreightCostMapping.period)\
            .label("period_with_P")).all()
        # Extract the results as dictionaries and build the response
        result = [
            {
                "freight_cost_id": row.FreightCostMapping.freight_cost_id,
                "period": row.FreightCostMapping.period,
                "year": row.FreightCostMapping.year,
                "rate": row.FreightCostMapping.rate,
                "period_with_P": row.period_with_P
            }
            for row in records
        ]
        return {"status": "success", "freight_cost_mapping": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_freight_cost_mapping/{year}')
def view_freight_mapping_by_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from freight_cost_mapping table """
    try:
        records = db.query(FreightCostMapping, func.concat("P", FreightCostMapping.period)\
            .label("period_with_P")).filter(FreightCostMapping.year == year).all()
        # Extract the results as dictionaries and build the response
        result = [
            {
                "freight_cost_id": row.FreightCostMapping.freight_cost_id,
                "period": row.FreightCostMapping.period,
                "year": row.FreightCostMapping.year,
                "rate": row.FreightCostMapping.rate,
                "period_with_P": row.period_with_P
            }
            for row in records
        ]
        return {"status": "success", "freight_cost_mapping": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create_freight_cost_mapping_records")
def create_freight_mapping(
    payload: schemas.FreightCostMappingSchema,
    db: Session = Depends(get_db)
):
    """Function to create records for freight_cost_mapping table """
    freight_cost_mapping_data = []
    distinct_freight_ids = db.query(FreightCostRate.freight_cost_id).distinct().all()

    for freight_cost_id_tuple in distinct_freight_ids:
        freight_cost_id = freight_cost_id_tuple[0]
        for period in range(1, 14):
            mapped_data = FreightCostMapping(
                freight_cost_id=freight_cost_id,
                year=payload.year,
                period=period,
                rate=payload.rate
            )
            db.add(mapped_data)
            db.commit()
            db.refresh(mapped_data)

            freight_cost_mapping_data.append(mapped_data)

    return freight_cost_mapping_data

@router.post("/update_freight_mapping/{freight_cost_id}/{year}/{period}")
def update_freight_mapping(
    freight_cost_id: int,
    year: int,
    period: int,
    new_rate: float,
    db: Session = Depends(get_db)
):
    """Function to update already existing records in freight_cost_mapping table by
    filtering through freight cost id, year and period column"""
    records_to_update = db.query(FreightCostMapping).filter(
        FreightCostMapping.freight_cost_id == freight_cost_id,
        FreightCostMapping.year == year,
        FreightCostMapping.period >= period
    ).all()
    if not records_to_update:
        raise HTTPException(status_code=404, detail="No records found for the given filter")
    for record in records_to_update:
        record.rate = new_rate
        db.commit()
    return records_to_update

@router.delete('delete/{year}')
def delete_post(year:int, db: Session = Depends(get_db)):
    records_to_delete = db.query(FreightCostMapping).filter(FreightCostMapping.year == year).all()
    if not records_to_delete:
        raise HTTPException(status_code=404,
                            detail=f'No region  with this year: {year} found')
    for record in records_to_delete:
            db.delete(record)
    db.commit()
    return {"message": f"Records for the year {year} deleted successfully."}

@router.get('/freight_cost_period_view')
def freight_cost_period_view(db: Session = Depends(get_db)):
    """Function to fetch all records from freight period view table """
    try:
        records = db.query(freight_cost_period_table).all()
        result = [
            {
                "plant_id": row.Plant_Id,
                "period": row.UNL_DATE_PD,
                "plant_name": row.plant_name,
                "dollarbymcwt": row.dollorcwt,
                "year": row.UNLOAD_YEAR,
                "totalspend":row.totalspend,
                "week":0,
                "period_with_P": f'P{row.UNL_DATE_PD}'
            }
            for row in records
        ]
        return {"freight_cost_period_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))   

@router.get('/freight_cost_period_view/{year}')
def freight_cost_period_view_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from freight period view table """
    try:
        records = db.query(freight_cost_period_table).filter(freight_cost_period_table.columns.UNLOAD_YEAR == year).all()
        result = [
            {
                "plant_id": row.Plant_Id,
                "period": row.UNL_DATE_PD,
                "plant_name": row.plant_name,
                "dollarbymcwt": row.dollorcwt,
                "totalspend":row.totalspend,
                "year": row.UNLOAD_YEAR,
                "week":0,
                "period_with_P": f'P{row.UNL_DATE_PD}'
            }
            for row in records
        ]
        return {"freight_cost_period_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.get('/create_freight_cost_period_view')
# def create_freight_cost_period_view_year(year:int,db: Session = Depends(get_db)):
#     """Function to fetch all records from freight period view table """
#     try:
#         records = db.query(freight_cost_period_table).all()
#         result = [
#             {
#                 "plant_id": row.Plant_Id,
#                 "period": row.period_num,
#                 "plant_name": row.plant_name,
#                 "dollarbycwt": 0,
#                 "year": year,
#                 "totalspend":0,
#                 "week":0,
#                 "period_with_P": f'P{row.period_num}'
#             }
#             for row in records
#         ]
#         return {"freight_cost_period_view": result}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e)) 

@router.get('/freight_cost_period_week_view')
def freight_cost_period_week_view(db: Session = Depends(get_db)):
    """Function to fetch all records from freight period week view table """
    try:
        records = db.query(freight_cost_period_week_table).all()
        result = [
            {
                "plant_id": row.Plant_Id,
                "plant_name": row.plant_name,
                "period": row.UNL_DATE_PD,
                "week" : row.Unl_Date_Wk_Num,
                "dollarbymcwt": row.dollorcwt,
                "year": row.UNLOAD_YEAR,
                "totalspend": row.totalspend,
                "P*W": f'P{row.UNL_DATE_PD}W{row.Unl_Date_Wk_Num}'
            }
            for row in records
        ]
        return {"freight_cost_period_week_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/freight_cost_period_week_view/{year}')
def freight_cost_period_week_view_year(year: int,db: Session = Depends(get_db)):
    """Function to fetch all records from freight period week view table """
    try:
        records = db.query(freight_cost_period_week_table).filter(freight_cost_period_week_table.columns.UNLOAD_YEAR == year).all()
        result = [
            {
                "plant_id": row.Plant_Id,
                "plant_name": row.plant_name,
                "period": row.UNL_DATE_PD,
                "week" : row.Unl_Date_Wk_Num,
                "dollarbymcwt": row.dollorcwt,
                "year": row.UNLOAD_YEAR,
                "totalspend": row.totalspend,
                "P*W": f'P{row.UNL_DATE_PD}W{row.Unl_Date_Wk_Num}'
            }
            for row in records
        ]
        return {"freight_cost_period_week_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/rate_growing_area')
def rate_growing_area(db: Session = Depends(get_db)):
    """Function to fetch all records from rate growing area table """
    try:
        records = db.query(rate_growing_area_table).all()
        result = [
            {
                "plant_id": row.plant_id,
                "plant_name": row.plant_name,
                "growing_area":row.growing_area_name,
                "growing_area_id": row.growing_area_id,
                "period": row.period,
                "fcst": row.rate_plan,
                "actual": row.rate_actual,
                "totaldollarbymcwt": row.totaldollarcwt,
                "year": row.p_year,
                "period_with_P": f'P{row.period}',
                "week": 0
            }
            for row in records
        ]
        return {"freight_cost_rate_growing_area": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get_rate_gowing_area/{year}")
def get_rate_growing_area_year(year: int, db: Session = Depends(get_db)):
    """Function to get records rate growing area table by year"""
    try:
        records = db.query(rate_growing_area_table).filter(rate_growing_area_table.columns.p_year == year).all()
        result = [
            {
                "plant_id": row.plant_id,
                "plant_name": row.plant_name,
                "growing_area":row.growing_area_name,
                "growing_area_id": row.growing_area_id,
                "period": row.period,
                "fcst": row.rate_plan,
                "actual": row.rate_actual,
                "totaldollarbymcwt": row.totaldollarcwt,
                "year": row.p_year,
                "period_with_P": f'P{row.period}',
                "week": 0
            }
            for row in records
        ]
        return {"freight_cost_rate_growing_area": result}
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=400, detail=str(e))
