from fastapi import APIRouter,Body,HTTPException, status, Depends, Query
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
from fastapi.security import HTTPBearer
import json
from typing import Optional


router = APIRouter()





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
    






