"""Solid Rates API for finance"""
# from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile, File
from models import (growing_area, solid_rate_mapping, solids_rate_table_period,solids_rate_plant_period,solids_period_totals,
                    solids_rates,region,FileUploadTemplate)
from schemas import solidRateMappingPayload,SolidRatesSchema
from pydantic import BaseModel
from io import BytesIO
import pandas as pd
import os
from datetime import datetime

router = APIRouter()

@router.get('/')
def get_solids_rates(db: Session = Depends(get_db)): # pragma: no cover
    """Function to get all records from solid_rates."""
    query = db.query(solids_rates).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solids_rates  found")
    return {"status": "success", "data": query}

@router.get('/getBySolidsRateId/{solids_rate_id}')
def get_by_solids_rate_id(solids_rate_id: int, db: Session = Depends(get_db)):
    """Function to get records by solids rate id"""
    solid_rate = db.query(solids_rates).filter(solids_rates.solids_rate_id ==
                                               solids_rate_id).first()
    if not solid_rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No solids_rate_id: {solids_rate_id} found")
    return {"status": "success", "solid_rate": solid_rate}

@router.get('/solid_rate_mapping/{year}')
def get_solid_rate_mapping(year: str, db: Session = Depends(get_db)):
    """Function to get all records from potato_rate_mapping."""
    query = db.query(solid_rate_mapping).join(solids_rates,
                                        solids_rates.solids_rate_id ==
                                        solid_rate_mapping.solids_rate_id
                                        ).filter(solid_rate_mapping.period_year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solid_rate_mapping  found")
    return {"status": "success", "data": query}

@router.post("/update_solid_rates_records/")
def update_solid_rates_records(payload: solidRateMappingPayload,db: Session = Depends(get_db)):
    """Function to update already existing records in solid_rate_mapping table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            db.query(solid_rate_mapping).filter(solid_rate_mapping.solids_rate_id
                                                == item.solids_rate_id,
                                                solid_rate_mapping.period==item.period,
                                                solid_rate_mapping.period_year==item.period_year).update(
                {solid_rate_mapping.rate: item.rate}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# @router.get('/solid_rate_period_year/{year}/{region_id}')
# def solid_rate_period_year(year:int, region_id:int,db: Session = Depends(get_db)):
#     """Function to fetch all records from solids_rate table for a particular year """
#     try:
#         records = db.query(solids_rate_table_period).filter(
#             solids_rate_table_period.columns.year == year,
#             solids_rate_table_period.columns.region == region_id
#             ).order_by(solids_rate_table_period.columns.growing_area_id,
#                        solids_rate_table_period.columns.period).all()
#         return {"solids_rate_period_year": records}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/solid_rate_period_year_region/{year}/{region}')
def solid_rate_period_year_region(year:int,region_name:str, db: Session = Depends(get_db)): 
    """Function to fetch all records from solids_rate table for a particular year """
    try:
        if region_name == 'All':
            records = db.query(solids_rate_table_period
                           ).filter(solids_rate_table_period.columns.year == year
                                    ).order_by(solids_rate_table_period.columns.growing_area_id,
                                               solids_rate_table_period.columns.period).all()
        elif region_name == 'US':
            records =db.query(solids_rate_table_period).join(
                growing_area,growing_area.growing_area_id==solids_rate_table_period.columns.growing_area_id).join(
                    region,growing_area.region == region.region_id).filter(
                        region.country == region_name,solids_rate_table_period.columns.year == year).order_by(
                            solids_rate_table_period.columns.growing_area_id,solids_rate_table_period.columns.period).all()
            
        else:
            records = db.query(solids_rate_table_period
                           ).filter(solids_rate_table_period.columns.year == year,
                                    solids_rate_table_period.columns.region_name == region_name
                                    ).order_by(solids_rate_table_period.columns.growing_area_id,
                                               solids_rate_table_period.columns.period).all()
        
        return {"solids_period_year_region": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/create_solid_rates_mappings_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_solid_rates_mappings_for_next_year(year: int, db: Session = Depends(get_db)): # pragma: no cover
    """Function to Create solid_rate_mapping records for next year."""
    all_records = db.query(solids_rates).all()
    query_view = db.query(solids_rate_table_period).filter(solids_rate_table_period.columns.year==(year-1)).all() #view which contains actual value by growing_area_id
    update_count = 0
    country = ''
    existingRecord = db.query(solid_rate_mapping)\
                    .filter(solid_rate_mapping.period_year==year).all()
    for ex in existingRecord:
        db.delete(ex)
    db.commit()
    for record in all_records: # Iterate over all solids_rates
        if record.currency=='USD':
            country = 'US'
        elif record.currency=='CAD':
            country ='Canada'
        for ele in query_view:  # Iterate through the view
            if ele.growing_area_id == record.growing_area_id:
                new_record = solid_rate_mapping(solids_rate_id = record.solids_rate_id, period=ele.period, period_year=year, rate=ele.actual_rate, country_code=country)
                db.add(new_record)
                update_count += 1
            # else:
            #     for period in range(1,14):
            #         new_record = solid_rate_mapping(solids_rate_id = record.solids_rate_id,
            #                                             period=period, period_year=year, rate=0,country_code=country)
            #         db.add(new_record)
            #         update_count += 1

    db.commit()
    return {"status": "success", "Records added": update_count, "for Year": year}


def create_solid_rate_in_db(payload: SolidRatesSchema, db: Session): # pragma: no cover
    if isinstance(payload, BaseModel):
        # Convert Pydantic model to dictionary
        payload_dict = payload.dict()
    else:
        # Assume payload is already a dictionary
        payload_dict = payload
    new_record = solids_rates(**payload_dict)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.post('/create_solids_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: SolidRatesSchema, db: Session = Depends(get_db)): # pragma: no cover
    new_record = create_solid_rate_in_db(payload, db)
    return {"status": "success", "solids_rate_id": new_record.solids_rate_id}


def update_solids_rates_default(db: Session, solids_rate_id: int, year: int): # pragma: no cover
    all_records = db.query(solids_rates).filter(solids_rates.solids_rate_id == solids_rate_id).first()
    if not all_records:
        return None  # Indicate no records found

    for period in range(1, 14):
        new_record = solid_rate_mapping(solids_rate_id=all_records.solids_rate_id,
                                        period=period, period_year=year, rate=0,country_code="US")
        db.add(new_record)
    db.commit()  
    return True  


@router.post("/update_solids_rates_with_default_value/{solids_rate_id}/{year}")
async def update_solids_rates_with_default_value(solids_rate_id:int, year:int, db: Session = Depends(get_db)): # pragma: no cover
    """Function to update records in solids_rates table."""
    result = update_solids_rates_default(db, solids_rate_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="No records found in the database")
    return {"status": "success"}

@router.get('/solid_rate_period_year_plant/{year}/{country}')
def solid_rate_period_year_plant(year:int,country:str, db: Session = Depends(get_db)):# pragma: no cover
    """Function to fetch all records from Solids-plant period view table """
    try:
        records = db.query(solids_rate_plant_period).filter(
            solids_rate_plant_period.columns.p_year == year,
            solids_rate_plant_period.columns.country == country
            ).order_by(solids_rate_plant_period.columns.plant_id,solids_rate_plant_period.columns.period).all()
        return {"solids_plant_period_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/solid_rate_period_plant_totals/{year}/{country}')
def solid_rate_period_plant_totals(year:int,country:str, db: Session = Depends(get_db)):# pragma: no cover
    """Function to fetch all records from Solids-plant period view totals table """
    try:
        records = db.query(solids_period_totals).filter(
            solids_period_totals.columns.p_year == year,
            solids_period_totals.columns.country == country
            ).order_by(solids_period_totals.columns.period).all()
        return {"solids_plant_period_totals": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
   
def solids_upload_file(uploaded_year: int, user_email: str, file: UploadFile, db: Session):  # pragma: no cover
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
        df = df.drop(['growing_area_id', 'growing_area_name'], axis=1, errors='ignore')
        
        # Melt DataFrame
        melted_df = df.melt(id_vars=['solids_rate_id', 'country', 'year'], var_name='period', value_name='rate')
        melted_df['period'] = melted_df['period'].str.extract(r'(\d+)').astype(int)
        
        # Replace null values in the rate column with 0
        melted_df['rate'] = melted_df['rate'].fillna(0)
        
        # Rename columns to match database schema
        melted_df.rename(columns={'year': 'period_year', 'country': 'country_code'}, inplace=True)
        
        # Ensure 'period_year' column exists and is not empty
        if 'period_year' not in melted_df.columns or melted_df['period_year'].isnull().all():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year data is missing in the uploaded excel template.")
        
        # Check if the 'period_year' column has multiple distinct values
        if len(melted_df['period_year'].unique()) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Year column in the uploaded file has multiple year values. Please check it once and then re-upload."
            )
        
        file_year = melted_df['period_year'].iloc[0]
        
        # Check if the uploaded_year matches the year value in the Excel file
        if uploaded_year != file_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dropdown year value {uploaded_year} does not match the year value {file_year} in the uploaded Excel file."
            )
        
        uploaded_year = int(uploaded_year)
        
        # Delete records for the specific year
        db.query(solid_rate_mapping).filter(
            solid_rate_mapping.period_year == uploaded_year
        ).delete()
        db.commit()
        
        # Insert new records
        records_to_insert = melted_df.to_dict(orient='records')
        db.execute(solid_rate_mapping.__table__.insert(), records_to_insert)
        db.commit()
        
        # Capture file process time
        file_process_time = datetime.now()
        
        # Get sheet name for logging
        sheet_name = next(iter(df_dict.keys()))
        file_name_without_ext = os.path.splitext(file.filename)[0]
        file_name = f"{file_name_without_ext}_{sheet_name}"
        file_type = file_extension
        file_process_status = True
        message = "Solids uploaded successfully"

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

    return {"detail": f"Solids successfully uploaded for the year: {uploaded_year}"}


# FastAPI route for file upload
@router.post("/upload_file_solids", status_code=status.HTTP_201_CREATED)
async def upload_file_solids(uploaded_year: int, user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):# pragma: no cover
    return solids_upload_file(uploaded_year, user_email, file, db)


