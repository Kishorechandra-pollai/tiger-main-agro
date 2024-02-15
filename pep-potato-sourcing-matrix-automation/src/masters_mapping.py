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

def new_ga_potato_solids(db,payload,current_time):
    growing_area_id = db.query(func.max(models.growing_area.growing_area_id)).scalar() or 0
    growing_area_id += 1
    ga_payload = {
        "growing_area_name": payload.psga_map.growing_area, 
        "country": payload.growing_area.country,
        "created_by": "JP",
        "created_time": current_time,
        "updated_by": "JP",
        "updated_time": current_time,
        "status": payload.growing_area.ga_status,
        "region": payload.plant.region_id, 
        "growing_area_desc": payload.growing_area.ga_desc,
        "fresh_period_start": payload.growing_area.fp_start,
        "fresh_period_end": payload.growing_area.fp_end,
        "fresh_week_start": payload.growing_area.fw_start,
        "fresh_week_end": payload.growing_area.fw_end,
        "storage_period_start": payload.growing_area.sp_start,
        "storage_week_start": payload.growing_area.sw_start,
        "growing_area_id": growing_area_id
        }

    # Insert into growing_area table
    new_growing_area = models.growing_area(**ga_payload)
    db.add(new_growing_area)
    print("inserted into growing area table")

    potato_rate_id = db.query(func.max(models.potato_rates.potato_rate_id)).scalar() or 0
    potato_rate_id += 1
    potato_rate_payload = {"potato_rate_id":potato_rate_id,
                            "year":datetime.utcnow().year,
                            "growing_area_id_old":999,
                            "created_time":current_time,
                            "created_by":"System",
                            "updated_time":current_time,
                            "updated_by":"SYSTEM",
                            "currency":"USD",
                            "growing_area_id":growing_area_id}
    create_potato_rate_in_db(potato_rate_payload, db)

    ## Solids Ratese
    solids_rate_id = db.query(func.max(models.solids_rates.solids_rate_id)).scalar() or 0
    solids_rate_id += 1
    solids_rate_payload = {"solids_rate_id":solids_rate_id,
                            "growing_area_id_old":999,
                            "created_time":current_time,
                            "created_by":"System",
                            "updated_time":current_time,
                            "updated_by":"SYSTEM",
                            "currency":"USD",
                            "growing_area_id":growing_area_id}
    create_solid_rate_in_db(solids_rate_payload, db)

    ## Potato mappings
    update_potato_rates_default(db,potato_rate_id,datetime.utcnow().year)

    ## Solids mappings
    update_solids_rates_default(db, solids_rate_id, datetime.utcnow().year)
    print("inserted into potato,solid rate and mapping table")
    return new_growing_area,True


