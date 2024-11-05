from fastapi import APIRouter,Body,HTTPException, status
from fastapi.responses import FileResponse,StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime
import pandas as pd
from pathlib import Path
import os
import schemas
import models
from io import BytesIO
import asyncio

SAVE_DIRECTORY = "saved_files"
Path(SAVE_DIRECTORY).mkdir(parents=True, exist_ok=True)
files_in_memory = {}
file_json = {}
router = APIRouter()
@router.get('/test')
def test_export(): # pragma: no cover
    return({"test":"succesful_passed"})

@router.post('/download_finance_summary_solids_new') 
def download_finance_summary_solids_new(payload:schemas.ExportExcelFinanceSummarySolidsList):# pragma: no cover
     dt = datetime.now()
     str_date = dt.strftime("%d%m%y%H%M%S")
     df = pd.DataFrame([item.dict() for item in payload.data])
     file_name = f"finance_summary_solids_{str_date}.xlsx"
     output = BytesIO()
     with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
     output.seek(0)
     files_in_memory[file_name] = output.getvalue()
     return {"download_url": f"<base_url>/api/export_excel/export_finance_summary_solids_new/{file_name}",
             "file name":file_name,
             "current_files": {k: len(v) for k, v in files_in_memory.items()}}


@router.get('/export_finance_summary_solids_new/{file_name}')
async def export_finance_summary_solids_new(file_name:str,retry:int=0): # pragma: no cover
     file_content = files_in_memory.get(file_name)
     file_new_temp=file_name
     retry_temp=retry
    
     if file_content:
        output = BytesIO(file_content)
        return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={file_new_temp}"}
            )
     if(retry_temp<10):
          await asyncio.sleep(1)
          return await export_finance_summary_solids_new(file_new_temp,retry_temp+1)


@router.post('/export_finance_summary_solids')
def export_finance_summary_solids(payload:schemas.ExportExcelFinanceSummarySolidsList): # pragma: no cover
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame([item.dict() for item in payload.data])
    file_name = f"finance_summary_solids_{str_date}.xlsx"
    file_path = os.path.join(SAVE_DIRECTORY, file_name)
    df.to_excel(file_path,index=False)
    download_link = f"https://<server_url>/api/export_excel/download_finance_summary_solids/{file_name}"
    return {"download_link":download_link,"file_name":file_name}

@router.get('/download_finance_summary_solids/{file_name}') # pragma: no cover
def download_finance_summary_solids(file_name:str):
    file_path = os.path.join(SAVE_DIRECTORY, file_name)
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post('/export_finance_summary_solids_two')
def export_finance_summary_solids_two(payload:schemas.ExportExcelFinanceSummarySolidsList): # pragma: no cover
     file_json["data"] = payload.data
     return{"file_json":file_json}

@router.get('/download_finance_summary_solids_two')
def download_finance_summary_solids_two(): # pragma: no cover
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    file_name = f"finance_summary_solids_{str_date}.xlsx"
    df = pd.DataFrame(file_json["data"])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={file_name}"}
            )
        





