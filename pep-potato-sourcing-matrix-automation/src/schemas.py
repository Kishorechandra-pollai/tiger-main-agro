from datetime import datetime, date
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


class ExPlantSchemaDummy(BaseModel):  # pragma: no cover
    plant_name: str
    region_id: int


class UpdatePlantSchema(BaseModel):  # pragma: no cover
    # plant_id: int
    plant_code: str
    plant_name: str
    company_name: Optional[str] = None
    region_id: int
    status: str
    crop_category_id: Optional[int] = None
    pgt_plant_name: str


class PlantSchemaDummy(BaseModel):  # pragma: no cover
    # plant_id: int
    plant_code: str
    plant_name: str
    company_name: Optional[str] = None
    region_id: int
    # status: str
    crop_category_id: Optional[int] = None
    pgt_plant_name: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PlantSiteGrowingAreaMappingDummy(BaseModel):  # pragma: no cover
    plant_name: str
    growing_area: str
    Vendor_Site_Code: str

    # plant_id: int
    # vendor_site_id: int
    # growing_area_id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GrowingAreaDummy(BaseModel):  # pragma: no cover
    ga_status: Optional[str] = "ACTIVE"
    country: str
    ga_desc: str
    fp_start: int
    fp_end: int
    fw_start: int
    fw_end: int
    sp_start: int
    sw_start: int


class VendorSiteCodeDummy(BaseModel):  # pragma: no cover
    vsc_status: Optional[str] = "ACTIVE"


class MastersMapping(BaseModel):  # pragma: no cover
    plant: PlantSchemaDummy
    psga_map: PlantSiteGrowingAreaMappingDummy
    growing_area: GrowingAreaDummy
    vsc: VendorSiteCodeDummy


class MastersMappingExPlant(BaseModel):
    plant: ExPlantSchemaDummy
    psga_map: PlantSiteGrowingAreaMappingDummy
    growing_area: GrowingAreaDummy
    vsc: VendorSiteCodeDummy


class UpdateGrowingAreaSchema(BaseModel):
    # growing_area_id: int
    growing_area_name: str
    region: int
    country: str
    status: str
    growing_area_desc: Optional[str] = None
    fresh_period_start: Optional[int] = None
    fresh_week_start: Optional[int] = None
    fresh_period_end: Optional[int] = None
    fresh_week_end: Optional[int] = None
    storage_period_start: Optional[int] = None
    storage_week_start: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    pgt_growing_area: str


class GrowingAreaSchemaMasters(BaseModel):
    # growing_area_id: int
    growing_area_name: str
    region: int
    country: str
    # status: str
    growing_area_desc: Optional[str] = None
    fresh_period_start: Optional[int] = None
    fresh_week_start: Optional[int] = None
    fresh_period_end: Optional[int] = None
    fresh_week_end: Optional[int] = None
    storage_period_start: Optional[int] = None
    storage_week_start: Optional[int] = None
    pgt_growing_area: str
    # created_time: Optional[datetime] = None
    # updated_time: Optional[datetime] = None
    # created_by: Optional[str] = None
    # updated_by: Optional[str] = None


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


class edit_gr_grarea_masters(BaseModel):
    grower_name: str
    grower_id: int
    growing_area_name: List[str]
    growing_area_id: List[int]


class GrowersDummy(BaseModel):  # pragma: no cover
    grower_name: str
    owner: str
    region: int
    country: str
    status: str
    volume: int
    grower_abbreviation_code: str
    pgt_grower_name: str

class GrowersDummyMulti(BaseModel):  # pragma: no cover
    grower_name: str
    owner: str
    region: int
    country: str
    status: str
    volume: int
    grower_abbreviation_code: str
    pgt_grower_name: str
    is_parent: str
    master_id: int


class GrAreaMapDummy(BaseModel):  # pragma: no cover
    growing_area_name: List[str]


class MastersMappingGrowers(BaseModel):  # pragma: no cover
    growers: GrowersDummy
    gr_area_map: GrAreaMapDummy


class ExGrowersDummy(BaseModel):  # pragma: no cover
    grower_name: str
    ex_growing_area_name: str
    new_growing_area_name: str


class MastersMappingExGrowers(BaseModel):  # pragma: no cover
    growers_gr_area: ExGrowersDummy


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


