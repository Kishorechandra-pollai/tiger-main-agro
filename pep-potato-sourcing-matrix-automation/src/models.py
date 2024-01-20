from sqlalchemy import FLOAT
from sqlalchemy import TIMESTAMP, Column, String, ForeignKey, Integer, Float, MetaData
from sqlalchemy.sql import func
from database import engine
import sqlalchemy as db
from database import Base

metadata = MetaData()


class Plant(Base):
    __tablename__ = 'plant'

    plant_id = Column(Integer(), primary_key=True, autoincrement=True)
    plant_code = Column(String, nullable=False)
    plant_name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    region_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    crop_category_id = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class growing_area(Base):
    __tablename__ = 'growing_area'

    growing_area_id = Column(Integer(), primary_key=True, autoincrement=True)
    growing_area_name = Column(String, nullable=False)
    region = Column(Integer(), nullable=True)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    growing_area_desc = Column(String, nullable=True)
    fresh_period_start = Column(Integer(), nullable=True)
    fresh_week_start = Column(Integer(), nullable=True)
    fresh_period_end = Column(Integer(), nullable=True)
    fresh_week_end = Column(Integer(), nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class growers(Base):
    __tablename__ = 'growers'

    grower_id = Column(Integer(), primary_key=True, autoincrement=True)
    grower_name = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    region = Column(Integer(), nullable=True)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    volume = Column(String, nullable=True)

    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class preferred_grower(Base):
    __tablename__ = 'grower_growing_area_mapping'

    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    grower_name = Column(String, nullable=True)
    grower_id = Column(Integer, nullable=True)
    growing_area_id = Column(Integer, nullable=True)


class region(Base):
    __tablename__ = 'region'

    region_id = Column(Integer(), primary_key=True, autoincrement=True)
    region_name = Column(String, nullable=False)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class plant_growing_area_mapping(Base):
    __tablename__ = 'plant_growing_area_mapping'
    plant_mapping_id = Column(Integer(), primary_key=True, autoincrement=True)
    plant_id = Column(Integer(), nullable=True)
    growing_area_id = Column(Integer(), nullable=True)


class category(Base):
    __tablename__ = 'crop_category'

    crop_category = Column(Integer(), primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class allocation(Base):
    __tablename__ = 'active_allocation'

    allocation_id = Column(String, primary_key=True)
    category_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    country = Column(String, nullable=True)
    period = Column(Integer, nullable=False)
    value = Column(Float, nullable=True)


class pcusage(Base):
    __tablename__ = 'pc_usage'

    pcusage_id = Column(String, primary_key=True)
    year = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    week_no = Column(Integer, nullable=False)
    plant_id = Column(String, nullable=True)
    forecasted_value = Column(Float, nullable=True)
    country = Column(String, nullable=True)


class OwnershipGrowerGrowing(Base):
    __tablename__ = 'ownership_grower_growing_area_mapping'

    row_id = Column(String, primary_key=True)
    growing_area_id = Column(Integer(), nullable=False)
    grower_id = Column(Integer(), nullable=False)
    contract = Column(Integer(), nullable=True)
    year = Column(Integer(), nullable=True)
    shrinkage = Column(FLOAT, nullable=True)
    contract_erp = Column(FLOAT, nullable=True)
    ownership_id = Column(String, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=False)
    status = Column(Integer(), nullable=True)


class PlantSiteGrowingAreaMapping(Base):
    """Class representing plant_site_growing_area_mapping table"""
    __tablename__ = 'plant_site_growing_area_mapping'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    vendor_site_code = Column(String, nullable=False)
    growing_area_code = Column(String, nullable=False)
    plant_name = Column(String, nullable=False)
    vendor_site_id = Column(Integer(), nullable=False)
    plant_id = Column(Integer(), nullable=False)
    growing_area_id = Column(Integer(), nullable=False)


class FreightCostRate(Base):
    """Class representing freight_cost_rate table"""
    __tablename__ = "freight_cost_rate"

    freight_cost_id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    plant_id = Column(Integer(), ForeignKey("plant_site_growing_area_mapping.plant_id"))
    growing_area_id = Column(Integer(), ForeignKey("plant_site_growing_area_mapping.growing_area_id"))
    vendor_site_id = Column(Integer(), ForeignKey("plant_site_growing_area_mapping.vendor_site_id"))
    #year = Column(Integer, index=True, nullable=False)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())

class FreightCostMapping(Base):
    """Class representing freight_cost_mapping table"""
    __tablename__ = "freight_cost_mapping"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    freight_cost_id = Column(Integer, nullable=False)
    year = Column(Integer, index=True, nullable=False)
    period = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)


class Ownership(Base):
    __tablename__ = 'ownership'

    ownership_id = Column(String, primary_key=True)
    growing_area_id = Column(Integer(), nullable=False)
    contract = Column(Float, nullable=False)
    shrinkage = Column(Float, nullable=True)
    to_ship = Column(Float, nullable=True)
    market_and_flex = Column(Integer(), nullable=True)
    total_ship = Column(Float, nullable=True)
    extension = Column(Integer(), nullable=True)
    contract_erp_value = Column(Float, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=True)
    year = Column(Integer(), nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class vendor_site_code(Base):
    __tablename__ = "vendor_site_code"

    VENDOR_SITE_ID = Column(Integer(), primary_key=True, autoincrement=True)
    VENDOR_SITE_CODE = Column(Integer, nullable=False)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    status = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    region_id = Column(Integer, nullable=False)


View_site_plant_growing_area_mapping = db.Table('View_site_plant_growing_area_mapping', metadata, autoload=True,
                                                autoload_with=engine)
view_plant_growing_area_Alice = db.Table('View_plant_growing_area', metadata, autoload=True, autoload_with=engine)
view_growing_area_mapping_Alice = db.Table('view_growing_area_mapping', metadata, autoload=True, autoload_with=engine)


class solids_rates(Base):
    __tablename__ = "solids_rates"
    solids_rate_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    growing_area_id = Column(Integer, nullable=True)
    growing_area_id_old = Column(Integer, nullable=True)
    currency = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class potato_rates(Base):
    __tablename__ = "potato_rates"
    potato_rate_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=True)
    growing_area_id = Column(Integer, nullable=True)
    growing_area_id_old = Column(Integer, nullable=True)
    currency = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class plantMtrx(Base):
    __tablename__ = "plant_matrix_growing_area"

    plant_matrix_id = Column(String, primary_key=True, nullable=False)
    plant_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    period = Column(Integer, nullable=True)
    week = Column(Integer, nullable=True)
    region_id = Column(Integer, nullable=True)
    growing_area_id = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=True)
    status = Column(String, nullable=True)


