from models import View_erp_raw_alerts
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db
from datetime import date,datetime
from sqlalchemy import or_
from period_week_calc import calculate_period_and_week

router = APIRouter()

@router.get('/get_alerts', status_code=status.HTTP_201_CREATED)
async def get_erp_alerts(db: Session = Depends(get_db)): # pragma: no cover
    """Function to fetch null data from erp table """

    #Getting current year and period
    try:
        today_date = date.today()
        year = int(today_date.year)
        period_week = calculate_period_and_week(year, today_date)
        period = int(period_week['Period'])    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    #Retrieving data
    try:
        records = db.query(View_erp_raw_alerts).filter(View_erp_raw_alerts.columns.RECEIPT_YEAR == year,
                                                       View_erp_raw_alerts.columns.REC_DATE_PD == period,
                                                       View_erp_raw_alerts.columns.plant_id != 28, # Ignoring Mexicali plant
                                                   or_(
                                                       View_erp_raw_alerts.columns.VENDOR_NAME == None,
                                                       View_erp_raw_alerts.columns.VENDOR_SITE_CODE == None,
                                                       View_erp_raw_alerts.columns.ShipToOrg == None,
                                                       View_erp_raw_alerts.columns.growing_area == None,
                                                       View_erp_raw_alerts.columns.Quantity_Accepted_MCWT == None)).all()
        
        alert_json = {}
        alert = "There are null values in ERP data --> {"

        #Creating a BPA dict to store Unique BPA numbers as keys
        bpa_data = {}

        #Looping the null data records to determine the columns which has null
        for items in records:
            bpa = str(items.BPA_Number)
            null_columns = []
            if items.VENDOR_NAME == None:
                null_columns.append("VENDOR_NAME")
            if items.VENDOR_SITE_CODE == None:
                null_columns.append("VENDOR_SITE_CODE")
            if items.ShipToOrg == None:
                null_columns.append("ShipToOrg")
            if items.growing_area == None:
                null_columns.append("growing_area")
            if items.Quantity_Accepted_MCWT == None:
                null_columns.append("Quantity_Accepted_MCWT")

            #Update the BPA dict
            if bpa not in bpa_data:
                bpa_data[bpa] = {"null_cols" : set(null_columns), "count":1}
            else:
                bpa_data[bpa]['null_cols'].update(null_columns)
                bpa_data[bpa]['count']+=1
            
        #Alert message
        for bpa,data in bpa_data.items():
            cols = ", ".join(data["null_cols"])
            alert += f"{bpa} = [{cols}, Count_of_null_records = {data['count']}], "

        alert = alert[:-2]+ "}"
        alert_json = {"Alert message": alert}

        #Returns the alert message if null values else null
        if len(records)>0:
            return {"message": alert_json}
        else:        
            return {"message": {"Alert message": "0"}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e