from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import Depends, HTTPException, status, APIRouter
import schemas
import models
from models import (View_Ownership, View_OwnershipMetrics_all,
                    View_OwnershipMetrics_region, View_OwnershipMetrics_country)
from database import get_db

router = APIRouter()


def get_ownership_common(db, region_filter, metric_filter,
                         metrics_model, year, detail_message=None):
    try:
        data = db.query(View_Ownership) \
            .join(models.growing_area,
                  View_Ownership.columns.growing_area_id == models.growing_area.growing_area_id) \
            .join(models.region,
                  models.growing_area.region == models.region.region_id) \
            .filter(region_filter,
                    or_(View_Ownership.columns.year == year - 1, View_Ownership.columns.year == year))\
            .order_by(View_Ownership.columns.growing_area_name,
                      View_Ownership.columns.year).all()

        ownership_metric = db.query(metrics_model) \
            .filter(metric_filter,
                    or_(metrics_model.columns.year == year - 1, metrics_model.columns.year == year)) \
            .distinct().all()

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=detail_message or f"Ownership data not found for : {region_filter}")

        return {"status": "success", "ownership": data, "ownership_metric_region": ownership_metric}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e) or "Error processing request")


@router.get('/region/{region}/year/{year}')
def get_ownership_region(region: str, year: int, db: Session = Depends(get_db)):
    region_filter = models.region.country == region if region in ['US', 'Canada'] else models.region.region_name == region
    metric_filter = models.View_OwnershipMetrics_country.columns.country == region if region in ['US', 'Canada'] \
        else models.View_OwnershipMetrics_region.columns.region_name == region
    return get_ownership_common(
        db, region_filter, metric_filter,
        View_OwnershipMetrics_country if region in ['US', 'Canada'] else View_OwnershipMetrics_region,
        year, f"Ownership data not found for : {region}"
    )


@router.get('/year/{year}')
def get_ownership(year: int, db: Session = Depends(get_db)):
    return get_ownership_common(
        db, True, True,
        View_OwnershipMetrics_all, year, "No ownership_id found")


def total_ship_calculation(ownership_id: str, db: Session = Depends(get_db)):
    ownership_record = db.query(models.Ownership) \
        .filter(models.Ownership.ownership_id == ownership_id).first()

    ownership_record.total_ship = ownership_record.to_ship + ownership_record.market_and_flex
    db.commit()


