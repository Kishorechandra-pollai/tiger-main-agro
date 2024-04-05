import sys
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(r"..\src\main.py")
# sys.path.append(r"..\pep-potato-sourcing-matrix-automation\src")
sys.path.append("src/")
sys.path.append("../")
sys.path.append("../src/")
from main import app
import models
import schemas
from plants import create_plant
from ownership import Create_new_Ownership, update_ownership_contract_erp
from extensionMapping import update_extension_mapping, update_extension_plantMtrx
from MarketFlexMapping import update_Market_flex, filtered_market_year
from OwnershipGrowerGrowing import (update_contract_erp, delete_post, create_grower_growing_area_mapping)
from allocation import (update_allocation, create_allocation, get_all_plants, update_only_allocation)
from pcusage import create_new_pcusage
from plant_mtrx import (update_plantMtrx, func_getcrop_type, update_extension, get_plantMtrx_common)
# from plantGrowingMapping import create_plant_growing_area_mapping, delete_plant_growing
from growingarea import create_growing_area, delete_growing_area
from growers import delete_grower, create_growers
from category import delete_category, create_category
from solidrates import (update_solid_rates_records)
from potatorates import (update_potato_rates_records)
from offcontractinfo import (create_off_contract_task_mapping_for_year, update_off_contract,
                             create_off_contract_info, create_off_contract_task_mapping,
                             update_off_contract_records)
from region import delete_region, create_region
from p4p_master_info import (create_p4p_task_mappings_info, create_p4p_task_mappings,
                             update_p4p_task_mappings_records)
from generaladministrative import (update_general_administrative_mappings, create_general_administrative_task,
                                   update_general_administrative_records)
from freighttaskinfo import (update_freight_task_mapping_records)

client = TestClient(app)

"""________dashboard.py_________"""


def test_dashboard_pc_volume_period_view_1():
    response = client.get('/api/dashboard/dashboard_pc_volume_period')
    assert response.status_code == 200


def test_dashboard_pc_volume_period_year_2():
    response = client.get('/api/dashboard/dashboard_pc_volume_period/2023')
    assert response.status_code == 200


def test_dashboard_pc_plan_volume_usage_3():
    response = client.get('/api/dashboard/dashboard_pc_plan_volume_usage')
    assert response.status_code == 200


def test_dashboard_pc_plan_volume_usage_year_4():
    response = client.get('/api/dashboard/dashboard_pc_plan_volume_usage/2023')
    assert response.status_code == 200


# def test_dashboard_weekly_combine_view_5():
#     response = client.get('/api/dashboard/dashboard_weekly_combine')
#     assert response.status_code == 200
#
#
# def test_dashboard_weekly_combine_year_6():
#     response = client.get('/api/dashboard/dashboard_weekly_combine/2023')
#     assert response.status_code == 200
#
#
# def test_dashboard_pc_usage_period_view_7():
#     response = client.get('/api/dashboard/pc_usage_period')
#     assert response.status_code == 200
#
#
# def test_dashboard_pc_period_view_year_country_8():
#     response = client.get('/api/dashboard/pc_usage_period view"/2023/CANADA')
#     assert response.status_code == 200
#
#
# def test_pc_volume_period_country_combine_9():
#     response = client.get('/api/dashboard/pc_volume_period_country_combine')
#     assert response.status_code == 200
#
#
# def test_pc_volume_period_country_combine_year_10():
#     response = client.get('/api/dashboard/pc_volume_period_country_combine"/2023')
#     assert response.status_code == 200


# def test_pc_volume_period_country_yearly_11():
#     response = client.get('/api/dashboard/pc_volume_period_country_yearly')
#     assert response.status_code == 200
#
#
# def test_pc_volume_period_country_year_12():
#     response = client.get('/api/dashboard/pc_volume_period_country_yearly"/2023')
#     assert response.status_code == 200


# def test_pc_volume_yearly_country_combine_13():
#     response = client.get('/api/dashboard/pc_volume_yearly_country_combine')
#     assert response.status_code == 200
#
#
# def test_pc_volume_yearly_country_combine_year_14():
#     response = client.get('/api/dashboard/dashboard_pc_volume_yearly_country_combine"/2023')
#     assert response.status_code == 200


