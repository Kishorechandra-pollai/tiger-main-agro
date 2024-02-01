from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
import models
from database import get_db
import pandas as pd
import get_dashboard_plmavol_company



router = APIRouter()

@router.get('/{year}/{company_name}')
def infl_defl(year:int,company_name:str,db: Session = Depends(get_db)): # pragma: no cover
    # df_plant_matrix_ga = pd.read_sql_table('plant_matrix_growing_area', engine)
    # df_plant = pd.read_sql_table('plant', engine)
    # df_growing_area = pd.read_sql_table('growing_area', engine)
    # df_region = pd.read_sql_table('region', engine)
    def run_sql(table_name):
        query = f"SELECT * FROM {table_name}"
        result = db.execute(query)
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
        return df
    df_plant_matrix_ga = run_sql("plant_matrix_growing_area")
    df_plant = run_sql("plant")
    df_growing_area = run_sql("growing_area")
    df_region = run_sql("region")
    
    df_view_dash = get_dashboard_plmavol_company.get_dashboard_plant_vol_company(df_plant_matrix_ga,df_plant,df_growing_area,df_region)

    # Display the DataFrame

    print(df_plant_matrix_ga.head())

    df_vbase = run_sql("v_base_info")

    p4p_mappings = run_sql("p4p_task_mappings_sum_p4p_task_mappings")

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



