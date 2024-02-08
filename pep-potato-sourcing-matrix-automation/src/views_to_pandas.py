import pandas as pd

def get_dashboard_plant_vol_company(df_plant_matrix_ga,df_plant,df_growing_area,df_region): # pragma: no cover
    part1_df = df_plant_matrix_ga.merge(df_plant, on='plant_id', suffixes=('', '_plant'))
    part1_df['period_with_P'] = 'P' + part1_df['period'].astype(str)
    # part1_df.rename(columns={'region_id_plant':'plant_region_id'},inplace=True)
    part1_df.drop(columns=['created_by', 'created_time','crop_category_id','crop_type','crop_year','plant_code','region_id','updated_by','updated_time'],inplace=True)
    part1_df.rename(columns={'region_id_plant':'plant_region_id'},inplace=True)

    part2_df = part1_df.merge(df_growing_area, on='growing_area_id', suffixes=('', '_growing_area'))
    part2_df.rename(columns={'region':'ga_region_id'},inplace=True)
    part2_df.drop(columns=['fresh_week_start', 'updated_time', 'status_growing_area', 'storage_week_start', 'updated_by', 'fresh_period_start', 'created_by', 'fresh_period_end', 'storage_period_start', 'country', 'created_time', 'fresh_week_end'],inplace=True)

    part3_df = part2_df.merge(df_region, left_on='plant_region_id', right_on='region_id', suffixes=('', '_region_plant'))
    part3_df.rename(columns={'region_name':'plant_region_name','country':'plant_country'},inplace=True)
    part3_df.drop(columns=['status_region_plant', 'updated_time', 'updated_by', 'region_id', 'created_by', 'created_time'],inplace=True)

    part4_df = part3_df.merge(df_region, left_on='ga_region_id', right_on='region_id', suffixes=('', '_ga_region'))
    part4_df['status_plant'] = part4_df['status_plant'].str.strip()
    part4_df['status'] = part4_df['status'].str.lower()
    part4_df.rename(columns={'country':'ga_country'},inplace=True)
    part4_df = part4_df[part4_df['status_plant'] == 'ACTIVE']
    part4_df.drop(columns=[],inplace=True)
    part4_df.drop(columns=["status_plant",'region_id','region_name'],inplace=True)
    part4_df.rename(columns={'plant_region_id':'region_id','plant_region_name':'region_name','plant_country':'country'},inplace=True)
    final_cols = ['plant_matrix_id', 'period', 'period_with_P', 'plant_name', 'plant_id', \
        'region_id', 'region_name', 'company_name', 'country', 'year', \
        'growing_area_id', 'week', 'growing_area_name', 'growing_area_desc', \
        'ga_region_id', 'ga_country', 'value', 'status'] 
    df_plant_mtrx = part4_df[final_cols]

    df_plant_mtrx['status'] = df_plant_mtrx['status'].str.strip()

    # Filter the DataFrame for 'ACTIVE' status
    df_active = df_plant_mtrx[df_plant_mtrx['status'] == 'active']

    # Group and calculate the sum of 'value' for each 'year', 'period', and 'company_name'
    grouped_df = df_active.groupby(['year', 'period', 'company_name']).agg(sum_period=pd.NamedAgg(column='value', aggfunc='sum')).reset_index()

    # Sort by 'year' descending and 'period', then assign row numbers
    grouped_df = grouped_df.sort_values(by=['year', 'period'], ascending=[False, True])
    grouped_df['Row_ID'] = grouped_df.groupby('year').cumcount() + 1

    # Select and order the columns as per your requirement
    df_view_dash = grouped_df[['Row_ID', 'period', 'year', 'company_name', 'sum_period']]

    return df_view_dash

