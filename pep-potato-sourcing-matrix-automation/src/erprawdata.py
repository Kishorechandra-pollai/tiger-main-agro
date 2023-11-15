from datetime import datetime, timedelta
from models import erp_raw_data_us, View_site_plant_growing_area_mapping, view_growing_area_mapping_Alice, view_plant_growing_area_Alice
from schemas import ErpRawDataUsSchema
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()

@router.get('/')
def get_all_data(db: Session = Depends(get_db)):
    """Function to getch all records from erp_raw_data_us Table."""
    try:
        records = db.query(erp_raw_data_us).all()
        return {"data": records}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


def cal_spend(item: erp_raw_data_us):
    """Function to calculate spend."""
    spend_column = item.UNIT_PRICE * item.QUANTITY_BILLED
    rec_qty_cwt = item.RECEIPT_QUANTITY/100
    rec_qty_mcqt = rec_qty_cwt/1000
    return ErpRawDataUsSchema(UNIT_PRICE=item.UNIT_PRICE, QUANTITY_BILLED =item.QUANTITY_BILLED,
                              Spend=spend_column, Rec_Qty_CWT= rec_qty_cwt, Rec_Qty_MCWT=rec_qty_mcqt)


def cal_spend_by_value(unit_price, quantity_billed):
    """Function to calculate spend."""
    spend_column = unit_price * quantity_billed
    return spend_column

@router.post("/update_spend/", status_code=status.HTTP_201_CREATED)
async def update_spend(db: Session = Depends(get_db)):
    """FastAPI endpoint to update spend value."""
    records = db.query(erp_raw_data_us).all()
    for row in records:
        spend = cal_spend_by_value(row.UNIT_PRICE, row.QUANTITY_BILLED)
        row.spend = spend
    db.commit()
    return {"status": "success"}


def calculate_period_week_combinations(unload_date: datetime) :
    """Function to calculate period and week for selected date."""
    start_date = datetime(unload_date.year, 1,1)
    while start_date.weekday()!=6:
        start_date -=timedelta(days=1)

    week = 1
    period = 1
    result = []
    loop_count=1
    current_date = start_date
    while current_date <= unload_date:
        result.append((f"P{period}W{week}",loop_count))
        loop_count+=1
        week+=1

        if week>4:
            period+=1
            week=1
        if period>13:
            break

        current_date+=timedelta(days=7)

        if current_date.month!=start_date.month:
            start_date = current_date

    return result

@router.post("/update_erp_raw_data/", status_code=status.HTTP_201_CREATED)
async def update_erp_raw_data(db: Session = Depends(get_db)):
    """Function to update records in ERP table."""
    # Fetch all records from the database
    all_records = db.query(erp_raw_data_us).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    # List to store the result in tabular format
    result_table = []
    i=1
    crop = ''
    # Calculate P*W values for each record
    for record in all_records:
        record_dict = {}
        print('records',i)
        i+=1
        record_dict = {"BPA_Number": record.BPA_Number}
        spend = cal_spend_by_value(record.UNIT_PRICE, record.QUANTITY_BILLED)
        plant_id=get_plant_by_name(record.Ship_To_Organization, db)
        site_id = get_site_id_by_vendor_name(record.VENDOR_SITE_CODE, db)
        grower_id = get_grower_id_by_vendor_name(record.VENDOR_NAME, db)
        growignarea_id = get_growing_area_id_by_vendor_name(record.VENDOR_NAME, db)
        region_id = get_region_by_name(record.Ship_To_Organization, db)
        if record.UNLOAD_DATE and isinstance(record.UNLOAD_DATE, str):
            crop = get_crop_year(record.UNLOAD_DATE)
            unload_date = datetime.strptime(record.UNLOAD_DATE, '%d-%b-%Y %H:%M:%S')
            result = calculate_period_week_combinations(unload_date)
            for unl_date_pw, loop_count in result:
                record.Unl_Date_PxW=unl_date_pw
                record.Unl_Date_Wk_Num = loop_count

        if record.RECEIPT_DATE:
            receipt = str(record.RECEIPT_DATE)

            rece_date = datetime.strptime(receipt, '%Y-%m-%d %H:%M:%S')
            formated_date  = rece_date.strftime('%d-%b-%Y %H:%M:%S')
            receipt_date = datetime.strptime(formated_date, '%d-%b-%Y %H:%M:%S')

            result= calculate_period_week_combinations(receipt_date)

            for rec_date_pw, loop_count in result:
                record.Rec_Date_PxW=rec_date_pw
                record.Rec_Date_wk_num = loop_count

        record.status = 'Success'
        record.spend = spend
        record.Region_id = region_id
        record.Plant_Id = plant_id
        record.growignarea_id = growignarea_id
        record.Site_Id = site_id
        record.crop_year = crop
        record.grower_Id = grower_id
        record.PROCESS_TIME = datetime.now()
        result_table.append(record_dict)
        db.commit()

    return {"status": "success","data":result_table}


