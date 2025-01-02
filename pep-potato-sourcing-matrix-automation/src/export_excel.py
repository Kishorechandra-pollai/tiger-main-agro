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
    