View_PlantMtrx_table = db.Table('View_PlantMtrx_table', metadata, autoload=True, autoload_with=engine)
View_PlantMtrx_position = db.Table('View_PlantMtrx_position', metadata, autoload=True, autoload_with=engine)
View_plant_matrix_actual = db.Table('View_plant_matrix_actual', metadata, autoload=True, autoload_with=engine)
View_Matrix_growingarea = db.Table('View_Matrix_growingarea', metadata, autoload=True, autoload_with=engine)


class plantMtrx_template(Base):
    __tablename__ = "plant_mtrx_template"

    plant_id = Column(String, nullable=True, primary_key=True)
    period = Column(Integer, nullable=True)
    week_no = Column(Integer, nullable=True)
    growing_area_id = Column(String, nullable=True)


View_forecast_pcusage = db.Table('View_forecast_pcusage', metadata, autoload=True, autoload_with=engine)

View_Ownership = db.Table('View_Ownership', metadata, autoload=True, autoload_with=engine)
View_OwnershipMetrics_region = db.Table('View_OwnershipMetrics_region', metadata, autoload=True, autoload_with=engine)
View_OwnershipMetrics_all = db.Table('View_OwnershipMetrics_all', metadata, autoload=True, autoload_with=engine)
View_OwnershipMetrics_country = db.Table('View_OwnershipMetrics_country', metadata, autoload=True, autoload_with=engine)
View_growing_area_contract_erp = db.Table('View_growing_area_contract_erp', metadata, autoload=True,
                                          autoload_with=engine)
View_total_sum_growing_area = db.Table('View_total_sum_growing_area', metadata, autoload=True, autoload_with=engine)


class potato_rate_mapping(Base):
    __tablename__ = "potato_rate_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    potato_rate_id = Column(Integer, nullable=True)
    week = Column(Integer, nullable=True)
    rate = Column(Float, nullable=True)
    p_year = Column(Integer, nullable=True)

class solid_rate_mapping(Base):
    __tablename__ = "solid_rate_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    solids_rate_id = Column(Integer, nullable=True)
    rate = Column(Float, nullable=True)
    period_year = Column(Integer, nullable=True)


class off_contract_info(Base):
    __tablename__ = "off_contract_info"
    off_contract_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class off_contract_task_mapping(Base):
    __tablename__ = "off_contract_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    off_contract_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class freight_task_info(Base):
    __tablename__ = "freight_task_info"
    freight_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class freight_task_mappings(Base):
    __tablename__ = "freight_task_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    freight_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class general_administrative_task(Base):
    __tablename__ = "general_administrative_task"
    general_administrative_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class general_administrative_mappings(Base):
    __tablename__ = "general_administrative_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    general_administrative_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class p4p_master_info(Base):
    __tablename__ = "p4p_master_info"
    p4p_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    p4p_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class p4p_task_mappings(Base):
    __tablename__ = "p4p_task_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    p4p_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class ExtensionOwnershipMapping(Base):
    __tablename__ = 'extension_ownership_mapping'

    extension_id = Column(String, nullable=False, primary_key=True)
    growing_area_id = Column(Integer(), nullable=True)
    period = Column(Integer(), nullable=True)
    week = Column(Integer(), nullable=True)
    total_value = Column(Float, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=True)
    year = Column(String, nullable=True)
    split = Column(String, nullable=True)
    status = Column(String, nullable=True)


class price_variance_task(Base):
    __tablename__ = "price_variance_task"
    price_variance_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class price_variance_task_mapping(Base):
    __tablename__ = "price_variance_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    price_variance_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class inflation_deflation_task(Base):
    __tablename__ = "inflation_deflation_task"
    inflation_deflation_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class inflation_deflation_task_mappings(Base):
    __tablename__ = "inflation_deflation_task_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    inflation_deflation_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)




freight_cost_period_table = db.Table('View_freight_cost_period_combine', metadata, autoload=True, autoload_with=engine)
freight_cost_period_week_table = db.Table('View_freight_cost_week_view_combine', metadata, autoload=True, autoload_with=engine)
rate_growing_area_table = db.Table('View_freight_plan_actual_combine', metadata, autoload=True, autoload_with=engine)
View_p4p_result_table = db.Table('View_p4p_result', metadata, autoload=True, autoload_with=engine)
potato_rate_table_period = db.Table('View_potato_pricing_combine_period', metadata, autoload=True, autoload_with=engine)
potato_rate_table_weekly = db.Table('View_potato_rates_period_week', metadata, autoload=True, autoload_with=engine)
solids_rate_table_period = db.Table('View_solid_plan_actual_combine_rate', metadata, autoload=True, autoload_with=engine)
dashboard_pc_volume_period = db.Table('View_dashboard_pc_volume_ratio', metadata, autoload=True, autoload_with=engine)
dashboard_weekly_combine = db.Table('View_dashboard_weekly_combine', metadata, autoload=True, autoload_with=engine)
dashboard_pc_usage_period= db.Table('View_dashboard_pc_usage_period',metadata, autoload=True, autoload_with=engine)
dashboard_pc_volume_period_country_combine = db.Table('View_dashboard_pc_volume_period_country_combine',
                                                     metadata, autoload=True, autoload_with=engine)
dashboard_pc_volume_period_country_yearly = db.Table('View_dashboard_pc_volume_period_country_yearly',
                                                     metadata, autoload=True, autoload_with=engine)
dashboard_pc_volume_yearly_country_combine = db.Table('View_dashboard_pc_volume_yearly_country_combine',
                                                      metadata, autoload=True, autoload_with=engine)
summary_solids = db.Table('View_solid_summary',metadata, autoload=True, autoload_with=engine)
summary_price_variance= db.Table('View_SUMMARY_PRICE_VARAINCE',metadata, autoload=True, autoload_with=engine)
summary_overall_cost = db.Table('View_summary_UNION_OVERALL',metadata, autoload=True, autoload_with=engine)
summary_total_exp_wo_solids = db.Table('view_summary_union_TOTAL_EXP_Without_Solids',metadata, autoload=True, autoload_with=engine)
summary_total_exp_w_solids = db.Table('view_summary_union_TOTAL_EXP_With_Solids',metadata, autoload=True, autoload_with=engine)
summary_material_spend = db.Table('view_summary_union.Material_spend',metadata, autoload=True, autoload_with=engine)
summary_freight_spend = db.Table('view_summary_union.Freight_spend',metadata, autoload=True, autoload_with=engine)
summary_overall_cost_solids = db.Table('view_summary_union.Solids_Impact$',metadata, autoload=True, autoload_with=engine)
summary_category_spend = db.Table('view_summary_union.Category_Spend',metadata, autoload=True, autoload_with=engine)
inflation_deflation_material = db.Table('view_summary_Material',metadata, autoload=True, autoload_with=engine)
inflation_deflation_freight = db.Table('view_summary_Freight',metadata, autoload=True, autoload_with=engine)

class MarketFlexMapping(Base):
    __tablename__ = 'ownership_grower_growing_area_market_area_mapping'
    row_id = Column(String, nullable=False, primary_key=True)
    growing_area_id = Column(Integer(), nullable=True)
    grower_id = Column(Integer(), nullable=True)
    ownership_id = Column(String, nullable=True)
    status = Column(String, nullable=True)
    market_flex_value = Column(Integer(), nullable=True)


View_p4p_result_table = db.Table('View_p4p_summary', metadata, autoload=True, autoload_with=engine)
View_p4p_result_update = db.Table('View_p4p_result_update', metadata, autoload=True, autoload_with=engine)


class solid_task_master(Base):
    __tablename__ = "solid_task_master"
    solids_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    order_position = Column(Integer, nullable=True)


class solids_task_mapping(Base):
    __tablename__ = "solids_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    solids_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    country_code = Column(String, nullable=True)


class country_division_name(Base):
    __tablename__ = "country_division_name"
    division_name_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    division_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class pc_plan_volume_usage(Base):
    """Class representing plan_volume_usage table"""
    __tablename__ = "plan_volume_usage"
    plan_volume_id = Column(String, nullable=False, primary_key=True)
    crop_type = Column(Integer, nullable=True)
    period = Column(Integer, nullable=True)
    week = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    volume = Column(Integer, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())