from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
import schemas
import models

router = APIRouter()


@router.get('/year/{year}')
def get_ownershipMapping(year: int, db: Session = Depends(get_db)):
    grower_growing = db.query(models.OwnershipGrowerGrowing.row_id,
                              models.OwnershipGrowerGrowing.ownership_id,
                              models.growers.grower_name,
                              models.OwnershipGrowerGrowing.shrinkage,
                              models.OwnershipGrowerGrowing.contract_erp,
                              models.OwnershipGrowerGrowing.contract,
                              models.OwnershipGrowerGrowing.year,
                              models.OwnershipGrowerGrowing.crop_year)\
        .join(models.growers,
              models.OwnershipGrowerGrowing.grower_id == models.growers.grower_id)\
        .filter(models.OwnershipGrowerGrowing.status == "ACTIVE",
                or_(models.OwnershipGrowerGrowing.year == year,
                    models.OwnershipGrowerGrowing.year == year - 1)).all()
    if not grower_growing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No mapping  found")
    return {"status": "success", "grower_growing": grower_growing}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_grower_growing_area_mapping(payload: schemas.OwnershipGrowerGrowingSchema, db: Session = Depends(get_db)):
    ext_grower_id = payload.grower_id
    ext_growing_area_id = payload.growing_area_id
    ext_year = payload.year
    existing_record = (db.query(models.OwnershipGrowerGrowing).filter(
        models.OwnershipGrowerGrowing.growing_area_id == ext_growing_area_id,
        models.OwnershipGrowerGrowing.grower_id == ext_grower_id,
        models.OwnershipGrowerGrowing.year == ext_year).first())
    if existing_record:
        return {"message": "record exist"}
    else:
        new_GrowerMapping = models.OwnershipGrowerGrowing(**payload.dict())
        db.add(new_GrowerMapping)
    db.commit()
    db.refresh(existing_record if existing_record else new_GrowerMapping)

    return {
        "status": "success",
        "grower_growing_mapping_id": (
            existing_record if existing_record else new_GrowerMapping).growing_area_id_mapper_id
    }


@router.get('/{GrowingAreaId}/{GrowerId}/{year}')
def get_post(GrowingAreaId: str, GrowerId, year, db: Session = Depends(get_db)):
    Growers_GrowingArea_yearWise = (db.query(models.growers, models.OwnershipGrowerGrowing)
                                    .join(models.growers,
                                          models.growers.grower_id == models.OwnershipGrowerGrowing.grower_id)
                                    .filter(models.OwnershipGrowerGrowing.growing_area_id == GrowingAreaId,
                                            models.OwnershipGrowerGrowing.grower_id == GrowerId,
                                            models.OwnershipGrowerGrowing.year == year).all())
    if not Growers_GrowingArea_yearWise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No records found")

    return {"status": "success", "Growers_GrowingAreaWise": Growers_GrowingArea_yearWise}


@router.delete('/{Growing_area_id}/{Grower_id}/{year}')
def delete_post(Growing_area_id: str, Grower_id, year, db: Session = Depends(get_db)):
    grower_growing = (db.query(models.OwnershipGrowerGrowing).filter(
        models.OwnershipGrowerGrowing.growing_area_id == Growing_area_id,
        models.OwnershipGrowerGrowing.grower_id == Grower_id,
        models.OwnershipGrowerGrowing.year == year, models.OwnershipGrowerGrowing.status == "ACTIVE").first())
    if not grower_growing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No records found')
    db.delete(grower_growing)
    db.commit()
    return {"status": "success",
            "record has been deleted for": f"Grower Id: {Grower_id}, Growing Area Id: {Growing_area_id}"}


@router.post("/update_contract_erp/{crop_year}")
def update_contract_erp(crop_year: str, db: Session = Depends(get_db)):
    try:
        view_data = (db.query(models.View_growing_area_contract_erp)
                     .filter(models.View_growing_area_contract_erp.columns.STORAGE_period == crop_year)
                     .all())
        print("view_data", view_data)
        if len(view_data) > 0:
            for data in view_data:
                print("data", data)
                row_id = f"{data.growignarea_id}#{data.grower_id}#{data.STORAGE_period}"
                ownershipId = f"{data.growignarea_id}#{data.STORAGE_period}"
                existing_record = (db.query(models.OwnershipGrowerGrowing)
                                   .filter(
                    models.OwnershipGrowerGrowing.growing_area_id == data.growignarea_id,
                    models.OwnershipGrowerGrowing.grower_id == data.grower_id,
                    models.OwnershipGrowerGrowing.crop_year == crop_year
                ).first())
                if existing_record is not None:
                    db.query(models.OwnershipGrowerGrowing).filter(
                        models.OwnershipGrowerGrowing.growing_area_id == data.growignarea_id,
                        models.OwnershipGrowerGrowing.grower_id == data.grower_id,
                        models.OwnershipGrowerGrowing.crop_year == crop_year
                    ).update({models.OwnershipGrowerGrowing.contract_erp: data.sum_contract,
                              models.OwnershipGrowerGrowing.status: "ACTIVE"})

                else:
                    payload = {"row_id": row_id,
                               "growing_area_id": data.growignarea_id,
                               "grower_id": data.grower_id,
                               "contract": 0,
                               "contract_erp": data.sum_contract,
                               "shrinkage": 0,
                               "year": data.STORAGE_period[:4],
                               "crop_type": data.CROP_TYPE,
                               "crop_year": data.STORAGE_period,
                               "ownership_id": ownershipId,
                               "status": "ACTIVE"}
                    new_record = models.OwnershipGrowerGrowing(**payload)
                    db.add(new_record)
                db.commit()
        return {"message": f"Contract ERP updated for {crop_year}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")