"""________OwnershipGrowerGrowing.py_________"""


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
        "market": 0,
        "flex": 0,
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


# @patch('database.get_db')
# def test_mock_update_ownership(mock_get_db):
#     mock_query_result = [(1, 'Storage', '2022-23')]
#     db_mock = MagicMock()
#     db_mock.query().filter().group_by().order_by().all.return_value = mock_query_result
#     mock_get_db.return_value = db_mock
#
#     payload = [{
#         "row_id": "254#170#2022-23",
#         "growing_area_id": 254,
#         "grower_id": 170,
#         "contract": 10,
#         "year": 2023,
#         "shrinkage": 0,
#         "contract_erp": 535.5,
#         "ownership_id": "254#2022-23",
#         "crop_type": "Storage",
#         "crop_year": "2022-23",
#         "status": "INACTIVE"
#     }]
#     test_payload = schemas.UpdateOwnershipGrowerGrowing(PayloadOwnership=payload)
#     result = Update_Ownership(cropyear_input="2022-23", payload=test_payload, db=db_mock)
#     assert result["status"] == "success"


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
        "week": -1,
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


def test_get_plantid():
    response = client.get('/api/plant/10')
    assert response.status_code == 200


def test_get_plants_country_based():
    response = client.get('/api/plant/get_country_company_name/US')
    assert response.status_code == 200


def test_get_plant_region_based():
    response = client.get('/api/plant/get_region/8')
    assert response.status_code == 200


"""________allocation.py_________"""


def test_get_allocation_year():
    response = client.get('/api/allocation/year/2023')
    assert response.status_code == 200


# @patch('database.get_db')
# def test_update_allocation(mock_get_db):
#     db_mock = MagicMock()
#     mock_get_db.return_value = db_mock
#
#     payload = [{
#         "allocation_id": "Co-Man#1#2022",
#         "category_name": "Co-Man",
#         "year": 2022,
#         "country": "USA",
#         "period": 1,
#         "value": 0
#     }]
#     test_payload = schemas.AllocationPayload(data=payload)
#     result = update_allocation(payload=test_payload, db=db_mock)
#
#     assert result["status"] == "success"


