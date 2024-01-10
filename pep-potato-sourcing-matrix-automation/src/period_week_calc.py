"""Period and week calculation API"""
from datetime import date, timedelta
from fastapi import APIRouter

router = APIRouter()


def calculate_period_and_week(year, specified_date: date, start_day=6, periods=13):  # pragma: no cover
    """Function to return the period, period*week, and
    number of weeks for a specific date of a particular year"""

    start_date = date(year, 1, 1)
    start_day_of_week = start_date.weekday()
    offset = (start_day - start_day_of_week) % 7

    if offset != 0:
        start_date -= timedelta(days=(start_day_of_week + 1))

    period = 1

    for i in range(periods):
        end_date = start_date + timedelta(days=(4 * 7) - 1)
        if period == 13:
            next_year_start_date = date(year + 1, 1, 1)
            num_weeks_period_13 = (next_year_start_date - start_date).days // 7
            end_date += timedelta(days=(num_weeks_period_13 * 7) - (4 * 7))
        if start_date <= specified_date <= end_date:
            week = min(((specified_date - start_date).days // 7) + 1, 5)
            return {
                'Period': period,
                'week': week,
                'year': specified_date.year,
                'Period_with_week': f'P{period}W{week}',
                'Start_Date': start_date,
                'End_Date': end_date,
            }

        start_date = end_date + timedelta(days=1)
        period += 1
    last_week_start_date = date(year - 1, 12, 31) - timedelta(days=start_day_of_week)
    last_week_end_date = last_week_start_date + timedelta(days=(4 * 7) - 1)

    if last_week_start_date <= specified_date <= last_week_end_date:
        next_year_start_date = date(year, 1, 1)
        first_week_end_date = next_year_start_date + timedelta(days=(4 * 7) - 1)

        if next_year_start_date <= specified_date <= first_week_end_date:
            return {
                'Period': 1,
                'week': 1,
                'year': specified_date.year,
                'Period_with_week': 'P1W1',
                'Start_Date': next_year_start_date,
                'End_Date': first_week_end_date,
            }
    return {'Period': 1, 'week': 1, 'year': specified_date.year+1}


def calculate_period_dates(year, start_day=6, periods=13):  # pragma: no cover
    """Function to get year wise period and weeks data"""
    start_date = date(year, 1, 1)
    start_day_of_week = start_date.weekday()
    offset = (start_day - start_day_of_week) % 7

    if offset != 0:
        start_date -= timedelta(days=(start_day_of_week + 1))
    period = 1
    period_dates = []
    for i in range(periods):
        end_date = start_date + timedelta(days=(4 * 7) - 1)
        if period == 13:
            next_year_start_date = date(year + 1, 1, 1)
            end_date = next_year_start_date - timedelta(days=1)
            num_weeks = (end_date - start_date).days // 7 + 1
        else:
            num_weeks = (end_date - start_date).days // 7

        period_dates.append({
            'Period': period,
            'Start_Date': start_date.strftime("%Y-%m-%d"),
            'End_Date': end_date.strftime("%Y-%m-%d"),
            'Weeks': []
        })

        current_date = start_date
        week = 1

        while current_date < end_date and week <= num_weeks:
            period_dates[-1]['Weeks'].append({
                'Week': week,
                'Start_Date': current_date.strftime("%Y-%m-%d"),
                'End_Date': (current_date + timedelta(days=6)).strftime("%Y-%m-%d")
            })

            current_date += timedelta(days=7)
            week += 1

        start_date = end_date + timedelta(days=1)
        period += 1

    return period_dates


@router.get("/get_period_and_week")
async def get_period_and_week(year: int, date_input: date):  # pragma: no cover
    """To get the period and period*week for a specific date in a calendar year"""
    result = calculate_period_and_week(year, date_input)
    return {"period_and_week": result}


@router.get("/get_all_periods")
async def get_all_periods(year: int):  # pragma: no cover
    """To get the start and end dates of all periods for a specific year"""
    period_dates = calculate_period_dates(year)
    return {"period_and_week": period_dates}


@router.get("/has_five_weeks")
def calculate_week_num(year: int, period: int):  # pragma: no cover
    """Function to check no of weeks in a period and return true or false"""
    start_date = date(year, 1, 1)
    start_day = 6
    start_day_of_week = start_date.weekday()
    offset = (start_day_of_week - start_day + 1) % 7
    if offset != 0:
        start_date += timedelta(days=7 - offset)
    period_dates = []
    for i in range(1, 14):
        end_date = start_date + timedelta(days=(4 * 7) - 1)
        if i == 13:
            next_year_start_date = date(year + 1, 1, 1)
            end_date = next_year_start_date - timedelta(days=1)
            num_weeks = (end_date - start_date).days // 7 + 1
        else:
            num_weeks = 4

        period_dates.append({
            'Period': i,
            'Start_Date': start_date.strftime("%Y-%m-%d"),
            'End_Date': end_date.strftime("%Y-%m-%d"),
            'Weeks': num_weeks,
            'Has_Five_Weeks': i == 13 and num_weeks == 5
        })

        start_date = end_date + timedelta(days=1)
    has_five_weeks = next((p['Has_Five_Weeks']
                           for p in period_dates if p['Period'] == period), None)
    return has_five_weeks
