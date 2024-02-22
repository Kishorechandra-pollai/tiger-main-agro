from datetime import date,datetime
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from potatorates import create_potato_rate_in_db, update_potato_rates_default
from solidrates import create_solid_rate_in_db, update_solids_rates_default
from freightcost import create_freight_rates_in_db,update_freight_cost_mapping_with_default_value,update_freight_rates_with_default_value

router = APIRouter()

@router.get('/get_mapping')
def get_mapping(db: Session = Depends(get_db)): # pragma: no cover
    """API to retrieve region details, crop category and vendor site codegit """
    # try:
    region = db.query(models.region.region_name,models.region.region_id) \
            .filter(models.region.status == "ACTIVE").all()
    crop_category = db.query(models.category.category_name,models.category.crop_category) \
            .filter(models.category.status == "ACTIVE").all()
    company_name = db.query(models.Plant.company_name).distinct().all()
    vendor_site_code = db.query(models.vendor_site_code.VENDOR_SITE_CODE,models.vendor_site_code.VENDOR_SITE_ID) \
            .filter(models.vendor_site_code.status == "ACTIVE").distinct().all()
    growing_area = db.query(models.growing_area.growing_area_name,models.growing_area.growing_area_id) \
            .filter(models.growing_area.status=="ACTIVE").distinct().all()

    # growing_area = (db.query(
    #                 func.concat(models.growing_area.growing_area_name, ' | ', \
    #                 models.growing_area.growing_area_desc).label('growing_area'), \
    #                 models.growing_area.growing_area_id) \
    #                 .filter(models.growing_area.status=="ACTIVE").distinct().all())
    growing_area = db.query(func.concat(models.growing_area.growing_area_name, ' | ', \
                                            models.growing_area.growing_area_desc).label('growing_area'), \
                                            models.growing_area.growing_area_id) \
                                            .filter(models.growing_area.status=="ACTIVE").distinct().all()

    return {"region": region, "crop_category":crop_category, "company_name":company_name, "vendor_site":vendor_site_code,"growing_area":growing_area}

@router.post('/add_plant', status_code=status.HTTP_201_CREATED)
def add_new_plant(payload: schemas.PlantSchemaDummy, db: Session = Depends(get_db)): # pragma: no cover
    """API Endpoint to add a new plant, add the plant with vendor site code mapping"""
    # try:
    plant_name = payload.plant_name
    plant_count = db.query(models.Plant).filter(models.Plant.plant_name == plant_name).count()
    if plant_count>0:
        return {"status":"plant already exists"}
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(payload.dict())
    new_plant = models.Plant(
        **payload.dict(),
        # plant_id=plant_id,
        created_time=current_time,
        updated_time=current_time,
        created_by="SYSTEM",
        updated_by="SYSTEM",
        status="ACTIVE"
    )
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)
    return {"status":"New Plant added successfully"}


@router.post('/add_grower', status_code=status.HTTP_201_CREATED)
def add_new_plant(payload: schemas.GrowersDummy, db: Session = Depends(get_db)): # pragma: no cover
    """Api to add grower in master table and the grower - growing area mapping table"""
    # try:
    grower_name = payload.grower_name
    grower_count = db.query(models.growers).filter(models.growers.grower_name == grower_name).count()
    if grower_count>0:
        return {"status":"grower already exists"}
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(payload.dict())
    new_grower = models.growers(
        # **payload.growers.dict(),
        **payload.dict(),
        # grower_id=grower_id,
        created_time=current_time,
        updated_time=current_time,
        created_by="SYSTEM",
        updated_by="JP"
    )
    db.add(new_grower)
    db.commit()
    db.refresh(new_grower)
    return {"status":"New grower added successfully"}

@router.post('/add_vendor_site', status_code=status.HTTP_201_CREATED)
def add_vendor_site(payload: schemas.VendorSiteCodeSchemaMasters, db: Session = Depends(get_db)): # pragma: no cover
    """Api to add grower in master table and the grower - growing area mapping table"""
    # try:
    vendor_site_code = payload.VENDOR_SITE_CODE
    vsc_count = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_CODE == vendor_site_code).count()
    if vsc_count>0:
        return {"status":"Vendor Site already exists"}
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(payload.dict())
    new_vsc = models.vendor_site_code(
        **payload.dict(),
        # grower_id=grower_id,
        created_time=current_time,
        updated_time=current_time,
        created_by="SYSTEM",
        updated_by="JP",
        status = "ACTIVE"
    )
    db.add(new_vsc)
    db.commit()
    db.refresh(new_vsc)
    return {"status":"New vendor site added successfully"}

@router.post('/add_growing_area', status_code=status.HTTP_201_CREATED)
def add_growing_area(payload: schemas.GrowingAreaSchemaMasters, db: Session = Depends(get_db)): # pragma: no cover
    """Api to add grower in master table and the grower - growing area mapping table"""
    # try:
    growing_area_name = payload.growing_area_name
    ga_count = db.query(models.growing_area).filter(models.growing_area.growing_area_name == growing_area_name).count()
    if ga_count>0:
        return {"status":"growing area already exists"}
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    new_ga = models.growing_area(
        **payload.dict(),
        # grower_id=grower_id,
        created_time=current_time,
        updated_time=current_time,
        created_by="SYSTEM",
        updated_by="JP",
        status="ACTIVE"
    )
    db.add(new_ga)
    db.commit()
    db.refresh(new_ga)
    return {"status":"New growing area added successfully"}

