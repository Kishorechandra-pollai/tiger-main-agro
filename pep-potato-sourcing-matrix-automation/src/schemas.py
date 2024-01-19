from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PlantSchema(BaseModel):
    plant_id: int
    plant_code: str
    plant_name: str
    company_name: Optional[str] = None
    region_id: int
    status: str
    crop_category_id: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GrowingAreaSchema(BaseModel):
    growing_area_id: int
    growing_area_name: str
    region: int
    country: str
    status: str
    growing_area_desc: Optional[str] = None
    fresh_period_start: Optional[int] = None
    fresh_week_start: Optional[int] = None
    fresh_period_end: Optional[int] = None
    fresh_week_end: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

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
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Region(BaseModel):
    region_name: str
    country: str
    status: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PlantGrowingMappingSchema(BaseModel):
    plant_id: int
    growing_area_id: int


class ActiveAllocation(BaseModel):
    allocation_id: str
    category_name: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    period: Optional[int] = None
    value: Optional[str] = None

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
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OwnershipGrowerGrowingSchema(BaseModel):
    """Class representing schema for ownership_grower_growing_area_mapping table"""
    row_id: str
    growing_area_id: Optional[int] = None
    grower_id: Optional[int] = None
    contract: Optional[int] = None
    year: Optional[int] = None
    shrinkage: Optional[float] = None
    contract_erp: Optional[float] = None
    ownership_id: str
    crop_type: Optional[str] = None
    crop_year: str
    status: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UpdateOwnershipGrowerGrowing(BaseModel):
    PayloadOwnership: List[OwnershipGrowerGrowingSchema]


class Pcusage(BaseModel):
    pcusage_id: str
    year: int
    period: int
    week_no: int
    plant_id: int
    forecasted_value: float
    country: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PlantSiteGrowingAreaMappingSchema(BaseModel):
    """Class representing schema for plant_site_growing_area_mapping table"""
    row_id: int
    vendor_site_code: str
    growing_area_code: str
    plant_name: str
    vendor_site_id: int
    plant_id: int
    growing_area_id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightCostRateSchema(BaseModel):
    """Class representing schema for freight_cost_rate table"""
    currency: Optional[str] = None
    comment: Optional[str] = None
    year: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightCostMappingSchema(BaseModel):
    """Class representing schema for freight_cost_mapping table"""
    year: Optional[int] = None
    rate: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OwnershipSchema(BaseModel):
    """Class representing schema for ownership table"""
    ownership_id: str
    growing_area_id: int
    contract: int
    contract_erp_value: Optional[int] = None
    shrinkage: float
    to_ship: int
    crop_type: str
    crop_year: str
    market_and_flex: Optional[int] = None
    total_ship: Optional[int] = None
    year: Optional[int] = None
    extension: Optional[float] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class PlantMatrix(BaseModel):
    plant_matrix_id: str
    plant_id: Optional[int] = None
    year: Optional[int] = None
    period: Optional[int] = None
    region_id: Optional[int] = None
    week: Optional[int] = None
    growing_area_id: Optional[int] = None
    value: Optional[float] = None
    crop_type: Optional[str] = None
    crop_year: Optional[str] = None
    status: Optional[str] = None

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


class VendorSiteCodeSchema(BaseModel):
    VENDOR_SITE_CODE: Optional[int] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    status: Optional[str] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    region_id: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class SolidRatesSchema(BaseModel):
    year: Optional[int] = None
    growing_area_id: Optional[int] = None
    currency: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


class PotatoRatesSchema(BaseModel):
    year: Optional[int] = None
    growing_area_id: Optional[int] = None
    currency: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


class potatoRateMappingSchema(BaseModel):
    __tablename__ = "potato_rate_mapping"
    period: Optional[int] = None
    potato_rate_id: Optional[int] = None
    week: Optional[int] = None
    p_year: Optional[int] = None
    rate: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class potatoRateMappingPayload(BaseModel):
    data: List[potatoRateMappingSchema]


