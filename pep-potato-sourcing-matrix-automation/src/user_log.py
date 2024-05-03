import csv
import io
import models
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
import schemas
from database import get_db

router = APIRouter()


@router.post('/', status_code=status.HTTP_201_CREATED)  # pragma: no cover
def user_log(payload: schemas.UserlogSchema, db: Session = Depends(get_db)):
    try:
        new_user_log = models.user_log(**payload.dict())
        db.add(new_user_log)
        db.commit()
        return {"status": "success", "result": "User log added Successfully !"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/get_last_30_days_log')  # pragma: no cover
def get_user_log(db: Session = Depends(get_db)):
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)

        records = db.query(models.user_log) \
            .filter(models.user_log.date >= thirty_days_ago.date()).all()
        return {"status": "success", "user_log": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/export_last_30_days')  # pragma: no cover
def export_last_30_days(db: Session = Depends(get_db)):
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)

        records = db.query(models.user_log) \
            .filter(models.user_log.date >= thirty_days_ago.date()).all()

        # Prepare CSV data
        csv_data = []
        for record in records:
            csv_data.append([record.id, record.email, record.date_time, record.date])

        # Generate CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'email', 'login-ddate-time', 'date'])
        writer.writerows(csv_data)

        # Create a streaming response for downloading the CSV file
        output.seek(0)
        csv_bytes = output.getvalue().encode('utf-8')
        return StreamingResponse(iter([csv_bytes]), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=last_30_days_records.csv"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
