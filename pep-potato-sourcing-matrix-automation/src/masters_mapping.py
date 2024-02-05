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
    try:
        region = db.query(models.region.region_name,models.region.region_id) \
                .filter(models.region.status == "ACTIVE").all()
        crop_category = db.query(models.category.category_name,models.category.crop_category) \
                .filter(models.category.status == "ACTIVE").all()
        Vendor_site_code = db.query(models.PlantSiteGrowingAreaMapping.Vendor_Site_Code,models.PlantSiteGrowingAreaMapping.vendor_site_id, \
                                    models.PlantSiteGrowingAreaMapping.growing_area,models.PlantSiteGrowingAreaMapping.growing_area_id).distinct().all()
        company_name = db.query(models.Plant.company_name).distinct().all()
        
        return {"region": region, "crop_category":crop_category, "vendor_site_ga":Vendor_site_code,"company_name":company_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/add_plant_mapping', status_code=status.HTTP_201_CREATED)
def create_plant(payload: schemas.MastersMapping, db: Session = Depends(get_db)): # pragma: no cover
    """API Endpoint to add a new plant, add the plant with vendor site code mapping"""
    try:
        plant_name = payload.plant.plant_name
        plant_count = db.query(models.Plant).filter(models.Plant.plant_name == plant_name).count()
        if plant_count>0:
            return {"status":"plant already exists"}
        vendor_site_id = payload.psga_map.vendor_site_id
        count = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_ID == vendor_site_id).count()

        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Or use the appropriate timezone

        plant_id = db.query(func.max(models.Plant.plant_id)).scalar() or 0
        plant_id+=1

        new_plant = models.Plant(
            **payload.plant.dict(),
            plant_id=plant_id,
            created_time=current_time,
            updated_time=current_time,
            created_by="SYSTEM",
            updated_by="SYSTEM"
        )
        db.add(new_plant)
        
        row_id = db.query(func.max(models.PlantSiteGrowingAreaMapping.row_id)).scalar() or 0
        row_id += 1
        new_mapping = models.PlantSiteGrowingAreaMapping(
            **payload.psga_map.dict(),
            row_id=row_id,
            plant_id=plant_id
        )
        db.add(new_mapping)

        if count>0:
            pass
        else:
            ga_payload = {
                "growing_area_name": payload.psga_map.growing_area,  # Assuming this is the correct mapping
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
            new_growing_area = models.growing_area(**ga_payload)
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
            new_vendor_site_code = models.vendor_site_code(**vsc_payload)
            db.add(new_vendor_site_code)
            ga_vsc=True

        db.commit()
        db.refresh(new_plant)
        db.refresh(new_mapping)
        if ga_vsc:
            db.refresh(new_growing_area)
            db.refresh(new_vendor_site_code)
        return {"status": "New plant added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

## owner,region,country
## growing_area_name
@router.get('/growingarea_region')
def get_plantMtrx_by_region(db: Session = Depends(get_db)): # pragma: no cover
    """API to retrieve region details, crop category and vendor site codegit """
    try:
        region = db.query(models.region.region_name,models.region.region_id) \
                .filter(models.region.status == "ACTIVE").all()
        owner = db.query(models.growers.owner).distinct().all()
        country = db.query(models.growers.country).distinct().all()
        return {"region":region,"owner":owner,"country":country}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


@router.post('/add_grower_mapping', status_code=status.HTTP_201_CREATED)
def create_plant(payload: schemas.MastersMappingGrowers, db: Session = Depends(get_db)): # pragma: no cover
    """Api to add grower in master table and the grower - growing area mapping table"""
    try:
        grower_name = payload.growers.grower_name
        grower_count = db.query(models.growers).filter(models.growers.grower_name == grower_name).count()
        if grower_count>0:
            return {"status":"grower already exists"}
        grower_id = db.query(func.max(models.growers.grower_id)).scalar() or 0
        grower_id+=1
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        new_grower = models.growers(
            **payload.growers.dict(),
            grower_id=grower_id,
            created_time=current_time,
            updated_time=current_time,
            created_by="SYSTEM",
            updated_by="JP"
        )
        db.add(new_grower)

        growing_area_name = payload.gr_area_map.growing_area_name
        count = db.query(models.preferred_grower).filter(models.preferred_grower.growing_area_name == growing_area_name).count()
        if count>0:
            growing_area_id = db.query(models.preferred_grower.growing_area_id).filter(models.preferred_grower.growing_area_name == growing_area_name).first()[0]
        else:
            growing_area_id = db.query(func.max(models.preferred_grower.growing_area_id)).scalar() or 0
            growing_area_id += 1
        
        row_id = db.query(func.max(models.preferred_grower.row_id)).scalar() or 0
        row_id += 1
        new_gr_mapping = models.preferred_grower(
            **payload.gr_area_map.dict(),
            row_id=row_id,
            grower_id=grower_id,
            growing_area_id=growing_area_id,
            grower_name=payload.growers.grower_name
        )
        db.add(new_gr_mapping)
        db.commit()
        db.refresh(new_grower)
        db.refresh(new_gr_mapping)
        return {"status": "New grower added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))