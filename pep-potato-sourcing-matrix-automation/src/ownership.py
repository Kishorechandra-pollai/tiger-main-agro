import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import Depends, HTTPException, status, APIRouter
import schemas
import models
from database import get_db

router = APIRouter()


@router.get('/')
def get_ownership(db: Session = Depends(get_db)):
    ownership = db.query(models.Ownership).all()
    if not ownership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No ownership_id found")
    return {"status": "success", "ownership": ownership}


# @router.post('/grower_growing_mapping/{year}')
# def Create_New_GrowerGrowingMapping(year: int, db: Session = Depends(get_db)):
#     pre_year = year - 1
#     pre_record = db.query(models.grower_growing_area_mapping).filter(
#         models.grower_growing_area_mapping.year == pre_year).all()
#     for pre_record_item in pre_record:
#         print(pre_record_item)
#         payload = {"grower_id": pre_record_item.grower_id, "growing_area_id": pre_record_item.growing_area_id,
#                    "contracted_value": pre_record_item.contracted_value, "year": year,
#                    "shrinkage": pre_record_item.shrinkage}
#         new_mapping_record = models.grower_growing_area_mapping(**payload)
#         db.add(new_mapping_record)
#     db.commit()
#     return {"status": "success", "message": "new records created"}


@router.post('/OwnershipMapping/{year}')
def Create_Ownership_Mapping(year: str, db: Session = Depends(get_db)):
    current_year = int(year.split('-')[0])
    next_year = current_year + 1
    crop_id = f"{str(current_year)}-{str(next_year)[2:]}"
    print(crop_id)

    # Check if records already exist for the specified year and crop_year
    existing_records = db.query(models.OwnershipGrowerGrowing).filter(
        models.OwnershipGrowerGrowing.year == year).all()
    # print(existing_records)
    # return{'status':'success'}

    # if existing_records:
    # return {"status": "success", "message": "Records already exist for the specified year and crop_year."}

    new_records = []
    for i in range(2):
        if int(current_year) == datetime.datetime.now().year:
            crop_type = "Fresh"
            crop_year = year
        else:
            crop_type = "Storage"
            crop_year = crop_id

        for existing_record in existing_records:
            new_record = models.OwnershipGrowerGrowing(
                grower_id=existing_record.grower_id,
                growing_area_id=existing_record.growing_area_id,
                contract=existing_record.contract,
                year=year,
                shrinkage=existing_record.shrinkage,
                crop_type=crop_type,
                crop_year=crop_year
            )
            # ownership_id based on growing_area_id and year
            growing_area_id = existing_record.growing_area_id
            ownership_id = f"{growing_area_id}#{crop_year}"
            new_record.ownership_id = ownership_id

            new_records.append(new_record)
        # print(new_records)
        # return {'status': 'success'}

        current_year += 1
    db.add_all(new_records)
    db.commit()
    return {"status": "success", "message": "New records created/updated."}


