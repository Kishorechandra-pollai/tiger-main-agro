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

class DynamicSchema(BaseModel):
    Plant_name: str
    pass

class DynamicSchemaList(BaseModel):
    data: List[DynamicSchema]
@router.post('/export_test')
def dynamicPeriodSchemaCreator(periods:List[str]):
    dynamic_period_list=[]
    for items in periods:
        for weeks in range(1,5):
            dynamic_period_with_P = f"P{items}|W{weeks}"
            dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_P,"dynamic_period":items,"dynamic_week":weeks}
            dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list

def dynamicPeriodOnlySchemaCreator(periods:List[str]):
    dynamic_period_list=[]
    for items in periods:
        dynamic_period_with_P = f"P{items}"
        dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_P,"dynamic_period":items}
        dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list

def dynamicPeriodSchemaCreatorForecast(periods:List[str]):
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
    export_object["Total"]=round(total/13,2)
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







@router.post('/export_finance_summary_solids')
def export_finance_summary_solids(payload:schemas.ExportExcelFinanceSummarySolidsList): # pragma: no cover
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame([item.dict() for item in payload.data])
    file_name = f"finance_summary_solids_{str_date}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    






