from fastapi import APIRouter,Body,HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime
import pandas as pd
from pathlib import Path
import os
import schemas
import logging


SAVE_DIRECTORY = "./saved_files"
Path(SAVE_DIRECTORY).mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()
@router.get('/test')
def test_export():
    return({"test":"succesful"})

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
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )




