from datetime import date,datetime
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter()

@router.get('/region_cropcategory')
def get_plantMtrx_by_region(db: Session = Depends(get_db)): # pragma: no cover
    """API to retrieve region details, crop category and vendor site codegit """
    region = db.query(models.region.region_name,models.region.region_id) \
            .filter(models.region.status == "ACTIVE").all()
    crop_category = db.query(models.category.category_name,models.category.crop_category) \
            .filter(models.category.status == "ACTIVE").all()
    Vendor_site_code = db.query(models.PlantSiteGrowingAreaMappingDummy.Vendor_Site_Code,models.PlantSiteGrowingAreaMappingDummy.vendor_site_id, \
                                models.PlantSiteGrowingAreaMappingDummy.growing_area,models.PlantSiteGrowingAreaMappingDummy.growing_area_id).distinct().all()
    
    return {"region": region, "crop_category":crop_category, "vendor_site_ga":Vendor_site_code}

@router.post('/add_plant_mapping', status_code=status.HTTP_201_CREATED)
def create_plant(payload: schemas.MastersMapping, db: Session = Depends(get_db)): # pragma: no cover
    """API Endpoint to add a new plant, add the plant with vendor site code mapping"""
    vendor_site_id = payload.psga_map.vendor_site_id
    count = db.query(models.vendor_site_code_dummy).filter(models.vendor_site_code_dummy.VENDOR_SITE_ID == vendor_site_id).count()

    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Or use the appropriate timezone
    new_plant = models.PlantDummy(
        **payload.plant.dict(),
        created_time=current_time,
        updated_time=current_time,
        created_by="SYSTEM",
        updated_by="SYSTEM"
    )
    db.add(new_plant)
    
    row_id = db.query(func.max(models.PlantSiteGrowingAreaMappingDummy.row_id)).scalar() or 0
    row_id += 1
    new_mapping = models.PlantSiteGrowingAreaMappingDummy(
        **payload.psga_map.dict(),
        row_id=row_id
    )
    db.add(new_mapping)

    if count>0:
        pass
    else:
        ga_payload = {
            "growing_area_name": payload.growing_area.ga_desc,  # Assuming this is the correct mapping
            "country": payload.growing_area.country,
            "created_by": "JP",
            "created_time": current_time,
            "updated_by": "JP",
            "updated_time": current_time,
            "status": payload.growing_area.ga_status,
            "region": payload.plant.region_id,  # Assuming you want to use the region_id from the plant part
            "growing_area_desc": payload.growing_area.ga_desc,
            "fresh_period_start": payload.growing_area.fp_start,
            "fresh_period_end": payload.growing_area.fp_end,
            "fresh_week_start": payload.growing_area.fw_start,
            "fresh_week_end": payload.growing_area.fw_end,
            "storage_period_start": payload.growing_area.sp_start,
            "storage_week_start": payload.growing_area.sw_start,
            "growing_area_id": payload.psga_map.growing_area_id  # Assuming this is the correct source for growing_area_id
        }

        # Insert into growing_area table
        new_growing_area = models.growing_area_dummy(**ga_payload)
        db.add(new_growing_area)

        vsc_payload = {
            "VENDOR_SITE_ID":payload.psga_map.vendor_site_id,
            "VENDOR_SITE_CODE":payload.psga_map.Vendor_Site_Code,
            "created_by":"SYSTEM",
            "created_time":current_time,
            "status":payload.vsc.vsc_status,
            "updated_by":"SYSTEM",
            "updated_time":current_time,
            "region_id":payload.plant.region_id}
        
        # Insert into Vendor Site Code table
        new_vendor_site_code = models.vendor_site_code_dummy(**vsc_payload)
        db.add(new_vendor_site_code)

    db.commit()
    db.refresh(new_plant)
    db.refresh(new_mapping)
    db.refresh(new_growing_area)
    db.refresh(new_vendor_site_code)
    return {"status": "success"}