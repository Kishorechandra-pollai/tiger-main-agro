"""Summary Overall Cost  API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import summary_overall_cost
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/year/{year}/company_name/{company_name}')
def summary_overall_cost_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_overall_cost view based on year and country_Code filter """
    try:
        records = db.query(summary_overall_cost).filter(
            summary_overall_cost.columns.year == year,
            summary_overall_cost.columns.company_name == company_name).all()
        return {"summary_solids_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