@router.post('/UpdateGrowerGrowingArea_mapping')
def Update_ContractValue_ShrinkageValue(payload: schemas.UpdateOwnershipGrowerGrowing,
                                        db: Session = Depends(get_db)):
    DataUpdateGrowerGrowing = payload.DataOGG
    update_count = 0
    try:
        for item in DataUpdateGrowerGrowing:
            db.query(models.OwnershipGrowerGrowing).filter(
                models.OwnershipGrowerGrowing.grower_id == item.grower_id).filter(
                models.OwnershipGrowerGrowing.row_id == item.row_id).update(
                {models.OwnershipGrowerGrowing.contract: item.contract,
                 models.OwnershipGrowerGrowing.shrinkage: item.shrinkage}, synchronize_session='fetch')
            update_count += 1

        year_id = '2023'
        mapping_data = db.query(models.OwnershipGrowerGrowing.growing_area_id,
                                func.sum(models.OwnershipGrowerGrowing.contract)).filter(
            models.OwnershipGrowerGrowing.crop_year == year_id).group_by(
            models.OwnershipGrowerGrowing.growing_area_id).order_by(
            models.OwnershipGrowerGrowing.growing_area_id).all()
        per_grower_shrinkage = db.query(
            models.OwnershipGrowerGrowing.growing_area_id,
            models.OwnershipGrowerGrowing.contract,
            models.OwnershipGrowerGrowing.shrinkage,
            models.OwnershipGrowerGrowing.ownership_id).filter(
            models.OwnershipGrowerGrowing.crop_year == year_id).order_by(
            models.OwnershipGrowerGrowing.growing_area_id).all()
        # print(per_grower_shrinkage)
        sums_dict = {}
        for item in per_grower_shrinkage:
            key = item[0]
            value1 = item[1]
            value2 = item[2]

            if key in sums_dict:
                sums_dict[key][0] += value1
                sums_dict[key][1] += value1 * value2 * 0.01
            else:
                sums_dict[key] = [value1, value1 * value2 * 0.01]
        output_data = [(key, value[0], round(value[1], 2)) for key, value in sums_dict.items()]
        shrinkage_output = [(item[0], round((item[2] * 100 / item[1]), 2), round((item[1] - item[2]), 2)) for item in
                            output_data]
        # print(shrinkage_output)
        ownership_id_dict = {item[0]: item[3] for item in per_grower_shrinkage}
        data_list = []
        for row in mapping_data:
            growing_area_id = row[0]
            contracted = row[1]
            ownership_id = ownership_id_dict.get(growing_area_id)
            if ownership_id is not None:
                data_list.append(
                    {"growing_area_id": growing_area_id, "contracted": contracted, "ownership_id": ownership_id})
        # print(data_list)
        combined_data = [(var1[0], var1[1], var1[2], var2['contracted'], var2['ownership_id']) for
                         var1, var2 in zip(shrinkage_output, data_list)]

        # Populating Ownership table
        for column_data in combined_data:
            growing_id, shrinkage_perc, toship, cont_volume, ownershipid = column_data[0], column_data[1], column_data[
                2], column_data[3], column_data[4]
            # Fetching data from ownership_grower_growing_area_mapping
            grower_growing_data = db.query(models.OwnershipGrowerGrowing).filter(
                models.OwnershipGrowerGrowing.growing_area_id == growing_id,
                models.OwnershipGrowerGrowing.crop_year == year_id).first()
            if grower_growing_data:
                existing_record = db.query(models.Ownership).filter(
                    models.Ownership.ownership_id == ownershipid).first()
                if existing_record:
                    existing_record.ownership_id = ownershipid
                    existing_record.growing_area_id = growing_id
                    existing_record.contract = cont_volume
                    existing_record.shrinkage = shrinkage_perc
                    existing_record.to_ship = toship
                    existing_record.year = grower_growing_data.year
                    existing_record.crop_type = grower_growing_data.crop_type
                    existing_record.crop_year = grower_growing_data.crop_year
                else:
                    new_record = models.Ownership(
                        ownership_id=ownershipid,
                        growing_area_id=growing_id,
                        shrinkage=shrinkage_perc,
                        contract=cont_volume,
                        to_ship=toship,
                        year=year_id,
                        crop_type=grower_growing_data.crop_type,
                        crop_year=grower_growing_data.crop_year
                    )
                    db.add(new_record)

        db.commit()
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.delete('/delete_all')
# def delete_all_records(db: Session = Depends(get_db)):
#     try:
#         records_to_delete = db.query(models.OwnershipGrowerGrowing).filter(
#             models.OwnershipGrowerGrowing.ownership_id.is_(None)).all()
#         print(len(records_to_delete))
        # for record in records_to_delete:
        #     db.delete(record)
        #
        # db.commit()
        #
        # return {"status": "success", "message": "All records deleted from the table"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
#
# @router.post('/update_ownership_grower')
# def update_growingID(payload: schemas.UpdateOwnershipGrowerGrowing, db: Session = Depends(get_db)):
#     try:
#         year = "2023"
#         growing_area_ids = db.query(models.growing_area.growing_area_id).all()
#         new_records = []
#         for growing_area_id in growing_area_ids:
#             Extract the integer value from the tuple
# growing_area_id = growing_area_id[0]
# ownership_id = f"{growing_area_id}#{year}"  # Create the ownership_id
# new_record = models.Ownership(growing_area_id=growing_area_id,
#                               ownership_id=ownership_id,
#                               contract=None,
#                               shrinkage=None,
#                               to_ship=None,
#                               position=None,
#                               market_and_flex=40,
#                               total_ship=None,
#                               year=2023,
#                               crop_type='fresh',
#                               crop_year='2023',
#                               created_time=None,
#                               updated_time=None,
#                               created_by=None,
#                               updated_by=None)
# new_records.append(new_record)
# db.add_all(new_records)
# db.commit()
# return {"status": "success", "records_updated": len(growing_area_ids)}
# except Exception as e:
#     raise HTTPException(status_code=400, detail=str(e))
