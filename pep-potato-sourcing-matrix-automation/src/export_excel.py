from fastapi import APIRouter,Body,HTTPException, status, Depends, Query
from fastapi.responses import FileResponse,StreamingResponse
from datetime import datetime
import pandas as pd
from pathlib import Path
import os
import schemas
import models
from io import BytesIO
import asyncio
from fastapi.security import HTTPBearer
import json
from typing import List, Optional, Type
from pydantic import BaseModel,create_model


router = APIRouter()

@router.post('/export_test')
def dynamicPeriodSchemaCreator(periods:List[str]): # pragma: no cover
    dynamic_period_list=[]
    for items in periods:
        for weeks in range(1,5):
            dynamic_period_with_P = f"P{items}|W{weeks}"
            dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_P,"dynamic_period":items,"dynamic_week":weeks}
            dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list

def dynamicPeriodOnlySchemaCreator(periods:List[str]): # pragma: no cover
    dynamic_period_list=[]
    for items in periods:
        dynamic_period_with_P = f"P{items}"
        dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_P,"dynamic_period":items}
        dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list

def dynamicPeriodSchemaCreatorForecast(periods:List[str]): # pragma: no cover
    list_placeholder=["Plan","Act","Diff"]
    dynamic_period_list=[]
    for item in periods:
        for lp in list_placeholder:
            dynamic_period_with_P = f"P{item}-{lp}"
            dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_P,"dynamic_period":item}
            dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list



@router.post('/export_plant_matrix_allocation')
def export_plant_matrix_allocation(periods:List[str],payload:schemas.ExportExcelPlantMatrixAllocationList): # pragma: no cover
    unique_plants =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list = dynamicPeriodSchemaCreator(periods)
    output_export_json = []
    for up in unique_plants: 
        export_object={"plant_name":up}
        total_value=0
        filtered_payload = [item for item in payload.data if item.plant_name==up]
        for pl in period_list:
           filtered_payload_period =  [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])
            ]
           allocation_placeholder = ""
           for fpp in filtered_payload_period:
               allocation_placeholder=allocation_placeholder+fpp.growing_area_name+"-"+str(round(fpp.value))+" "
               total_value+=fpp.value
           export_object[pl["dynamic_period_with_P"]]=allocation_placeholder
        export_object["Total"]=round(total_value)
        output_export_json.append(export_object)
        weekly_average = 0
        for fp in filtered_payload:
            weekly_average+=round(fp.value)
        export_object["Annual Weekly Avg."] = round(weekly_average/52)
        
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"plant_matrix_allocation_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_excel_ownership')
def export_excel_ownership(payload:schemas.ExportExcelOwnershipList): # pragma: no cover
    key_order =["Growing_Area","Contract","Shrinkage","To_Ship","Market","Flex","A2S","Extension","Demand","Position"]
    reordered_payload = [{key: item.dict().get(key) for key in key_order} for item in payload.data]
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(reordered_payload)
    file_name = f"ownership_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_plant_matrix_region_week')
def export_plant_matrix_region_week(periods:List[str],payload:schemas.ExportExcelplantmatrixregionweekList): # pragma: no cover
    unique_region = ["East - US","Central - US","West - US","Canada"]
    period_list = dynamicPeriodSchemaCreator(periods) 
    output_export_json = []
    for ur in unique_region:
        export_object = {"Region":ur}
        filtered_payload = [item for item in payload.data if item.region_name==ur]
        total=0
        for pl in period_list:
           filtered_payload_period =  [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])
            ]
           export_object[pl["dynamic_period_with_P"]]=round(filtered_payload_period[0].totalValue_regionWise)
           total+=round(filtered_payload_period[0].totalValue_regionWise)
        export_object["Total"]=total
        output_export_json.append(export_object)
    export_object_FLUS={"Region":"FLUS Total"}
    export_object_FLNA ={"Region":"FLNA Total"}
    total_FLUS=0
    total_FLNA =0
    for pl in period_list:
        filtered_payload_East_US=[item for item in payload.data if item.region_name=="East - US" and str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])]
        filtered_payload_West_US=[item for item in payload.data if item.region_name=="West - US" and str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])]
        filtered_payload_Central_US=[item for item in payload.data if item.region_name=="Central - US" and str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])]
        filtered_payload_Canada=[item for item in payload.data if item.region_name=="Canada" and str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])]

        export_object_FLUS[pl["dynamic_period_with_P"]]=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise)

        export_object_FLNA[pl["dynamic_period_with_P"]]=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise+filtered_payload_Canada[0].totalValue_regionWise)

        total_FLUS +=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise)

        total_FLNA+=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise+filtered_payload_Canada[0].totalValue_regionWise)

        export_object_FLUS["Total"]=total_FLUS
        export_object_FLNA["Total"]=total_FLNA
    output_export_json.append(export_object_FLUS)
    output_export_json.append(export_object_FLNA)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"plant_matrix_region_week_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_plant_matrix_region_period')
def export_plant_matrix_region_period(periods:List[str],payload:schemas.ExportExcelplantmatrixregionweekList): # pragma: no cover
    unique_region = ["East - US","Central - US","West - US","Canada"]
    period_list = dynamicPeriodOnlySchemaCreator(periods) 
    output_export_json = []
    for ur in unique_region:
        export_object = {"Region":ur}
        filtered_payload = [item for item in payload.data if item.region_name==ur]
        total=0
        for pl in period_list:
           filtered_payload_period =  [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"])
            ]
           export_object[pl["dynamic_period_with_P"]]=round(filtered_payload_period[0].totalValue_regionWise)
           total+=round(filtered_payload_period[0].totalValue_regionWise)
        export_object["Total"]=total
        output_export_json.append(export_object)
    export_object_FLUS={"Region":"FLUS Total"}
    export_object_FLNA ={"Region":"FLNA Total"}
    total_FLUS=0
    total_FLNA =0
    for pl in period_list:
        filtered_payload_East_US=[item for item in payload.data if item.region_name=="East - US" and str(item.period) == str(pl["dynamic_period"])]
        filtered_payload_West_US=[item for item in payload.data if item.region_name=="West - US" and str(item.period) == str(pl["dynamic_period"])]
        filtered_payload_Central_US=[item for item in payload.data if item.region_name=="Central - US" and str(item.period) == str(pl["dynamic_period"])]
        filtered_payload_Canada=[item for item in payload.data if item.region_name=="Canada" and str(item.period) == str(pl["dynamic_period"])]

        export_object_FLUS[pl["dynamic_period_with_P"]]=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise)

        export_object_FLNA[pl["dynamic_period_with_P"]]=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise+filtered_payload_Canada[0].totalValue_regionWise)

        total_FLUS +=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise)

        total_FLNA+=round(filtered_payload_East_US[0].totalValue_regionWise+filtered_payload_Central_US[0].totalValue_regionWise+filtered_payload_West_US[0].totalValue_regionWise+filtered_payload_Canada[0].totalValue_regionWise)

        export_object_FLUS["Total"]=total_FLUS
        export_object_FLNA["Total"]=total_FLNA
    output_export_json.append(export_object_FLUS)
    output_export_json.append(export_object_FLNA)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"plant_matrix_region_period_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_plant_matrix_grower_week')
