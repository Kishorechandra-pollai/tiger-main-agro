from datetime import datetime
from typing import List
from pydantic import BaseModel
class PlantSchema(BaseModel):
    plant_id: int
    plant_code: str
    plant_name: str
    company_name: str | None = None
    region_id: int
    #country: str
    status: str
    crop_category_id: int | None = None
    created_time: datetime | None = None
    updated_time: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class GrowingAreaSchema(BaseModel):
    growing_area_id: int
    growing_area_name: str
    site: str
    owner_name: str
    region: int
    country: str
    status: str
    growing_area_desc: str | None = None
    created_time: datetime | None = None
    updated_time: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GrowerSchema(BaseModel):
    grower_name: str
    owner: str
    region: int
    country: str
    status: str
    volume: str
    created_time: datetime | None = None
    updated_time: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Region(BaseModel):
    region_name: str
    country: str
    status: str
    created_time: datetime | None = None
    updated_time: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PlantGrowingMappingSchema(BaseModel):
    plant_id: int
    growing_area_id: int


class ActiveAllocation(BaseModel):
    allocation_id: str
    category_name: str | None = None
    year: int | None = None
    country: str | None = None
    period: int | None = None
    value: float | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class AllocationPayload(BaseModel):
    data: List[ActiveAllocation]


class Category(BaseModel):
    category_name: str
    country: str
    status: str
    created_time: datetime | None = None
    updated_time: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OwnershipGrowerGrowingSchema(BaseModel):
    row_id: int
    growing_area_id: int
    grower_id: int
    contract: int
    year: int
    total_ship: int
    extension: int
    shrinkage: float
    ownership_id: str
    crop_type: str
    crop_year: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UpdateOwnershipGrowerGrowing(BaseModel):
    DataOGG: List[OwnershipGrowerGrowingSchema]


class Pcusage(BaseModel):
    pcusage_id: str
    year: int
    period: int
    week_no: int
    plant_id: int
    forecasted_value: float
    actual_value: str
    # region_id: str
    country: str

    # created_time: datetime | None = None
    # updated_time: datetime | None = None
    # created_by: str | None = None
    # updated_by: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class PlantSiteGrowingAreaMappingSchema(BaseModel):
    """Class representing schema for plant_site_growing_area_mapping table"""
    row_id :int
    vendor_site_code : str
    growing_area_code : str
    plant_name : str
    vendor_site_id : int
    plant_id : int
    growing_area_id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightCostRateSchema(BaseModel):
    """Class representing schema for freight_cost_rate table"""
    currency : str | None = None
    comment : str| None = None
    year: int | None = None
    created_time: datetime | None = None
    updated_time: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightCostMappingSchema(BaseModel):
    """Class representing schema for freight_cost_mapping table"""
    year: int | None = None
    rate : float | None = None
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OwnershipSchema(BaseModel):
    ownership_id: str
    growing_area_id: int
    contract: int
    shrinkage: float
    to_ship: int
    position: int
    market_and_flex: int
    total_ship: int
    year: int
    crop_type: str
    crop_year: str
    created_time: datetime | None = None
    updated_time: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None


class PlantMatrix(BaseModel):
    plant_matrix_id: str
    plant_id: int | None = None
    year: int | None = None
    period: int | None = None
    region_id: int | None = None
    week: int | None = None
    growing_area_id: int| None = None
    value: float | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UpdateOwnership(BaseModel):
    DataContracted: List[OwnershipSchema]


class PlantMtrxPayload(BaseModel):
    data: List[PlantMatrix]


class plantMtrx_template(BaseModel):
    plant_id: int
    period: int
    week_no: int
    growing_area_id: int
    percentage_value: float