def solids_impact(df_view_dash,df_solids_task_mapp,df_solid_task_master): # pragma: no cover
    df_solid_master_mapping = pd.merge(df_solids_task_mapp, df_solid_task_master, on='solids_task_id')
    order_solid_master_mapping = ['solids_task_id', 'period', 'year', 'value', 'country_code','task_name']

    df_solid_master_mapping_column_sorted = df_solid_master_mapping[order_solid_master_mapping]
    df_solid_master_mapping_pandas = df_solid_master_mapping_column_sorted.sort_values(by=df_solid_master_mapping_column_sorted.columns.tolist()).reset_index(drop=True)

    pivottable_df = df_solid_master_mapping_pandas.pivot_table(
        values='value',
        index=['period', 'year', 'country_code'],
        columns='task_name',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    result_df = pivottable_df[['period', 'year', 'country_code', 'PLAN', 'FORECAST', 'Conversion Factor', 'PRIOR', 'M$ IMPACT B/(W)']]

    order_solid_task_mapping_pivot = ['period', 'year', 'country_code', 'PLAN', 'FORECAST',
        'Conversion Factor', 'PRIOR', 'M$ IMPACT B/(W)']

    df_solid_task_mapping_pivot_column_sorted = result_df[order_solid_task_mapping_pivot]

    df_solid_task_mapping_pivot_pandas = df_solid_task_mapping_pivot_column_sorted.sort_values(by=df_solid_task_mapping_pivot_column_sorted.columns.tolist()).reset_index(drop=True)
    df_View_Dashboard_plant_sum = df_view_dash.copy()

    df_solid_task_mapping_copy = df_solid_task_mapping_pivot_pandas.copy()
    df_solid_task_mapping_copy['FORE_PLAN'] = df_solid_task_mapping_copy['FORECAST'] - df_solid_task_mapping_copy['PLAN']
    df_solid_task_mapping_copy['YAG_Index'] = df_solid_task_mapping_copy.apply(lambda x: 0 if x['FORECAST'] == 0 or x['PRIOR'] == 0 else (x['FORECAST'] / x['PRIOR'] * 100), axis=1)

    df_solid_task_mapping_copy['M_dollar_IMPACT'] = df_solid_task_mapping_copy.apply(
        lambda x: x['M$ IMPACT B/(W)'] if x['M$ IMPACT B/(W)'] != 0 else
        (x['FORECAST'] - x['PLAN']) * x['Conversion Factor'] * (
            df_View_Dashboard_plant_sum[
                (df_View_Dashboard_plant_sum['company_name'] == x['country_code']) &
                (df_View_Dashboard_plant_sum['period'] == x['period']) &
                (df_View_Dashboard_plant_sum['year'] == x['year'])
            ]['sum_period'].values[0] if not df_View_Dashboard_plant_sum[
                (df_View_Dashboard_plant_sum['company_name'] == x['country_code']) &
                (df_View_Dashboard_plant_sum['period'] == x['period']) &
                (df_View_Dashboard_plant_sum['year'] == x['year'])
            ].empty else 0
        ) * (-1),
        axis=1
    )
    df_solid_task_mapping_copy['Row#'] = df_solid_task_mapping_copy.sort_values(['year', 'period']).groupby('year').cumcount() + 1
    df_solid_task_mapping_copy = df_solid_task_mapping_copy[['Row#', 'period', 'year', 'country_code', 'PRIOR', 'PLAN',
                        'FORECAST', 'Conversion Factor', 'FORE_PLAN', 'YAG_Index', 'M_dollar_IMPACT']]

    order_View_solid_summary_column_sorted = ['Row#', 'period', 'year', 'country_code', 'PRIOR', 'PLAN', 'FORECAST',
        'Conversion Factor', 'FORE_PLAN', 'YAG_Index', 'M_dollar_IMPACT']

    df_View_solid_summary_column_sorted_p = df_solid_task_mapping_copy[order_View_solid_summary_column_sorted]

    View_summary_plant_current_prev = df_View_Dashboard_plant_sum[['period', 'year', 'company_name', 'sum_period']].copy()

    View_summary_plant_current_prev['sum_period_prev'] = View_summary_plant_current_prev.groupby('company_name')['sum_period'].shift(1).fillna(0)


    View_summary_plant_current_prev['type'] = 'MCWT_VOLUME_FCST'
    df_Solids_Impact_MCWT_VOLUME = pd.merge(
        df_View_solid_summary_column_sorted_p,
        View_summary_plant_current_prev,
        left_on=['period','country_code','year'],
        right_on=['period','company_name','year']
    )

    df_Solids_Impact_MCWT_VOLUME['sum_values'] = df_Solids_Impact_MCWT_VOLUME['M_dollar_IMPACT'] / df_Solids_Impact_MCWT_VOLUME['sum_period']
    df_Solids_Impact_MCWT_VOLUME_pandas = df_Solids_Impact_MCWT_VOLUME[['period', 'year', 'company_name', 'sum_values', 'M_dollar_IMPACT', 'sum_period']]

    return df_Solids_Impact_MCWT_VOLUME_pandas


def material_forecast_summary(df_potato_rate_mapping,df_potato_rates,df_plant_matrix_growing_area,df_plant,df_growing_area,df_region): # pragma: no cover
    df_potato_rate_mapping.rename(columns={"p_year": "year",
                                       "country_code":"country"}, inplace=True)
    df_potato_plan_rate = pd.merge(
        df_potato_rate_mapping,
        df_potato_rates,
        left_on='potato_rate_id',
        right_on='potato_rate_id',
        how='left'
    )
    df_potato_plan_rate['country'] = df_potato_plan_rate['country'].str.strip()
    df_plant_matrix_plant = pd.merge(df_plant_matrix_growing_area, df_plant, on='plant_id', how='left')
    df_plant_matrix_plant_growing_area = pd.merge(df_plant_matrix_plant, df_growing_area, on='growing_area_id', how = 'inner')
    df_pm_p_ga_region = pd.merge(df_plant_matrix_plant_growing_area, df_region, on='region_id', how = 'inner')
    df_pm_p_ga_region['country']=df_pm_p_ga_region['country'].str.strip()

    cte_reports = pd.merge(
        df_pm_p_ga_region,
        df_potato_plan_rate,
        how='left',on=['growing_area_id', 'period', 'week','year','country']
    )
    cte_reports['vol_rate'] = cte_reports['value'] * cte_reports['rate']
    sum_period = cte_reports.groupby(['period', 'year', 'company_name'])[['value', 'vol_rate']].sum().reset_index()

    sum_period['sum_period'] = sum_period['vol_rate'] / sum_period['value']
    sum_period['type'] = 'Material Forecast ($/unit)'
    sum_period['position'] = 3  
    sum_period = sum_period[['period', 'year', 'sum_period', 'company_name', 'type', 'position']]
    desired_order = ['period', 'year', 'company_name', 'sum_period', 'type', 'position']
    df1 = sum_period[desired_order]
    df_View_summary_MATERIAL_FORECAST_pandas = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True)

    return df_View_summary_MATERIAL_FORECAST_pandas


