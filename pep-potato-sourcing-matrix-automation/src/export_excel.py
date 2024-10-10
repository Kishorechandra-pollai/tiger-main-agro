from fastapi import APIRouter,Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime
import pandas as pd
import os
import schemas
import models


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
    df.to_excel(file_name,index=False)
    return FileResponse(
        path=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )


