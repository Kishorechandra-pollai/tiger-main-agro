from sqlalchemy import or_, delete
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import Depends, HTTPException, status, APIRouter
import schemas
import models
from models import Ownership, OwnershipGrowerGrowing
from database import get_db

router = APIRouter()


@router.get('/region/{region}/year/{year}')
def get_ownership_region(region: str, year: int, db: Session = Depends(get_db)):
    if region == 'US' or region == 'Canada':
        data = db.query(models.View_Ownership) \
            .join(models.growing_area,
                  models.View_Ownership.columns.growing_area_id == models.growing_area.growing_area_id) \
            .join(models.region, models.growing_area.region == models.region.region_id) \
            .filter(models.region.country == region, or_(models.View_Ownership.columns.year == year - 1,
                                                         models.View_Ownership.columns.year == year)).all()

        ownership_metric = db.query(models.View_OwnershipMetrics_country) \
            .filter(models.View_OwnershipMetrics_country.columns.country == region,
                    or_(models.View_OwnershipMetrics_region.columns.year == year - 1,
                        models.View_OwnershipMetrics_region.columns.year == year)) \
            .distinct().all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Ownership data not found for : {region}")
    else:
        data = db.query(models.View_Ownership) \
            .join(models.growing_area,
                  models.View_Ownership.columns.growing_area_id ==
                  models.growing_area.growing_area_id) \
            .join(models.region, models.growing_area.region == models.region.region_id) \
            .filter(models.region.region_name == region,
                    or_(models.View_Ownership.columns.year == year - 1,
                        models.View_Ownership.columns.year == year)).all()

        ownership_metric = db.query(models.View_OwnershipMetrics_region) \
            .filter(models.View_OwnershipMetrics_region.columns.region_name == region,
                    or_(models.View_OwnershipMetrics_region.columns.year == year - 1,
                        models.View_OwnershipMetrics_region.columns.year == year)) \
            .distinct().all()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Ownership data not found for : {region}")

    return {"status": "success", "ownership": data, "ownership_metric_region": ownership_metric}


@router.get('/year/{year}')
def get_ownership(year: int, db: Session = Depends(get_db)):
    ownership = db.query(models.View_Ownership) \
        .filter(or_(models.View_Ownership.columns.year == year - 1,
                    models.View_Ownership.columns.year == year)).all()
    ownership_metric_all = db.query(models.View_OwnershipMetrics_all) \
        .filter(or_(models.View_OwnershipMetrics_all.columns.year == year - 1,
                    models.View_OwnershipMetrics_all.columns.year == year)) \
        .distinct().all()
    if not ownership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No ownership_id found")
    return {"status": "success", "ownership": ownership,
            "ownership_metric_region": ownership_metric_all}


# def total_ship_calculation(ownership_id: str, db: Session = Depends(get_db)):
#     ownership_record = db.query(models.Ownership) \
#         .filter(models.Ownership.ownership_id == ownership_id).first()
#
#     ownership_record.total_ship = ownership_record.to_ship + ownership_record.market_and_flex
#     db.commit()
#
#
# @router.post('/UpdateOwnershipGrowing_mapping/{cropyear_input}')
# def Update_Ownership(cropyear_input: str, payload: schemas.UpdateOwnershipGrowerGrowing,
#                      db: Session = Depends(get_db)):
#     DataUpdateGrowerGrowing = payload.PayloadOwnership
#     update_count = 0
#     cropyear_input = cropyear_input.lstrip().rstrip()
#
#     try:
#         for item in DataUpdateGrowerGrowing:
#             row_id = item.row_id
#             existing_record = db.query(models.OwnershipGrowerGrowing).filter(
#                 models.OwnershipGrowerGrowing.row_id == row_id).first()
#             if existing_record is not None:
#                 if item.contract == 0:
#                     (db.query(models.OwnershipGrowerGrowing).filter(
#                         models.OwnershipGrowerGrowing.row_id == row_id)
#                      .update({models.OwnershipGrowerGrowing.contract: item.contract,
#                               models.OwnershipGrowerGrowing.shrinkage: 0,
#                               models.OwnershipGrowerGrowing.status: "INACTIVE"}))
#                 else:
#                     (db.query(models.OwnershipGrowerGrowing).filter(
#                         models.OwnershipGrowerGrowing.row_id == row_id)
#                      .update({models.OwnershipGrowerGrowing.contract: item.contract,
#                               models.OwnershipGrowerGrowing.shrinkage: item.shrinkage,
#                               models.OwnershipGrowerGrowing.status: "ACTIVE"}))
#             else:  # pragma: no cover
#                 if item.contract == 0:
#                     payload = {"row_id": item.row_id,
#                                "growing_area_id": item.growing_area_id,
#                                "grower_id": item.grower_id,
#                                "contract_erp": item.contract_erp,
#                                "contract": item.contract,
#                                "shrinkage": 0,
#                                "contract": item.contract,
#                                "shrinkage": item.shrinkage,
#                                "year": item.year,
#                                "crop_type": item.crop_type,
#                                "crop_year": item.crop_year,
#                                "ownership_id": item.ownership_id,
#                                "status": "INACTIVE"}
#                 else:
#                     payload = {"row_id": item.row_id,
#                                "growing_area_id": item.growing_area_id,
#                                "grower_id": item.grower_id,
#                                "contract": item.contract,
#                                "contract_erp": item.contract_erp,
#                                "shrinkage": item.shrinkage,
#                                "year": item.year,
#                                "crop_type": item.crop_type,
#                                "crop_year": item.crop_year,
#                                "ownership_id": item.ownership_id,
#                                "status": "ACTIVE"}
#                 new_record = models.OwnershipGrowerGrowing(**payload)
#                 db.add(new_record)
#             db.commit()
#             update_count += 1
#             mapping_data = db.query(models.OwnershipGrowerGrowing.growing_area_id,
#                                     func.sum(models.OwnershipGrowerGrowing.contract)) \
#                 .filter(models.OwnershipGrowerGrowing.crop_year == cropyear_input,
#                         models.OwnershipGrowerGrowing.status == 'ACTIVE',
#                         models.OwnershipGrowerGrowing.growing_area_id == item.growing_area_id,
#                         models.OwnershipGrowerGrowing.contract != 0) \
#                 .group_by(models.OwnershipGrowerGrowing.growing_area_id) \
#                 .order_by(models.OwnershipGrowerGrowing.growing_area_id).all()
#             if len(mapping_data) == 0:
#                 db.query(models.Ownership) \
#                     .filter(models.Ownership.ownership_id == item.ownership_id) \
#                     .update({models.Ownership.contract: 0,
#                              models.Ownership.shrinkage: 0,
#                              models.Ownership.to_ship: 0}, synchronize_session='fetch')
#                 total_ship_calculation(item.ownership_id, db)
#             else:
#                 per_grower_shrinkage = db.query(
#                     models.OwnershipGrowerGrowing.growing_area_id,
#                     models.OwnershipGrowerGrowing.contract,
#                     models.OwnershipGrowerGrowing.shrinkage,
#                     models.OwnershipGrowerGrowing.ownership_id) \
#                     .filter(models.OwnershipGrowerGrowing.crop_year == cropyear_input,
#                             models.OwnershipGrowerGrowing.status == 'ACTIVE',
#                             models.OwnershipGrowerGrowing.growing_area_id == item.growing_area_id) \
#                     .order_by(models.OwnershipGrowerGrowing.growing_area_id).all()
#                 sums_dict = {}
#                 for items in per_grower_shrinkage:
#                     key = items[0]  # item[0]: growing_area_id
#                     value1 = items[1]  # item[1]: contract
#                     value2 = items[2]  # item[2]: shrinkage
#
#                     if key in sums_dict:
#                         sums_dict[key][0] += value1
#                         sums_dict[key][1] += value1 * value2 * 0.01
#                     else:
#                         sums_dict[key] = [value1, value1 * value2 * 0.01]
#                 output_data = [(key, value[0], value[1]) for key, value in sums_dict.items()]
#                 # output_data has growing_id, total_contract_value and total
#                 shrinkage_output = [(item[0], (item[2] * 100 / item[1]), (item[1] - item[2])) for item
#                                     in
#                                     output_data]
#                 ownership_id_dict = {item[0]: item[3] for item in per_grower_shrinkage}
#                 data_list = []
#                 for row in mapping_data:
#                     growing_area_id = row[0]
#                     contracted = row[1]
#                     ownership_id = ownership_id_dict.get(growing_area_id)
#                     if ownership_id is not None:
#                         data_list.append(
#                             {"growing_area_id": growing_area_id, "contracted": contracted,
#                              "ownership_id": ownership_id})
#
#                 combined_data = [
#                     (var1[0], var1[1], var1[2], var2['contracted'], var2['ownership_id'])
#                     for
#                     var1, var2 in zip(shrinkage_output, data_list)]
#
#                 # Populating Ownership table
#                 for column_data in combined_data:
#                     growing_id, shrinkage_perc, toship, cont_volume, ownershipid = column_data[0], \
#                         column_data[1], column_data[
#                         2], column_data[3], column_data[4]
#                     db.query(models.Ownership).filter(models.Ownership.ownership_id == ownershipid) \
#                         .update({models.Ownership.ownership_id: ownershipid,
#                                  models.Ownership.growing_area_id: growing_id,
#                                  models.Ownership.contract: cont_volume,
#                                  models.Ownership.shrinkage: shrinkage_perc,
#                                  models.Ownership.to_ship: toship}, synchronize_session='fetch')
#
#                     db.commit()
#                 total_ship_calculation(item.ownership_id, db)
#
#         return {"status": "success", "records_updated": update_count}
#     except Exception as e:  # pragma: no cover
#         raise HTTPException(status_code=400, detail=str(e))


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
                       "extension": 0, "market": 0, "flex": 0, "total_ship": 0, "year": year,
                       "crop_type": fresh_crop_type,
                       "crop_year": fresh_crop_year, "final_extension": 0}
            new_ownership = models.Ownership(**payload)
            db.add(new_ownership)
            db.commit()
            payload = {"ownership_id": storage_ownership_id, "growing_area_id": growing_area.growing_area_id,
                       "contract": 0, "contract_erp_value": 0, "shrinkage": 0, "to_ship": 0,
                       "extension": 0, "market": 0, "flex": 0, "total_ship": 0, "year": year,
                       "crop_type": storage_crop_type,
                       "crop_year": storage_crop_year, "final_extension": 0}
            new_ownership = models.Ownership(**payload)
            db.add(new_ownership)
            db.commit()

        return {"Status": "success", "records_inserted": "Next year data are added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_contract_erp/{crop_year}")
def update_ownership_contract_erp(crop_year: str, db: Session = Depends(get_db)):
    try:
        max_crop_year = db.query(func.max(models.View_total_sum_growing_area.columns.crop_year)) \
            .filter(models.View_total_sum_growing_area.columns.STORAGE_period == crop_year).scalar()
        view_data = db.query(models.View_total_sum_growing_area) \
            .filter(models.View_total_sum_growing_area.columns.STORAGE_period == crop_year,
                    models.View_total_sum_growing_area.columns.crop_year == max_crop_year) \
            .all()
        if len(view_data) > 0:
            for data in view_data:
                existing_record = db.query(models.Ownership) \
                    .filter(models.Ownership.growing_area_id == data.growing_area_id,
                            models.Ownership.crop_year == crop_year) \
                    .first()
                if existing_record is not None:
                    db.query(models.Ownership).filter(
                        models.Ownership.growing_area_id == data.growing_area_id,
                        models.Ownership.crop_year == crop_year
                    ).update({models.Ownership.contract_erp_value: data.totalsum})

                db.commit()
            return {"message": f"Total Contract ERP updated for {crop_year} in Ownership table"}
        else:
            return {"message": f"Total Contract ERP is not available for {crop_year} in erp table."}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


def generate_ownership_payload(growing_area_id, crop_year, crop_type, year):  # pragma: no cover
    ownership_id = str(growing_area_id) + "#" + str(crop_year)
    payload = {
        "ownership_id": ownership_id,
        "growing_area_id": growing_area_id,
        "contract": 0,
        "contract_erp_value": 0,
        "shrinkage": 0,
        "to_ship": 0,
        "extension": 0,
        "market": 0,
        "flex": 0,
        "total_ship": 0,
        "year": year,
        "crop_type": crop_type,
        "crop_year": str(crop_year),
        "final_extension": 0
    }
    return payload