def view_summary_Total_freight_forecast(freight_task_mappings, View_freight_cost_period_CATEGORY_COUNTRY_FREIGHT_FORECAST,View_Dashboard_plant_matrix_volume_company_name): # pragma: no cover
    # FOR VIEW [dbo].[freight_task_mappings_sum_freight_cost_mapping] usinf db freight_task_mappings 
    freight_task_mappings_sum_freight_cost_mapping = freight_task_mappings.groupby(['company_name', 'year', 'period']).agg(sum_period=('value', 'sum')).reset_index()

    # Creating VIEW view_summary_sum_freight_misc using View_Dashboard_plant_matrix_volume_company_name & freight_task_mappings_sum_freight_cost_mapping
    cte_gen_a_exp = freight_task_mappings_sum_freight_cost_mapping.groupby(['period', 'year', 'company_name']).agg(sum_period=('sum_period', 'sum')).reset_index()

    # Final VIEW view_summary_sum_freight_misc
    view_summary_sum_freight_misc = pd.merge(View_Dashboard_plant_matrix_volume_company_name, cte_gen_a_exp, on=['period', 'year', 'company_name'], how='inner')
    view_summary_sum_freight_misc['sum_period'] = view_summary_sum_freight_misc.apply(lambda row: 0.0 if row['sum_period_x'] == 0 else row['sum_period_y'] / row['sum_period_x'], axis=1)
    view_summary_sum_freight_misc = view_summary_sum_freight_misc[['period', 'year', 'company_name', 'sum_period']]

    # print(view_summary_sum_freight_misc)

    # Creating the view view_summary_sum_freight_forecast using dbo.View_freight_cost_period_CATEGORY_COUNTRY_FREIGHT_FORECAST
    view_summary_sum_freight_forecast = View_freight_cost_period_CATEGORY_COUNTRY_FREIGHT_FORECAST.rename(columns={'category_name': 'company_name'})[['period', 'year', 'company_name', 'sum_period']]

    # Displaying the resulting DataFrame (equivalent to the view)
    # print(view_summary_sum_freight_forecast)

    #  Creating Final VIEW [view_summary_Total_freight_forecast]
    # view_summary_sum_freight_forecast 
    # view_summary_sum_freight_misc 

    # Creating the view
    merged_view = pd.merge(view_summary_sum_freight_forecast, view_summary_sum_freight_misc, on=['period', 'year', 'company_name'], how='left', suffixes=('_forecast', '_misc'))
    merged_view['Total_freight_cost'] = merged_view['sum_period_forecast'].fillna(0) + merged_view['sum_period_misc'].fillna(0)
    view_summary_Total_freight_forecast = merged_view[['period', 'year', 'company_name', 'Total_freight_cost']]

    return view_summary_Total_freight_forecast

