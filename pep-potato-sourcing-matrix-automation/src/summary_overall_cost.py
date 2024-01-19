"""Summary Overall Cost  API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import (summary_overall_cost,summary_total_exp_wo_solids
,summary_total_exp_w_solids,summary_material_spend,summary_freight_spend,
summary_overall_cost_solids,summary_category_spend)
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/year/{year}/company_name/{company_name}')
def summary_overall_cost_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_overall_cost view based on year and country_Code filter """
    try:
        records = db.query(summary_overall_cost).filter(
            summary_overall_cost.columns.year == year,
            summary_overall_cost.columns.company_name == company_name
            ).order_by(summary_overall_cost.columns.period).all()
        return {"summary_overall_cost": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('total_exp_wo_solids/year/{year}/company_name/{company_name}')
def summary_total_exp_wo_solids_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_total_exp_wo_solids view based on year and country_Code filter """
    try:
        records = db.query(summary_total_exp_wo_solids).filter(
            summary_total_exp_wo_solids.columns.year == year,
            summary_total_exp_wo_solids.columns.company_name == company_name
            ).order_by(summary_total_exp_wo_solids.columns.period).all()
        return {"summary_total_exp_wo_solids": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('total_exp_w_solids/year/{year}/company_name/{company_name}')
def summary_total_exp_w_solids_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_total_exp_wo_solids view based on year and country_Code filter """
    try:
        records = db.query(summary_total_exp_w_solids).filter(
            summary_total_exp_w_solids.columns.year == year,
            summary_total_exp_w_solids.columns.company_name == company_name
            ).order_by(summary_total_exp_w_solids.columns.period).all()
        return {"summary_total_exp_w_solids": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('overall_cost_material_spend/year/{year}/company_name/{company_name}')
def summary_material_spend_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_material_spend view based on year and country_Code filter """
    try:
        records = db.query(summary_material_spend).filter(
            summary_material_spend.columns.year == year,
            summary_material_spend.columns.company_name == company_name
            ).order_by(summary_material_spend.columns.period).all()
        return {"summary_material_spend": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('overall_cost_freight_spend/year/{year}/company_name/{company_name}')
def summary_freight_spend_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_freight_spend view based on year and country_Code filter """
    try:
        records = db.query(summary_freight_spend).filter(
            summary_freight_spend.columns.year == year,
            summary_freight_spend.columns.company_name == company_name
            ).order_by(summary_freight_spend.columns.period).all()
        return {"summary_freight_spend": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('overall_cost_solids/year/{year}/company_name/{company_name}')
def summary_overall_cost_solids_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_overall_cost_solids view based on year and country_Code filter """
    try:
        records = db.query(summary_overall_cost_solids).filter(
            summary_overall_cost_solids.columns.year == year,
            summary_overall_cost_solids.columns.company_name == company_name
            ).order_by(summary_overall_cost_solids.columns.period).all()
        return {"summary_overall_cost_solids": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('overall_cost_category_spend/year/{year}/company_name/{company_name}')
def summary_category_spend_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch all records from summary_overall_cost_solids view based on year and country_Code filter """
    try:
        records = db.query(summary_category_spend).filter(
            summary_category_spend.columns.year == year,
            summary_category_spend.columns.company_name == company_name
            ).order_by(summary_category_spend.columns.period).all()
        return {"summary_category_spend": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e