@patch('database.get_db')
def test_create_allocation(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    year = 2025

    table_data = [("Co-Man", "USA")]
    db_mock.query().all.return_value = table_data
    result = create_allocation(year=year, db=db_mock)

    assert result == {"Status": "success", "new_records": 13}


@patch('database.get_db')
def test_update_allocation(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_date = date(2023, 1, 1)
    with patch('allocation.date') as mock_date_today:
        mock_date_today.today.return_value = mock_date
        payload_data = [
            {"allocation_id": 1, "value": 100, "year": 2025, "period": 10},
            {"allocation_id": 2, "value": 100, "year": 2025, "period": 13},
            {"allocation_id": 3, "value": 100, "year": 2023, "period": 10}
        ]
        mock_payload = MagicMock(data=payload_data)
        with patch('period_week_calc.calculate_period_and_week') as mock_calculate_period_and_week:
            mock_date_today.today.return_value.year = 2023
            mock_calculate_period_and_week.return_value = {'Period': 3, 'year': 2023}
            update_only_allocation_mock = MagicMock()
            update_forecast_volume_mock = MagicMock()

            with patch('allocation.update_only_allocation',
                       side_effect=update_only_allocation_mock) as mock_update_only_allocation, \
                    patch('allocation.update_forecast_volume',
                          side_effect=update_forecast_volume_mock) as mock_update_forecast_volume:
                result = update_allocation(payload=mock_payload, db=db_mock)

                assert mock_update_only_allocation.call_count == 2
                assert mock_update_forecast_volume.call_count == 2
                assert result["status"] == "success"
                assert result["records_updated"] == 2


"""__________pcusage.py__________"""


def test_get_filtered_usage_company():
    response = client.get('/api/pcusage/company_name/Co-Man/year/2023')
    assert response.status_code == 200


def test_get_filtered_usage_region():
    response = client.get('/api/pcusage/region_id/10/year/2023')
    assert response.status_code == 200


def test_getusage_company_periodwise():
    response = client.get('/api/pcusage/all_week_data/year/2023')
    assert response.status_code == 200


def test_get_usage_period_wise():
    response = client.get('/api/pcusage/period_wise/company_name/Co-Man/year/2023')
    assert response.status_code == 200


def test_get_usage_period_wise_region_wise():
    response = client.get('/api/pcusage/period_wise/region_id/10/year/2023')
    assert response.status_code == 200


def test_get_period_usage_all_data():
    response = client.get('/api/pcusage/all_period_data/year/2023')
    assert response.status_code == 200


# @patch('database.get_db')
# def test_create_new_pcusage(mock_get_db):
#     db_mock = MagicMock()
#     mock_get_db.return_value = db_mock
#     year = 2025
#
#     mock_plants_data = [(44, 10, 1)]  # plants data
#     mock_category_name = [("Co-Man", "FLC")]  # category names
#     mock_index_value = [(2, 0)]  # index values
#     mock_last_year_actual = [(2, 0)]  # last year actual values
#
#     db_mock.query().filter().all.side_effect = [mock_plants_data, mock_category_name, mock_index_value,
#                                                 mock_last_year_actual]
#     result = create_new_pcusage(year=year, db=db_mock)
#
#     assert result == {"status": "success", "message": "New forecast records are generated"}


"""_________growing_area.py_________"""


def test_get_growing_area_1():
    response = client.get('/api/growing-area/')
    assert response.status_code == 200


def test_get_preferred_grower_2():
    response = client.get('/api/growing-area/preferred_grower')
    assert response.status_code == 200


def test_get_growing_area_3():
    response = client.get('/api/growing-area/10')
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


# @patch('database.get_db')
# def test_func_getcrop_type(mock_get_db):
#     db_mock = mock_get_db.return_value
#     mock_query_result = models.growing_area(
#         fresh_period_start=1, fresh_week_start=1, fresh_period_end=4, fresh_week_end=8
#     )
#     db_mock.query().filter().first.return_value = mock_query_result
#
#     test_cases = [{"period": 1, "week": 1, "year": 2023, "growing_area_id": 1,
#                    "expected_crop_type": "Fresh", "expected_crop_year": "2023"},
#                   {"period": 1, "week": 1, "year": 2023, "growing_area_id": 1,
#                    "expected_crop_type": "Storage", "expected_crop_year": "2022-23"},
#                   {"period": 5, "week": 5, "year": 2023, "growing_area_id": 1,
#                    "expected_crop_type": "Storage", "expected_crop_year": "2023-24"}]
#
#     for case in test_cases:
#         crop_type, crop_year = func_getcrop_type(case["period"], case["week"],
#                                                  case["year"], case["growing_area_id"])
#         assert crop_type == case["expected_crop_type"]
#         assert crop_year == case["expected_crop_year"]


# @patch('database.get_db')
# def test_update_plantmtrx(mock_get_db):
#     db_mock = MagicMock()
#     mock_get_db.return_value = db_mock
#     mock_existing_record = MagicMock()
#     db_mock.query().filter().first.return_value = mock_existing_record
#     func_getcrop_type.return_value = ("Fresh", "2023")
#
#     payload_data = [
#         {"plant_matrix_id": 1, "plant_id": 1, "growing_area_id": 1,
#          "period": 7, "week": 2, "year": 2023, "value": 50}]
#
#     payload_plant_mtrx = schemas.PlantMtrxPayload(data=payload_data)
#     result = update_plantMtrx(MagicMock(data=payload_plant_mtrx), db=db_mock)
#
#     assert result["status"] == "success"


@patch('database.get_db')
def test_get_plantMtrx_common(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    filter_conditions = [10]
    name_or_id = "PlantX"
    year = 2023

    mock_position_data = [(1, 'Position1'), (2, 'Position2')]
    mock_plant_mtrx_data = [(1, 'PlantX', 1, 12, 'P12', 3, 2023, 100, 101, 'Area1'),
                            (2, 'PlantX', 2, 12, 'P12', 4, 2023, 150, 102, 'Area2')]
    db_mock.query().filter().all.side_effect = [mock_position_data, mock_plant_mtrx_data]

    result = get_plantMtrx_common(filter_conditions, name_or_id, year, db_mock)
    assert {"status": "success"}


"""______________category.py______________"""


def test_get_category():
    response = client.get('/api/category/')
    assert response.status_code == 200


def test_get_by_categoryid():
    response = client.get('/api/category/1')
    assert response.status_code == 200


def test_get_by_categoryid_exception():
    response = client.get('/api/category/100')
    assert response.status_code == 404


@patch('database.get_db')
def test_delete_category(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query().filter().update.return_value = 1

    result = delete_category(categoryId="1", db=db_mock)
    assert result.status_code == 204


@patch('database.get_db')
def test_create_category(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_category = {
        "category_name": "TEST",
        "country": "US",
        "status": "INACTIVE",
        "created_time": "2024-01-08T08:07:40.901Z",
        "updated_time": "2024-01-08T08:07:40.901Z",
        "created_by": "string",
        "updated_by": "string"
    }
    mock_payload = schemas.Category(**payload_category)
    result = create_category(payload=mock_payload, db=db_mock)
    assert result["status"] == "success"


"""--------solidrates.py---------"""


def test_get_solid_rates():
    response = client.get('/api/solid_rates/')
    assert response.status_code == 200


def test_get_solid_rate_mapping():
    response = client.get('/api/solid_rates/solid_rate_mapping/2024')
    assert response.status_code == 200


def test_getBySolidsRateId():
    response = client.get('/api/solid_rates/getBySolidsRateId/249')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_update_solid_rates_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload = [
        {
            "period": 1,
            "solids_rate_id": 24,
            "rate": 120,
            "period_year": 2023
        }
    ]
    test_payload = schemas.solidRateMappingPayload(data=payload)
    result = update_solid_rates_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"


def test_solid_rate_period_year_region():
    response = client.get('/api/solid_rates/solid_rate_period_year_region/2024/{region}?region_name=US')
    assert response.status_code == 200


"""--------solidrates.py---------"""

"""--------potatorates.py---------"""


def test_get_potato_rates():
    response = client.get('/api/potato_rates/')
    assert response.status_code == 200


def test_get_potato_rate_mapping_data():
    response = client.get('/api/potato_rates/potato_rate_mapping_by_year/2024')
    assert response.status_code == 200


def test_get_potato_rate_mappings():
    response = client.get('/api/potato_rates/get_potato_rate_mapping/2024')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_update_potato_rates_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "potato_rate_id": 241,
            "rate": 120,
            "week": 2
        }
    ]

    test_payload = schemas.potatoRateMappingPayload(data=payload)
    result = update_potato_rates_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"


def potato_rate_period_year_region():
    response = client.get('/api/potato_rates/potato_rate_period_year_region/2024/{region}?region_name=US')
    assert response.status_code == 200


def potato_rate_period_week_year_region():
    response = client.get('/api/potato_rates/potato_rate_period_week_year_region/2024/{region}?region_name=US')
    assert response.status_code == 200



"""--------offcontractinfo.py---------"""


def test_off_contract_info():
    response = client.get('/api/off_contract_info/')
    assert response.status_code == 200


def test_getByoff_contract_task_id():
    response = client.get('/api/off_contract_info/getByoff_contract_task_id/1')
    assert response.status_code == 200


def test_off_contract_task_mapping():
    response = client.get('/api/off_contract_info/off_contract_task_mapping/')
    assert response.status_code == 200


def test_off_contract_task_mapping_by_year():
    response = client.get('/api/off_contract_info/off_contract_task_mapping_by_year/2023/US-CORE')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_create_off_contract_task_mapping_for_year(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    year = 2023
    result = create_off_contract_task_mapping_for_year(year=year, db=db_mock)
    assert result["status"] == "success"


@patch('database.get_db')
def test_mock_create_off_contract_info(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "task_name": "productivity-task",
        "task_desc": "productivity-task",
        "status": "Active",
        "created_by": "System",
        "created_time": "2023-11-10T13:03:23.790000",
        "updated_by": "System",
        "updated_time": "2023-11-10T13:03:23.790000"
    }
    test_ownership_schema = schemas.OffContractInfoSchema(**mapping_payload)
    result = create_off_contract_info(payload=test_ownership_schema, db=db_mock)

    assert result['status'] == 'success'


@patch('database.get_db')
def test_mock_create_off_contract_task_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "period": 1,
        "off_contract_task_id": 1,
        "year": 2023,
        "value": 100,
        "company_name": "US-CORE"
    }
    test_ownership_schema = schemas.OffContractTaskMappingSchema(**mapping_payload)
    result = create_off_contract_task_mapping(payload=test_ownership_schema, db=db_mock)
    assert result['status'] == 'success'


"""--------region.py---------"""


def test_get_region_all():
    response = client.get('/api/region/')
    assert response.status_code == 200


def test_get_regionid():
    response = client.get('/api/region/14')
    assert response.status_code == 200


# def test_get_region_name():
#     response = client.get('/api/region/Canada')
#     assert response.status_code == 200


@patch('database.get_db')
def test_delete_existing_region(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query().filter().update.return_value = 1
    region_id = 8

    response = delete_region(regionId=region_id, db=db_mock)
    assert response.status_code == 204


@patch('database.get_db')
def test_create_region_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = {
        "region_name": "string",
        "country": "string",
        "status": "string",
        "created_time": "2024-01-09T19:03:54.166Z",
        "updated_time": "2024-01-09T19:03:54.166Z",
        "created_by": "string",
        "updated_by": "string"
    }
    region_payload = schemas.Region(**payload)
    result = create_region(payload=region_payload, db=db_mock)
    assert result["status"] == "success"


"""--------p4p_master_info.py---------"""


def test_get_p4p_master_info():
    response = client.get('/api/p4p-master-info/')
    assert response.status_code == 200


def test_get_p4p_master_info_byId():
    response = client.get('/api/p4p-master-info/get_p4p_master_info/1')
    assert response.status_code == 200


def test_get_p4p_task_mappings():
    response = client.get('/api/p4p-master-info/p4p_task_mappings/')
    assert response.status_code == 200


def test_p4p_task_mappings_by_year():
    response = client.get('/api/p4p-master-info/p4p_task_mappings_by_year/2023/US-CORE')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_update_p4p_task_mappings_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "p4p_id": 1,
            "year": 2023,
            "value": 2,
            "company_name": "US-CORE"
        }
    ]

    test_payload = schemas.p4pTaskMappingsPayload(data=payload)
    result = update_p4p_task_mappings_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"


@patch('database.get_db')
def test_mock_create_p4p_task_mappings(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "period": 1,
        "p4p_id": 1,
        "year": 2023,
        "value": 2,
        "company_name": "US-CORE"
    }
    test_schema = schemas.p4pTaskMappingsSchema(**mapping_payload)
    result = create_p4p_task_mappings(payload=test_schema, db=db_mock)

    assert result['status'] == 'success'


@patch('database.get_db')
def test_mock_create_p4p_task_mappings_info(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "p4p_name": "jsadh",
        "description": "jsadh",
        "status": 2023,
        "created_by": "System",
        "updated_by": "System"
    }
    test_schema = schemas.p4pMasterInfoSchema(**mapping_payload)
    result = create_p4p_task_mappings_info(payload=test_schema, db=db_mock)
    assert result['status'] == 'success'


"""--------offcontractinfo.py---------"""


@patch('database.get_db')
def test_mock_update_off_contract_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "off_contract_task_id": 1,
            "year": 2023,
            "value": 2,
            "company_name": "US-CORE"
        }
    ]

    test_payload = schemas.OffContractTaskMappingPayload(data=payload)
    result = update_off_contract_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"


