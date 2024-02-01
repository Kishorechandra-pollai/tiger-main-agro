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

    