def export_plant_matrix_grower_week(periods:List[str],payload:schemas.ExportExcelplantmatrixgrowerweekList): # pragma: no cover
    unique_growers = sorted(list(set([entry.growing_area_name for entry in payload.data])))
    period_list = dynamicPeriodSchemaCreator(periods) 
    output_export_json = []
    for ug in unique_growers:
        export_object={"Growing_Area":ug}
        filtered_payload = [item for item in payload.data if item.growing_area_name==ug]
        total=0
        for pl in period_list:
             filtered_payload_period =  [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])
            ]
             if len(filtered_payload_period)>0:
                 export_object[pl["dynamic_period_with_P"]]=round(filtered_payload_period[0].total_value)
                 total+=round(filtered_payload_period[0].total_value)
             else:
                 export_object[pl["dynamic_period_with_P"]]=0
        export_object["total"]=total
        output_export_json.append(export_object)
    
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"plant_matrix_grower_week_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_plant_matrix_grower_period')
def export_plant_matrix_grower_period(periods:List[str],payload:schemas.ExportExcelplantmatrixgrowerweekList): # pragma: no cover
    unique_growers = sorted(list(set([entry.growing_area_name for entry in payload.data])))
    period_list = dynamicPeriodOnlySchemaCreator(periods) 
    output_export_json = []
    for ug in unique_growers:
        export_object={"Growing_Area":ug}
        filtered_payload = [item for item in payload.data if item.growing_area_name==ug]
        total=0
        for pl in period_list:
             filtered_payload_period =  [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) 
            ]
             if len(filtered_payload_period)>0:
                 export_object[pl["dynamic_period_with_P"]]=round(filtered_payload_period[0].total_value)
                 total+=round(filtered_payload_period[0].total_value)
             else:
                 export_object[pl["dynamic_period_with_P"]]=0
        export_object["total"]=total
        output_export_json.append(export_object)
    
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"plant_matrix_grower_week_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_forecast')
def export_forecast(periods:List[str],payload:schemas.ExportExcelForecastList): # pragma: no cover
    unique_plants =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list =dynamicPeriodOnlySchemaCreator(periods)
    output_export_json = []
    for up in unique_plants:
        export_object={"plant_name":up}
        filtered_payload = [item for item in payload.data if item.plant_name==up]
        total_act =0
        total_fore=0
        total_delta=0
        for pl in period_list:
            filtered_payload_period = [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) 
            ]
            
            export_object[f"{pl['dynamic_period_with_P']}-Act"]=round(filtered_payload_period[0].total_forecast_value)
            total_fore+=round(filtered_payload_period[0].total_forecast_value)
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload_period[0].total_actual_value)
            total_act+=round(filtered_payload_period[0].total_actual_value)
            export_object[f"{pl['dynamic_period_with_P']}-Diff"]=round(filtered_payload_period[0].total_forecast_value)-round(filtered_payload_period[0].total_actual_value)
            total_delta+=round(filtered_payload_period[0].total_forecast_value)-round(filtered_payload_period[0].total_actual_value)
            
        export_object["Total_plan"]=total_fore
        export_object["Total_Act"]=total_act
        export_object["Total_Delta"]=total_delta
        output_export_json.append(export_object)
    
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"forecast_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_inflation_deflation')
def export_inflation_deflation(payload:schemas.ExportExcelInflationDeflationList): # pragma: no cover
    output_export_json =[]
    export_object = {"Performance vs YAG":"Material CY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].material,2)
        total+=round(filtered_payload[0].material,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Frieght CY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].freight,2)
        total+=round(filtered_payload[0].freight,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Total"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total,2)
        total+=round(filtered_payload[0].total,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Material PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].material_prev,2)
        total+=round(filtered_payload[0].material_prev,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Freight PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].freight_prev,2)
        total+=round(filtered_payload[0].freight_prev,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Total PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total_prior,2)
        total+=round(filtered_payload[0].total_prior,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"(B)/W vs PY MAT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].bw_than_py_matl,2)
        total+=round(filtered_payload[0].bw_than_py_matl,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"(B)/W vs. PY FRT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].bw_than_py_frt,2)
        total+=round(filtered_payload[0].bw_than_py_frt,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"(B)/W vs. PY TOT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].bw_than_py_total,2)
        total+=round(filtered_payload[0].bw_than_py_total,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"$ Impact vs PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].impact_bw_vs_prior_year,0)
        total+=round(filtered_payload[0].impact_bw_vs_prior_year,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Index (%) -MAT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].index_mat,1)
        total+=round(filtered_payload[0].index_mat,1)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Index (%) -FRT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].index_frt,2)
        total+=round(filtered_payload[0].index_frt,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs YAG":"Index (%) -TOT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].index,1)
        total+=round(filtered_payload[0].index,1)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"inflation_deflation_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )


