from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
import models
from database import get_db
import pandas as pd
from views_to_pandas import get_dashboard_plant_vol_company,solids_impact,material_forecast_summary, \
    view_summary_Total_freight_forecast,get_view_summary_sum_p4p_task_mappings, \
    view_summary_sum_off_contract_task_mapping, summary_sum_general_administrative,get_vbase_info

router = APIRouter()

@router.get('/material/{year}/{company_name}')
def infl_defl(year:int,company_name:str,db: Session = Depends(get_db)): # pragma: no cover
    def run_sql(table_name,columns):
        query = f"SELECT {columns} FROM {table_name}"
        result = db.execute(query)
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
        return df
    
    ## Loading the tables
    df_plant_matrix_ga = run_sql("plant_matrix_growing_area","*")
    df_plant = run_sql("plant","*")
    df_growing_area = run_sql("growing_area","*")
    df_region = run_sql("region","*")
    df_solids_task_mapp = run_sql("solids_task_mapping","solids_task_id, period, year, value, country_code")
    df_solid_task_master = run_sql("solid_task_master","solids_task_id, task_name")
    df_potato_rate_mapping = run_sql("potato_rate_mapping","p_year,rate, period, week, country_code,potato_rate_id")
    df_potato_rates = run_sql("potato_rates","growing_area_id,potato_rate_id")
    df_plant_matrix_growing_area = run_sql("plant_matrix_growing_area","period, year,growing_area_id, week, plant_id, value")
    freight_task_mappings = run_sql("freight_task_mappings","*")
    p4p_master_info = run_sql("p4p_master_info","*")
    p4p_task_mappings = run_sql("p4p_task_mappings","*")
    View_freight_cp_cat_country_frght_frcst= run_sql("View_freight_cost_period_CATEGORY_COUNTRY_FREIGHT_FORECAST","*")
    df_off_contract_task_mapping = run_sql("off_contract_task_mapping","*")
    ga_mapping = run_sql("general_administrative_mappings","*")

    ## Selecting required columns for material
    df_plant_matl = df_plant[["plant_name", "plant_id", "region_id", "company_name"]]
    df_growing_area_matl = df_growing_area[["growing_area_name", "growing_area_desc", "growing_area_id"]]
    df_region_matl = df_region[["region_id", "country"]]


    df_view_dash = get_dashboard_plant_vol_company(df_plant_matrix_ga,df_plant,df_growing_area,df_region)

    df_solids_impact = solids_impact(df_view_dash,df_solids_task_mapp,df_solid_task_master)
    print("solids impact -> ",df_solids_impact.columns)

    df_View_summary_MATERIAL_FORECAST_pandas = material_forecast_summary(df_potato_rate_mapping, \
                                                                         df_potato_rates,df_plant_matrix_growing_area, \
                                                                            df_plant_matl,df_growing_area_matl,df_region_matl)
    print("summary material forecast -> ",df_View_summary_MATERIAL_FORECAST_pandas.columns)

    df_summary_Total_freight_forecast = view_summary_Total_freight_forecast(freight_task_mappings, View_freight_cp_cat_country_frght_frcst,df_view_dash)
    print("Total_freight_forecast -> ",df_summary_Total_freight_forecast.columns)

    df_summary_sum_p4p_task_mappings, df_p4p_task_mappings_sum_p4p_task_mappings = get_view_summary_sum_p4p_task_mappings(p4p_master_info, p4p_task_mappings,df_view_dash)
    print("summary_sum_p4p_task_mappings -> ",df_summary_sum_p4p_task_mappings.columns)
    print("p4p_task_mappings_sum_p4p_task_mappings -> ",df_p4p_task_mappings_sum_p4p_task_mappings.columns)


    df_summary_sum_off_contract_task_mapping = view_summary_sum_off_contract_task_mapping (df_off_contract_task_mapping,df_view_dash)
    print("summary_sum_off_contract_task_mapping -> ",df_summary_sum_off_contract_task_mapping.columns)

    df_summary_genadm_sum = summary_sum_general_administrative(ga_mapping,df_view_dash)
    print("df_summary_genadm_sum -> ",df_summary_genadm_sum.columns)

    df_vbase = get_vbase_info(df_summary_genadm_sum,df_summary_sum_off_contract_task_mapping,df_summary_sum_p4p_task_mappings, \
                   df_summary_Total_freight_forecast,df_View_summary_MATERIAL_FORECAST_pandas,df_solids_impact)

    # df_vbase = run_sql("v_base_info")

    # p4p_mappings = run_sql("p4p_task_mappings_sum_p4p_task_mappings")
    p4p_mappings = df_p4p_task_mappings_sum_p4p_task_mappings.copy()

    agg_p4p_mappings = p4p_mappings.groupby(['period', 'year', 'company_name'])['sum_period'].sum().reset_index()

    merged_df = pd.merge(df_view_dash, agg_p4p_mappings, on=['period', 'year', 'company_name'], how='inner', suffixes=('', '_agg'))

    merged_df['sum_period'] = merged_df.apply(lambda row: 0.0 if row['sum_period'] == 0 else row['sum_period_agg'] / row['sum_period'], axis=1)

    df_summary_p4p = merged_df.drop(columns=['sum_period_agg','Row_ID'])

    matdf_with_mcwt_fcst = pd.merge(df_vbase,df_summary_p4p,on=['period','year','company_name'],how='left')

    def calculate_material_by_period(df, year, company_name):
        # Filter DataFrame for the specific company and year
        company_year_df = df[(df['company_name'] == company_name) & (df['year'] == year)]

        # Initialize a dictionary to hold MATERIAL values for each period
        material_values = {}

        # Iterate over each period in the filtered DataFrame
        for period in sorted(company_year_df['period'].unique()):
            # Filter for the specific period
            period_df = company_year_df[company_year_df['period'] == period]

            # Calculate Prior Year Material Expense Net (using data up to the previous year)
            prior_years = df[(df['company_name'] == company_name) & (df['year'] < year)]
            prior_year_material_expense_net = prior_years['Total_Material'].sum() + \
                                            (prior_years['Total_exp_With_Solid'].sum() - prior_years['Total_exp_Without_Solid'].sum())

            # Calculate Current Period Values
            total_material_current_period = period_df['Total_Material'].sum()
            total_exp_with_solid_current_period = period_df['Total_exp_With_Solid'].sum()
            total_exp_without_solid_current_period = period_df['Total_exp_Without_Solid'].sum()
            mcwt_volume_fcst_current_period = period_df['sum_period'].sum()

            # Compute MATERIAL for the period
            material = (total_material_current_period + (total_exp_with_solid_current_period - total_exp_without_solid_current_period) - prior_year_material_expense_net) * mcwt_volume_fcst_current_period

            # Store the MATERIAL value for the period
            material_values[f'P{period}'] = material

        return material_values

    # year = 2023
    # company_name = "US-CORE"
    material_values_by_period = calculate_material_by_period(matdf_with_mcwt_fcst, year, company_name)
    print(material_values_by_period)
    return {"material_values_by_period":material_values_by_period}
    # for period, material_value in material_values_by_period.items():
    #     print(f"The MATERIAL value for {company_name} in {year} {period} is: {material_value}")