class ErpRawDataUsSchema(BaseModel):
    BPA_Number: int | None = None
    AGREED_QUANTITY: int | None = None
    UOM: str | None = None
    REMAINING_QTY: int | None = None
    RECEIVED_QTY: int | None = None
    OUTSTANDING_ORD: float | None = None
    QUANTITY_REJECTED: int | None = None
    CROP_TYPE: str | None = None
    Release_No: int | None = None
    Line_No: int | None = None
    Shipment: int | None = None
    ITEM: int | None = None
    UOM_CODE: str | None = None
    Ship_To_Organization: str | None = None
    SHIP_TO_LOCATION_CODE: str | None = None
    UNIT_PRICE: float | None = None
    QUANTITY: int | None = None
    QUANTITY_RECEIVED: int | None = None
    QUANTITY_CANCELLED: int | None = None
    QUANTITY_REJECTED_1: int | None = None
    QUANTITY_BILLED: int | None = None
    VENDOR_NAME: str | None = None
    VENDOR_SITE_CODE: str | None = None
    BPA_BUYER: str | None = None
    RELEASE_BUYER: str | None = None
    AUTHORIZATION_STATUS: str | None = None
    NEED_BY_DATE: datetime | None = None
    RECEIPT_NUM: int | None = None
    RECEIPT_QUANTITY: int | None = None
    RECEIPT_DATE: datetime | None = None
    UNLOAD_DATE: str | None = None
    SOLID: float | None = None
    TIER: float | None = None
    SHIPPED_DATE: datetime | None = None
    status: str | None = None
    PROCESS_TIME: datetime | None = None
    Plant_Id: int | None = None
    growignarea_id: int | None = None
    Region_Id: int | None = None
    Site_Id: int | None = None
    grower_Id: int | None = None
    spend: float | None = None
    BU: str | None = None
    Unl_Date_Wk_Num: int | None = None
    Unl_Date_PxW: str | None = None
    Rec_Date_wk_num: int | None = None
    Rec_Date_PxW: str | None = None
    Rec_Date_PxW : str | None = None
    crop_year : str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class VendorSiteCodeSchema(BaseModel):
    VENDOR_SITE_CODE: int | None = None
    created_by: str | None = None
    created_time: datetime | None = None
    status: str | None = None
    updated_by: str | None = None
    updated_time: datetime | None = None
    region_id: int | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class SolidRatesSchema(BaseModel):
    year : int | None = None
    growing_area_id : int | None = None
    currency : str | None = None
    created_by : str | None = None
    updated_by : str | None = None
    created_time: datetime | None = None
    updated_time: datetime | None = None

class PotatoRatesSchema(BaseModel):
    year : int | None = None
    growing_area_id : int | None = None
    currency : str | None = None
    created_by : str | None = None
    updated_by : str | None = None
    created_time: datetime | None = None
    updated_time: datetime | None = None

class potatoRateMappingSchema(BaseModel):
    __tablename__ = "potato_rate_mapping"
    period : int | None = None
    potato_rate_id : int | None = None
    week : int | None = None
    rate : float | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class potatoRateMappingPayload(BaseModel):
    data: List[potatoRateMappingSchema]

class solidRateMappingSchema(BaseModel):
    __tablename__ = "solid_rate_mapping"
    period : int | None = None
    solids_rate_id : int | None = None
    rate : float | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class solidRateMappingPayload(BaseModel):
    data: List[solidRateMappingSchema]

class OffContractInfoSchema(BaseModel):
    task_name : str | None = None
    task_desc : str | None = None
    status : str | None = None
    created_by : str | None = None
    created_time : datetime | None = None
    updated_by : str | None = None
    updated_time : datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class OffContractTaskMappingSchema(BaseModel):
    period : int | None = None
    off_contract_task_id : int | None = None
    year : int | None = None
    value : float | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
class OffContractTaskMappingPayload(BaseModel):
    data:List[OffContractTaskMappingSchema]

class FreightTaskInfoSchema(BaseModel):
    task_name : str | None = None
    task_desc : str | None = None
    status : str | None = None
    created_by : str | None = None
    created_time : datetime | None = None
    updated_by : str | None = None
    updated_time : datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightTaskMappingsSchema(BaseModel):
    period : int | None = None
    freight_task_id : int | None = None
    year : int | None = None
    value : float | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightTaskMappingsPayload(BaseModel):
    data: List[FreightTaskMappingsSchema]

class GeneralAdministrativeTaskSchema(BaseModel):
    task_name : str | None = None
    task_desc : str | None = None
    status : str | None = None
    created_by : str | None = None
    created_time : datetime | None = None
    updated_by : str | None = None
    updated_time : datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class GeneralAdministrativeMappingsSchema(BaseModel):
    period : int | None = None
    general_administrative_id : int | None = None
    year : int | None = None
    value : float | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class GeneralAdministrativeMappingsPayload(BaseModel):
    data:List[GeneralAdministrativeMappingsSchema]