@router.post('/export_performance_vs_plan')
def export_performance_vs_plan(payload1:schemas.ExportExcelPVP_PVPList,payload2:schemas.ExportExcelPVP_PVList): # pragma: no cover
    output_export_json =[]
    export_object = {"Performance vs Plan":"Actual($/u)-Material"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total_material_actual,2)
        total+=round(filtered_payload[0].total_material_actual,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Actual($/u)-Freight"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total_freight_cost_actual,2)
        total+=round(filtered_payload[0].total_freight_cost_actual,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)


    export_object = {"Performance vs Plan":"Actual($/u)-Total"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round((filtered_payload[0].total_freight_cost_actual+filtered_payload[0].total_material_actual),2)
        total+=round((filtered_payload[0].total_freight_cost_actual+filtered_payload[0].total_material_actual),2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Plan($/u)-Material"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,2)
        total+=round(filtered_payload[0].value,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Plan($/u)-Freight"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,2)
        total+=round(filtered_payload[0].value,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Plan($/u)-Raw Material"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,2)
        total+=round(filtered_payload[0].value,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Plan($/u)-total"}
    total=0
    for pr in range(1,14):
        filtered_payload_1 = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==1]
        filtered_payload_2 = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==2]
        filtered_payload_3 = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload_1[0].value+filtered_payload_2[0].value+filtered_payload_3[0].value,2)
        total+=round(filtered_payload_1[0].value+filtered_payload_2[0].value+filtered_payload_3[0].value,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"PV($/u)-Material-B/(W)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].MATERIAL_BW_per_unit,2)
        total+=round(filtered_payload[0].MATERIAL_BW_per_unit,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"PV($/u)-Frieght-B/(W)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].FREIGHT_BW_per_unit,2)
        total+=round(filtered_payload[0].FREIGHT_BW_per_unit,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Total"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].FREIGHT_BW_per_unit+filtered_payload[0].MATERIAL_BW_per_unit,2)
        total+=round(filtered_payload[0].FREIGHT_BW_per_unit+filtered_payload[0].MATERIAL_BW_per_unit,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"IMP B/(W) Vs Plan ($)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].IMPACT_BW_vs_Plan,0)
        total+=round(filtered_payload[0].IMPACT_BW_vs_Plan,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    


    export_object = {"Performance vs Plan":"Index (%) -MAT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].Index_percent_MAT,2)
        total+=round(filtered_payload[0].Index_percent_MAT,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Index (%) -FRT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].Index_percent_FRT,2)
        total+=round(filtered_payload[0].Index_percent_FRT,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Performance vs Plan":"Index (%) -TOTT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].Index_percent,2)
        total+=round(filtered_payload[0].Index_percent,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Performance_VS_Plan_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_offcontract')
def export_offcontract(payload:schemas.ExportOffContractList,payload_plan:schemas.ExportOffContractList):  # pragma: no cover
    output_export_json =[]
    export_object = {"Off Contract Adj-Act":"Misc Bills"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==9]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"Price ADJ"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==7]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"Project"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==8]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"Standards Adjustement"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==10]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"JE (+)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"JE (-)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==6]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"Stoarage research"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"End year ADJ"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {"Off Contract Adj-Act":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.off_contract_task_id==13]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object={"Off Contract Adj-Act":"Total Off Contract Adj"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    output_export_json_plan =[]
    export_object = {"Off Contract Adj-Plan":"Misc Bills"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"Price ADJ"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"Project"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"Standards Adjustement"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==4]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"JE (+)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==5]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"JE (-)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==6]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"Stoarage research"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==7]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"End year ADJ"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==8]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object = {"Off Contract Adj-Plan":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.off_contract_plan_task_id==9]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total/13,2)
    output_export_json_plan.append(export_object)

    export_object={"Off Contract Adj-Plan":"Total Off Contract plan"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json_plan:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json_plan.append(export_object)


    export_object={"Off Contract Adj-Plan":"Delta Off Contract"}
    total=0
    for pr in range(1,14):
        filtered_object_1 = [item for item in output_export_json if item["Off Contract Adj-Act"]=="Total Off Contract Adj"]
        filtered_object_2 = [item for item in output_export_json_plan if item["Off Contract Adj-Plan"]=="Total Off Contract plan"]
        export_object[f"P{pr}"]=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
        total+=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
    export_object["Total"]=round(total,0)
    output_export_json_plan.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df1 = pd.DataFrame(output_export_json)
    df2 = pd.DataFrame(output_export_json_plan)
    file_name = f"Off_contract_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name='Sheet1',startrow=0, header=True)
        writer.sheets['Sheet1'].append([])
        df2.to_excel(writer, index=False, sheet_name='Sheet1', startrow=len(df1)+2, header=True)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_Adjustments_freight')
def export_Adjustments_freight(payload:schemas.ExportExcelAdjustmentsFreightList,payload_plan:schemas.ExportExcelAdjustmentsFreightList): # pragma: no cover
    output_export_json =[]
    export_object = {"Freight Adjustments-Act":"Adjustments"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Freight Adjustments-Act":"Sourcing"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Freight Adjustments-Act":"Rail Lease Expense"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Freight Adjustments-Act":"Productivity"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==4]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Freight Adjustments-Act":"Auto=pay-fuel"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==5]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Freight Adjustments-Act":"Fuel Surcharge"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==6]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Freight Adjustments-Act":"Accesorial"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==7]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {"Freight Adjustments-Act":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr and item.freight_task_id==8]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object={"Freight Adjustments-Act":"Total Freight Adjustment"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)


    output_export_json_plan =[]
    export_object = {"Freight Adjustments-Plan":"Adjustments"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Sourcing"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Rail Lease Expense"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Productivity"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==4]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Auto-pay-fuel"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==5]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Fuel Surcharge"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==6]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Accesorial"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==7]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==8]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    export_object={"Freight Adjustments-Plan":"Total Freight Adjustment"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json_plan:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json_plan.append(export_object)

    export_object={"Freight Adjustments-Plan":"Delta Freight Adjustments"}
    total=0
    for pr in range(1,14):
        filtered_object_1 = [item for item in output_export_json if item["Freight Adjustments-Act"]=="Total Freight Adjustment"]
        filtered_object_2 = [item for item in output_export_json_plan if item["Freight Adjustments-Plan"]=="Total Freight Adjustment"]
        export_object[f"P{pr}"]=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
        total+=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
    export_object["Total"]=round(total,0)
    output_export_json_plan.append(export_object)

    export_object = {"Freight Adjustments-Plan":"Trip Count"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload_plan.data if item.period==pr and item.freight_task_plan_id==9]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,2)
        total+=round(filtered_payload[0].value,2)
    export_object["Total"]=round(total,2)
    output_export_json_plan.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df1 = pd.DataFrame(output_export_json)
    df2 = pd.DataFrame(output_export_json_plan)
    file_name = f"Frieght_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name='Sheet1',startrow=0, header=True)
        writer.sheets['Sheet1'].append([])
        df2.to_excel(writer, index=False, sheet_name='Sheet1', startrow=len(df1)+2, header=True)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_adjustments_P4P')
