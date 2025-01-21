"""Freight Cost Management API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from models import (FreightCostMapping, FreightCostRate,growing_area,
                    PlantSiteGrowingAreaMapping, freight_cost_period_table,
                    freight_cost_period_week_table, rate_growing_area_table,freight_rates_period_totals,
                    freight_rates_week_totals, FileUploadTemplate,Plant,View_freight_fuel_cost)
from sqlalchemy import func, and_,text,or_
from sqlalchemy.orm import Session
from pydantic import BaseModel
from io import BytesIO
import pandas as pd
import os
from datetime import datetime

router = APIRouter()


@router.get('/get_freight_cost_rate')
def view_freight_cost(db: Session = Depends(get_db)):
    """Function to fetch all records from freight_cost_rate table """
    try:
        records = db.query(FreightCostRate).all()
        return {"All_data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/freight_alert')
def view_freight_cost(db: Session = Depends(get_db)):
    """Function to alert the user about new freight mappings """
    try:
        records = (db.query(PlantSiteGrowingAreaMapping.plant_name,
                                PlantSiteGrowingAreaMapping.Vendor_Site_Code,
                                growing_area.growing_area_desc,
                                FreightCostRate.miles,
                                FreightCostMapping.round_trip,
                                FreightCostMapping.fuel_cf,
                                FreightCostMapping.rate)
                    .select_from(FreightCostRate)
                    .join(growing_area,
                          growing_area.growing_area_id == FreightCostRate.growing_area_id)
                    .join(FreightCostMapping,
                          FreightCostMapping.freight_cost_id == FreightCostRate.freight_cost_id)
                    .join(PlantSiteGrowingAreaMapping,
                     and_(FreightCostRate.growing_area_id == PlantSiteGrowingAreaMapping.growing_area_id,
                          FreightCostRate.plant_id == PlantSiteGrowingAreaMapping.plant_id,
                          FreightCostRate.vendor_site_id == PlantSiteGrowingAreaMapping.vendor_site_id))
                    .filter(
                        or_(FreightCostRate.miles==None,
                            FreightCostMapping.fuel_cf==None,
                            FreightCostMapping.round_trip==None,
                            FreightCostMapping.rate==None)).all())
        
        alert = "New Mapping is created in Freight Rates tables --> "
        for items in records:
            mappings = f"Plant : {items.plant_name}, Vendor_Site_Code : {items.Vendor_Site_Code}, Growing_area : {items.growing_area_desc}"
            alert += "{" + mappings +"}, "

        if len(records)>0:
            return {"message":{"Alert_message": alert[:-2] + ". Please enter the Freight Rates, Miles, Round Trip and Conversion factor for this new Mapping"}}
        else:
            return {"message":{"Alert_message": "0"}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_freight_cost_records")
def create_freight_cost(payload: schemas.FreightCostRateSchema, db: Session = Depends(get_db)): # pragma: no cover
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
                           FreightCostMapping.company_name,
                           func.concat("P", FreightCostMapping.period).label("period_with_P"),
                           FreightCostMapping.rate,FreightCostMapping.fuel_cf,FreightCostMapping.round_trip).filter(FreightCostMapping.year == year).all()
        return {"status": "success", "freight_cost_mapping": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_freight_cost_mapping_records")
def create_freight_mapping(
    payload: schemas.FreightCostMappingSchema,
    db: Session = Depends(get_db)
): # pragma: no cover
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


@router.post("/update_freight_mapping/{freight_cost_id}/{year}/{period}/{country}")
def update_freight_mapping(
    freight_cost_id: int,
    year: int,
    period: int,
    country: str,
    new_rate: float,
    round_trip: int,
    db: Session = Depends(get_db)
):
    # Query to fetch records for the given year with period >= the provided period
    records_to_update_current_year = db.query(FreightCostMapping).filter(
        FreightCostMapping.freight_cost_id == freight_cost_id,
        FreightCostMapping.year == year,
        FreightCostMapping.company_name == country,
        FreightCostMapping.period >= period
    ).all()

    # Query to fetch all records for the next year (year + 1)
    records_to_update_next_year = db.query(FreightCostMapping).filter(
        FreightCostMapping.freight_cost_id == freight_cost_id,
        FreightCostMapping.year == year + 1,
        FreightCostMapping.company_name == country
    ).all()

    # Combine records from the current year and next year
    records_to_update = records_to_update_current_year + records_to_update_next_year

    if not records_to_update:
        raise HTTPException(status_code=404, detail="No records found for the given filter")

    # Update the rate and round_trip for each record
    for record in records_to_update:
        record.rate = new_rate
        record.round_trip = round_trip

    # Commit the changes to the database
    db.commit()

    return {"updated_records_count": len(records_to_update), "details": records_to_update}


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
    
@router.get('/freight_cost_period_total/{year}/{country}')
def freight_cost_period_year_total(year:int,country:str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from freight period total table """
    try:
        records = db.query(freight_rates_period_totals).filter(
            freight_rates_period_totals.columns.p_year == year,
            freight_rates_period_totals.columns.country == country
            ).order_by(freight_rates_period_totals.columns.period).all()
        return {"freight_cost_period_totals": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/freight_cost_period_week_totals/{year}/{country}')
def freight_cost_period_week_view_totals(year: int,country:str,db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from freight period week view totals table """
    try:
        records = db.query(freight_rates_week_totals).filter(
            freight_rates_week_totals.columns.p_year == year,
            freight_rates_week_totals.columns.country == country
            ).order_by(freight_rates_week_totals.columns.period,
                      freight_rates_week_totals.columns.week_no).all()
        return {"freight_cost_period_week_totals": records}
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
    
def create_freight_rates_in_db(payload: schemas.FreightCostRatesSchema, db: Session): # pragma: no cover
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
def create_potato_rates(payload: schemas.FreightCostRatesSchema, db: Session = Depends(get_db)): # pragma: no cover
    new_record = create_freight_rates_in_db(payload, db)
    return {"status": "success", "freight_cost_id": new_record.freight_cost_id}

# @router.post('/create_freight_rates', status_code=status.HTTP_201_CREATED)
# def create_potato_rates(payload: schemas.FreightCostRatesSchema, db: Session = Depends(get_db)): # pragma: no cover
#     new_record = create_freight_rates_in_db(payload, db)
#     return {"status": "success", "freight_cost_id": new_record.freight_cost_id}


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
            if old_rates is not None:  # Ensure old_rates is not None
                new_record = FreightCostMapping(freight_cost_id=freight_cost_id,
                                                period=period, year=year,
                                                rate=old_rates.rate,
                                                company_name=old_rates.company_name)
                db.add(new_record)
                update_count += 1
        db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}

def update_freight_rates_with_default_value(freight_cost_id: int, year: int, db: Session = Depends(get_db)): # pragma: no cover
    country_records = db.query(Plant.plant_id, Plant.company_name).join(
        FreightCostRate, Plant.plant_id == FreightCostRate.plant_id
    ).filter(
        FreightCostRate.freight_cost_id == freight_cost_id
    ).first()
    if not country_records:
        raise HTTPException(status_code=404, detail=f"No growing area found for freight_cost_id: {freight_cost_id}")
    plant_id, country = country_records

    if country == 'US-CORE' or country == 'CO-MAN':
        country = 'US'
    elif country == 'CANADA-CORE':
        country = 'Canada'
    for period in range(1, 14):
        new_record = FreightCostMapping(
            freight_cost_id=freight_cost_id,
            period=period,
            year=year,
            rate=0,
            company_name=country,
            round_trip=1,
            fuel_cf=0.54
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


@router.get("/fetch_freight_records/{year}/{country}")
async def fetch_records(
    year: int,
    country:str,
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
                FreightCostMapping.fuel_cf,
                FreightCostMapping.round_trip,
                FreightCostRate.miles,
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
            .filter(FreightCostMapping.year == year,FreightCostMapping.company_name == country).distinct(FreightCostMapping.freight_cost_id)
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
                fuel_cf,
                round_trip,
                miles,
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
                    "fuel_cf": fuel_cf,
                    "round_trip": round_trip,
                    "miles": miles,
                    "growing_area_id": growing_area_id,
                    "vendor_site_id": vendor_site_id,
                    "plant_id": plant_id,
                    "plant_name": plant_name,
                    "growing_area": growing_area,
                    "Vendor_Site_Code": Vendor_Site_Code,
                }
            )
        # count= len(consolidated_data)
        # print(count)

        return {"status": "success", "data": consolidated_data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def handle_upload_file(uploaded_year: int, user_email: str, file: UploadFile, db: Session):# pragma: no cover
    # Capture file upload start time
    file_uploaded_time = datetime.now()

    try:
        # Extract file extension
        file_extension = os.path.splitext(file.filename)[-1].lower()
        
        # Check if file extension is allowed
        if file_extension not in [".xls", ".xlsx"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Supported formats are xls, xlsx.")

        # Read file content based on file format
        contents = file.file.read()
        data = BytesIO(contents)
        # Read all sheets from the Excel file
        df_dict = pd.read_excel(data, sheet_name=None)
        # Check number of sheets
        if len(df_dict.keys()) != 1:
            raise HTTPException(status_code=400, detail="Multiple sheets detected. Please upload a file with only one sheet.")
        # Extract the DataFrame from the dictionary
        df = next(iter(df_dict.values()))
        # Drop unnecessary columns
        df = df.drop(['growing_area_id', 'plant_id', 'vendor_site_id', 'plant_name', 'growing_area', 'Vendor_Site_Code'], axis=1, errors='ignore')
        # Melt DataFrame
        melted_df = df.melt(id_vars=['freight_cost_id', 'company_name', 'year'], var_name='period', value_name='rate')
        melted_df['period'] = melted_df['period'].str.extract('(\d+)').astype(int)
        # Replace null values in the rate column with 0
        melted_df['rate'] = melted_df['rate'].fillna(0)
        # Ensure 'year' column exists and is not empty
        if 'year' not in melted_df.columns or melted_df['year'].isnull().all():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year data is missing in the uploaded excel template.")
        # Check if the 'year' column has multiple distinct values
        if len(melted_df['year'].unique()) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year column in the uploaded file has multiple year values.Please check it once and then re-upload.")
        file_year = melted_df['year'].iloc[0]

        # Check if the uploaded_year matches the year value in the Excel file
        if uploaded_year != file_year:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Dropdown year value {uploaded_year} does not match the year value {file_year} in the uploaded Excel file.")
        
        uploaded_year = int(uploaded_year)
        
        # Get distinct freight_cost_id values from the DataFrame
        #freight_cost_ids = melted_df['freight_cost_id'].unique()
        
        # Delete records for the specific freight_cost_id values for the given year
        db.query(FreightCostMapping).filter(
            FreightCostMapping.year == uploaded_year
        ).delete()
        db.commit()
        
        if 'round_trip' not in melted_df.columns:
            melted_df['round_trip'] = 1
        if 'fuel_cf' not in melted_df.columns:
            melted_df['fuel_cf'] = 0
        
        # Insert new records
        records_to_insert = melted_df.to_dict(orient='records')
        db.execute(FreightCostMapping.__table__.insert(), records_to_insert)
        db.commit()
        
        # Capture file process time
        file_process_time = datetime.now()
        
        sheet_name = next(iter(df_dict.keys()))
        file_name_without_ext = os.path.splitext(file.filename)[0]
        file_name = f"{file_name_without_ext}_{sheet_name}"
        file_type = file_extension
        file_process_status = True
        message = " rates uploaded successfully"

        file_upload_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,  
            message=message  
        )
        db.add(file_upload_data)
        db.commit()
    except HTTPException as he:
        db.rollback()
        # File details
        file_name = file.filename
        file_type = file_extension
        file_process_time = None
        file_process_status = False
        message = str(he.detail)
        
        file_upload_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email, 
            message=message  
        )
        db.add(file_upload_data)
        db.commit()

        raise he
    except Exception as e:
        db.rollback()
        # File details
        file_name = file.filename
        file_type = file_extension
        file_process_time = None
        file_process_status = False
        message = str(e)

        file_upload_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email, 
            message=message  
        )
        db.add(file_upload_data)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"detail": f" rates successfully uploaded for the year: {uploaded_year}"}

# FastAPI route for file upload
@router.post("/upload_file", status_code=status.HTTP_201_CREATED)
async def upload_file(uploaded_year: int, user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):# pragma: no cover
    return handle_upload_file(uploaded_year, user_email, file, db)

@router.get('/get_file_upload_details')
async def get_file_details(db: Session = Depends(get_db)):# pragma: no cover
    """Function to fetch all records from file_upload_template table """
    try:
        records = db.query(FileUploadTemplate).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.post("/miles")
async def update_miles(payload: schemas.FreightMiles, db: Session = Depends(get_db)): # pragma: no cover
    """Function to update freight miles for plant,vendor site code and growing area combination"""
    try:
        records = db.query(FreightCostRate).filter(FreightCostRate.plant_id == payload.plant_id,
                                                   FreightCostRate.growing_area_id == payload.growing_area_id,
                                                   FreightCostRate.vendor_site_id == payload.vendor_site_id).all()
        if not records:
            raise HTTPException(status_code=404, detail="No records found for the given filter")
        for record in records:
            record.miles = payload.miles
        db.commit()
        
        return {"Miles updated for": payload.plant_id and payload.vendor_site_id and payload.growing_area_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/fuel_conv_factor")
def update_fuel_cf(payload: schemas.FreightMilesSchema,
    db: Session = Depends(get_db)
): # pragma: no cover
    """Function to update fuel conversion factor"""
    update_records = db.query(FreightCostMapping).filter(
        FreightCostMapping.year == payload.year,
        FreightCostMapping.company_name == payload.country,
        FreightCostMapping.period == payload.period
    ).all()
    if not update_records:
        raise HTTPException(status_code=404, detail="No records found for the given filter")
    for record in update_records:
        record.fuel_cf = payload.fuel_cf
        db.commit()
    return update_records


@router.get('/freight_fuel_cost/{year}/{country}')
def fuel_cost(year: int,country:str,db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from freight period week view totals table """
    try:
        records = db.query(View_freight_fuel_cost).filter(
            View_freight_fuel_cost.columns.year == year,
            View_freight_fuel_cost.columns.country_name == country
            ).order_by(View_freight_fuel_cost.columns.period
                      ).all()
        return {"freight_fuel_cost": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    
@router.get("/freight_cost/{year}/{country_name}/{company_name}")
def get_freight_cost(year: int, country_name: str, company_name: str, db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch records from the table-valued function using raw SQL.
    """
    try:
        # Define raw SQL query to call the TVF
        query = text("""
            SELECT * FROM [dbo].[getplant_view_freight_cost] (:year, :country_name, :company_name)
        """)

        # Execute the query with parameters
        results = db.execute(query, {
            "year": year,
            "country_name": country_name,
            "company_name": company_name
        }).fetchall()

        # Convert the results to a list of dictionaries
        data = [dict(row._mapping) for row in results]

        return {"freight_cost": data}
    except Exception as e:
        # Raise HTTPException for any errors
        raise HTTPException(status_code=400, detail=f"Error querying TVF: {str(e)}") from e
    
    