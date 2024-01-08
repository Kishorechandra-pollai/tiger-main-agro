import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient

#sys.path.append(r"..\src\main.py")
#sys.path.append(r"..\pep-potato-sourcing-matrix-automation\src")
sys.path.append(r"..\src\")
from main import app
import models
import schemas
from plants import create_plant
from ownership import Create_new_Ownership, Update_Ownership, update_ownership_contract_erp
from extensionMapping import update_extension_mapping, update_extension_plantMtrx
from MarketFlexMapping import update_Market_flex, filtered_market_year
from OwnershipGrowerGrowing import (update_contract_erp, delete_post, create_grower_growing_area_mapping)
from allocation import update_allocation, create_allocation
from pcusage import create_new_pcusage
from plant_mtrx import update_plantMtrx, func_getcrop_type, update_extension
# from plantGrowingMapping import create_plant_growing_area_mapping, delete_plant_growing
from growingarea import create_growing_area, delete_growing_area
from growers import delete_grower, create_growers

client = TestClient(app)

"""--------OwnershipGrowerGrowing.py---------"""


def test_get_OwnershipGrowerGrowing():
    response = client.get('/api/ownershipMapping/year/2023')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_create_grower_growing_area_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "row_id": "254#170#2022-23",
        "growing_area_id": 254,
        "grower_id": 170,
        "contract": 10,
        "year": 2023,
        "shrinkage": 0,
        "contract_erp": 0,
        "ownership_id": "254#2022-23",
        "crop_type": "Storage",
        "crop_year": "2022-23",
        "status": "INACTIVE"
    }
    test_ownership_schema = schemas.OwnershipGrowerGrowingSchema(**mapping_payload)
    result = create_grower_growing_area_mapping(payload=test_ownership_schema, db=db_mock)

    assert result['message'] == 'record exist'