def get_view_summary_sum_p4p_task_mappings(p4p_master_info, p4p_task_mappings,df_view_dash): # pragma: no cover
    view_v_p4p_task_mappings = pd.merge(p4p_master_info, p4p_task_mappings, on='p4p_id', how='inner')

    # Selecting required columns
    view_v_p4p_task_mappings = view_v_p4p_task_mappings[['p4p_name', 'company_name', 'period', 'value', 'year']]
    view_v_p4p_task_mappings.rename(columns={'value': 'sum_period'}, inplace=True)

    # Performing the equivalent operation in pandas
    view_p4p_task_mappings_sum_p4p_task_mappings = view_v_p4p_task_mappings[view_v_p4p_task_mappings['p4p_name'].isin(['solid-actual', 'defects-actual'])]
    view_p4p_task_mappings_sum_p4p_task_mappings = view_p4p_task_mappings_sum_p4p_task_mappings.groupby(['year', 'period', 'company_name']).agg(sum_period=('sum_period', 'sum')).reset_index()

    cte_gen_a_exp = view_p4p_task_mappings_sum_p4p_task_mappings.groupby(['period', 'year', 'company_name']).agg(sum_period=('sum_period', 'sum')).reset_index()

    # Final SELECT
    view_summary_sum_p4p_task_mappings = pd.merge(df_view_dash, cte_gen_a_exp, on=['period', 'year', 'company_name'], how='inner')
    view_summary_sum_p4p_task_mappings['sum_period'] = view_summary_sum_p4p_task_mappings.apply(lambda row: 0.0 if row['sum_period_x'] == 0 else row['sum_period_y'] / row['sum_period_x'], axis=1)
    view_summary_sum_p4p_task_mappings = view_summary_sum_p4p_task_mappings[['period', 'year', 'company_name', 'sum_period']]

    return view_summary_sum_p4p_task_mappings,view_p4p_task_mappings_sum_p4p_task_mappings

def view_summary_sum_off_contract_task_mapping (df_off_contract_task_mapping,df_view_dash): # pragma: no cover
    View_Dashboard_sum_off_contract_task_mapping = df_off_contract_task_mapping.groupby(['year', 'period','company_name']).agg(sum_period=('value', 'sum')).reset_index()
    # CTE_Gen_A_exp
    cte_gen_a_exp = View_Dashboard_sum_off_contract_task_mapping.groupby(['period', 'year', 'company_name']).agg(sum_period=('sum_period', 'sum')).reset_index()

    # Final SELECT
    view_summary_sum_off_contract_task_mapping = pd.merge(df_view_dash, cte_gen_a_exp, on=['period', 'year', 'company_name'], how='inner')
    view_summary_sum_off_contract_task_mapping['sum_period'] = view_summary_sum_off_contract_task_mapping.apply(lambda row: 0.0 if row['sum_period_x'] == 0 else row['sum_period_y'] / row['sum_period_x'], axis=1)
    view_summary_sum_off_contract_task_mapping = view_summary_sum_off_contract_task_mapping[['period', 'year', 'company_name', 'sum_period']]

    return view_summary_sum_off_contract_task_mapping

