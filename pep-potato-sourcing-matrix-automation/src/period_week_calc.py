"""Period and week calculation API"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException

router = APIRouter()


def calculate_period_and_week(year, specified_date, start_day=6, periods=13, weeks=4):
    """Function to return the period and period*week for a specific date of a particular year"""
    start_date = datetime(year, 1, 1)

    start_day_of_week = start_date.weekday()

    offset = (start_day - start_day_of_week) % 7

    if offset != 0:
        start_date -= timedelta(days=(start_day_of_week + 1))

    period = 1

    for i in range(periods):
        end_date = start_date + timedelta(days=(weeks * 7) - 1)       
        if start_date <= specified_date <= end_date:
            # Calculate the week within the period
            week = (specified_date - start_date).days // 7 + 1
            return {
                'Period': period,
                'Period_with_week': f'P{period}W{week}',
                'Start_Date': start_date,
                'End_Date': end_date
            }

        start_date = end_date + timedelta(days=1)

        # Move to the next period
        period += 1

    raise HTTPException(status_code=404, detail="No period found for the specified date")

@router.get("/get_period_and_week")
async def get_period_and_week(year: int, date: str):
    """To get the period and period*week for a specific date in a calender year"""
    specified_date = datetime.strptime(date, "%Y-%m-%d")
    result = calculate_period_and_week(year, specified_date)
    return {"period_and_week": result}
