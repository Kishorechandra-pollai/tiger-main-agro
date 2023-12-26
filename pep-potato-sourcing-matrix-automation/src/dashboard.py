"""Home - Dashboard API"""
from schemas import planVolumeUsagePayload
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import (dashboard_pc_volume_period,dashboard_weekly_combine,
                    dashboard_pc_usage_period,pc_plan_volume_usage,
                    dashboard_pc_volume_period_country_combine,
                    dashboard_pc_volume_period_country_yearly,
                    dashboard_pc_volume_yearly_country_combine)
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/dashboard_pc_volume_period')
def dashboard_pc_volume_period_view(db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_volume_period view"""
    try:
        records = db.query(dashboard_pc_volume_period).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "us_forecasted": row.us_forecasted,
                "us_actual":row.us_actual,
                "us_index_plan": row.us_index_plan,
                "canada_index_plan":row.canada_index_plan,
                "canada_forecasted": row.canada_forecasted,
                "canada_actual":row.canada_actual,
                "us_sum": row.us_sum,
                "can_sum":row.can_sum,
                "ratio_us": row.ratio_us,
                "ratio_can":row.ratio_can,
                "week":0,
                "period_with_P": f'P{row.period}'
            }
            for row in records
        ]
        return {"dashboard_pc_volume_period": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/dashboard_pc_volume_period/{year}')
def dashboard_pc_volume_period_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_volume_period view for a particular year """
    try:
        records = db.query(dashboard_pc_volume_period).filter(
            dashboard_pc_volume_period.columns.year == year).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "us_forecasted": row.us_forecasted,
                "us_actual":row.us_actual,
                "us_index_plan": row.us_index_plan,
                "canada_index_plan":row.canada_index_plan,
                "canada_forecasted": row.canada_forecasted,
                "canada_actual":row.canada_actual,
                "us_sum": row.us_sum,
                "can_sum":row.can_sum,
                "ratio_us": row.ratio_us,
                "ratio_can":row.ratio_can,
                "week":0,
                "period_with_P": f'P{row.period}'
            }
            for row in records
        ]
        return {"dashboard_pc_volume_period_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/dashboard_pc_plan_volume_usage')
def dashboard_pc_plan_volume_usage(db: Session = Depends(get_db)):
    """Function to fetch all records from plan_volume_usage table"""
    try:
        records = db.query(pc_plan_volume_usage).all()
        result = [
            {
                "crop_type": row.crop_type,
                "period": row.period,
                "week":row.week,
                "year": row.year,
                "volume": row.volume,
                "period_with_P": f'P{row.period}W{row.week}'
            }
            for row in records
        ]
        return {"dashboard_pc_plan_volume_usage": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/dashboard_pc_plan_volume_usage/{year}')
def dashboard_pc_plan_volume_usage_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_plan_volume_usage table
    for a particular year """
    try:
        records = db.query(pc_plan_volume_usage).filter(
            pc_plan_volume_usage.year == year).all()
        result = [
            {
                "crop_type": row.crop_type,
                "period": row.period,
                "week":row.week,
                "year": row.year,
                "volume": row.volume,
                "period_with_P": f'P{row.period}W{row.week}'
            }
            for row in records
        ]
        return {"dashboard_pc_plan_volume_usage_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/update_plan_volume_usage/, response_model=dict")
def update_plan_volume_usage(payload: planVolumeUsagePayload,db: Session = Depends(get_db)):
    """Function to update already existing records in dashboard_pc_plan_volume_usage table """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            result=db.query(pc_plan_volume_usage).filter(pc_plan_volume_usage.crop_type
                                                == item.crop_type,
                                                pc_plan_volume_usage.period==item.period,
                                                pc_plan_volume_usage.week==item.week,
                                                pc_plan_volume_usage.year==item.year).update(
                {pc_plan_volume_usage.volume :item.volume}, synchronize_session='fetch')
            if result == 0:
                raise HTTPException(status_code=404, detail=f"No records found: {item}")

            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/dashboard_weekly_combine')
def dashboard_weekly_combine_view(db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_weekly_combine view"""
    try:
        records = db.query(dashboard_weekly_combine).all()
        result = [
            {
                "period": row.period,
                "week": row.week,
                "year": row.year,
                "US_SUM": row.US_SUM,
                "canada_SUM":row.canada_SUM,
                "US_actual": row.US_actual,
                "canada_actual":row.canada_actual,
                "us_forecasted": row.us_forecasted,
                "canada_forecasted":row.canada_forecasted,
                "USA_DELTA": row.USA_DELTA,
                "Canada_Delta":row.Canada_Delta,
                "USA_CWT": row.USA_CWT,
                "Canada_cwt":row.Canada_cwt,
                "ratio_us": row.ratio_us,
                "ratio_canada":row.ratio_canada,
                "period_week": f'P{row.period}W{row.week}'
            }
            for row in records
        ]
        return {"dashboard_weekly_combine_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/dashboard_weekly_combine/{year}')
def dashboard_weekly_combine_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_weekly_combine view for a particular year """
    try:
        records = db.query(dashboard_weekly_combine).filter(
            dashboard_weekly_combine.columns.year == year).all()
        result = [
            {
                "period": row.period,
                "week": row.week,
                "year": row.year,
                "US_SUM": row.US_SUM,
                "canada_SUM":row.canada_SUM,
                "US_actual": row.US_actual,
                "canada_actual":row.canada_actual,
                "us_forecasted": row.us_forecasted,
                "canada_forecasted":row.canada_forecasted,
                "USA_DELTA": row.USA_DELTA,
                "Canada_Delta":row.Canada_Delta,
                "USA_CWT": row.USA_CWT,
                "Canada_cwt":row.Canada_cwt,
                "ratio_us": row.ratio_us,
                "ratio_canada":row.ratio_canada,
                "period_week": f'P{row.period}W{row.week}'
            }
            for row in records
        ]
        return {"dashboard_weekly_combine_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/pc_usage_period')
def dashboard_pc_usage_period_view(db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_usage_period view"""
    try:
        records = db.query(dashboard_pc_usage_period).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "country":row.Country,
                "plan": row.sum_forecasted_value,
                "actuals":row.sum_total_actual_value,
                "Index_v/s_plan": row.index_plan,
                "week":0,
                "period_with_P": f'P{row.period}'
            }
            for row in records
        ]
        return {"dashboard_pc_usage_period_view": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/pc_usage_period view"/{year}/{country}')
def dashboard_pc_period_view_year_country(year:int,country:str, db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_volume_period view for a particular year """
    try:
        records = db.query(dashboard_pc_usage_period).filter(
            dashboard_pc_usage_period.columns.year == year,
            dashboard_pc_usage_period.columns.Country == country).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "country":row.Country,
                "plan": row.sum_forecasted_value,
                "actuals":row.sum_total_actual_value,
                "Index_v/s_plan": row.index_plan,
                "week":0,
                "period_with_P": f'P{row.period}'
            }
            for row in records
        ]
        return {"dashboard_pc_usage_period_view_year_country": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/pc_volume_period_country_combine')
def pc_volume_period_country_combine(db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_volume_period_country_combine view"""
    try:
        records = db.query(dashboard_pc_volume_period_country_combine).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "US_forecasted":row.US_forecasted,
                "US_actual": row.US_actual,
                "US_index_plan":row.US_index_plan,
                "Canada_forecasted":row.Canada_forecasted,
                "Canada_actual": row.Canada_actual,
                "Canada_index_plan":row.Canada_index_plan,
                "week":0,
                "period_with_P": f'P{row.period}'
            }
            for row in records
        ]
        return {"dashboard_pc_volume_period_country_combine": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/pc_volume_period_country_combine"/{year}')
def pc_volume_period_country_combine_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from
    dashboard_pc_volume_period_country_combine view for a particular year """
    try:
        records = db.query(dashboard_pc_volume_period_country_combine).filter(
            dashboard_pc_volume_period_country_combine.columns.year == year).all()
        result = [
            {
                "period": row.period,
                "year": row.year,
                "US_forecasted":row.US_forecasted,
                "US_actual": row.US_actual,
                "US_index_plan":row.US_index_plan,
                "Canada_forecasted":row.Canada_forecasted,
                "Canada_actual": row.Canada_actual,
                "Canada_index_plan":row.Canada_index_plan,
                "week":0,
                "period_with_P": f'P{row.period}'
            }
            for row in records
        ]
        return {"dashboard_pc_volume_period_country_combine_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/pc_volume_period_country_yearly')
def pc_volume_period_country_yearly(db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_volume_period_country_yearly view"""
    try:
        records = db.query(dashboard_pc_volume_period_country_yearly).all()
        result = [
            {
                "Country": row.Country,
                "year": row.year,
                "sum_total_actual_value":row.sum_total_actual_value,
                "sum_total_actual_value_previous": row.sum_total_actual_value_previous,
                "yoyind":row.yoyind
            }
            for row in records
        ]
        return {"dashboard_pc_volume_period_country_yearly": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/pc_volume_period_country_yearly"/{year}')
def pc_volume_period_country_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from
    dashboard_pc_volume_period_country_yearly view for a particular year """
    try:
        records = db.query(dashboard_pc_volume_period_country_yearly).filter(
            dashboard_pc_volume_period_country_yearly.columns.year == year).all()
        result = [
            {
                "Country": row.Country,
                "year": row.year,
                "sum_total_actual_value":row.sum_total_actual_value,
                "sum_total_actual_value_previous": row.sum_total_actual_value_previous,
                "yoyind":row.yoyind
            }
            for row in records
        ]
        return {"dashboard_pc_volume_period_country_yearly": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/pc_volume_yearly_country_combine')
def pc_volume_yearly_country_combine(db: Session = Depends(get_db)):
    """Function to fetch all records from dashboard_pc_volume_period_country_yearly view"""
    try:
        records = db.query(dashboard_pc_volume_yearly_country_combine).all()
        result = [
            {
                "year": row.year,
                "US_actual_value_previous":row.US_actual_value_previous,
                "US_actual_value": row.US_actual_value,
                "US_yoyind":row.US_yoyind,
                "Canada_actual_value_previous":row.Canada_actual_value_previous,
                "Canada_actual_value": row.Canada_actual_value,
                "Canada_yoyind":row.Canada_yoyind,
            }
            for row in records
        ]
        return {"dashboard_pc_volume_yearly_country_combine": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/dashboard_pc_volume_yearly_country_combine"/{year}')
def pc_volume_yearly_country_combine_year(year:int, db: Session = Depends(get_db)):
    """Function to fetch all records from
    dashboard_pc_volume_yearly_country_combine view for a particular year """
    try:
        records = db.query(dashboard_pc_volume_yearly_country_combine).filter(
            dashboard_pc_volume_yearly_country_combine.columns.year == year).all()
        result = [
            {
                "year": row.year,
                "US_actual_value_previous":row.US_actual_value_previous,
                "US_actual_value": row.US_actual_value,
                "US_yoyind":row.US_yoyind,
                "Canada_actual_value_previous":row.Canada_actual_value_previous,
                "Canada_actual_value": row.Canada_actual_value,
                "Canada_yoyind":row.Canada_yoyind,
            }
            for row in records
        ]
        return {"dashboard_pc_volume_yearly_country_combine": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
