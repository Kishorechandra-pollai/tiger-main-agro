"""Summary Overall Cost  API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import summary_overall_cost
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/year/{year}/country_code/{country_code}')
def summary_overall_cost_year_country_code(year: int, country_code: str, db: Session = Depends(get_db)):
    """Function to fetch all records from summary_overall_cost view based on year and country_Code filter """
    try:
        records = db.query(summary_overall_cost).filter(
            summary_overall_cost.columns.year == year,
            summary_overall_cost.columns.country_code == country_code).all()
        return {"summary_solids_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
