from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
import models
from database import get_db
import pandas as pd



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
    df_merged = df_plant_matrix_ga.merge(df_plant, on='plant_id', how='inner')
    # Perform the joins
    df_merged = df_plant_matrix_ga.merge(df_plant, on='plant_id', how='inner')
    df_merged = df_merged.merge(df_growing_area, on='growing_area_id', how='inner', suffixes=('', '_ga'))

    # Join with region for the plant
    df_merged = df_merged.merge(df_region, left_on='region_id_x', right_on='region_id', how='inner', suffixes=('', '_plant'))

    # Join with region for the growing area
    # Ensure 'region' column from growing_area is included in the merge
    df_merged = df_merged.merge(df_region, left_on='region', right_on='region_id', how='inner', suffixes=('', '_ga'))

    # Apply transformations and filter
    df_merged['period_with_P'] = 'P' + df_merged['period'].astype(str)
    df_merged['status_plant'] = df_merged['status_plant'].str.strip()
    df_final = df_merged[df_merged['status_plant'] == 'ACTIVE']  # Adjust the status column as needed

    # Select the required columns as per the SQL view
    columns = [
        'plant_matrix_id', 'period', 'period_with_P', 'plant_name', 'plant_id', 
        'region_id_x', 'region_name', 'company_name', 'country_plant', 'year', 
        'growing_area_id', 'week', 'growing_area_name', 'growing_area_desc', 
        'region', 'country_ga', 'value', 'status'
    ]
    df_final = df_final[columns]
    # Ensure the status column is properly formatted
    df_final['status'] = df_final['status'].str.strip()

    # Filter the DataFrame for 'ACTIVE' status
    df_active = df_final[df_final['status'] == 'ACTIVE']

    # Group and calculate the sum of 'value' for each 'year', 'period', and 'company_name'
    grouped_df = df_active.groupby(['year', 'period', 'company_name']).agg(sum_period=pd.NamedAgg(column='value', aggfunc='sum')).reset_index()

    # Sort by 'year' descending and 'period', then assign row numbers
    grouped_df = grouped_df.sort_values(by=['year', 'period'], ascending=[False, True])
    grouped_df['Row_ID'] = grouped_df.groupby('year').cumcount() + 1

    # Select and order the columns as per your requirement
    df_view_dash = grouped_df[['Row_ID', 'period', 'year', 'company_name', 'sum_period']]

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



