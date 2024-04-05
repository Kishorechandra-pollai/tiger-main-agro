from datetime import date,datetime
from fastapi import Depends, HTTPException, status, APIRouter,File, UploadFile
import pandas as pd
from io import StringIO,BytesIO
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
    try:
        region = db.query(models.region.region_name,models.region.region_id) \
                .filter(models.region.status == "ACTIVE").all()
        crop_category = db.query(models.category.category_name,models.category.crop_category) \
                .filter(models.category.status == "ACTIVE").all()
        company_name = db.query(models.Plant.company_name).distinct().all()
        vendor_site_code = db.query(models.vendor_site_code.VENDOR_SITE_CODE,models.vendor_site_code.VENDOR_SITE_ID) \
                .filter(models.vendor_site_code.status == "ACTIVE").distinct().all()
        growing_area = db.query(models.growing_area.growing_area_name,models.growing_area.growing_area_id) \
                .filter(models.growing_area.status=="ACTIVE").distinct().all()

        growing_area_desc = db.query(func.concat(models.growing_area.growing_area_name, ' | ', \
                                                models.growing_area.growing_area_desc).label('growing_area'), \
                                                models.growing_area.growing_area_id) \
                                                .filter(models.growing_area.status=="ACTIVE").distinct().all()

        return {"region": region, "crop_category":crop_category, "company_name":company_name, "vendor_site":vendor_site_code,"growing_area":growing_area,"gr_area_desc":growing_area_desc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_plant', status_code=status.HTTP_201_CREATED)
def add_new_plant(payload: schemas.PlantSchemaDummy, db: Session = Depends(get_db)): # pragma: no cover
    """API Endpoint to add a new plant, add the plant with vendor site code mapping"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/add_grower', status_code=status.HTTP_201_CREATED)
def add_new_plant(payload: schemas.GrowersDummy, db: Session = Depends(get_db)): # pragma: no cover
    """Api to add grower in master table and the grower - growing area mapping table"""
    try:
        grower_name = payload.grower_name
        grower_count = db.query(models.growers).filter(models.growers.grower_name == grower_name).count()
        if grower_count>0:
            return {"status":"grower already exists"}
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(payload.dict())
        new_grower = models.growers(
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_vendor_site', status_code=status.HTTP_201_CREATED)
def add_vendor_site(payload: schemas.VendorSiteCodeSchemaMasters, db: Session = Depends(get_db)): # pragma: no cover
    """Api to add grower in master table and the grower - growing area mapping table"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_growing_area', status_code=status.HTTP_201_CREATED)
def add_growing_area(payload: schemas.GrowingAreaSchemaMasters, db: Session = Depends(get_db)): # pragma: no cover
    """Api to add grower in master table and the grower - growing area mapping table"""
    try:
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
        growing_area_id = new_ga.growing_area_id
        potato_rate_payload = {# "potato_rate_id":potato_rate_id,
                                "year":datetime.utcnow().year,
                                "growing_area_id_old":999,
                                "created_time":current_time,
                                "created_by":"System",
                                "updated_time":current_time,
                                "updated_by":"SYSTEM",
                                "currency":"USD",
                                "growing_area_id":growing_area_id}
        potato_rates_record = create_potato_rate_in_db(potato_rate_payload, db)
        potato_rate_id = potato_rates_record.potato_rate_id

        ## Solids Rates
        solids_rate_payload = {# "solids_rate_id":solids_rate_id,
                                "growing_area_id_old":999,
                                "created_time":current_time,
                                "created_by":"System",
                                "updated_time":current_time,
                                "updated_by":"SYSTEM",
                                "currency":"USD",
                                "growing_area_id":growing_area_id}
        solid_rate_record = create_solid_rate_in_db(solids_rate_payload, db)
        solids_rate_id = solid_rate_record.solids_rate_id
        ## Potato mappings
        update_potato_rates_default(db,potato_rate_id,datetime.utcnow().year)

        ## Solids mappings
        update_solids_rates_default(db, solids_rate_id, datetime.utcnow().year)
        db.commit()
        return {"status":"New growing area added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_plants')
def get_plants(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_plants = (db.query(models.Plant.plant_id,
                               models.Plant.company_name,
                               func.trim(models.Plant.created_by).label("created_by"),
                               func.trim(models.Plant.status).label("status"),
                               func.trim(models.Plant.updated_by).label("updated_by"),
                               models.Plant.created_time,
                               models.Plant.pgt_plant_name,
                               models.Plant.plant_code,
                               models.Plant.plant_name,
                               models.Plant.region_id,
                               models.Plant.crop_category_id,
                               models.Plant.updated_time).filter(models.Plant.status=="ACTIVE").distinct().all())
        return {"plants":all_plants}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_plant/{plant_name}')
def get_plant(plant_name: str, db: Session = Depends(get_db)): # pragma: no cover
    try:
        plant_details = (db.query(models.Plant.plant_id,
                               models.Plant.company_name,
                               func.trim(models.Plant.created_by).label("created_by"),
                               func.trim(models.Plant.status).label("status"),
                               func.trim(models.Plant.updated_by).label("updated_by"),
                               models.Plant.created_time,
                               models.Plant.pgt_plant_name,
                               models.Plant.plant_code,
                               models.Plant.plant_name,
                               models.Plant.region_id,
                               models.Plant.crop_category_id,
                               models.Plant.updated_time).filter(models.Plant.plant_name == plant_name,models.Plant.status=="ACTIVE").first())
        vsc_ga = db.query(models.PlantSiteGrowingAreaMapping.growing_area,models.PlantSiteGrowingAreaMapping.Vendor_Site_Code,
                        models.PlantSiteGrowingAreaMapping.growing_area_id,
                        models.PlantSiteGrowingAreaMapping.vendor_site_id).filter(models.PlantSiteGrowingAreaMapping.plant_name==plant_name).all()
        empty_json =  [{
            "growing_area": "Not Appl",
            "Vendor_Site_Code": "Not Appl",
            "growing_area_id": 000,
            "vendor_site_id": 000
            }]
        combined_result = {
            "plant_detail": plant_details if plant_details else ["No plant detail found"],
            "vsc_ga": vsc_ga if vsc_ga else empty_json}
        return {"details":combined_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/modify_ex_plant')
def modify_ex_plant(payload: schemas.EditPSGAMastersSchema,db:Session = Depends(get_db)):  # pragma: no cover
    try:
        plant_name = payload.plant_name
        plant_id = payload.plant_id
        flag=False
        existingRecord = db.query(models.PlantSiteGrowingAreaMapping)\
                                .filter(models.PlantSiteGrowingAreaMapping.plant_name==plant_name).all()
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        seen_combinations = set()
        for ex in existingRecord:
            db.delete(ex)

        for ga, vsc, ga_id, vs_id in zip(payload.growing_area, payload.vsc, payload.ga_id, payload.vs_id):
            unique_combination = (payload.plant_name, vsc, ga)
            if unique_combination in seen_combinations:
                continue

            seen_combinations.add(unique_combination)
            new_mapping = models.PlantSiteGrowingAreaMapping(
                plant_name=payload.plant_name,
                growing_area=ga,
                Vendor_Site_Code=vsc,
                growing_area_id=ga_id,
                vendor_site_id=vs_id,
                plant_id=plant_id
            )
            db.add(new_mapping)
            flag=True

            freight_cost_exists = db.query(models.FreightCostRate).filter(
                models.FreightCostRate.plant_id == plant_id,
                models.FreightCostRate.growing_area_id == ga_id,
                models.FreightCostRate.vendor_site_id == vs_id
            ).first()
            
            if not freight_cost_exists:
                freight_cost_id = db.query(func.max(models.FreightCostRate.freight_cost_id)).scalar() or 0
                freight_cost_id += 1
                freight_cost_rate_payload = {"freight_cost_id":freight_cost_id,
                                            "plant_id":plant_id,
                                            "vendor_site_id":vs_id,
                                            "comment": "comment",
                                            "created_time":current_time,
                                            "created_by":"System",
                                            "updated_time":current_time,
                                            "updated_by":"SYSTEM",
                                            "currency":"USD",
                                            "growing_area_id":ga_id}
                create_freight_rates_in_db(freight_cost_rate_payload, db)

                ## Freight Cost mappings
                update_freight_rates_with_default_value(freight_cost_id,datetime.utcnow().year,db)



        db.commit()
        if flag:
            db.refresh(new_mapping)
        return {"status":"Updated the mapping successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_plant/{plant_id}', status_code=status.HTTP_200_OK)
def update_plant(plant_id: int, update_payload: schemas.UpdatePlantSchema, db: Session = Depends(get_db)): # pragma: no cover
    try:
        # Fetch the existing region
        plant_to_update = db.query(models.Plant).filter(models.Plant.plant_id == plant_id).first()
        
        if not plant_to_update:
            raise HTTPException(status_code=404, detail="Plant not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plant_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            plant_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "plant updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/update_grower/{grower_id}', status_code=status.HTTP_200_OK)
def update_plant(grower_id: int, update_payload: schemas.GrowersDummy, db: Session = Depends(get_db)): # pragma: no cover
    try:
        # Fetch the existing region
        grower_to_update = db.query(models.growers).filter(models.growers.grower_id == grower_id).first()
        
        if not grower_to_update:
            raise HTTPException(status_code=404, detail="Grower not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(grower_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            grower_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "grower updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/update_growing_area/{growing_area_id}', status_code=status.HTTP_200_OK)
def update_plant(growing_area_id: int, update_payload: schemas.UpdateGrowingAreaSchema, db: Session = Depends(get_db)): # pragma: no cover
    try:
        # Fetch the existing region
        ga_to_update = db.query(models.growing_area).filter(models.growing_area.growing_area_id == growing_area_id).first()
        
        if not ga_to_update:
            raise HTTPException(status_code=404, detail="Growing Area not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ga_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            ga_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "Growing Area updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_vendor_site/{vendor_site_id}', status_code=status.HTTP_200_OK)
def update_plant(vendor_site_id: int, update_payload: schemas.UpdateVendorSiteCodeSchema, db: Session = Depends(get_db)): # pragma: no cover
    try:
        # Fetch the existing region
        vsc_to_update = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_ID == vendor_site_id).first()
        
        if not vsc_to_update:
            raise HTTPException(status_code=404, detail="vendor site not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vsc_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            vsc_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "Vendor Site updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_growers')
def get_growers(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_growers = (db.query(models.growers.grower_name, 
                               func.trim(models.growers.owner).label("owner"), 
                               func.trim(models.growers.country).label("country"), 
                               func.trim(models.growers.volume).label("volume"), 
                               func.trim(models.growers.status).label("status"),
                               models.growers.updated_by,
                               models.growers.updated_time,
                               models.growers.pgt_grower_name,
                               models.growers.region,
                               models.growers.grower_id,
                               models.growers.created_by,
                               models.growers.created_time,
                               models.growers.grower_abbreviation_code)
                               .filter(models.growers.status=="ACTIVE").distinct().all())
        return {"growers":all_growers}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_grower/{grower_name}')
def get_plant(grower_name: str, db: Session = Depends(get_db)): # pragma: no cover
    try:
        grower_details = (db.query(models.growers.grower_name, 
                               func.trim(models.growers.owner).label("owner"), 
                               func.trim(models.growers.country).label("country"), 
                               func.trim(models.growers.volume).label("volume"), 
                               func.trim(models.growers.status).label("status"),
                               models.growers.updated_by,
                               models.growers.updated_time,
                               models.growers.pgt_grower_name,
                               models.growers.region,
                               models.growers.grower_id,
                               models.growers.created_by,
                               models.growers.created_time,
                               models.growers.grower_abbreviation_code)
                               .filter(models.growers.grower_name == grower_name,models.growers.status == "ACTIVE").all())
        grower_growing_area_details = (db.query(models.preferred_grower.grower_name,models.preferred_grower.growing_area_name,
                                                models.preferred_grower.grower_id,models.preferred_grower.growing_area_id).
                                        filter(models.preferred_grower.grower_name==grower_name).distinct().all())
        empty_json = {
        "grower_name": "Not Appl",
        "growing_area_name": "Not Appl",
        "grower_id": 000,
        "growing_area_id": 0
        }
        return {"grower_details":grower_details,"gr_grarea_details":grower_growing_area_details if grower_growing_area_details else [empty_json]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/modify_ex_grower')
def modify_ex_grower(payload: schemas.edit_gr_grarea_masters,db:Session = Depends(get_db)):  # pragma: no cover
    try:
        grower_name = payload.grower_name
        grower_id = payload.grower_id
        flag=False
        existingRecord = db.query(models.preferred_grower)\
                                .filter(models.preferred_grower.grower_name==grower_name).all()
        seen_combinations = set()
        for ex in existingRecord:
            db.delete(ex)

        for ga, ga_id in zip(payload.growing_area_name, payload.growing_area_id):
            unique_combination = (payload.grower_name, ga)
            if unique_combination in seen_combinations:
                continue

            seen_combinations.add(unique_combination)
            new_mapping = models.preferred_grower(
                grower_name=payload.grower_name,
                growing_area_name=ga,
                growing_area_id=ga_id,
                grower_id=grower_id
            )
            db.add(new_mapping)
            flag=True
        db.commit()
        if flag:
            db.refresh(new_mapping)
        return {"status":"Updated the grower growing area mapping successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_region')
def get_region(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_regions = (db.query(models.region.region_name,
                                func.trim(models.region.country).label("country"),
                                func.trim(models.region.updated_by).label("updated_by"),
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.created_by).label("created_by"),
                                models.region.region_id,
                                models.region.created_time).filter(models.region.status=="ACTIVE").distinct().all())
        return {"regions":all_regions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_region/{region_name}')
def get_plant(region_name: str, db: Session = Depends(get_db)): # pragma: no cover
    try:
        region_details = (db.query(models.region.region_name,
                                func.trim(models.region.country).label("country"),
                                func.trim(models.region.updated_by).label("updated_by"),
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.created_by).label("created_by"),
                                models.region.region_id,
                                models.region.created_time).filter(models.region.region_name == region_name,
                                                        models.region.status == "ACTIVE").all())
        return {"region_details":region_details}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_region', status_code=status.HTTP_201_CREATED)
def add_new_region(payload: schemas.Region, db: Session = Depends(get_db)): # pragma: no cover
    try:
        new_region = models.region(**payload.dict())
        db.add(new_region)
        db.commit()
        return {"status":"New region added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_region/{region_id}', status_code=status.HTTP_200_OK)
def update_region(region_id: int, update_payload: schemas.UpdateRegion, db: Session = Depends(get_db)): # pragma: no cover
    try:
        # Fetch the existing region
        region_to_update = db.query(models.region).filter(models.region.region_id == region_id).first()
        
        if not region_to_update:
            raise HTTPException(status_code=404, detail="Region not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(region_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            region_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "Region updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/get_crop_category')
def get_crop_category(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_crop_cat = (db.query(models.category.crop_category,
                                func.trim(models.category.created_by).label("created_by"),
                                func.trim(models.category.status).label("status"),
                                models.category.updated_time,
                                func.trim(models.category.updated_by).label("updated_by"),
                                models.category.category_name,
                                func.trim(models.category.country).label("country"),
                                models.category.created_time).filter(models.category.status=="ACTIVE").distinct().all())
        return {"crop_categories":all_crop_cat}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_crop_cat/{category_name}')
def get_plant(category_name: str, db: Session = Depends(get_db)): # pragma: no cover
    try:
        crop_details = (db.query(models.category.crop_category,
                                func.trim(models.category.created_by).label("created_by"),
                                func.trim(models.category.status).label("status"),
                                models.category.updated_time,
                                func.trim(models.category.updated_by).label("updated_by"),
                                models.category.category_name,
                                func.trim(models.category.country).label("country"),
                                models.category.created_time).filter(models.category.category_name == category_name,
                                                        models.category.status == "ACTIVE").all())
        return {"crop_details":crop_details}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_crop', status_code=status.HTTP_201_CREATED)
def add_new_crop(payload: schemas.Category, db: Session = Depends(get_db)): # pragma: no cover
    try:
        new_crop_cat = models.category(**payload.dict())
        db.add(new_crop_cat)
        db.commit()
        return {"status":"New crop category added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_crop/{crop_category}', status_code=status.HTTP_200_OK)
def update_region(crop_category: int, update_payload: schemas.Category, db: Session = Depends(get_db)): # pragma: no cover
    try:
        # Fetch the existing region
        crop_to_update = db.query(models.category).filter(models.category.crop_category == crop_category).first()
        
        if not crop_to_update:
            raise HTTPException(status_code=404, detail="Crop category not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(crop_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            crop_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "crop category updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/plant/{plant_id}/{status}')
def delete_plant(plant_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    grower_query = db.query(models.Plant).filter(models.Plant.plant_id == plant_id).update({'status': status})
    if not grower_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')

    db.commit()
    if status=="INACTIVE":
        return {"status":"Plant deleted successfully"}
    else:
        return {"status":"Plant made into Active state"}

@router.post('/grower/{grower_id}/{status}')
def delete_grower(grower_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    grower_query = db.query(models.growers).filter(models.growers.grower_id == grower_id).update({'status': status})
    if not grower_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')

    db.commit()
    if status=="INACTIVE":
        return {"status":"Grower deleted successfully"}
    else:
        return {"status":"Grower made into Active state"}

@router.post('/growing_area/{growing_area_id}/{status}')
def delete_growing_area(growing_area_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    grower_query = db.query(models.growing_area).filter(models.growing_area.growing_area_id == growing_area_id).update({'status': status})
    if not grower_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')

    db.commit()
    if status=="INACTIVE":
        return {"status":"Growing area deleted successfully"}
    else:
        return {"status":"Growing area made into Active state"}

@router.post('/vendor_site/{vendor_site_id}/{status}')
def delete_vendor_site(vendor_site_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    vendor_site_query = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_ID == vendor_site_id).update({'status': status})
    if not vendor_site_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')

    db.commit()
    if status=="INACTIVE":
        return {"status":"Vendor Site deleted successfully"}
    else:
        return {"status":"Vendor Site made into Active state"}

@router.post('/region/{region_id}/{status}')
def delete_region(region_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    region_query = db.query(models.region).filter(models.region.region_id == region_id).update({'status': status})
    if not region_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')

    db.commit()
    if status=="INACTIVE":
        return {"status":"Region deleted successfully"}
    else:
        return {"status":"Region made into Active state"}

@router.post('/crop_category/{crop_cat_id}/{status}')
def delete_category(crop_cat_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    category_query = db.query(models.category).filter(models.category.crop_category == crop_cat_id).update({'status': status})
    if not category_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')

    db.commit()
    if status=="INACTIVE":
        return {"status":"Crop category deleted successfully"}
    else:
        return {"status":"Crop category made into Active state"}
    
@router.get('/get_inactive_plants')
def get_plants(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_plants = db.query(models.Plant.plant_id,
                               models.Plant.company_name,
                               func.trim(models.Plant.created_by).label("created_by"),
                               func.trim(models.Plant.status).label("status"),
                               func.trim(models.Plant.updated_by).label("updated_by"),
                               models.Plant.created_time,
                               models.Plant.pgt_plant_name,
                               models.Plant.plant_code,
                               models.Plant.plant_name,
                               models.Plant.region_id,
                               models.Plant.crop_category_id,
                               models.Plant.updated_time).filter(models.Plant.status=="INACTIVE").distinct().all()
        empty_json =  [{
            "plant_id": 000,
            "company_name": "Not Appl.",
            "created_by": "Not Appl.",
            "status": "Not Appl.",
            "updated_by": "Not Appl.",
            "created_time": "2023-10-18T13:17:55.120000",
            "pgt_plant_name": "Not Appl.",
            "plant_code": "Not Appl.",
            "plant_name": "Not Appl.",
            "region_id": 000,
            "crop_category_id": 000,
            "updated_time": "2024-03-18T16:29:09.660000"
            }]
        return {"in_plants":all_plants if all_plants else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
		
		
@router.get('/get_inactive_growers')
def get_growers(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_growers = (db.query(models.growers.grower_name, 
                               func.trim(models.growers.owner).label("owner"), 
                               func.trim(models.growers.country).label("country"), 
                               func.trim(models.growers.volume).label("volume"), 
                               func.trim(models.growers.status).label("status"),
                               models.growers.updated_by,
                               models.growers.updated_time,
                               models.growers.pgt_grower_name,
                               models.growers.region,
                               models.growers.grower_id,
                               models.growers.created_by,
                               models.growers.created_time,
                               models.growers.grower_abbreviation_code).filter(models.growers.status=="INACTIVE").distinct().all())
        empty_json =  [{
                "grower_name": "Not Appl.",
                "owner": "Not Appl.",
                "country": "Not Appl.",
                "volume": "000",
                "status": "Not Appl.",
                "updated_by": "Not Appl.",
                "updated_time": "2024-03-28T07:49:16.353000",
                "pgt_grower_name": "Not Appl.",
                "region": 000,
                "grower_id": 000,
                "created_by": "Not Appl.",
                "created_time": "2023-10-12T08:10:20",
                "grower_abbreviation_code": "Not Appl."
                }]
        
        return {"in_growers":all_growers if all_growers else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
		
		
@router.get('/get_growing_area')
def get_growers(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_ga = db.query(models.growing_area).filter(models.growing_area.status=="ACTIVE").distinct().all()
        return {"growing_area":all_ga}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_inactive_growing_area')
def get_growers(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_ga = db.query(models.growing_area).filter(models.growing_area.status=="INACTIVE").distinct().all()
        empty_json = [{
                "created_by": "Not Appl.",
                "growing_area_name": "Not Appl.",
                "region": 000,
                "status": "Not Appl.",
                "fresh_period_start": 000,
                "fresh_period_end": 000,
                "storage_period_start": 000,
                "created_time": "2023-10-18T23:05:22.570000",
                "pgt_growing_area": "Not Appl.",
                "country": "Not Appl.",
                "growing_area_id": 000,
                "updated_by": "Not Appl.",
                "growing_area_desc": "Not Appl.",
                "fresh_week_start": 000,
                "fresh_week_end": 000,
                "storage_week_start": 000,
                "updated_time": "2023-10-18T23:05:22.570000"
                }]
        return {"in_growing_area":all_ga if all_ga else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_vsc')
def get_growers(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_vsc = db.query(models.vendor_site_code).filter(models.vendor_site_code.status=="ACTIVE").distinct().all()
        return {"vsc":all_vsc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_inactive_vsc')
def get_growers(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_vsc = db.query(models.vendor_site_code).filter(models.vendor_site_code.status=="INACTIVE").distinct().all()
        empty_json = [{
                "created_by": "Not Appl.",
                "VENDOR_SITE_CODE": "Not Appl.",
                "status": "Not Appl.",
                "updated_time": "2024-03-15T11:06:13.363000",
                "pgt_vsc": "Not Appl.",
                "VENDOR_SITE_ID": 000,
                "created_time": "2024-03-15T11:06:13.363000",
                "updated_by": "Not Appl.",
                "region_id": 000
                }]
        return {"in_vsc":all_vsc if all_vsc else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

	
@router.get('/get_inactive_region')
def get_region(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_regions = db.query(models.region.region_name,
                                func.trim(models.region.country).label("country"),
                                func.trim(models.region.updated_by).label("updated_by"),
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.created_by).label("created_by"),
                                models.region.region_id,
                                models.region.created_time).filter(models.region.status=="INACTIVE").distinct().all()
        empty_json = [{
                "region_name": "East - US",
                "country": "US        ",
                "updated_by": "SYSTEM    ",
                "created_time": "2023-10-12T11:21:15.750000",
                "created_by": "SYSTEM    ",
                "region_id": 8,
                "status": "ACTIVE    ",
                "updated_time": "2023-10-12T11:21:15.750000"
                }]
        return {"in_regions":all_regions if all_regions else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
		
		
@router.get('/get_inactive_crop_category')
def get_crop_category(db: Session = Depends(get_db)):  # pragma: no cover
    try:
        all_crop_cat = db.query(models.category.crop_category,
                                func.trim(models.category.created_by).label("created_by"),
                                func.trim(models.category.status).label("status"),
                                models.category.updated_time,
                                func.trim(models.category.updated_by).label("updated_by"),
                                models.category.category_name,
                                func.trim(models.category.country).label("country"),
                                models.category.created_time).filter(models.category.status=="INACTIVE").distinct().all()
        empty_json = [{
                    "crop_category": 0,
                    "created_by": "Not Appl.",
                    "status": "Not Appl.",
                    "updated_time": "2024-03-01T09:37:39.473000",
                    "updated_by": "Not Appl.",
                    "category_name": "Not Appl.",
                    "country": "Not Appl.",
                    "created_time": "2024-03-01T09:37:39.473000"
                    }]
        return {"in_crop_categories":all_crop_cat if all_crop_cat else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_file")
def upload_file(file: UploadFile = File(...)):
    contents = file.file.read()
    file_format = file.filename.split(".")[1]
    if file_format=="csv":
        s = str(contents,'utf-8')
        data = StringIO(s) 
        df = pd.read_csv(data)
    elif file_format in ["xls","xlsx"]:
        data = BytesIO(contents)
        df = pd.read_excel(data)
    data.close()
    file.file.close()
    response_json = df.head().to_dict(orient="records")
    return {"filename": file.filename, "file_content":response_json}