@patch('database.get_db')
def test_update_off_contract_existing_record(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    existing_record_mock = MagicMock()
    existing_record_mock.value = 100
    existing_record_mock.period = 1
    existing_record_mock.year = 2022
    db_mock.query().filter().first.return_value = existing_record_mock
    payload = {
        "period": 1,
        "off_contract_task_id": 1,
        "year": 2023,
        "value": 200,
        "company_name": "US-CORE"
    }
    test_payload = schemas.OffContractTaskMappingSchema(**payload)
    result = update_off_contract(off_contract_task_id=1, payload=test_payload, db=db_mock)
    assert result.value == payload['value']


"""--------freighttaskinfo.py---------"""


def test_freight_task_info():
    response = client.get('/api/freight_task_info/')
    assert response.status_code == 200


def test_getByoff_contract_task_id_2():
    response = client.get('/api/freight_task_info/getByoff_contract_task_id/1')
    assert response.status_code == 200


def test_freight_task_mappings():
    response = client.get('/api/freight_task_info/freight_task_mappings/2023/US-CORE')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_update_freight_task_mapping_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    year = 2023
    result = update_freight_task_mapping_records(year=year, db=db_mock)
    assert result["forYear"] == year


@patch('database.get_db')
def test_mock_create_freight_task_mappings(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "task_name": "productivity-task",
        "task_desc": "productivity-task",
        "status": "Active",
        "created_by": "System",
        "created_time": "2023-11-10T13:03:23.790000",
        "updated_by": "System",
        "updated_time": "2023-11-10T13:03:23.790000"
    }

    test_schema = schemas.FreightTaskInfoSchema(data=mapping_payload)
    result = create_off_contract_info(payload=test_schema, db=db_mock)

    assert result['status'] == 'success'


# @patch('database.get_db')
# def test_mock_update_freight_task_records(mock_get_db):
#     db_mock = MagicMock()
#     mock_get_db.return_value = db_mock
#     payload = [
#         {
#             "period": 1,
#             "off_contract_task_id": 1,
#             "year": 2023,
#             "value": 2,
#             "company_name": "US-CORE"
#         }
#     ]
#
#     test_payload = schemas.OffContractTaskMappingPayload(data=payload)
#     result = update_freight_task_records(payload=test_payload, db=db_mock)
#     assert result["status"] == "success"


"""________generaladministrative.py_________"""


def test_get_freight_task_info():
    response = client.get('/api/general_administrative/')
    assert response.status_code == 200


def test_getBygeneral_administrative_id():
    response = client.get('/api/general_administrative/getBygeneral_administrative_id/1')
    assert response.status_code == 200


def test_get_general_administrative_mappings():
    response = client.get('/api/general_administrative/general_administrative_mappings/')
    assert response.status_code == 200


def test_general_administrative_mappings_by_year():
    response = client.get('/api/general_administrative/general_administrative_mappings_by_year/2023/US-CORE')
    assert response.status_code == 200


@patch('database.db')
def test_update_general_administrative_mappings(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_records = [MagicMock(general_administrative_id=6, task_name='Task 1')]
    mock_all_records = MagicMock(all=MagicMock(return_value=mock_records))
    mock_countries = [MagicMock(task_desc='Country A')]
    db_mock.query.side_effect = [mock_all_records, mock_countries]

    result = update_general_administrative_mappings(year=2023, db=db_mock)
    assert result["status"] == "success"


@patch('database.get_db')
def test_create_general_administrative_task(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_add = MagicMock()
    db_mock.add = mock_add
    mock_commit = MagicMock()
    db_mock.commit = mock_commit

    payload_data = {
        "task_name": "Task1",
        "task_desc": "Task_desc",
        "status": "INACTIVE",
        "created_by": "string",
        "created_time": "2024-01-10T09:48:36.144Z",
        "updated_by": "string",
        "updated_time": "2024-01-10T09:48:36.144Z"
    }
    mock_payload = schemas.GeneralAdministrativeTaskSchema(**payload_data)
    result = create_general_administrative_task(payload=mock_payload, db=db_mock)
    assert result == {"status": "success"}


# @patch('database.get_db')
# def test_create_general_administrative_mappings(mock_get_db):
#     db_mock = MagicMock()
#     mock_get_db.return_value = db_mock
#     mock_add = MagicMock()
#     db_mock.add = mock_add
#     mock_commit = MagicMock()
#     db_mock.commit = mock_commit
#
#     payload_data = {
#         "period": 2,
#         "general_administrative_id": 1,
#         "year": 2025,
#         "value": 0,
#         "company_name": "string"
#     }
#     mock_payload = schemas.GeneralAdministrativeMappingsSchema(**payload_data)
#     result = create_general_administrative_mappings(payload=mock_payload, db=db_mock)
#     assert result == {"status": "success", "general_administrative_id": 1}


@patch('database.get_db')
def test_update_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {"general_administrative_id": 1,
             "period": 2,
             "year": 2023,
             "value": 0,
             "company_name": "test_comp"}
        ]
    }
    test_payload = schemas.GeneralAdministrativeMappingsPayload(**payload_data)
    mock_query = db_mock.query.return_value
    mock_query.filter.return_value.update.return_value = 1
    result = update_general_administrative_records(payload=test_payload, db=db_mock)
    assert result == {"status": "success", "records_updated": 1}


"""________inflation_deflation.py_________"""


def test_get_inflation_deflation_task_mappings():
    response = client.get('/api/inflation_deflation/inflation_deflation_task_mapping')
    assert response.status_code == 200


def test_get_inflation_deflation_task():
    response = client.get('/api/inflation_deflation/inflation_deflation_task')
    assert response.status_code == 200


def test_inflation_deflation_task_mappings_by_year():
    response = client.get('/api/inflation_deflation/inflation_deflation_task_mappings_by_year/2023/CANADA')
    assert response.status_code == 200

def test_inflation_deflation_year_country_code():
    response = client.get('/api/inflation_deflationinflation_deflation/year/2024/company_name/US-CORE')
    assert response.status_code == 200


"""________vendor_site_code.py_________"""


def test_get_view_vendor_site_code():
    response = client.get('/api/vendor_site_code/get_vendor_site_code')
    assert response.status_code == 200


"""________freightcost.py_________"""


def test_view_freight_cost():
    response = client.get('/api/freight-cost/get_freight_cost_rate')
    assert response.status_code == 200


def test_view_freight_mapping_by_year():
    response = client.get('/api/freight-cost/get_freight_cost_mapping/2023')
    assert response.status_code == 200


def test_freight_cost_period_view_year():
    response = client.get('/api/freight-cost/freight_cost_period_view/2024/US')
    assert response.status_code == 200


def test_freight_cost_period_week_view_year():
    response = client.get('/api/freight-cost/freight_cost_period_week_view/2024/US')
    assert response.status_code == 200

def test_get_rate_growing_area_year():
    response = client.get('/api/freight-cost/get_rate_gowing_area/2024')
    assert response.status_code == 200
   
def test_fetch_records():
    response = client.get('/api/freight-cost/fetch_freight_records/2024/US')
    assert response.status_code == 200
    


"""________vendor_site_code.py_________"""


def test_get_view_vendor_site_code():
    response = client.get('/api/vendor_site_code/get_vendor_site_code')
    assert response.status_code == 200


"""________summary_price_variance.py_________"""


def test_get_price_variance_task_mapping():
    response = client.get('/api/summary_price_variance/price_variance_task_mapping')
    assert response.status_code == 200


def test_get_price_variance_task():
    response = client.get('/api/summary_price_variance/price_variance_task')
    assert response.status_code == 200


def test_get_price_variance_task_mapping_by_year():
    response = client.get('/api/summary_price_variance/price_variance_task_mapping_by_year/2023/Canada')
    assert response.status_code == 200


def test_get_total_price_variance():
    response = client.get('/api/summary_price_variance/get_total_price_variance/2023/Canada')
    assert response.status_code == 200
    
"""________user_info.py_________"""
def test_get_user_information():
    response = client.get('/api/user_info/get_user_information')
    assert response.status_code == 200
    
def test_get_user_page_mapping():
    response = client.get('/api/user_info/get_user_page_mapping')
    assert response.status_code == 200

def test_get_user_page_mapping_table():
    response = client.get('/api/user_info/get_user_page_mapping_table?email=John.Perry%40pepsico.com')
    assert response.status_code == 200
        
def test_get_user_information_mapping_view():
    response = client.get('/api/user_info/user_information_mapping_view')
    assert response.status_code == 200
   
"""________page_info.py_________"""
def test_get_page_information():
    response = client.get('/api/page_info/get_page_information')
    assert response.status_code == 200
    
def test_get_country_information():
    response = client.get('/api/page_info/get_country_information')
    assert response.status_code == 200

def test_get_access_type_information():
    response = client.get('/api/page_info/get_access_information')
    assert response.status_code == 200

# """________plantGrowingMapping.py_________"""
#
#
# def test_get_plant_growing():
#     response = client.get('/api/plant-growing-mapping/')
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