class UpdateRegion(BaseModel):
    region: str
    country: Optional[str] = None
    status: Optional[str] = None
    updated_time: Optional[datetime] = None
    updated_by: Optional[str] = None


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
    market: Optional[float] = None
    flex: Optional[float] = None
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


class EditPSGAMastersSchema(BaseModel):
    plant_name: str
    plant_id: int
    growing_area: List[str]
    vsc: List[str]
    ga_id: List[int]
    vs_id: List[int]

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


class FreightCostRatesSchema(BaseModel):
    """Class representing schema for freight_cost_rates table"""
    plant_id: Optional[int] = None
    growing_area_id: Optional[int] = None
    vendor_site_id: Optional[int] = None
    currency: Optional[str] = None
    comment: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

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
    final_extension: Optional[float] = None

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


class VendorSiteCodeSchemaMasters(BaseModel):
    VENDOR_SITE_CODE: Optional[str] = None
    # created_by: Optional[str] = None
    # created_time: Optional[datetime] = None
    # status: Optional[str] = None
    # updated_by: Optional[str] = None
    # updated_time: Optional[datetime] = None
    region_id: Optional[int] = None
    pgt_vsc: str


class UpdateVendorSiteCodeSchema(BaseModel):
    VENDOR_SITE_CODE: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    status: Optional[str] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    region_id: Optional[int] = None
    pgt_vsc: str


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
    

class FreightTaskPlanInfoSchema(BaseModel):
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


class FreightTaskPlanMappingsSchema(BaseModel):
    period: Optional[int] = None
    freight_task_plan_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightTaskPlanMappingsPayload(BaseModel):
    data: List[FreightTaskPlanMappingsSchema]


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
    
class GeneralAdministrativePlanTaskSchema(BaseModel):
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


class GeneralAdministrativePlanMappingsSchema(BaseModel):
    period: Optional[int] = None
    general_administrative_plan_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GeneralAdministrativePlanMappingsPayload(BaseModel):
    data: List[GeneralAdministrativePlanMappingsSchema]


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
    year: int
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
    order_position: Optional[int] = None

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


class UserInfoSchema(BaseModel):
    email: Optional[str] = None
    country: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_status: Optional[bool] = None
    is_admin: Optional[bool] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class EditActiveStatusSchema(BaseModel):
    email: Optional[str] = None
    user_status: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
class NewUserInfoSchema(BaseModel):
    email: Optional[str] = None
    page_name: Optional[str] = None
    access_name: Optional[str] = None
    country_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class NewUserInfoPayload(BaseModel):
    data: List[NewUserInfoSchema]        

class UserCreationPayload(BaseModel):
    email: Optional[str] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UpdateUserInfoSchema(BaseModel):
    email: Optional[str] = None
    page_name: Optional[str] = None
    access_name: Optional[str] = None
    country_name: Optional[str] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UpdateUserInfoPayload(BaseModel):
    data: List[UpdateUserInfoSchema] 


class CountryInfoSchema(BaseModel):
    country_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class AccessInfoSchema(BaseModel):
    access_name: Optional[str] = None
    access_value: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PageInfoSchema(BaseModel):
    page_name: Optional[str] = None
    page_description: Optional[str] = None
    page_status: Optional[bool] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    is_read_only:Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UserlogSchema(BaseModel):
    email: str
    date_time: datetime
    date: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ExportExcelPayloadSchema(BaseModel): # pragma: no cover
    Payload_ID: int
    Payload: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
    

class ExportExcelFinanceSummarySolids(BaseModel): # pragma: no cover
    solids:str
    P1:Optional[float] = None
    P2:Optional[float] = None
    P3:Optional[float] = None
    P4:Optional[float] = None
    P5:Optional[float] = None
    P6:Optional[float] = None
    P7:Optional[float] = None
    P8:Optional[float] = None
    P9:Optional[float] = None
    P10:Optional[float] = None
    P11:Optional[float] = None
    P12:Optional[float] = None
    P13:Optional[float] = None
    Total:str

   

class ExportExcelFinanceSummarySolidsList(BaseModel): # pragma: no cover
    data: List[ExportExcelFinanceSummarySolids]

class ExportExcelBigJSON(BaseModel): # pragma: no cover
    growing_area_name: str
    growing_area_id: int
    period: int
    period_with_P: str
    week: int
    year: int
    total_value: float

class ExportExcelBigJSONList(BaseModel): # pragma: no cover
    data: List[ExportExcelBigJSON]