def export_adjustments_P4P(payload:schemas.ExportExcelAdjustmentsP4PList): # pragma: no cover
    output_export_json =[]
    export_object = {"P4P Adjustments":"Solids-Plan"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].solid_plan,0)
        total+=round(filtered_payload[0].solid_plan,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Solids-Actual/Fcst"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].solid_actual,0)
        total+=round(filtered_payload[0].solid_actual,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Diff(Solids)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].diff_solid,0)
        total+=round(filtered_payload[0].diff_solid,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Defects-Plan"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].defects_plan,0)
        total+=round(filtered_payload[0].defects_plan,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Defects-Actual/Fcst"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].defects_actual,0)
        total+=round(filtered_payload[0].defects_actual,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Diff(Defects)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].diff_Defects,0)
        total+=round(filtered_payload[0].diff_Defects,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)
 
    export_object = {"P4P Adjustments":"Total-P4P VS Plan"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].p4pDiff,0)
        total+=round(filtered_payload[0].p4pDiff,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Actual P4P"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].ptdActualP4P,0)
        total+=round(filtered_payload[0].ptdActualP4P,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Plan Solids"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].solid_actual,0)
        total+=round(filtered_payload[0].solid_actual,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Plan Defects"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].defects_actual,0)
        total+=round(filtered_payload[0].defects_actual,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    export_object = {"P4P Adjustments":"Total P4P"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.periods==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total,0)
        total+=round(filtered_payload[0].total,0)
    export_object["Total"]=round(total,0)
    output_export_json.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Adjustments_P4P_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_excel_adjustments_GA')
def export_excel_adjustments_GA(payload1:schemas.ExportExcelAdjustmentsGAList,payload2:schemas.ExportExcelAdjustmentsGAplanList): # pragma: no cover
    output_export_json1 =[]
    export_object = {"G&A Adj - Act":"HeadQuarters30510-2000100226"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.general_administrative_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json1.append(export_object)

    export_object = {"G&A Adj - Act":"Rhinelander30541-2798100200"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.general_administrative_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json1.append(export_object)

    export_object = {"G&A Adj - Act":"Research30548-2798100201"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.general_administrative_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json1.append(export_object)

    export_object = {"G&A Adj - Act":"Seed30516-2000100228"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.general_administrative_id==4]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json1.append(export_object)

    export_object = {"G&A Adj - Act":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.general_administrative_id==5]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json1.append(export_object)

    export_object={"G&A Adj - Act":"Total"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json1:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total/1000
        total+=sub_total
    export_object["Total"]=round(total,0)/1000
    output_export_json1.append(export_object)

    output_export_json2 =[]
    export_object = {"G&A Adj - Plan":"HeadQuarters30510-2000100226"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.general_administrative_plan_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json2.append(export_object)

    export_object = {"G&A Adj - Plan":"Rhinelander30541-2798100200"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.general_administrative_plan_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json2.append(export_object)

    export_object = {"G&A Adj - Plan":"Research30548-2798100201"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.general_administrative_plan_id==4]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json2.append(export_object)

    export_object = {"G&A Adj - Plan":"Seed30516-2000100228"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.general_administrative_plan_id==5]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json2.append(export_object)

    export_object = {"G&A Adj - Plan":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.general_administrative_plan_id==6]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,0)/1000
    output_export_json2.append(export_object)

    export_object={"G&A Adj - Plan":"Total"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json2:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total/1000
        total+=sub_total
    export_object["Total"]=round(total,0)/1000
    output_export_json2.append(export_object)

    export_object={"G&A Adj - Plan":"Delta Total- G&A expense"}
    total=0
    for pr in range(1,14):
        filtered_object_1 = [item for item in output_export_json1 if item["G&A Adj - Act"]=="Total"]
        filtered_object_2 = [item for item in output_export_json2 if item["G&A Adj - Plan"]=="Total"]
        export_object[f"P{pr}"]=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
        total+=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
    export_object["Total"]=round(total,0)
    output_export_json2.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df1 = pd.DataFrame(output_export_json1)
    df2 = pd.DataFrame(output_export_json2)
    file_name = f"Adjustments_GA_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name='Sheet1',startrow=0, header=True)
        writer.sheets['Sheet1'].append([])
        df2.to_excel(writer, index=False, sheet_name='Sheet1', startrow=len(df1)+2, header=True)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_excel_adjustments_BTL')
def export_excel_adjustments_BTL(payload1:schemas.ExportExcelAdjustmentsBTLList,payload2:schemas.ExportExcelAdjustmentsBTLplanList): # pragma: no cover
    output_export_json1 =[]
    export_object = {"BTL - Act":"BTL(+)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.btl_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json1.append(export_object)

    export_object = {"BTL - Act":"BTL(-)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.btl_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json1.append(export_object)

    export_object = {"BTL - Act":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.btl_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json1.append(export_object)

    export_object={"BTL - Act":"Total BTL"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json1:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json1.append(export_object)

    output_export_json2 =[]
    export_object = {"BTL - Plan":"BTL(+)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.btl_plan_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json2.append(export_object)

    export_object = {"BTL - Plan":"BTL(-)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.btl_plan_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json2.append(export_object)

    export_object = {"BTL - Plan":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.btl_plan_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json2.append(export_object)

    export_object={"BTL - Plan":"Total BTL- Plan"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json2:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json2.append(export_object)

    export_object={"BTL - Plan":"Delta Total- BTL"}
    total=0
    for pr in range(1,14):
        filtered_object_1 = [item for item in output_export_json1 if item["BTL - Act"]=="Total BTL"]
        filtered_object_2 = [item for item in output_export_json2 if item["BTL - Plan"]=="Total BTL- Plan"]
        export_object[f"P{pr}"]=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
        total+=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
    export_object["Total"]=round(total,0)
    output_export_json2.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df1 = pd.DataFrame(output_export_json1)
    df2 = pd.DataFrame(output_export_json2)
    file_name = f"Adjustments_BTL_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name='Sheet1',startrow=0, header=True)
        writer.sheets['Sheet1'].append([])
        df2.to_excel(writer, index=False, sheet_name='Sheet1', startrow=len(df1)+2, header=True)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_excel_adjustments_Productivity')
def export_excel_adjustments_Productivity(payload1:schemas.ExportExcelAdjustmentsProductivityList,payload2:schemas.ExportExcelAdjustmentsProductivityPlanList): # pragma: no cover
    output_export_json1 =[]
    export_object = {"Productivity - Act":"Productivity - Task"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.productivity_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json1.append(export_object)

    export_object = {"Productivity - Act":"Productivity Gross"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.productivity_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json1.append(export_object)

    export_object = {"Productivity - Act":"Productivity-net"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.productivity_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json1.append(export_object)

    export_object = {"Productivity - Act":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr and item.productivity_task_id==4]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json1.append(export_object)

    export_object={"Productivity - Act":"Total Productivity"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json1:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json1.append(export_object)

    output_export_json2 =[]
    export_object = {"Productivity-Plan":"Productivity - Task"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.productivity_plan_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json2.append(export_object)

    export_object = {"Productivity-Plan":"Productivity Gross"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.productivity_plan_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json2.append(export_object)

    export_object = {"Productivity-Plan":"Productivity-net"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.productivity_plan_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json2.append(export_object)

    export_object = {"Productivity-Plan":"Others"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.productivity_plan_task_id==4]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,0)
        total+=round(filtered_payload[0].value,0)
    export_object["Total"]=round(total,2)
    output_export_json2.append(export_object)

    export_object={"Productivity-Plan":"Total productivity-Plan"}
    total=0
    for pr in range(1,14):
        sub_total=0
        for oej in output_export_json2:
            sub_total+=oej[f"P{pr}"]
        export_object[f"P{pr}"]=sub_total
        total+=sub_total
    export_object["Total"]=round(total,0)
    output_export_json2.append(export_object)

    export_object={"Productivity-Plan":"Delta Total Productivity"}
    total=0
    for pr in range(1,14):
        filtered_object_1 = [item for item in output_export_json1 if item["Productivity - Act"]=="Total Productivity"]
        filtered_object_2 = [item for item in output_export_json2 if item["Productivity-Plan"]=="Total productivity-Plan"]
        export_object[f"P{pr}"]=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
        total+=filtered_object_1[0][f"P{pr}"]-filtered_object_2[0][f"P{pr}"]
    export_object["Total"]=round(total,0)
    output_export_json2.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df1 = pd.DataFrame(output_export_json1)
    df2 = pd.DataFrame(output_export_json2)
    file_name = f"Adjustments_Productivity_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name='Sheet1',startrow=0, header=True)
        writer.sheets['Sheet1'].append([])
        df2.to_excel(writer, index=False, sheet_name='Sheet1', startrow=len(df1)+2, header=True)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_Freight_Rates_vendor_site')
def export_Freight_Rates_vendor_site(periods:List[str],payload:schemas.ExportExcelAFreightRateVendorSiteCodeList): # pragma: no cover
    output_export_json =[]
    period_list = dynamicPeriodOnlySchemaCreator(periods)
    for pld in payload.data:
        export_object ={"Vendor Code":pld.Vendor_Site_Code,
                        "G.Area":pld.growing_area,
                        "Plants":pld.plant_name,
                        "Miles":pld.miles}
        for pl in period_list:
            filtered_payload = [
                item for item in payload.data
                if str(item.period) == str(pl["dynamic_period"]) and item.Vendor_Site_Code==pld.Vendor_Site_Code and item.plant_name==pld.plant_name
            ]
            export_object[f"{pl['dynamic_period_with_P']}-Rate"]=filtered_payload[0].rate
            export_object[f"{pl['dynamic_period_with_P']}-RT"]=filtered_payload[0].round_trip
            export_object[f"{pl['dynamic_period_with_P']}-Fuel_CF"]=filtered_payload[0].fuel_cf
        output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Freight_Rates_Vendor_site_code_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_freight_rate_period')
def export_freight_rate_period(periods:List[str],payload:schemas.ExportExcelFreightRateperiodList): # pragma: no cover
    unique_plants =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list = dynamicPeriodOnlySchemaCreator(periods)
    output_export_json = []
    for up in unique_plants:
        export_object = {"Plant Name":up}
        total_forecast_dollar_bymcwt=0
        total_forecast_total_dollar_spend=0
        total_actual_dollar_bymcwt=0
        total_actual_total_dollar_spend=0
        for pl in period_list:
            filtered_payload = [
                item for item in payload.data
                if str(item.period) == str(pl["dynamic_period"]) and item.plant_name==up
            ]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=filtered_payload[0].forecast_dollar_bymcwt
                total_forecast_dollar_bymcwt+=filtered_payload[0].forecast_dollar_bymcwt
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=filtered_payload[0].forecast_total_dollar_spend
                total_forecast_total_dollar_spend+=filtered_payload[0].forecast_total_dollar_spend
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=filtered_payload[0].actual_dollar_bymcwt
                total_actual_dollar_bymcwt+=filtered_payload[0].actual_dollar_bymcwt
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].actual_total_dollar_spend
                total_actual_total_dollar_spend+=filtered_payload[0].actual_total_dollar_spend
        export_object["total-Plan-$/MCWT"]=total_forecast_dollar_bymcwt
        export_object["total--Plan-Total$"]=total_forecast_total_dollar_spend
        export_object["total-Actual-$/MCWT"]=total_actual_dollar_bymcwt
        export_object["total-Actual-Total$"]=total_forecast_total_dollar_spend
        output_export_json.append(export_object)
        dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Freight_Rates_Period_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_freight_rate_week')
def export_freight_rate_week(periods:List[str],payload:schemas.ExportExcelFreightRateweekList): # pragma: no cover
    unique_plants =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list = dynamicPeriodSchemaCreator(periods)
    output_export_json = []
    for up in unique_plants:
        export_object = {"Plant Name":up}
        total_forecast_dollar_bymcwt=0
        total_forecast_total_dollar_spend=0
        total_actual_dollar_bymcwt=0
        total_actual_total_dollar_spend=0
        for pl in period_list:
            filtered_payload = [
                item for item in payload.data
                if str(item.period) == str(pl["dynamic_period"]) and str(item.week_no) == str(pl["dynamic_week"]) and item.plant_name==up
            ]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=filtered_payload[0].forecast_dollor_cwt
                total_forecast_dollar_bymcwt+=filtered_payload[0].forecast_dollor_cwt
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=filtered_payload[0].forecast_spend_week
                total_forecast_total_dollar_spend+=filtered_payload[0].forecast_spend_week
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=filtered_payload[0].actual_dollor_MCWT_week
                total_actual_dollar_bymcwt+=filtered_payload[0].actual_dollor_MCWT_week
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].Total_dollor_spend_week
                total_actual_total_dollar_spend+=filtered_payload[0].Total_dollor_spend_week
        export_object["total-Plan-$/MCWT"]=total_forecast_dollar_bymcwt
        export_object["total--Plan-Total$"]=total_forecast_total_dollar_spend
        export_object["total-Actual-$/MCWT"]=total_actual_dollar_bymcwt
        export_object["total-Actual-Total$"]=total_forecast_total_dollar_spend
        output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Freight_Rates_Week_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_freight_growing_area')
def export_freight_growing_area(payload:schemas.ExportExcelFreightRateGrowingAreaList): # pragma: no cover
    unique_growing_area =  sorted(list(set([entry.plant_name for entry in payload.data])))
    output_export_json = []
    for uga in unique_growing_area:
        export_object={"Destination":uga}
        for pl in range(1,14):
            filtered_payload = [item for item in payload.data if item.plant_name==uga and item.period==pl]
            if len(filtered_payload)>0:
                 
                 export_object["Origin"]=filtered_payload[0].growing_area_name
                 export_object[f"P{pl}|Plan"]=filtered_payload[0].rate_plan
                 export_object[f"P{pl}|Actual"]=filtered_payload[0].rate_actual
        output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Freight_Rates_GrowingArea_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/Export_Excel_PotatoRates_GrowingArea_period')
def Export_Excel_PotatoRates_GrowingArea_period(periods:List[str],payload:schemas.ExportExcelPotatoRatesGrowingAreaPeriodList): # pragma: no cover
    unique_growing_area =  sorted(list(set([entry.growing_area_name for entry in payload.data])))
    period_list = dynamicPeriodOnlySchemaCreator(periods)
    output_export_json = []
    for uga in unique_growing_area:
        total_forecast_dollar_bymcwt=0
        total_forecast_total_dollar_spend=0
        total_actual_dollar_bymcwt=0
        total_actual_total_dollar_spend=0
        export_object={"Growing Area":uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.growing_area_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=filtered_payload[0].fcst_rate
                total_forecast_dollar_bymcwt+=filtered_payload[0].fcst_rate
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].fcst_total_dollor,0)
                total_forecast_total_dollar_spend+=round(filtered_payload[0].fcst_total_dollor,0)
                if filtered_payload[0].actual_volume==0:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                else:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_total_dollor/filtered_payload[0].actual_volume,2)
                    total_actual_dollar_bymcwt+=round(filtered_payload[0].actual_total_dollor/filtered_payload[0].actual_volume,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].actual_total_dollor
                total_actual_total_dollar_spend+=filtered_payload[0].actual_total_dollor
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0

        export_object["total-Plan-$/MCWT"]=total_forecast_dollar_bymcwt
        export_object["total--Plan-Total$"]=total_forecast_total_dollar_spend
        export_object["total-Actual-$/MCWT"]=total_actual_dollar_bymcwt
        export_object["total-Actual-Total$"]=total_actual_total_dollar_spend
        output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Potatorates_GrowingArea_period_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/Export_Excel_PotatoRates_GrowingArea_week')
def Export_Excel_PotatoRates_GrowingArea_week(periods:List[str],payload:schemas.ExportExcelPotatoRatesGrowingAreaWeekList): # pragma: no cover
    unique_growing_area =  sorted(list(set([entry.growing_area_name for entry in payload.data])))
    period_list = dynamicPeriodSchemaCreator(periods)
    output_export_json = []
    for uga in unique_growing_area:
        total_forecast_dollar_bymcwt=0
        total_forecast_total_dollar_spend=0
        total_actual_dollar_bymcwt=0
        total_actual_total_dollar_spend=0
        export_object={"Growing Area":uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.growing_area_name==uga and str(item.period) == str(pl["dynamic_period"]) and  str(item.week)==str(pl["dynamic_week"])] 
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=filtered_payload[0].rate
                total_forecast_dollar_bymcwt+=filtered_payload[0].rate
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].forecaste_total_dollor,0)
                total_forecast_total_dollar_spend+=round(filtered_payload[0].forecaste_total_dollor,0)
                if filtered_payload[0].actual_volume==0:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                else:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_total_dollor/filtered_payload[0].actual_volume,2)
                    total_actual_dollar_bymcwt+=round(filtered_payload[0].actual_total_dollor/filtered_payload[0].actual_volume,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].actual_total_dollor
                total_actual_total_dollar_spend+=filtered_payload[0].actual_total_dollor
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0

        export_object["total-Plan-$/MCWT"]=total_forecast_dollar_bymcwt
        export_object["total--Plan-Total$"]=total_forecast_total_dollar_spend
        export_object["total-Actual-$/MCWT"]=total_actual_dollar_bymcwt
        export_object["total-Actual-Total$"]=total_actual_total_dollar_spend
        output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Potatorates_GrowingArea_week_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )


@router.post('/Export_Excel_PotatoRates_plantview_period')
def Export_Excel_PotatoRates_plantview_period(periods:List[str],payload:schemas.ExportExcelPotatoRatesPlantViewPeriodList): # pragma: no cover      
    unique_plant =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list = dynamicPeriodOnlySchemaCreator(periods)
    output_export_json = []
    for uga in unique_plant:
        total_forecast_dollar_bymcwt=0
        total_forecast_total_dollar_spend=0
        total_actual_dollar_bymcwt=0
        total_actual_total_dollar_spend=0
        export_object={"Plant Name":uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=filtered_payload[0].forecast_dollar_bymcwt
                total_forecast_dollar_bymcwt+=filtered_payload[0].forecast_dollar_bymcwt
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].forecast_total_dollar_spend,0)
                total_forecast_total_dollar_spend+=round(filtered_payload[0].forecast_total_dollar_spend,0)
                if filtered_payload[0].actual_volume==0:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                else:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_dollar_bymcwt,2)
                    total_actual_dollar_bymcwt+=round(filtered_payload[0].actual_dollar_bymcwt,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=round(filtered_payload[0].actual_total_dollar_spend,0)
                total_actual_total_dollar_spend+=round(filtered_payload[0].actual_total_dollar_spend,0)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0

        export_object["total-Plan-$/MCWT"]=total_forecast_dollar_bymcwt
        export_object["total--Plan-Total$"]=total_forecast_total_dollar_spend
        export_object["total-Actual-$/MCWT"]=total_actual_dollar_bymcwt
        export_object["total-Actual-Total$"]=total_actual_total_dollar_spend
        output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Potatorates_PlantView_period_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/Export_Excel_PotatoRates_PlantView_Week')
def Export_Excel_PotatoRates_PlantView_Week(periods:List[str],payload:schemas.ExportExcelPotatoRatesPlantViewWeekList): # pragma: no cover
    unique_plant =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list = dynamicPeriodSchemaCreator(periods)
    output_export_json = []
    for uga in unique_plant:
        total_forecast_dollar_bymcwt=0
        total_forecast_total_dollar_spend=0
        total_actual_dollar_bymcwt=0
        total_actual_total_dollar_spend=0
        export_object={"Plant Name":uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"]) and str(item.week_no)==str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=filtered_payload[0].forecast_dollor_cwt
                total_forecast_dollar_bymcwt+=filtered_payload[0].forecast_dollor_cwt
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].forecast_spend_week,0)
                total_forecast_total_dollar_spend+=round(filtered_payload[0].forecast_spend_week,0)
                if filtered_payload[0].actual_volume==0:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                else:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_dollor_MCWT_week,2)
                    total_actual_dollar_bymcwt+=round(filtered_payload[0].actual_dollor_MCWT_week,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=round(filtered_payload[0].Total_dollor_spend_week,0)
                total_actual_total_dollar_spend+=round(filtered_payload[0].Total_dollor_spend_week,0)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0

        export_object["total-Plan-$/MCWT"]=total_forecast_dollar_bymcwt
        export_object["total--Plan-Total$"]=total_forecast_total_dollar_spend
        export_object["total-Actual-$/MCWT"]=total_actual_dollar_bymcwt
        export_object["total-Actual-Total$"]=total_actual_total_dollar_spend
        output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Potatorates_PlantView_week_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_excel_solids_growingarea')
def export_excel_solids_growingarea(periods:List[str],payload:schemas.ExportExcelSolidsGrowingAreaViewList): # pragma: no cover
    unique_growing_area =  list(set([entry.growing_area_name for entry in payload.data]))
    period_list = dynamicPeriodOnlySchemaCreator(periods)
    output_export_json = []
    for uga in unique_growing_area:
        export_object= {"Growing Area":uga}
        total_plan=0
        total_actual=0
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.growing_area_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload[0].plan_rate,2)
                total_plan += round(filtered_payload[0].plan_rate,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=round(filtered_payload[0].actual_rate,2)
                total_actual += round(filtered_payload[0].actual_rate,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=0
        count_plan = sum(1 for key, value in export_object.items() if 'Plan' in key and value != 0)
        if count_plan>0:
            export_object["Total plan"]=total_plan/count_plan
        else:
            export_object["Total plan"]=0
        count_act = sum(1 for key, value in export_object.items() if 'Actual' in key and value != 0)
        if count_act>0:
            export_object["Total actual"]=total_actual/count_act
        else:
            export_object["Total actual"]=0
        output_export_json.append(export_object)
    
    export_object={"Growing Area":"Total"}
    total_plan=0
    total_actual=0
    for pl in period_list:
        sub_total_plan=0
        sub_total_act=0
        for oej in output_export_json:
            sub_total_plan+=oej[f"{pl['dynamic_period_with_P']}-Plan"]
            sub_total_act+=oej[f"{pl['dynamic_period_with_P']}-Actual"]
        count_plan=len([item for item in output_export_json if item.get(f"{pl['dynamic_period_with_P']}-Plan") != 0])
        if count_plan>0:
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=sub_total_plan/count_plan
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=0
        count_act=len([item for item in output_export_json if item.get(f"{pl['dynamic_period_with_P']}-Actual") != 0])
        if count_act>0:
            export_object[f"{pl['dynamic_period_with_P']}-Actual"]=sub_total_act/count_act
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Actual"]=0

    for oej in output_export_json:
        total_plan+=oej["Total plan"]
        total_actual+=oej["Total actual"]
    export_object["Total plan"]=total_plan/len(output_export_json)
    export_object["Total actual"]=total_actual/len(output_export_json)
    output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Solids_GrowingArea{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/export_excel_solids_plant')
def export_excel_solids_plant(periods:List[str],payload:schemas.ExportExcelSolidsPlantViewList): # pragma: no cover
    unique_plant =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list = dynamicPeriodOnlySchemaCreator(periods)
    output_export_json = []
    for uga in unique_plant:
        export_object= {"Plant Name":uga}
        total_plan=0
        total_actual=0
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload[0].forecast_solids,2)
                total_plan += round(filtered_payload[0].forecast_solids,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=round(filtered_payload[0].actual_solids,2)
                total_actual += round(filtered_payload[0].actual_solids,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=0
        export_object["Total plan"]=total_plan/len(period_list)
        export_object["Total actual"]=total_actual/len(period_list)
        output_export_json.append(export_object)
    
    export_object={"Plant Name":"Total"}
    total_plan=0
    total_actual=0
    for pl in period_list:
        sub_total_plan=0
        sub_total_act=0
        for oej in output_export_json:
            sub_total_plan+=oej[f"{pl['dynamic_period_with_P']}-Plan"]
            sub_total_act+=oej[f"{pl['dynamic_period_with_P']}-Actual"]
        export_object[f"{pl['dynamic_period_with_P']}-Plan"]=sub_total_plan/len(output_export_json)
        export_object[f"{pl['dynamic_period_with_P']}-Actual"]=sub_total_act/len(output_export_json)
    for oej in output_export_json:
        total_plan+=oej["Total plan"]
        total_actual+=oej["Total actual"]
    export_object["Total plan"]=total_plan/len(output_export_json)
    export_object["Total actual"]=total_actual/len(output_export_json)

    
    output_export_json.append(export_object)
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Solids_Plant_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )




@router.post('/export_finance_summary_solids')
def export_finance_summary_solids(payload:schemas.ExportExcelFinanceSummarySolidsList): # pragma: no cover
    output_export_json=[]
    export_object = {"Solids":"Prior"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].prior,2)
        total+=round(filtered_payload[0].prior,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Plan"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].plan,2)
        total+=round(filtered_payload[0].plan,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Forecast"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].forecast,2)
        total+=round(filtered_payload[0].forecast,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Fcst/Act"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].fcst_act,2)
        total+=round(filtered_payload[0].fcst_act,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"+/(-) VS Plan"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].fore_plan,2)
        total+=round(filtered_payload[0].fore_plan,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Index VS Plan"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].yag_index,2)
        total+=round(filtered_payload[0].yag_index,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"M$Imp B/(W) Plan"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].m_dollar_impact_plan,3)
        total+=round(filtered_payload[0].m_dollar_impact_plan,3)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"M$Imp B/(W) Plan"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].m_dollar_impact,3)
        total+=round(filtered_payload[0].m_dollar_impact,3)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Delta M$ Imp"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].delta_m_imp,2)
        total+=round(filtered_payload[0].delta_m_imp,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Conv. Factor"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].conversion_factor,2)
        total+=round(filtered_payload[0].conversion_factor,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Finance_solids_summary_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    
@router.post('/Export_Home_Pop_Up')
def Export_Home_Pop_Up(payload1:schemas.ExportExcelHomePopUpList,payload2:schemas.ExportExcelHomePopUpPlanList,periods:List[str]): # pragma: no cover
     period_list = dynamicPeriodSchemaCreator(periods)
     output_export_json1=[]
     output_export_json2=[]
     export_object ={"BU-Act":"FLUS"}
     total=0
     for pl in period_list:
            filtered_payload = [item for item in payload1.data if item.category_name=="FLUS" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
             export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
             total+=filtered_payload[0].volume
            else:
             export_object[pl['dynamic_period_with_P']]=0
     export_object["Total"] =total     
     output_export_json1.append(export_object)

     export_object ={"BU-Act":"Co-Man"}
     total=0
     for pl in period_list:
            filtered_payload = [item for item in payload1.data if item.category_name=="Co-Man" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
             export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
             total+=filtered_payload[0].volume
            else:
             export_object[pl['dynamic_period_with_P']]=0
     export_object["Total"] =total 
     output_export_json1.append(export_object)

     

     export_object ={"BU-Act":"FLC"}
     total=0
     for pl in period_list:
            filtered_payload = [item for item in payload1.data if item.category_name=="FLC" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
             export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
             total+=filtered_payload[0].volume
            else:
             export_object[pl['dynamic_period_with_P']]=0
     export_object["Total"] =total 
     output_export_json1.append(export_object)

     export_object ={"BU-Plan":"FLUS"}
     total=0
     for pl in period_list:
            filtered_payload = [item for item in payload2.data if item.category_name=="FLUS" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
             export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
             total+=filtered_payload[0].volume
            else:
             export_object[pl['dynamic_period_with_P']]=0
     export_object["Total"] =total
     output_export_json2.append(export_object)

     export_object ={"BU-Plan":"Co-Man"}
     total=0
     for pl in period_list:
            filtered_payload = [item for item in payload2.data if item.category_name=="Co-Man" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
             export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
             total+=filtered_payload[0].volume
            else:
             export_object[pl['dynamic_period_with_P']]=0
     export_object["Total"] =total
     output_export_json2.append(export_object)

     export_object ={"BU-Plan":"FLC"}
     total=0
     for pl in period_list:
            filtered_payload = [item for item in payload2.data if item.category_name=="FLC" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
             export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
             total+=filtered_payload[0].volume
            else:
             export_object[pl['dynamic_period_with_P']]=0
     export_object["Total"] =total
     output_export_json2.append(export_object)

     dt = datetime.now()
     str_date = dt.strftime("%d%m%y%H%M%S")
     df1 = pd.DataFrame(output_export_json1)
     df2 = pd.DataFrame(output_export_json2)
     file_name = f"Homepopup_{str_date}.xlsx"
     output = BytesIO()
     with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name='Sheet1',startrow=0, header=True)
        writer.sheets['Sheet1'].append([])
        df2.to_excel(writer, index=False, sheet_name='Sheet1', startrow=len(df1)+2, header=True)
     output.seek(0)
     return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

@router.post('/Export_active_allocation_index')
def Export_active_allocation_index(payload:schemas.ExportExcelActiveAllocationIndexList): # pragma: no cover
    output_export_json =[]
    export_object = {"Country":"Co-Man"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.category_name=="Co-Man" and item.period==pl]
        if len(filtered_payload)>0:
          export_object[f"P{pl}"]=filtered_payload[0].value
          total+=filtered_payload[0].value
    export_object["FY"]=total/13
    output_export_json.append(export_object)

    export_object = {"Country":"FLC"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.category_name=="FLC" and item.period==pl]
        if len(filtered_payload)>0:
          export_object[f"P{pl}"]=filtered_payload[0].value
          total+=filtered_payload[0].value
    export_object["FY"]=total/13
    output_export_json.append(export_object)

    export_object = {"Country":"FLUS"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.category_name=="FLUS" and item.period==pl]
        if len(filtered_payload)>0:
          export_object[f"P{pl}"]=filtered_payload[0].value
          total+=filtered_payload[0].value
    export_object["FY"]=total/13
    output_export_json.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Active_allocation_index_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )


@router.post('/export_forecast_week')
def export_forecast_week(periods:List[str],payload:schemas.ExportExcelForecastWeekList): # pragma: no cover
    unique_plants =  sorted(list(set([entry.plant_name for entry in payload.data])))
    period_list =dynamicPeriodSchemaCreator(periods)
    output_export_json = []
    for up in unique_plants:
        export_object={"plant_name":up}
        filtered_payload = [item for item in payload.data if item.plant_name==up]
        total_act =0
        total_fore=0
        total_delta=0
        for pl in period_list:
            filtered_payload_period = [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"]) 
            ]
            
            export_object[f"{pl['dynamic_period_with_P']}-Act"]=round(filtered_payload_period[0].forecasted_value)
            total_fore+=round(filtered_payload_period[0].forecasted_value)
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload_period[0].total_actual_value)
            total_act+=round(filtered_payload_period[0].total_actual_value)
            export_object[f"{pl['dynamic_period_with_P']}-Diff"]=round(filtered_payload_period[0].forecasted_value)-round(filtered_payload_period[0].total_actual_value)
            total_delta+=round(filtered_payload_period[0].forecasted_value)-round(filtered_payload_period[0].total_actual_value)
            
        export_object["Total_plan"]=total_fore
        export_object["Total_Act"]=total_act
        export_object["Total_Delta"]=total_delta
        output_export_json.append(export_object)
    
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"forecast_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )









