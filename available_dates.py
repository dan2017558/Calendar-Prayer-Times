import datetime as dt
import pytz
import calendar

def generate_date_range(start_date, end_date):
    # Convert the string dates into datetime objects
    start = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end = dt.datetime.strptime(end_date, '%Y-%m-%d')
    
    # Generate a list of all dates in the range, including start and end
    date_list = []
    current_date = start
    
    while current_date <= end:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += dt.timedelta(days=1)

    return date_list

# Get the current date in UTC and convert to CST (America/Chicago timezone)
utc_now = dt.datetime.now(pytz.utc)
cst_tz = pytz.timezone("America/Chicago")
cst_now = utc_now.astimezone(cst_tz)

# Get the current year and month
year = cst_now.year
month = cst_now.month

# Get the last day of the current month
_, last_day = calendar.monthrange(year, month)

# Create a datetime object for the last day of the month in CST
last_day_of_month = dt.datetime(year, month, last_day, tzinfo=cst_tz)

# Format the dates as yyyy-mm-dd
formatted_last_day = last_day_of_month.strftime('%Y-%m-%d')
formatted_date = cst_now.strftime('%Y-%m-%d')


# Generate a list of dates from the current date to the last day of the month
date_range = generate_date_range(formatted_date, formatted_last_day)