def summary_sum_general_administrative(ga_mapping,df_view_dash): # pragma: no cover
    subquery = ga_mapping.groupby(['year', 'period', 'company_name'])['value'].sum().reset_index(name='sum_period')

    # Step 2: Merge the subquery result back with the original DataFrame
    merged_df = ga_mapping.merge(subquery, on=['year', 'period', 'company_name'])

    # Step 3: Perform final grouping (if needed, depending on further use of this DataFrame)
    ga_mapping_sum_gamap = merged_df.groupby(['year', 'period', 'company_name']).first().reset_index()

    ga_mapping_sum_gamap = ga_mapping_sum_gamap[['company_name', 'year', 'period', 'sum_period']]

    ga_mapping_sum_aggregated = ga_mapping_sum_gamap.groupby(['period', 'year', 'company_name'])['sum_period'].sum().reset_index(name='sum_period_aggregated')

    # Step 2: Merge this aggregated result back with ga_mapping_sum_gamap (CTE logic)
    cte_gen_a_exp = ga_mapping_sum_gamap.merge(ga_mapping_sum_aggregated, on=['period', 'year', 'company_name'])

    # Step 3: Join this with df_view_dash
    merged_df = df_view_dash.merge(cte_gen_a_exp, on=['period', 'year', 'company_name'], suffixes=('_view_dash', '_cte'))

    # Step 4: Apply the conditional logic for sum_period calculation
    merged_df['sum_period'] = merged_df.apply(
        lambda row: 0.0 if row['sum_period_view_dash'] == 0 else (row['sum_period_cte'] / row['sum_period_view_dash']) / 1000, 
        axis=1
    )

    # Select only the required columns
    df_sum_genadm_sum = merged_df[['period', 'year', 'company_name', 'sum_period']]
    # df_sum_genadm_sum['company_name'] = df_sum_genadm_sum['company_name'].str.strip()
    return df_sum_genadm_sum    


def get_vbase_info(df_summary_genadm_sum,df_summary_sum_off_contract_task_mapping,df_summary_sum_p4p_task_mappings, \
                   df_summary_Total_freight_forecast,df_View_summary_MATERIAL_FORECAST_pandas,df_solids_impact): # pragma: no cover
    df_summary_genadm_sum.rename(columns={'sum_period': 'genadm_sum_period'}, inplace=True)
    df_summary_sum_off_contract_task_mapping.rename(columns={'sum_period': 'off_contract_sum_period'}, inplace=True)
    df_summary_sum_p4p_task_mappings.rename(columns={'sum_period': 'p4p_sum_period'}, inplace=True)
    df_summary_Total_freight_forecast.rename(columns={'Total_freight_cost': 'freight_cost'}, inplace=True)
    df_View_summary_MATERIAL_FORECAST_pandas.rename(columns={'sum_period': 'mtl_fcst_sum_period'}, inplace=True)
    df_solids_impact.rename(columns={'sum_period': 'solids_sum_period', 'sum_values': 'solids_sum_values'}, inplace=True)

    # Join DataFrames using appropriate join keys and types
    merged_df = pd.merge(df_summary_genadm_sum, df_summary_sum_off_contract_task_mapping, on=['period', 'year', 'company_name'], how='inner')
    merged_df = pd.merge(merged_df, df_summary_sum_p4p_task_mappings, on=['period', 'year', 'company_name'], how='inner')
    merged_df = pd.merge(merged_df, df_summary_Total_freight_forecast, on=['period', 'year', 'company_name'], how='inner')
    merged_df = pd.merge(merged_df, df_View_summary_MATERIAL_FORECAST_pandas, on=['period', 'year', 'company_name'], how='left')
    merged_df = pd.merge(merged_df, df_solids_impact, on=['period', 'year', 'company_name'], how='left')

    # Calculate the 'Total_Material' column based on the corresponding columns
    merged_df['Total_Material'] = (
        merged_df['genadm_sum_period']
        + merged_df['off_contract_sum_period']
        + merged_df['p4p_sum_period']
        + merged_df['mtl_fcst_sum_period']
    )

    # Calculate other required columns
    merged_df['Total_freight_cost'] = merged_df['freight_cost']
    merged_df['Total_exp_Without_Solid'] = (
        merged_df['genadm_sum_period']
        + merged_df['off_contract_sum_period']
        + merged_df['p4p_sum_period']
        + merged_df['mtl_fcst_sum_period']
        + merged_df['Total_freight_cost']
    )
    merged_df['m$'] = merged_df['solids_sum_values']
    merged_df['Total_exp_With_Solid'] = (
        merged_df['genadm_sum_period']
        + merged_df['off_contract_sum_period']
        + merged_df['p4p_sum_period']
        + merged_df['mtl_fcst_sum_period']
        + merged_df['Total_freight_cost']
        - merged_df['solids_sum_values']
    )

    # Select the desired columns
    result_df = merged_df[
        ['period', 'year', 'company_name', 'Total_Material', 'Total_freight_cost', 'Total_exp_Without_Solid', 'm$', 'Total_exp_With_Solid']
    ]

    return result_df






    