# @router.post('/OwnershipGrowingGrowerMapping/{year}')
# def Create_New_crop_year_Records(year: str, db: Session = Depends(get_db)):
#     current_year = int(year.split('-')[0])
#     prev_year = current_year - 1
#     next_year = current_year + 1
#     next_crop = f"{str(prev_year)}-{str(current_year)[2:]}"  # to extract storage data
#     next_crop_year = f"{str(current_year)}-{str(next_year)[2:]}"  # to assign crop year
#
#     fresh_record = db.query(models.OwnershipGrowerGrowing).filter(
#         models.OwnershipGrowerGrowing.crop_year == str(current_year)).all()
#     # for crop_type "Fresh" and crop_year "YYYY"
#     if not fresh_record:
#         fresh_records = db.query(models.OwnershipGrowerGrowing).filter(
#             models.OwnershipGrowerGrowing.crop_year == str(prev_year)).all()
#         for existing_record in fresh_records:
#             crop_type = "Fresh"
#             crop_year = year
#             payload_fresh = {"row_id": f"{existing_record.growing_area_id}#{existing_record.grower_id}#{crop_year}",
#                              "growing_area_id": existing_record.growing_area_id,
#                              "grower_id": existing_record.grower_id,
#                              "contract": existing_record.contract,
#                              "year": year,
#                              "shrinkage": existing_record.shrinkage,
#                              "ownership_id": f"{existing_record.growing_area_id}#{crop_year}",
#                              "crop_type": crop_type,
#                              "crop_year": crop_year}
#             new_record = models.OwnershipGrowerGrowing(**payload_fresh)
#             db.add(new_record)
#         db.commit()
#
#     # for crop_type "Storage" and crop_year "YYYY-YY"
#     storage_record = db.query(models.OwnershipGrowerGrowing).filter(
#         models.OwnershipGrowerGrowing.crop_year == str(next_crop_year)).all()
#     if not storage_record:
#         storages_records = db.query(models.OwnershipGrowerGrowing).filter(
#             models.OwnershipGrowerGrowing.crop_year == str(next_crop)).all()
#         for existing_record in storages_records:
#             crop_type = "Storage"
#             crop_year = next_crop_year
#             payload_fresh = {
#                 "row_id": f"{existing_record.growing_area_id}#{existing_record.grower_id}#{crop_year}",
#                 "growing_area_id": existing_record.growing_area_id,
#                 "grower_id": existing_record.grower_id,
#                 "contract": existing_record.contract,
#                 "year": year,
#                 "shrinkage": existing_record.shrinkage,
#                 "ownership_id": f"{existing_record.growing_area_id}#{crop_year}",
#                 "crop_type": crop_type,
#                 "crop_year": crop_year}
#             new_record = models.OwnershipGrowerGrowing(**payload_fresh)
#             db.add(new_record)
#     db.commit()
#
#     # Updating Ownership Table for Fresh
#     try:
#         mapping_data = db.query(models.OwnershipGrowerGrowing.growing_area_id,
#                                 func.sum(models.OwnershipGrowerGrowing.contract)).filter(
#             models.OwnershipGrowerGrowing.crop_year == str(current_year)).group_by(
#             models.OwnershipGrowerGrowing.growing_area_id).order_by(
#             models.OwnershipGrowerGrowing.growing_area_id).all()
#         per_grower_shrinkage = db.query(
#             models.OwnershipGrowerGrowing.growing_area_id,
#             models.OwnershipGrowerGrowing.contract,
#             models.OwnershipGrowerGrowing.shrinkage,
#             models.OwnershipGrowerGrowing.ownership_id).filter(
#             models.OwnershipGrowerGrowing.crop_year == str(current_year)).order_by(
#             models.OwnershipGrowerGrowing.growing_area_id).all()
#         print("mapping_data", mapping_data)
#         print("per_grower_shrinkage", per_grower_shrinkage)
#         sums_dict = {}
#         for items in per_grower_shrinkage:
#             key = items[0]  # item[0]: growing_area_id
#             value1 = items[1]  # item[1]: contract
#             value2 = items[2]  # item[2]: shrinkage
#
#             if key in sums_dict:
#                 sums_dict[key][0] += value1
#                 sums_dict[key][1] += value1 * value2 * 0.01
#             else:
#                 sums_dict[key] = [value1, value1 * value2 * 0.01]
#         output_data = [(key, value[0], round(value[1], 2)) for key, value in sums_dict.items()]
#         # output_data has growing_id, total_contract_value and tatal
#         shrinkage_output = [(item[0], round((item[2] * 100 / item[1]), 2), round((item[1] - item[2]), 2)) for item
#                             in
#                             output_data]
#         print("shrinkage_output", shrinkage_output)
#         ownership_id_dict = {item[0]: item[3] for item in per_grower_shrinkage}
#         data_list = []
#         for row in mapping_data:
#             growing_area_id = row[0]
#             contracted = row[1]
#             market_n_flex = row[2]
#             ownership_id = ownership_id_dict.get(growing_area_id)
#             if ownership_id is not None:
#                 data_list.append(
#                     {"growing_area_id": growing_area_id, "contracted": contracted, "ownership_id": ownership_id})
#         combined_data = [
#             (var1[0], var1[1], var1[2], var2['contracted'], var2['ownership_id'])
#             for
#             var1, var2 in zip(shrinkage_output, data_list)]
#         print("combined_data", combined_data)
#
#         # Populating Ownership table
#         for column_data in combined_data:
#             growing_id, shrinkage_perc, toship, cont_volume, ownershipid = column_data[0], \
#                 column_data[1], column_data[2], column_data[3], column_data[4]
#
#             crop_type = "Fresh"
#             crop_year = str(current_year)
#             payload_ownership = {"ownership_id": ownershipid,
#                                  "growing_area_id": growing_id,
#                                  "contract": cont_volume,
#                                  "shrinkage": shrinkage_perc,
#                                  "to_ship": toship,
#                                  "year": current_year,
#                                  "crop_type": crop_type,
#                                  "crop_year": crop_year}
#             print("payload_ownership", payload_ownership)
#             new_record = models.Ownership(**payload_ownership)
#             db.add(new_record)
#         db.commit()
#
#         # Updating Ownership Table for Storage
#         mapping_data = db.query(models.OwnershipGrowerGrowing.growing_area_id,
#                                 func.sum(models.OwnershipGrowerGrowing.contract)).filter(
#             models.OwnershipGrowerGrowing.crop_year == str(next_crop_year)).group_by(
#             models.OwnershipGrowerGrowing.growing_area_id).order_by(
#             models.OwnershipGrowerGrowing.growing_area_id).all()
#         per_grower_shrinkage = db.query(
#             models.OwnershipGrowerGrowing.growing_area_id,
#             models.OwnershipGrowerGrowing.contract,
#             models.OwnershipGrowerGrowing.shrinkage,
#             models.OwnershipGrowerGrowing.ownership_id).filter(
#             models.OwnershipGrowerGrowing.crop_year == str(next_crop_year)).order_by(
#             models.OwnershipGrowerGrowing.growing_area_id).all()
#         print("mapping_data", mapping_data)
#         print("per_grower_shrinkage", per_grower_shrinkage)
#         sums_dict = {}
#         for items in per_grower_shrinkage:
#             key = items[0]  # item[0]: growing_area_id
#             value1 = items[1]  # item[1]: contract
#             value2 = items[2]  # item[2]: shrinkage
#
#             if key in sums_dict:
#                 sums_dict[key][0] += value1
#                 sums_dict[key][1] += value1 * value2 * 0.01
#             else:
#                 sums_dict[key] = [value1, value1 * value2 * 0.01]
#         output_data = [(key, value[0], round(value[1], 2)) for key, value in sums_dict.items()]
#         # output_data has growing_id, total_contract_value and tatal
#         shrinkage_output = [(item[0], round((item[2] * 100 / item[1]), 2), round((item[1] - item[2]), 2)) for item
#                             in
#                             output_data]
#         print("shrinkage_output", shrinkage_output)
#         ownership_id_dict = {item[0]: item[3] for item in per_grower_shrinkage}
#         data_list = []
#         for row in mapping_data:
#             growing_area_id = row[0]
#             contracted = row[1]
#             market_n_flex = row[2]
#             ownership_id = ownership_id_dict.get(growing_area_id)
#             if ownership_id is not None:
#                 data_list.append(
#                     {"growing_area_id": growing_area_id, "contracted": contracted, "ownership_id": ownership_id})
#         combined_data = [
#             (var1[0], var1[1], var1[2], var2['contracted'], var2['ownership_id'])
#             for
#             var1, var2 in zip(shrinkage_output, data_list)]
#         print("combined_data", combined_data)
#
#         # Populating Ownership table
#         for column_data in combined_data:
#             growing_id, shrinkage_perc, toship, cont_volume, ownershipid = column_data[0], \
#                 column_data[1], column_data[2], column_data[3], column_data[4]
#
#             crop_type = "Fresh"
#             crop_year = str(next_crop_year)
#             payload_ownership = {"ownership_id": ownershipid,
#                                  "growing_area_id": growing_id,
#                                  "contract": cont_volume,
#                                  "shrinkage": shrinkage_perc,
#                                  "to_ship": toship,
#                                  "year": current_year,
#                                  "crop_type": crop_type,
#                                  "crop_year": crop_year}
#             print("payload_ownership", payload_ownership)
#             new_record = models.Ownership(**payload_ownership)
#             db.add(new_record)
#         db.commit()
#         return {"status": "success", "message": "New set of records created/updated."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))