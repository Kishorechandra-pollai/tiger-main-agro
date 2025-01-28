from models import View_erp_raw_alerts,admin_alert,Plant,growers,growing_area,vendor_site_code
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db
from datetime import date,datetime
from sqlalchemy import or_,func, and_
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
    

@router.get('/get_alerts_new', status_code=status.HTTP_201_CREATED)
async def get_erp_alerts_new(db: Session = Depends(get_db)): # pragma: no cover
    """Function to return alert based on ERP data """

    #Getting current year and period
    today_date = date.today()
    year = int(today_date.year)
    period_week = calculate_period_and_week(year, today_date)
    period = int(period_week['Period'])
    week = int(period_week['week'])
    
    #Retrieving data
    try:
        existing_records = db.query(admin_alert).all()
        if len(existing_records) != 0:
            for record in existing_records:
                db.delete(record)
            db.commit()

        if int(period) ==1 and int(week)<4:
            data = (db.query(View_erp_raw_alerts)
                .filter(or_(
                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == 13,
                        View_erp_raw_alerts.columns.REC_DATE_WK >= int(week)+1,
                        View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year)-1),
                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == int(period),
                        View_erp_raw_alerts.columns.REC_DATE_WK <= int(week),
                        View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year))),
                        View_erp_raw_alerts.columns.plant_id != 28,
                        View_erp_raw_alerts.columns.Quantity_Accepted_MCWT== None).all())
        else:
            lower_limit = (int(period)*5)+int(week)-4
            upper_limit = (int(period)*5)+int(week)
            data = (db.query(View_erp_raw_alerts)
                .filter((View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK >= lower_limit,
                        (View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK <= upper_limit,
                         View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year),
                         View_erp_raw_alerts.columns.plant_id != 28,
                         View_erp_raw_alerts.columns.Quantity_Accepted_MCWT== None).all())
        
    
        null_volume = {}
        for record in data:
            bpa = str(record.BPA_Number)
            if bpa not in null_volume:
                null_volume[bpa]=1
            else:
                null_volume[bpa]+=1
    
        # Updating alert table
        for key,values in null_volume.items():

            Admin_payload_1 = {"category": "Volume missing",
                             "bpa_number" : key,
                             "Quantity_Accepted_MCWT" : None,
                             "count": values,
                             "year" : year,
                             "period" : period}

            NewAlertRecord_1 = admin_alert(**Admin_payload_1)
            db.add(NewAlertRecord_1)
        db.commit()

        vol_table = (db.query(admin_alert.bpa_number,admin_alert.count)
                     .filter(admin_alert.category=="Volume missing")
                     .all())
        
        #Category - 2
        if int(period) ==1 and int(week)<4:
            data = (db.query(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area,
                            func.count().label('count'))
                           .filter(or_(
                                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == 13,
                                             View_erp_raw_alerts.columns.REC_DATE_WK >= int(week)+1,
                                             View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year)-1),
                                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == int(period),
                                             View_erp_raw_alerts.columns.REC_DATE_WK <= int(week),
                                             View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year))),
                                    View_erp_raw_alerts.columns.plant_id != 28, # Ignoring Mexicali plant
                                or_(View_erp_raw_alerts.columns.VENDOR_NAME == None,
                                    View_erp_raw_alerts.columns.VENDOR_SITE_CODE == None,
                                    View_erp_raw_alerts.columns.ShipToOrg == None,
                                    View_erp_raw_alerts.columns.growing_area == None))
                            .group_by(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area)
                            .all())
        else:
            lower_limit = (int(period)*5)+int(week)-4
            upper_limit = (int(period)*5)+int(week)
            data = (db.query(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area,
                            func.count().label('count'))
                           .filter((View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK >= lower_limit,
                                   (View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK <= upper_limit,
                                    View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year),
                                    View_erp_raw_alerts.columns.plant_id != 28, # Ignoring Mexicali plant
                                or_(View_erp_raw_alerts.columns.VENDOR_NAME == None,
                                    View_erp_raw_alerts.columns.VENDOR_SITE_CODE == None,
                                    View_erp_raw_alerts.columns.ShipToOrg == None,
                                    View_erp_raw_alerts.columns.growing_area == None))
                            .group_by(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area)
                            .all())
        
        for rows in data:
            plant_name = db.query(Plant.plant_name).filter(Plant.plant_id == rows.plant_id).first()
            Admin_payload_2 = {"category": "Data missing",
                               "bpa_number" : rows.BPA_Number,
                               "plant_name": plant_name.plant_name,
                               "vendor_name": rows.VENDOR_NAME,
                               "vendor_site_code": rows.VENDOR_SITE_CODE,
                               "ship_to_org": rows.ShipToOrg,
                               "growing_area": rows.growing_area,
                               "count": rows.count,
                               "year" : year,
                               "period" : period}

            NewAlertRecord_2 = admin_alert(**Admin_payload_2)
            db.add(NewAlertRecord_2)
        db.commit()

        other_table = (db.query(admin_alert.bpa_number,
                               admin_alert.plant_name,
                               admin_alert.vendor_name,
                               admin_alert.vendor_site_code,
                               admin_alert.growing_area,
                               admin_alert.ship_to_org,
                               admin_alert.count)
                         .filter(admin_alert.category=="Data missing")
                         .all())

        if len(vol_table)>0 or len(other_table)>0:
            return {"message":"Null data is identified in the erp data", 
                    "vol_table": vol_table,
                    "other_table": other_table}
        else:        
            return {"message":"0", 
                    "vol_table": vol_table,
                    "other_table":other_table}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error loading alert") from e