def get_crop_year(selected_date : datetime):
    """Function to calculate crop year."""
    unload_date = datetime.strptime(selected_date, '%d-%b-%Y %H:%M:%S')

    original_year = unload_date.year
    year = str(unload_date.year)[-2:]
    prev_year = int(year)-1
    next_year = int(year)+1

    for month in range(1,12):
        if month <=4:
            return f"{prev_year}{year} Storage"
        elif month >=11:
            return f"{year}{next_year} Fresh"
        else:
            return f"{original_year} Storage"

def get_plant_by_name(plant_name, db: Session = Depends(get_db)):
    """Function to get plant id."""
    plant_query = (db.query(View_site_plant_growing_area_mapping.columns.plant_id)
                  .where(View_site_plant_growing_area_mapping.columns.plant_name==plant_name)
                  .first())

    if not plant_query:
        plant_id = None
        return plant_id

    plant_id =plant_query.plant_id
    return plant_id

def get_site_id_by_vendor_name(site_code, db: Session = Depends(get_db)):
    """Function to get site id."""
    site_query = (db.query(View_site_plant_growing_area_mapping.columns.VENDOR_SITE_ID)
                  .where(View_site_plant_growing_area_mapping.columns.VENDOR_SITE_CODE==site_code)
                  .first())
    if not site_query:
        site_id = None
        return site_id

    site_id =site_query.VENDOR_SITE_ID
    return site_id

def get_grower_id_by_vendor_name(vender_name, db: Session = Depends(get_db)):
    """Function to get grower id."""
    grower_query = (db.query(view_growing_area_mapping_Alice.columns.grower_id)
                  .where(view_growing_area_mapping_Alice.columns.grower_name==vender_name)
                  .first())

    if not grower_query:
        grower_id = None
        return grower_id
    grower_id =grower_query.grower_id
    return grower_id

def get_growing_area_id_by_vendor_name(vendor_name, db: Session = Depends(get_db)):
    """Function to get growing area id."""
    site_query = (db.query(view_growing_area_mapping_Alice.columns.growing_area_id)
                  .where(view_growing_area_mapping_Alice.columns.grower_name==vendor_name)
                  .first())
    if not site_query:
        growing_area_id = None
        return growing_area_id

    growing_area_id =site_query.growing_area_id
    return growing_area_id

def get_region_by_name(plant_name, db: Session = Depends(get_db)):
    """Function to get region name."""
    region_query = (db.query(view_plant_growing_area_Alice.columns.region_ID)
                    .where(view_plant_growing_area_Alice.columns.plant_name==plant_name)
                    .first())

    if not region_query:
        region_id = None
        return region_id

    region_id =region_query.region_ID
    return region_id

@router.post("/update_data/", status_code=status.HTTP_201_CREATED)
async def update_data(db: Session = Depends(get_db)):
    """Function to update records in ERP table."""
    # Fetch all records from the database
    all_records = db.query(erp_raw_data_us).all()
    # Ensure there are records in the database
    if all_records.count==0:
        raise HTTPException(status_code=404, detail="No records found in the database")

    for record in all_records:
        if record.UNLOAD_DATE and isinstance(record.UNLOAD_DATE, str):
           crop = get_crop_year(record.UNLOAD_DATE)
           record.crop_year = crop

        db.commit()

    return {"status": "success"}