@router.post('/add_plant_mapping', status_code=status.HTTP_201_CREATED)
def create_plant(payload: schemas.MastersMapping, db: Session = Depends(get_db)): # pragma: no cover
    """API Endpoint to add a new plant, add the plant with vendor site code mapping"""
    try:
        plant_name = payload.plant.plant_name
        plant_count = db.query(models.Plant).filter(models.Plant.plant_name == plant_name).count()
        if plant_count>0:
            return {"status":"plant already exists"}
        ga_vsc = False
        ga_status = False
        vendor_site_code = payload.psga_map.Vendor_Site_Code
        count = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_CODE == vendor_site_code).count()
        growing_area_name = payload.psga_map.growing_area
        count_ga = db.query(models.growing_area).filter(models.growing_area.growing_area_name == growing_area_name).count()

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
        print("inserted into plant table")

        if count>0: # Existing vendor site
            if count_ga>0:
                ## existing growing area ; only need to add in psga
                growing_area_id = db.query(models.growing_area.growing_area_id).filter(
                models.growing_area.growing_area_name == growing_area_name).first()[0]
                print("existing growing area and existing vendor site")
            else:
                # if new growing area
                new_growing_area,ga_status = new_ga_potato_solids(db,payload,current_time)
                print("new growing area and existing vendor site")
                growing_area_id = db.query(func.max(models.PlantSiteGrowingAreaMapping.growing_area_id)).scalar() or 0
                growing_area_id += 1
            ## If new growing area or not should be checked here
            ## If new growing area, increment id by one,  potato and solid rate tables would be used only if it is new
                
            # growing_area_name = payload.psga_map.growing_area
                
            # Fetching the vendor site ID
            # Fetch the vendor site ID directly
            vendor_site_id = db.query(models.vendor_site_code.VENDOR_SITE_ID).filter(
                models.vendor_site_code.VENDOR_SITE_CODE == vendor_site_code
            ).first()[0]

            # Fetch the growing area ID directly
            # growing_area_id = db.query(models.PlantSiteGrowingAreaMapping.growing_area_id).filter(
            #     models.PlantSiteGrowingAreaMapping.Vendor_Site_Code == vendor_site_code,
            #     models.PlantSiteGrowingAreaMapping.growing_area == growing_area_name
            # ).first()[0]


            ## remove vendor_site_id and growing_area_id from payload
            # new_mapping = models.PlantSiteGrowingAreaMapping(
            #     **payload.psga_map.dict(),
            #     row_id=row_id,
            #     plant_id=plant_id,
            #     vendor_site_id=vendor_site_id,
            #     growing_area_id=growing_area_id
            # )
            # db.add(new_mapping)
        else: ## New vendor site
            ## Is it a new growing area or existing growing area should be shown here
            ## If new growing area, increment id by one,  potato and solid rate tables would be used only if it is new
            if count_ga>0:
                ## existing growing area ; only need to add in psga
                growing_area_id = db.query(models.growing_area.growing_area_id).filter(
                models.growing_area.growing_area_name == growing_area_name).first()[0]
                print("existing growing area and new vendor site")
            else: # if new growing area
                new_growing_area,ga_status = new_ga_potato_solids(db,payload,current_time)
                print("new growing area and new vendor site")
                growing_area_id = db.query(func.max(models.PlantSiteGrowingAreaMapping.growing_area_id)).scalar() or 0
                growing_area_id += 1
                
            vendor_site_id = db.query(func.max(models.vendor_site_code.VENDOR_SITE_ID)).scalar() or 0
            vendor_site_id += 1

            # new_mapping = models.PlantSiteGrowingAreaMapping(
            #     **payload.psga_map.dict(),
            #     row_id=row_id,
            #     plant_id=plant_id,
            #     vendor_site_id=vendor_site_id,
            #     growing_area_id=growing_area_id
            # )
            # db.add(new_mapping)

            # ga_payload = {
            #     "growing_area_name": payload.psga_map.growing_area, 
            #     "country": payload.growing_area.country,
            #     "created_by": "JP",
            #     "created_time": current_time,
            #     "updated_by": "JP",
            #     "updated_time": current_time,
            #     "status": payload.growing_area.ga_status,
            #     "region": payload.plant.region_id, 
            #     "growing_area_desc": payload.growing_area.ga_desc,
            #     "fresh_period_start": payload.growing_area.fp_start,
            #     "fresh_period_end": payload.growing_area.fp_end,
            #     "fresh_week_start": payload.growing_area.fw_start,
            #     "fresh_week_end": payload.growing_area.fw_end,
            #     "storage_period_start": payload.growing_area.sp_start,
            #     "storage_week_start": payload.growing_area.sw_start,
            #     "growing_area_id": growing_area_id
            # }

            # # Insert into growing_area table
            # new_growing_area = models.growing_area(**ga_payload)
            # db.add(new_growing_area)

            vsc_payload = {
                "VENDOR_SITE_ID":vendor_site_id,
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
            print("inserted into vendor site table")


            # Potato Rates
            # potato_rate_id = db.query(func.max(models.potato_rates.potato_rate_id)).scalar() or 0
            # potato_rate_id += 1
            # potato_rate_payload = {"potato_rate_id":potato_rate_id,
            #                         "year":datetime.utcnow().year,
            #                         "growing_area_id_old":999,
            #                         "created_time":current_time,
            #                         "created_by":"System",
            #                         "updated_time":current_time,
            #                         "updated_by":"SYSTEM",
            #                         "currency":"USD",
            #                         "growing_area_id":growing_area_id}
            # create_potato_rate_in_db(potato_rate_payload, db)

            # ## Solids Ratese
            # solids_rate_id = db.query(func.max(models.solids_rates.solids_rate_id)).scalar() or 0
            # solids_rate_id += 1
            # solids_rate_payload = {"solids_rate_id":solids_rate_id,
            #                         "growing_area_id_old":999,
            #                         "created_time":current_time,
            #                         "created_by":"System",
            #                         "updated_time":current_time,
            #                         "updated_by":"SYSTEM",
            #                         "currency":"USD",
            #                         "growing_area_id":growing_area_id}
            # create_solid_rate_in_db(solids_rate_payload, db)

            # ## Potato mappings
            # update_potato_rates_default(db,potato_rate_id,datetime.utcnow().year)

            # ## Solids mappings
            # update_solids_rates_default(db, solids_rate_id, datetime.utcnow().year)

        ## Add in PSGA mapping table
        new_mapping = models.PlantSiteGrowingAreaMapping(
            **payload.psga_map.dict(),
            row_id=row_id,
            plant_id=plant_id,
            vendor_site_id=vendor_site_id,
            growing_area_id=growing_area_id)
        db.add(new_mapping)
        print("inserted into psga map table")
        
        ## Freight cost should be handled in edit plant as well (possiblity of new GA Or VSC)
        freight_cost_id = db.query(func.max(models.FreightCostRate.freight_cost_id)).scalar() or 0
        freight_cost_id += 1
        freight_cost_rate_payload = {"freight_cost_id":freight_cost_id,
                                    "plant_id":plant_id,
                                    "vendor_site_id":vendor_site_id,
                                    "comment": "comment",
                                    "created_time":current_time,
                                    "created_by":"System",
                                    "updated_time":current_time,
                                    "updated_by":"SYSTEM",
                                    "currency":"USD",
                                    "growing_area_id":growing_area_id}
        create_freight_rates_in_db(freight_cost_rate_payload, db)

        ## Freight Cost mappings
        # update_freight_cost_mapping_with_default_value(freight_cost_id,datetime.utcnow().year,db) 
        update_freight_rates_with_default_value(freight_cost_id,datetime.utcnow().year,db)  
        print("inserted into freight rate and mapping table")

        db.commit()
        db.refresh(new_plant)
        db.refresh(new_mapping)
        if ga_vsc:
            # db.refresh(new_growing_area)
            db.refresh(new_vendor_site_code)
        ## need to add refresh of growing area here in another condition
        if ga_status:
            db.refresh(new_growing_area)
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