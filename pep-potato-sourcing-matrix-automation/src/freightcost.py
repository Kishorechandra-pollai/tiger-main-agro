"""Freight Cost Management API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (FreightCostMapping, FreightCostRate,growing_area,
                    PlantSiteGrowingAreaMapping, freight_cost_period_table,
                    freight_cost_period_week_table, rate_growing_area_table)
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()


@router.get('/get_freight_cost_rate')
def view_freight_cost(db: Session = Depends(get_db)):
    """Function to fetch all records from freight_cost_rate table """
    try:
        records = db.query(FreightCostRate).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


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

@router.get('/get_freight_cost_mapping/{year}')
def view_freight_mapping_by_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from freight_cost_mapping table """
    try:
        records = db.query(FreightCostMapping.freight_cost_id,
                           FreightCostMapping.period,
                           func.concat("P", FreightCostMapping.period).label("period_with_P"),
                           FreightCostMapping.rate).filter(FreightCostMapping.year == year).all()
        return {"status": "success", "freight_cost_mapping": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

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



@router.get('/freight_cost_period_view/{year}/{country}')
def freight_cost_period_view_year(year:int,country:str, db: Session = Depends(get_db)):
    """Function to fetch all records from freight period view table """
    try:
        records = db.query(freight_cost_period_table).filter(
            freight_cost_period_table.columns.p_year == year,
            freight_cost_period_table.columns.country == country
            ).order_by(freight_cost_period_table.columns.period).all()
        return {"freight_cost_period_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/freight_cost_period_week_view/{year}/{country}')
def freight_cost_period_week_view_year(year: int,country:str,db: Session = Depends(get_db)):
    """Function to fetch all records from freight period week view table """
    try:
        records = db.query(freight_cost_period_week_table).filter(
            freight_cost_period_week_table.columns.p_year == year,
            freight_cost_period_week_table.columns.country == country
            ).order_by(freight_cost_period_week_table.columns.period,
                      freight_cost_period_week_table.columns.week_no).all()
        return {"freight_cost_period_week_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/get_rate_gowing_area/{year}")
def get_rate_growing_area_year(year: int, db: Session = Depends(get_db)):
    """Function to get records rate growing area table by year"""
    try:
        records = db.query(rate_growing_area_table).filter(
            rate_growing_area_table.columns.p_year == year).order_by(rate_growing_area_table.columns.growing_area_id,
                                                                     rate_growing_area_table.columns.period).all()
        return {"freight_cost_rate_growing_area": records}
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    
def create_freight_rates_in_db(payload: schemas.FreightCostRatesSchema, db: Session):
    if isinstance(payload, BaseModel):
        # Convert Pydantic model to dictionary
        payload_dict = payload.dict()
    else:
        # Assume payload is already a dictionary
        payload_dict = payload
    new_record = FreightCostRate(**payload_dict)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.post('/create_freight_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: schemas.FreightCostRatesSchema, db: Session = Depends(get_db)):
    new_record = create_freight_rates_in_db(payload, db)
    return {"status": "success", "freight_cost_id": new_record.freight_cost_id}


@router.post("/create_freight_cost_mapping_records_for_next_year/{year}")
def create_freight_cost_mapping_records_for_next_year(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to create records for freight_cost_mapping table """
    distinct_freight_ids = db.query(FreightCostRate.freight_cost_id).distinct().all()
    update_count = 0
    if distinct_freight_ids.count == 0:
        raise HTTPException(status_code=404, detail="No records found in the database")
    dict_existing_record = []
    existingRecord = db.query(FreightCostMapping)\
        .filter(FreightCostMapping.year == year).all()
    for ex in existingRecord:
        # key = str(ex.freight_cost_id)+"-"+ex.company_name+"-"+str(ex.period)
        # dict_existing_record.append(key)
        db.delete(ex)
    db.commit()
    for freight_cost_id_tuple in distinct_freight_ids:
        freight_cost_id = freight_cost_id_tuple[0]
        for period in range(1, 14):
            old_rates = db.query(FreightCostMapping)\
                .filter(FreightCostMapping.year == (year-1),
                        FreightCostMapping.freight_cost_id == freight_cost_id,
                        FreightCostMapping.period == period).first()
            # isKey = str(freight_cost_id)+"-"+old_rates.company_name+"-"+str(period)
            # if isKey in dict_existing_record:
            #     return {"status": "error", "Records already exists for Year": year}
            # else:
            new_record = FreightCostMapping(freight_cost_id=freight_cost_id,
                                            period=period, year=year,
                                            rate=old_rates.rate,
                                            company_name=old_rates.company_name)
            db.add(new_record)
            update_count += 1
    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}

def update_freight_rates_with_default_value(freight_cost_id: int, year: int, db: Session = Depends(get_db)):
    country_records = db.query(growing_area.growing_area_id, growing_area.country).join(
        FreightCostRate, growing_area.growing_area_id == FreightCostRate.growing_area_id
    ).filter(
        FreightCostRate.freight_cost_id == freight_cost_id
    ).first()
    if not country_records:
        raise HTTPException(status_code=404, detail=f"No growing area found for freight_cost_id: {freight_cost_id}")
    growing_area_id, country = country_records

    if country == 'USA':
        country = 'US'
    for period in range(1, 14):
        new_record = FreightCostMapping(
            freight_cost_id=freight_cost_id,
            period=period,
            year=year,
            rate=0,
            company_name=country
        )
        db.add(new_record)

    db.commit()

    return {"status": "success"}

@router.post("/update_freight_rates_with_default_value/{freight_cost_id}/{year}")
async def update_freight_cost_mapping_with_default_value(freight_cost_id:int, year:int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update records in freight_cost_mapping table."""
    result = update_freight_rates_with_default_value(freight_cost_id, year,db)
    if result is None:
        raise HTTPException(status_code=404, detail="No records found in the database")
    return {"status": "success"}


@router.get("/fetch_freight_records/{year}")
async def fetch_records(
    year: int,
    db: Session = Depends(get_db)
):
    try:
        records = (
            db.query(
                FreightCostMapping.freight_cost_id,
                FreightCostMapping.year,
                FreightCostMapping.period,
                func.concat("P", FreightCostMapping.period).label("period_with_P"),
                FreightCostMapping.rate,
                FreightCostMapping.company_name,
                PlantSiteGrowingAreaMapping.growing_area_id,
                PlantSiteGrowingAreaMapping.vendor_site_id,
                PlantSiteGrowingAreaMapping.plant_id,
                PlantSiteGrowingAreaMapping.plant_name,
                PlantSiteGrowingAreaMapping.growing_area,
                PlantSiteGrowingAreaMapping.Vendor_Site_Code,
            )
            .select_from(FreightCostMapping)
            .join(
                FreightCostRate,
                and_(
                    FreightCostRate.freight_cost_id == FreightCostMapping.freight_cost_id,
                )
            )
            .join(
                PlantSiteGrowingAreaMapping,
                and_(
                    FreightCostRate.growing_area_id == PlantSiteGrowingAreaMapping.growing_area_id,
                    FreightCostRate.plant_id == PlantSiteGrowingAreaMapping.plant_id,
                    FreightCostRate.vendor_site_id == PlantSiteGrowingAreaMapping.vendor_site_id,
                )
            )
            .filter(FreightCostMapping.year == year)
            .all()
        )

        if not records:
            return {"status": "success", "data": []}

        consolidated_data = []
        for record in records:
            (
                freight_cost_id,
                record_year,
                record_period,
                period_with_P,
                rate,
                company_name,
                growing_area_id,
                vendor_site_id,
                plant_id,
                plant_name,
                growing_area,
                Vendor_Site_Code,
            ) = record

            consolidated_data.append(
                {
                    "freight_cost_id": freight_cost_id,
                    "year": record_year,
                    "period": record_period,
                    "period_with_P":period_with_P,
                    "rate": rate,
                    "company_name": company_name,
                    "growing_area_id": growing_area_id,
                    "vendor_site_id": vendor_site_id,
                    "plant_id": plant_id,
                    "plant_name": plant_name,
                    "growing_area": growing_area,
                    "Vendor_Site_Code": Vendor_Site_Code,
                }
            )

        return {"status": "success", "data": consolidated_data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