class solidRateMappingSchema(BaseModel):
    __tablename__ = "solid_rate_mapping"
    period: Optional[int] = None
    solids_rate_id: Optional[int] = None
    rate: Optional[float] = None
    period_year: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class solidRateMappingPayload(BaseModel):
    data: List[solidRateMappingSchema]


class OffContractInfoSchema(BaseModel):
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OffContractTaskMappingSchema(BaseModel):
    period: Optional[int] = None
    off_contract_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OffContractTaskMappingPayload(BaseModel):
    data: List[OffContractTaskMappingSchema]


class FreightTaskInfoSchema(BaseModel):
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightTaskMappingsSchema(BaseModel):
    period: Optional[int] = None
    freight_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightTaskMappingsPayload(BaseModel):
    data: List[FreightTaskMappingsSchema]


class GeneralAdministrativeTaskSchema(BaseModel):
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GeneralAdministrativeMappingsSchema(BaseModel):
    period: Optional[int] = None
    general_administrative_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GeneralAdministrativeMappingsPayload(BaseModel):
    data: List[GeneralAdministrativeMappingsSchema]


class ExtensionMappingSchema(BaseModel):
    """Class representing schema for extension_ownership_mapping table"""
    extension_id: str
    growing_area_id: Optional[int] = None
    period: Optional[int] = None
    week: Optional[int] = None
    crop_type: Optional[str] = None
    crop_year: Optional[str] = None
    total_value: Optional[float] = None
    split: str
    status: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ExtensionOwnershipPayload(BaseModel):
    ExtensionData: List[ExtensionMappingSchema]


class PriceVarianceMappingSchema(BaseModel):
    period: Optional[int] = None
    price_variance_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PriceVarianceMappingPayload(BaseModel):
    data: List[PriceVarianceMappingSchema]


class InflationDeflationMappingSchema(BaseModel):
    period: Optional[int] = None
    inflation_deflation_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class InflationDeflationMappingPayload(BaseModel):
    data: List[InflationDeflationMappingSchema]


class p4pMasterInfoSchema(BaseModel):
    p4p_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class p4pTaskMappingsSchema(BaseModel):
    period: Optional[int] = None
    p4p_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class p4pTaskMappingsPayload(BaseModel):
    data: List[p4pTaskMappingsSchema]


class TaskItemDataObject(BaseModel):
    plan: int
    actuals: int


class TaskItemPayload(BaseModel):
    taskId: int
    solids: TaskItemDataObject
    defects: TaskItemDataObject


class MarketFlexMappingSchema(BaseModel):
    row_id: str
    growing_area_id: Optional[int] = None
    grower_id: Optional[int] = None
    ownership_id: Optional[str] = None
    status: Optional[str] = None
    market_flex_value: Optional[int] = None

class SolidTaskMasterSchema(BaseModel):
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class MarketFlexPayload(BaseModel):
    Payload_MarketFlex: List[MarketFlexMappingSchema]


class SolidsTaskMappingSchema(BaseModel):
    period: Optional[int] = None
    solids_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    country_code: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class SolidsTaskMappingSchemaPayload(BaseModel):
    data: List[SolidsTaskMappingSchema]


class CountryDivisionNameName(BaseModel):
    division_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None


class PlantMtrxTemplateSchema(BaseModel):
    period: Optional[int] = None
    plant_id: Optional[int] = None
    week: Optional[int] = None
    growing_area_id: Optional[int] = None


class planVolumeUsageSchema(BaseModel):
    __tablename__ = "plan_volume_usage"
    plan_volume_id: str
    crop_type: Optional[int] = None
    period: Optional[int] = None
    week: Optional[int] = None
    year: Optional[int] = None
    volume: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class planVolumeUsagePayload(BaseModel):
    data: List[planVolumeUsageSchema]
