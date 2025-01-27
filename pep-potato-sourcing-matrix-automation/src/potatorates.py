"""Potato Rates API for finance"""
# from datetime import datetime
from database import get_db
from io import BytesIO
import pandas as pd
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status,UploadFile, File
from models import (growing_area, potato_rate_mapping,FileUploadTemplate,
                    potato_rate_table_period, potato_rate_table_weekly,
                    potato_rates,region,potato_rate_plant_weekly,potato_rate_plant_period)
from schemas import potatoRateMappingPayload,PotatoRatesSchema
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session


router = APIRouter()

@router.get('/')
def get_potato_rates(db: Session = Depends(get_db)):
    """Function to get all records from potato_rates."""
    query = db.query(potato_rates).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rates  found")
    return {"status": "success", "data": query}

@router.get('/potato_rate_mapping_by_year/{year}')
def get_potato_rate_mapping_data(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(potato_rate_mapping).join(potato_rates,
                                        potato_rates.potato_rate_id == potato_rate_mapping
                                        .potato_rate_id).filter(potato_rates.year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}

@router.get("/get_potato_rate_mapping/{year}")
def get_potato_rate_mappings(year: str, db: Session = Depends(get_db)):
    """Function to records in potato_rate_mapping table."""
    records = (db.query(potato_rate_mapping.potato_rate_id,
                        potato_rate_mapping.period, potato_rate_mapping.rate, potato_rates)
               .distinct(potato_rate_mapping.period)
               .join(potato_rates,potato_rates
                     .potato_rate_id == potato_rate_mapping.potato_rate_id)
               .order_by(potato_rate_mapping.potato_rate_id, potato_rate_mapping.period)
                                .filter(potato_rates.year==year)
                                .all())
    results = [{"potato_rate_id":row.potato_rate_id, "period":row.period,
                                                "rate":row.rate, "week":0} for row in records]
    return results


@router.post("/update_potato_rates_records/")
def update_potato_rates_records(payload: potatoRateMappingPayload, db: Session = Depends(get_db)):
    """Function to update already existing records in potato_rates table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.potato_rate_id<=0 or item.period<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(potato_rate_mapping
                     ).filter(potato_rate_mapping.potato_rate_id == item.potato_rate_id,
                              potato_rate_mapping.period==item.period,
                              potato_rate_mapping.week==item.week,
                              potato_rate_mapping.p_year==item.p_year).update(
                                  {potato_rate_mapping.rate: item.rate},
                                  synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    
@router.get('/potato_rate_period_year_region/{year}/{region}')
def potato_rate_period_year_region(year:int,region_name:str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from potato_rate table for a particular year and region """
    try:
        if region_name == 'All':
            records = db.query(potato_rate_table_period
                           ).filter(potato_rate_table_period.columns.p_year == year
                                    ).order_by(potato_rate_table_period.columns.growing_area_id,
                                               potato_rate_table_period.columns.period).all()
        elif region_name == 'US':
            records =db.query(potato_rate_table_period).join(
                growing_area,growing_area.growing_area_id==potato_rate_table_period.columns.growing_area_id).join(
                    region,growing_area.region == region.region_id).filter(
                        region.country == region_name,potato_rate_table_period.columns.p_year == year).order_by(
                            potato_rate_table_period.columns.growing_area_id,potato_rate_table_period.columns.period).all()
            
        else:
            records = db.query(potato_rate_table_period
                           ).filter(potato_rate_table_period.columns.p_year == year,
                                    potato_rate_table_period.columns.region_name == region_name
                                    ).order_by(potato_rate_table_period.columns.growing_area_id,
                                               potato_rate_table_period.columns.period).all()
        
        return {"potato_rate_period_year_region": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    
@router.get('/potato_rate_period_week_year_region/{year}/{region}')
def potato_rate_period_week_year_region(year:int,region_name:str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from potato_rate table for a particular year and region """
    try:
        if region_name == 'All':
            records = db.query(potato_rate_table_weekly
                           ).filter(potato_rate_table_weekly.columns.p_year == year
                                    ).order_by(potato_rate_table_weekly.columns.growing_area_id,
                                               potato_rate_table_weekly.columns.period).all()
        elif region_name == 'US':
            records =db.query(potato_rate_table_weekly).join(
                growing_area,growing_area.growing_area_id==potato_rate_table_weekly.columns.growing_area_id).join(
                    region,growing_area.region == region.region_id).filter(
                        region.country == region_name,potato_rate_table_weekly.columns.p_year == year).order_by(
                            potato_rate_table_weekly.columns.growing_area_id,potato_rate_table_weekly.columns.period).all()
            
        else:
            records = db.query(potato_rate_table_weekly
                           ).filter(potato_rate_table_weekly.columns.p_year == year,
                                    potato_rate_table_weekly.columns.region_name == region_name
                                    ).order_by(potato_rate_table_weekly.columns.growing_area_id,
                                               potato_rate_table_weekly.columns.period).all()
        
        return {"potato_rate_period_week_year_region": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_potato_rate_mapping_for_next_year/{year}", status_code=status.HTTP_201_CREATED)
async def create_potato_rate_mapping_for_next_year(year: int , db: Session = Depends(get_db)):  # pragma: no cover
    """Function to Create potato_rate_mapping records for next year."""
    all_records = db.query(potato_rates).all()
    query_view = db.query(potato_rate_table_weekly).filter(potato_rate_table_weekly.columns.p_year==(year-1)).all() #view which contains actual value by growing_area_id
    update_count = 0
    country = ''
    existingRecord = db.query(potato_rate_mapping)\
                    .filter(potato_rate_mapping.p_year==year).all()
    for ex in existingRecord:
        db.delete(ex)
    db.commit()
    for record in all_records: # Iterate over all potato_rates
        for ele in query_view:  # Iterate through the view
            if ele.potato_rate_id == record.potato_rate_id and ele.growing_area_id == record.growing_area_id:
                if record.currency=='USD':
                    country = 'US'
                elif record.currency=='CAD':
                    country ='Canada'
                new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id, period=ele.period, week=ele.week, p_year=year, rate=ele.actual_rate, country_code=country)
                db.add(new_record)
                update_count += 1
            # else:
            #     for period in range(1,14):
            #         for week in range(1,5):
            #             new_record = potato_rate_mapping(potato_rate_id = record.potato_rate_id,
            #                                             period=period, week=week, p_year=year, rate=0,country_code=country)
            #             db.add(new_record)
            #             update_count += 1

    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}

def create_potato_rate_in_db(payload: PotatoRatesSchema, db: Session): # pragma: no cover
    if isinstance(payload, BaseModel):
        # Convert Pydantic model to dictionary
        payload_dict = payload.dict()
    else:
        # Assume payload is already a dictionary
        payload_dict = payload
    new_record = potato_rates(**payload_dict)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record



@router.post('/create_potato_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: PotatoRatesSchema, db: Session = Depends(get_db)):# pragma: no cover
    new_record = create_potato_rate_in_db(payload, db)
    return {"status": "success", "potato_rate_id": new_record.potato_rate_id}


def update_potato_rates_default(db: Session, potato_rate_id: int, year: int): # pragma: no cover
    all_records = db.query(potato_rates).filter(potato_rates.potato_rate_id == potato_rate_id).first()
    if not all_records:
        return None  # Indicate no records found

    for period in range(1, 14):
        for week in range(1, 5):
            new_record = potato_rate_mapping(potato_rate_id=all_records.potato_rate_id,
                                             period=period, week=week, p_year=year, rate=0,country_code="US")
            db.add(new_record)
    db.commit()
    return True


@router.post("/update_potato_rates_with_default_value/{potato_rate_id}/{year}")
async def update_potato_rates_with_default_value(potato_rate_id:int, year:int, db: Session = Depends(get_db)):  # pragma: no cover
    """Function to update records in potato_rates table."""
    result = update_potato_rates_default(db, potato_rate_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="No records found in the database")
    return {"status": "success"}

@router.get('/potato_rate_plant_period_view/{year}/{country}')
def potato_rate_plant_period_view(year:int,country:str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from potato rate plant period view table """
    try:
        records = db.query(potato_rate_plant_period).filter(
            potato_rate_plant_period.columns.p_year == year,
            potato_rate_plant_period.columns.country == country
            ).order_by(potato_rate_plant_period.columns.period).all()
        return {"potato_rates_plant_period_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/potato_rate_plant_week_view/{year}/{country}')
def potato_rate_plant_week_view(year: int,country:str,db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from potato rate plant week view table """
    try:
        records = db.query(potato_rate_plant_weekly).filter(
            potato_rate_plant_weekly.columns.p_year == year,
            potato_rate_plant_weekly.columns.country == country
            ).order_by(potato_rate_plant_weekly.columns.period,
                      potato_rate_plant_weekly.columns.week_no).all()
        return {"potato_rates_plant_week_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    
def potato_rates_upload_file(uploaded_year: int, user_email: str, file: UploadFile, db: Session):  # pragma: no cover
    # Capture file upload start time
    file_uploaded_time = datetime.now()

    try:
        file_extension_details= os.path.splitext(file.filename)[-1].lower()
        
        if file_extension_details not in [".xls", ".xlsx"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Supported formats are xls, xlsx.")

        contents = file.file.read()
        data = BytesIO(contents)
        
        df_dict = pd.read_excel(data, sheet_name=None)
        
        if len(df_dict.keys()) != 1:
            raise HTTPException(status_code=400, detail="Multiple sheets detected. Please upload a file with only one sheet.")
        
        df = next(iter(df_dict.values()))
        rename_columns = {
            'country': 'country_code',  # Rename 'country' in Excel to 'country_code'
            'year': 'p_year'           # Rename 'year' in Excel to 'p_year'
        }
        df = df.rename(columns=rename_columns)

        df = df.drop(['growing_area_id', 'growing_area_name'], axis=1, errors='ignore')
        
        melted_df = df.melt(id_vars=['potato_rate_id', 'country_code', 'p_year'], 
                            var_name='period_week', value_name='rate')

        melted_df['period'] = melted_df['period_week'].str.extract(r'P(\d+)').astype(int)
        melted_df['week'] = melted_df['period_week'].str.extract(r'W(\d+)').astype(int)

        melted_df = melted_df.drop(columns=['period_week'])

        melted_df['rate'] = melted_df['rate'].fillna(0)
   
        if 'p_year' not in melted_df.columns or melted_df['p_year'].isnull().all():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year data is missing in the uploaded excel template.")
        
        # Check if the 'p_year' column has multiple distinct values
        if len(melted_df['p_year'].unique()) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Year column in the uploaded file has multiple year values. Please check it once and then re-upload."
            )
        
        file_year = melted_df['p_year'].iloc[0]
        
        # Check if the uploaded_year matches the year value in the Excel file
        if uploaded_year != file_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dropdown year value {uploaded_year} does not match the year value {file_year} in the uploaded Excel file."
            )
        
        uploaded_year = int(uploaded_year)
        
        # Delete records for the specific year
        db.query(potato_rate_mapping).filter(
            potato_rate_mapping.p_year == uploaded_year
        ).delete()
        db.commit()
        
        # Insert new records
        records_to_insert = melted_df.to_dict(orient='records')
        db.execute(potato_rate_mapping.__table__.insert(), records_to_insert)
        db.commit()
        
        # Capture file process time
        file_process_time = datetime.now()
        
        # Get sheet name for logging
        sheet_name = next(iter(df_dict.keys()))
        file_name_without_ext = os.path.splitext(file.filename)[0]
        file_name = f"{file_name_without_ext}_{sheet_name}"
        file_type = file_extension_details
        file_process_status = True
        message = "Potato Rates uploaded successfully"

        upload_file_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(upload_file_data)
        db.commit()
    except HTTPException as he:
        db.rollback()
        
        # File details
        file_name = file.filename
        file_type = file_extension_details
        file_process_time = None
        file_process_status = False
        message = str(he.detail)
        
        upload_file_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(upload_file_data)
        db.commit()

        raise he
    except Exception as e:
        db.rollback()
        
        # File details
        file_name = file.filename
        file_type = file_extension_details
        file_process_time = None
        file_process_status = False
        message = str(e)

        upload_file_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(upload_file_data)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"detail": f"Rates successfully uploaded for the year: {uploaded_year}"}

@router.post("/upload_file_potato_rates", status_code=status.HTTP_201_CREATED)
async def upload_file_potato_rates(uploaded_year: int, user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):# pragma: no cover
    return potato_rates_upload_file(uploaded_year, user_email, file, db)