@router.post('/UpdateOwnershipGrowing_mapping/{cropyear_input}')
def Update_Ownership(cropyear_input: str, payload: schemas.UpdateOwnershipGrowerGrowing,
                     db: Session = Depends(get_db)):
    DataUpdateGrowerGrowing = payload.PayloadOwnership
    update_count = 0
    cropyear_input = cropyear_input.lstrip().rstrip()

    try:
        for item in DataUpdateGrowerGrowing:
            row_id = item.row_id
            existing_record = db.query(models.OwnershipGrowerGrowing).filter(
                models.OwnershipGrowerGrowing.row_id == row_id).first()
            if existing_record is not None:
                if item.contract == 0:
                    (db.query(models.OwnershipGrowerGrowing).filter(
                        models.OwnershipGrowerGrowing.row_id == row_id)
                     .update({models.OwnershipGrowerGrowing.contract: item.contract,
                              models.OwnershipGrowerGrowing.shrinkage: 0,
                              models.OwnershipGrowerGrowing.status: "INACTIVE"}))
                else:
                    (db.query(models.OwnershipGrowerGrowing).filter(
                        models.OwnershipGrowerGrowing.row_id == row_id)
                     .update({models.OwnershipGrowerGrowing.contract: item.contract,
                              models.OwnershipGrowerGrowing.shrinkage: item.shrinkage,
                              models.OwnershipGrowerGrowing.status: "ACTIVE"}))
            else:
                if item.contract == 0:
                    payload = {"row_id": item.row_id,
                               "growing_area_id": item.growing_area_id,
                               "grower_id": item.grower_id,
                               "contract_erp": item.contract_erp,
                               "contract": item.contract,
                               "shrinkage": 0,
                               "contract": item.contract,
                               "shrinkage": item.shrinkage,
                               "year": item.year,
                               "crop_type": item.crop_type,
                               "crop_year": item.crop_year,
                               "ownership_id": item.ownership_id,
                               "status": "INACTIVE"}
                else:
                    payload = {"row_id": item.row_id,
                               "growing_area_id": item.growing_area_id,
                               "grower_id": item.grower_id,
                               "contract": item.contract,
                               "contract_erp": item.contract_erp,
                               "shrinkage": item.shrinkage,
                               "year": item.year,
                               "crop_type": item.crop_type,
                               "crop_year": item.crop_year,
                               "ownership_id": item.ownership_id,
                               "status": "ACTIVE"}
                new_record = models.OwnershipGrowerGrowing(**payload)
                db.add(new_record)
            db.commit()
            update_count += 1
            mapping_data = db.query(models.OwnershipGrowerGrowing.growing_area_id,
                                    func.sum(models.OwnershipGrowerGrowing.contract))\
                .filter(models.OwnershipGrowerGrowing.crop_year == cropyear_input,
                        models.OwnershipGrowerGrowing.status == 'ACTIVE',
                        models.OwnershipGrowerGrowing.growing_area_id == item.growing_area_id)\
                .group_by(models.OwnershipGrowerGrowing.growing_area_id)\
                .order_by(models.OwnershipGrowerGrowing.growing_area_id).all()
            if len(mapping_data) == 0:
                db.query(models.Ownership)\
                    .filter(models.Ownership.ownership_id == item.ownership_id) \
                    .update({models.Ownership.contract: 0,
                             models.Ownership.shrinkage: 0,
                             models.Ownership.to_ship: 0}, synchronize_session='fetch')
                total_ship_calculation(item.ownership_id, db)
            else:
                per_grower_shrinkage = db.query(
                    models.OwnershipGrowerGrowing.growing_area_id,
                    models.OwnershipGrowerGrowing.contract,
                    models.OwnershipGrowerGrowing.shrinkage,
                    models.OwnershipGrowerGrowing.ownership_id) \
                    .filter(models.OwnershipGrowerGrowing.crop_year == cropyear_input,
                            models.OwnershipGrowerGrowing.status == 'ACTIVE',
                            models.OwnershipGrowerGrowing.growing_area_id == item.growing_area_id)\
                    .order_by(models.OwnershipGrowerGrowing.growing_area_id).all()

                sums_dict = {}
                for items in per_grower_shrinkage:
                    key = items[0]  # item[0]: growing_area_id
                    value1 = items[1]  # item[1]: contract
                    value2 = items[2]  # item[2]: shrinkage

                    if key in sums_dict:
                        sums_dict[key][0] += value1
                        sums_dict[key][1] += value1 * value2 * 0.01
                    else:
                        sums_dict[key] = [value1, value1 * value2 * 0.01]
                output_data = [(key, value[0], value[1]) for key, value in sums_dict.items()]
                # output_data has growing_id, total_contract_value and total
                shrinkage_output = [(item[0], (item[2] * 100 / item[1]), (item[1] - item[2])) for item
                                    in
                                    output_data]
                ownership_id_dict = {item[0]: item[3] for item in per_grower_shrinkage}
                data_list = []
                for row in mapping_data:
                    growing_area_id = row[0]
                    contracted = row[1]
                    ownership_id = ownership_id_dict.get(growing_area_id)
                    if ownership_id is not None:
                        data_list.append(
                            {"growing_area_id": growing_area_id, "contracted": contracted,
                             "ownership_id": ownership_id})

                combined_data = [
                    (var1[0], var1[1], var1[2], var2['contracted'], var2['ownership_id'])
                    for
                    var1, var2 in zip(shrinkage_output, data_list)]
                for column_data in combined_data:
                    growing_id, shrinkage_perc, toship, cont_volume, ownershipid = column_data[0], \
                        column_data[1], column_data[
                        2], column_data[3], column_data[4]
                    db.query(models.Ownership).filter(models.Ownership.ownership_id == ownershipid) \
                        .update({models.Ownership.ownership_id: ownershipid,
                                 models.Ownership.growing_area_id: growing_id,
                                 models.Ownership.contract: cont_volume,
                                 models.Ownership.shrinkage: shrinkage_perc,
                                 models.Ownership.to_ship: toship}, synchronize_session='fetch')

                    db.commit()
                total_ship_calculation(item.ownership_id, db)

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_new_ownership/{year}')
def Create_new_Ownership(year: int, db: Session = Depends(get_db)):
    try:
        growing_area_list = db.query(models.growing_area).filter(models.growing_area.status == 'ACTIVE').all()
        for growing_area in growing_area_list:
            fresh_crop_year = str(year)
            fresh_crop_type = 'Fresh'
            storage_crop_type = 'Storage'
            storage_crop_year = str(year) + "-" + str(year + 1)[2:]
            fresh_ownership_id = str(growing_area.growing_area_id) + "#" + fresh_crop_year
            storage_ownership_id = str(growing_area.growing_area_id) + "#" + storage_crop_year

            payload = {"ownership_id": fresh_ownership_id, "growing_area_id": growing_area.growing_area_id,
                       "contract": 0, "contract_erp_value": 0, "shrinkage": 0, "to_ship": 0,
                       "extension": 0, "market_and_flex": 0, "total_ship": 0, "year": year,
                       "crop_type": fresh_crop_type,
                       "crop_year": fresh_crop_year}
            new_ownership = models.Ownership(**payload)
            db.add(new_ownership)
            db.commit()
            payload = {"ownership_id": storage_ownership_id, "growing_area_id": growing_area.growing_area_id,
                       "contract": 0, "contract_erp_value": 0, "shrinkage": 0, "to_ship": 0,
                       "extension": 0, "market_and_flex": 0, "total_ship": 0, "year": year,
                       "crop_type": storage_crop_type,
                       "crop_year": storage_crop_year}
            new_ownership = models.Ownership(**payload)
            db.add(new_ownership)
            db.commit()

        return {"Status": "success", "records_inserted": "Next year data are added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_contract_erp/{crop_year}")
def update_ownership_contract_erp(crop_year: str, db: Session = Depends(get_db)):
    try:
        view_data = db.query(models.View_total_sum_growing_area)\
            .filter(models.View_total_sum_growing_area.columns.STORAGE_period == crop_year)\
            .all()
        if len(view_data) > 0:
            for data in view_data:
                existing_record = db.query(models.Ownership)\
                    .filter(models.Ownership.growing_area_id == data.growing_area_id,
                            models.Ownership.crop_year == crop_year)\
                    .first()
                if existing_record is not None:
                    db.query(models.Ownership).filter(
                        models.Ownership.growing_area_id == data.growing_area_id,
                        models.Ownership.crop_year == crop_year
                    ).update({models.Ownership.contract_erp_value: data.totalsum})

                db.commit()
        return {"message": f"Total Contract ERP updated for {crop_year} in Ownership table"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")