@patch('database.get_db')
def test_successful_update_contract_erp(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    crop_year = "2023-24"
    db_mock.query().filter().all.return_value = [
        MagicMock(row_id='248#174#2023-24',
                  growing_area_id=248,
                  grower_id=174,
                  contract=670,
                  contract_erp=10,
                  shrinkage=5,
                  year=2023,
                  crop_type='Storage',
                  crop_year='2023-24',
                  ownership_id='248#2023-24',
                  status="INACTIVE"),
        MagicMock(row_id='111#111#2023-24',
                  growing_area_id=111,
                  grower_id=111,
                  contract=670,
                  contract_erp=0,
                  shrinkage=5,
                  year=2023,
                  crop_type='Storage',
                  crop_year='2023-24',
                  ownership_id='248#2023-24',
                  status="INACTIVE")]

    result = update_contract_erp(crop_year=crop_year, db=db_mock)
    assert result == {"message": f"Contract ERP updated for {crop_year}"}


@patch('database.get_db')
def test_successful_update_contract_erp_2(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    crop_year = "2023-24"

    db_mock.query().filter().all.return_value = [
        MagicMock(row_id='111#111#2023-24',
                  growing_area_id=111,
                  grower_id=111,
                  contract=100,
                  contract_erp=0,
                  shrinkage=0,
                  year=2023,
                  crop_type='Storage',
                  crop_year='2023-24',
                  ownership_id='111#2023-24',
                  status="INACTIVE")]

    result = update_contract_erp(crop_year=crop_year, db=db_mock)
    assert result == {"message": f"Contract ERP updated for {crop_year}"}


@patch('database.get_db')
def test_successful_delete_post(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    Growing_area_id = 248
    Grower_id = 174
    year = "2023-24"
    mock_record = MagicMock()
    db_mock.query().filter().first.return_value = mock_record
    result = delete_post(Growing_area_id=Growing_area_id, Grower_id=Grower_id, year=year, db=db_mock)

    assert result == {"status": "success",
                      "record has been deleted for": f"Grower Id: {Grower_id}, Growing Area Id: {Growing_area_id}"}


"""--------Ownership.py---------"""


def test_get_ownership_region_0():
    response = client.get('/api/ownership/region/US/year/2023')
    assert response.status_code == 200


def test_get_ownership_region_1():
    response = client.get('/api/ownership/region/7/year/2023')
    assert response.status_code == 404


def test_get_ownership_region_2():
    response = client.get('/api/ownership/year/2023')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_create_new_ownership_success(mock_get_db):
    db_mock = Mock()
    growing_area_list_mock = [
        Mock(growing_area_id=44),
        Mock(status='ACTIVE')
    ]
    mock_get_db.return_value = db_mock
    db_mock.query().filter().all.return_value = growing_area_list_mock
    result = Create_new_Ownership(year=2025, db=db_mock)

    assert result["Status"] == "success"


@patch('database.get_db')
def test_mock_create_new_Ownership_exception(mock_get_db):
    db_mock = Mock()
    mock_get_db.return_value = db_mock
    db_mock.query().filter().all.return_value = []
    with patch('database.get_db', return_value=db_mock):
        try:
            Create_new_Ownership(year=2023)
        except Exception as e:
            assert e.status_code == 400


@patch('database.get_db')
def test_mock_update_ownership(mock_get_db):
    mock_query_result = [(1, 'Storage', '2022-23')]
    db_mock = MagicMock()
    db_mock.query().filter().group_by().order_by().all.return_value = mock_query_result
    mock_get_db.return_value = db_mock

    payload = [{
        "row_id": "254#170#2022-23",
        "growing_area_id": 254,
        "grower_id": 170,
        "contract": 10,
        "year": 2023,
        "shrinkage": 0,
        "contract_erp": 535.5,
        "ownership_id": "254#2022-23",
        "crop_type": "Storage",
        "crop_year": "2022-23",
        "status": "INACTIVE"
    }]
    test_payload = schemas.UpdateOwnershipGrowerGrowing(PayloadOwnership=payload)
    result = Update_Ownership(cropyear_input="2022-23", payload=test_payload, db=db_mock)
    assert result["status"] == "success"


@patch('database.get_db')
def test_update_ownership_contract_erp(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_view_data = [
        MagicMock(growing_area_id=1, totalsum=500),
        MagicMock(growing_area_id=2, totalsum=700)]

    db_mock.query().filter().all.return_value = mock_view_data
    existing_record_mock = models.Ownership(
        growing_area_id=1,
        crop_year="2023",
        contract_erp_value=200
    )
    db_mock.query().filter().first.return_value = existing_record_mock

    result = update_ownership_contract_erp(crop_year="2023", db=db_mock)
    assert result["message"] == "Total Contract ERP updated for 2023 in Ownership table"


"""--------extensionMapping.py---------"""


def test_get_extension_mapping():
    response = client.get('/api/extensionMapping/')
    assert response.status_code == 200


def test_get_filtered_extension():
    response = client.get('/api/extensionMapping/year/2023')
    assert response.status_code == 200


@patch('database.get_db')
def test_update_extension_plantMtrx(mock_get_db):
    db_mock = MagicMock()
    query_mock = MagicMock()
    db_mock.query = query_mock
    mock_get_db.return_value = db_mock
    ext_record_mock = MagicMock()
    ext_record_mock.status = 'ACTIVE'
    ext_record_mock.growing_area_id = 1
    ext_record_mock.year = 2023
    ext_record_mock.period = 1
    ext_record_mock.week = 1
    ext_record_mock.total_value = 100
    ext_record_mock.split = 'false'
    query_mock.return_value.filter.return_value.first.return_value = ext_record_mock

    result = update_extension_plantMtrx(1, 2023, 1, 1, 80, db=db_mock)

    assert result == "updated"
    assert ext_record_mock.total_value == 80


@patch('database.get_db')
def test_mock_update_extension_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload = [{
        "extension_id": "10#5#1#2022",
        "growing_area_id": 10,
        "period": 5,
        "week": 1,
        "crop_type": "Fresh",
        "crop_year": "2022",
        "total_value": 0,
        "year": 2022,
        "split": "none",
        "status": "INACTIVE"
    }]
    test_payload = schemas.ExtensionOwnershipPayload(ExtensionData=payload)
    result = update_extension_mapping(payload=test_payload, db=db_mock)
    assert "status" in result
    assert result["status"] == "success"


@patch('database.get_db')
def test_mock_update_extension_mapping_1(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_2 = [{
        "extension_id": "10#11#1#2022",
        "growing_area_id": 10,
        "period": 11,
        "week": 1,
        "crop_type": "Fresh",
        "crop_year": "2022",
        "total_value": 0,
        "year": 2022,
        "split": "none",
        "status": "INACTIVE"
    }]
    test_payload = schemas.ExtensionOwnershipPayload(ExtensionData=payload_2)
    result = update_extension_mapping(payload=test_payload, db=db_mock)
    assert "status" in result
    assert result["status"] == "success"


"""--------MarketFlexMapping.py---------"""


def test_get_marketflex_mapping():
    response = client.get('/api/MarketFlexMapping/')
    assert response.status_code == 200


@patch('database.get_db')
def test_filtered_market_year(mock_get_db):
    db_mock = MagicMock()
    query_mock = MagicMock()
    db_mock.query = query_mock
    mock_get_db.return_value = db_mock

    mock_filtered_market = [models.MarketFlexMapping(ownership_id=1, status="ACTIVE"),
                            models.MarketFlexMapping(ownership_id=2, status="ACTIVE")]
    query_mock.return_value.join.return_value.filter.return_value.all.return_value = mock_filtered_market

    result = filtered_market_year(2023, db=db_mock)

    assert result['status'] == 'success'
    assert len(result['MarketFlexMapping']) == len(mock_filtered_market)


@patch('database.get_db')
def test_mock_update_Market_flex(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_market = [{
        "row_id": "123#123#1",
        "growing_area_id": 123,
        "grower_id": 123,
        "ownership_id": "123#123",
        "status": "INACTIVE",
        "market_flex_value": 0
    }]
    marketflex_payload = schemas.MarketFlexPayload(Payload_MarketFlex=payload_market)
    result = update_Market_flex(payload=marketflex_payload, db=db_mock)
    assert "status" in result
    assert result["status"] == "success"


@patch('database.get_db')
def test_mock_update_Market_flex_1(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_market = [{
        "row_id": "123#123#1",
        "growing_area_id": 123,
        "grower_id": 123,
        "ownership_id": "123#123",
        "status": "INACTIVE",
        "market_flex_value": 100
    }]
    marketflex_payload = schemas.MarketFlexPayload(Payload_MarketFlex=payload_market)
    result = update_Market_flex(payload=marketflex_payload, db=db_mock)
    assert "status" in result
    assert result["status"] == "success"


"""--------plants.py---------"""


@patch('database.get_db')
def test_create_plant(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    plant_payload = {
        "plant_id": 1,
        "plant_code": "Test_1",
        "plant_name": "Test_1",
        "company_name": "Test_1",
        "region_id": 0,
        "status": "INACTIVE",
        "crop_category_id": 0,
        "created_time": "2023-12-15T13:51:55.222Z",
        "updated_time": "2023-12-15T13:51:55.222Z",
        "created_by": "string",
        "updated_by": "string"
    }
    mock_payload = schemas.PlantSchema(**plant_payload)
    result = create_plant(payload=mock_payload, db=db_mock)

    assert result == {"status": "success", "plants_id": 1}


def test_get_plant():
    response = client.get('/api/plant/')
    assert response.status_code == 200


"""________allocation.py_________"""


def test_get_allocation():
    response = client.get('/api/allocation/get_all')
    assert response.status_code == 200


def test_get_allocation_year():
    response = client.get('/api/allocation/filter/2023')
    assert response.status_code == 200


@patch('database.get_db')
def test_update_allocation(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload = [{
        "allocation_id": "Co-Man#1#2022",
        "category_name": "Co-Man",
        "year": 2022,
        "country": "USA",
        "period": 1,
        "value": 0
    }]
    test_payload = schemas.AllocationPayload(data=payload)
    result = update_allocation(payload=test_payload, db=db_mock)

    assert result["status"] == "success"


@patch('database.get_db')
def test_create_allocation(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    year = 2025

    table_data = [("Co-Man", "USA")]
    db_mock.query().all.return_value = table_data
    result = create_allocation(year=year, db=db_mock)

    assert result == {"Status": "success", "new_records": 13}


"""__________pcusage.py__________"""


def test_get_filtered_usage_company():
    response = client.get('/api/pcusage/company_name/US')
    assert response.status_code == 200


def test_get_filtered_usage_region():
    response = client.get('/api/pcusage/region_id/8')
    assert response.status_code == 200


def test_getusage_company_periodwise():
    response = client.get('/api/pcusage/period_wise/company_name/US')
    assert response.status_code == 200


def test_get_usage_period_wise():
    response = client.get('/api/pcusage/period_wise/region_id/8')
    assert response.status_code == 200


@patch('database.get_db')
def test_create_new_pcusage(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    year = 2025

    mock_plants_data = [(44, 10, 1)]  # plants data
    mock_category_name = [("Co-Man", "FLC")]  # category names
    mock_index_value = [(2, 0)]  # index values
    mock_last_year_actual = [(2, 0)]  # last year actual values

    db_mock.query().filter().all.side_effect = [mock_plants_data, mock_category_name, mock_index_value,
                                                mock_last_year_actual]
    result = create_new_pcusage(year=year, db=db_mock)

    assert result == {"status": "success", "message": "New forecast records are generated"}


"""_________growing_area.py_________"""


def test_get_growing_area_1():
    response = client.get('/api/growing-area/')
    assert response.status_code == 200


def test_get_preferred_grower_2():
    response = client.get('/api/growing-area/preferred_grower')
    assert response.status_code == 200


def test_get_post_3():
    response = client.get('/api/growing-area/44')
    assert response.status_code == 200


@patch('database.get_db')
def test_create_growing_area_4(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    growing_payload = {
        "growing_area_id": 1,
        "growing_area_name": "string",
        "region": 0,
        "country": "string",
        "status": "string",
        "growing_area_desc": "string",
        "fresh_period_start": 0,
        "fresh_week_start": 0,
        "fresh_period_end": 0,
        "fresh_week_end": 0,
        "created_time": "2023-12-28T10:04:33.964Z",
        "updated_time": "2023-12-28T10:04:33.964Z",
        "created_by": "string",
        "updated_by": "string"
    }
    mock_payload = schemas.GrowingAreaSchema(**growing_payload)
    result = create_growing_area(payload=mock_payload, db=db_mock)
    assert result == {"status": "success", "growing_area_id": 1}


@patch('database.get_db')
def test_delete_post(mock_get_db):
    db_mock = MagicMock()
    mock_query = MagicMock()
    mock_commit = MagicMock()
    db_mock.query = mock_query
    mock_query.return_value.filter.return_value.update.return_value = 1
    db_mock.commit = mock_commit
    mock_get_db.return_value = db_mock

    result = delete_growing_area("243", db=db_mock)
    assert result.status_code == 204


"""_______growers.py_______"""


def test_get_growers():
    response = client.get('/api/grower/')
    assert response.status_code == 200


def test_get_growers_id():
    response = client.get('/api/grower/126')
    assert response.status_code == 200


@patch('database.get_db')
def test_create_growers(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    growers_payload = {
        "grower_id": 1,
        "grower_name": "string",
        "owner": "string",
        "region": 0,
        "country": "string",
        "status": "string",
        "volume": "string",
        "created_time": "2023-12-28T10:34:57.549Z",
        "updated_time": "2023-12-28T10:34:57.549Z",
        "created_by": "string",
        "updated_by": "string"
    }
    mock_payload = schemas.GrowerSchema(**growers_payload)
    result = create_growers(payload=mock_payload, db=db_mock)
    assert "status" in result
    assert result["status"] == "success"


@patch('database.get_db')
def test_delete_grower(mock_get_db):
    db_mock = MagicMock()
    mock_query = MagicMock()
    mock_commit = MagicMock()
    db_mock.query = mock_query
    mock_query.return_value.filter.return_value.update.return_value = 1
    db_mock.commit = mock_commit
    mock_get_db.return_value = db_mock

    result = delete_grower("126", db=db_mock)
    assert result.status_code == 204


"""_________plant_mtrx.py_________"""


def test_get_plant_mtrx():
    response = client.get('/api/plant_mtrx/plant/region_id/8/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_2():
    response = client.get('/api/plant_mtrx/growing_area/all_data/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_3():
    response = client.get('/api/plant_mtrx/plant/company_name/US/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_growing_area():
    response = client.get('/api/plant_mtrx/growing_area/region/8/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_growing_area_2():
    response = client.get('/api/plant_mtrx/growing_area/country/US/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_region():
    response = client.get('/api/plant_mtrx/only_region_data/year/2023')
    assert response.status_code == 200


@patch('database.get_db')
def test_func_getcrop_type(mock_get_db):
    db_mock = mock_get_db.return_value
    mock_query_result = models.growing_area(
        fresh_period_start=1, fresh_week_start=1, fresh_period_end=4, fresh_week_end=8
    )
    db_mock.query().filter().first.return_value = mock_query_result

    test_cases = [{"period": 1, "week": 1, "year": 2023, "growing_area_id": 1,
                   "expected_crop_type": "Fresh", "expected_crop_year": "2023"},
                  {"period": 1, "week": 1, "year": 2023, "growing_area_id": 1,
                   "expected_crop_type": "Storage", "expected_crop_year": "2022-23"},
                  {"period": 5, "week": 5, "year": 2023, "growing_area_id": 1,
                   "expected_crop_type": "Storage", "expected_crop_year": "2023-24"}]

    for case in test_cases:
        crop_type, crop_year = func_getcrop_type(case["period"], case["week"],
                                                 case["year"], case["growing_area_id"])
        assert crop_type == case["expected_crop_type"]
        assert crop_year == case["expected_crop_year"]


@patch('database.get_db')
def test_update_plantMtrx(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_existing_record = MagicMock()
    db_mock.query().filter().first.return_value = mock_existing_record
    func_getcrop_type.return_value = ("Fresh", "2023")

    payload_data = [
        {"plant_matrix_id": 1, "plant_id": 1, "growing_area_id": 1,
         "period": 7, "week": 2, "year": 2023, "value": 50}]

    payload_plant_mtrx = schemas.PlantMtrxPayload(data=payload_data)
    result = update_plantMtrx(MagicMock(data=payload_plant_mtrx), db=db_mock)

    assert result["status"] == "success"

# """________plantGrowingMapping.py_________"""
#
#
# def test_get_plant_growing():
#     response = client.get('/api/plant-growing-mapping/')
#     assert response.status_code == 200
#
#
# def test_get_plants():
#     response = client.get('/api/plant-growing-mapping/17')
#     assert response.status_code == 200
#
#
# def test_get_plant_growing_area():
#     response = client.get('/api/plant-growing-mapping/285/pid=17')
#     assert response.status_code == 200
#
#
# def test_get_plant_id():
#     response = client.get('/api/plant-growing-mapping/17')
#     assert response.status_code == 200
#
#
# def test_get_plant_growing_id():
#     response = client.get('/api/plant-growing-mapping/44/pid=17')
#     assert response.status_code == 200
#
#
# @patch('database.get_db')
# def test_delete_plant_growing(mock_get_db):
#     db_mock = MagicMock()
#     mock_query = MagicMock()
#     mock_commit = MagicMock()
#     db_mock.query = mock_query
#     mock_query.return_value.filter.return_value.update.return_value = 1
#     db_mock.commit = mock_commit
#     mock_get_db.return_value = db_mock
#
#     result = delete_plant_growing("1", db=db_mock)
#     assert result.status_code == 204