@router.post('/new_growing_area/{growing_area_name}')
def new_growing_area(growing_area_name: str, db: Session = Depends(get_db)):  # pragma: no cover
    try:
        growing_area_id = db.query(models.growing_area.growing_area_id) \
            .filter(models.growing_area.growing_area_name == growing_area_name).scalar()
        current_year = date.today().year
        fresh_crop_year = str(current_year)
        previous_crop_year = str(current_year - 1) + "-" + str(current_year)[2:]
        storage_crop_year = str(current_year) + "-" + str(current_year + 1)[2:]

        prev_storage_ownership_payload = generate_ownership_payload(growing_area_id, previous_crop_year,
                                                                    'Storage', current_year - 1)
        fresh_ownership_payload = generate_ownership_payload(growing_area_id, fresh_crop_year,
                                                             'Fresh', current_year)
        storage_ownership_payload = generate_ownership_payload(growing_area_id, storage_crop_year,
                                                               'Storage', current_year)

        prev_ownership = models.Ownership(**prev_storage_ownership_payload)
        fresh_ownership = models.Ownership(**fresh_ownership_payload)
        storage_ownership = models.Ownership(**storage_ownership_payload)
        db.add(prev_ownership)
        db.add(fresh_ownership)
        db.add(storage_ownership)
        db.commit()
        return {"Status": "success",
                "message": f" Ownership record is added for {previous_crop_year}, "
                           f"{fresh_crop_year}, {storage_crop_year} seasons."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


def calculate_to_ship(growing_area_id: int, crop_period: str, db):
    total_contract = 0
    total_to_ship = 0
    total_shrinkage_per = 0
    get_contract_shrinkage = db.query(OwnershipGrowerGrowing.contract, OwnershipGrowerGrowing.shrinkage) \
        .filter(OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                OwnershipGrowerGrowing.crop_year == crop_period,
                OwnershipGrowerGrowing.status == 'ACTIVE').all()
    if len(get_contract_shrinkage) != 0:
        print(len(get_contract_shrinkage))
        for item in get_contract_shrinkage:
            print(item[0], item[1])
            total_contract += item[0]
            total_to_ship += item[0] - (item[0] * (item[1] / 100))
        if total_contract == 0:
            total_shrinkage_per = 0
        else:
            total_shrinkage_per = ((total_contract - total_to_ship) / total_contract) * 100
    """Update the Ownership Table."""
    db.query(Ownership) \
        .filter(Ownership.crop_year == crop_period,
                Ownership.growing_area_id == growing_area_id) \
        .update({Ownership.contract: total_contract,
                 Ownership.shrinkage: total_shrinkage_per,
                 Ownership.to_ship: total_to_ship}, synchronize_session=False)
    db.commit()


def calculate_market_and_flex(growing_area_id: int, crop_period: str, db):
    total_market = 0
    total_flex = 0
    get_market_flex = db.query(OwnershipGrowerGrowing.market, OwnershipGrowerGrowing.flex) \
        .filter(OwnershipGrowerGrowing.status == 'ACTIVE',
                OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                OwnershipGrowerGrowing.crop_year == crop_period).all()
    if len(get_market_flex) != 0:
        for item in get_market_flex:
            total_market += item[0]
            total_flex += item[1]
    """Update the Ownership Table."""
    db.query(Ownership) \
        .filter(Ownership.crop_year == crop_period,
                Ownership.growing_area_id == growing_area_id) \
        .update({Ownership.market: total_market,
                 Ownership.flex: total_flex}, synchronize_session=False)
    db.commit()


def total_ship_calculation(growing_area_id: int, crop_period: str, db):
    ownership_record = db.query(Ownership) \
        .filter(Ownership.growing_area_id == growing_area_id,
                Ownership.crop_year == crop_period).first()
    print(ownership_record.to_ship)
    ownership_record.total_ship = float(ownership_record.to_ship) + float(ownership_record.market) \
                                  + float(ownership_record.flex)
    db.commit()


@router.post('/update_contract_shrinkage_mkt_flex/growing_area_id/{growing_area_id}/crop/{crop_period}')
def update_contract_shrinkage_mkt_flex(payload: schemas.UpdateOwnershipGrowerGrowing,
                                       growing_area_id: int, crop_period: str, db: Session = Depends(get_db)):
    try:
        data = payload.PayloadOwnership
        old_records = db.query(OwnershipGrowerGrowing) \
            .filter(OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                    OwnershipGrowerGrowing.crop_year == str(crop_period)).all()
        if old_records:
            db.execute(delete(OwnershipGrowerGrowing)
                       .filter(OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                               OwnershipGrowerGrowing.crop_year == crop_period))
            db.commit()
            print("Records deleted successfully.")
        # Insert the records:
        for data_items in data:
            new_records = OwnershipGrowerGrowing(**data_items.dict())
            db.add(new_records)
        db.commit()
        print("--------- calculation started -------")
        calculate_to_ship(growing_area_id, crop_period, db)
        print("--------- to ship completed -------")
        calculate_market_and_flex(growing_area_id, crop_period, db)
        print("--------- market and flex -------")
        total_ship_calculation(growing_area_id, crop_period, db)
        return {"status": "success",
                "message": f"Ownership is updated for this growing_area_id: {growing_area_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/get_recent_extensions')
def get_extensions(db: Session = Depends(get_db)):
    try:
        today_date = date.today()
        year = int(today_date.year)
        records =(db.query( models.View_Ownership.columns.growing_area_name,
                            models.View_Ownership.columns.demand,
                            models.View_Ownership.columns.Position,
                            models.View_Ownership.columns.extension,
                            Ownership.updated_time)
                    .select_from(models.View_Ownership)
                    .join(Ownership,
                          Ownership.ownership_id == models.View_Ownership.columns.ownership_id)
                    .filter(models.View_Ownership.columns.extension!=0,
                            models.View_Ownership.columns.year==year).all())
        return {"record":records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))