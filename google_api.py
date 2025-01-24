import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fetch import prayer_times
from messagebox import show_error

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_user():
    """Authenticate the user and return the service."""
    creds = None

    # Check if token.json exists and is not empty
    if os.path.exists("token.json") and os.path.getsize("token.json") > 0:
        try:
            # Try loading the credentials from the token file
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except Exception as e:
            show_error(f"Error loading token: {e}", quit=True)
            creds = None  # If the file is empty or corrupt, set creds to None

    # If there are no (valid) credentials available, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh the token if expired
        else:
            # Run the OAuth flow for authentication
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)  # Opens the browser for login

        # Save the credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())  # Save the credentials as a JSON file

    return creds

# Call the authenticate function
creds = authenticate_user()


# Function to resolve the prayer times for a given day
def resolve(day):

    # Extract the Gregorian portion of the string (before the Islamic date) -> Convert to ISO format
    gregorian_part = day[0].split("  ")[0]
    gregorian_date = dt.datetime.strptime(gregorian_part, '%B %d, %Y')
    formatted_date = gregorian_date.strftime('%Y-%m-%d')

    # Parse the time in 12-hour format and convert it to 24-hour format
    def hour_format(time):
        return dt.datetime.strptime(time, '%I:%M %p').strftime('%H:%M')

    fajr = hour_format(day[3])
    dhuhr = hour_format(day[6])
    asr = hour_format(day[8])
    maghrib = hour_format(day[10])
    isha = hour_format(day[12])

    return {"formatted_date": formatted_date, "Fajr": fajr, "Dhuhr": dhuhr, "Asr": asr, "Maghrib": maghrib, "Isha": isha}


# Function to check if event is already in the Google Calendar
def check_event(time: str):
    service = build("calendar", "v3", credentials=creds)
    
    # Time of prayer + 1 minute -> Creates a range of 1 minute to check for events
    org_time = dt.datetime.fromisoformat(time)
    adjusted_time = org_time + dt.timedelta(minutes=1)
    adjusted_time_str = adjusted_time.isoformat()

    # Retrieve events from calendar
    events_result = service.events().list(calendarId='primary', timeMin=time, timeMax=adjusted_time_str, singleEvents=True, q="Prayer").execute()

    # Process and print events
    events = events_result.get('items', [])
    if not events:
        return True
    return False
    


# Function to add an event to Google Calendar
def add_events(start, stop, q):  # start, stop -> Day range to add events -> days of the month

    # Retrieve desired days
    days = [prayer_times[i] for i in range(start-1, stop)]
    num_events = len(days) * 5  # 5 prayer times per day

    # Run through days and add events
    for i, day in enumerate(days):
        resolved_day = resolve(day)
        date = resolved_day["formatted_date"]

        try:
            for j in range(5):  # Loop through the 5 prayer times

                event = i*5 + j
                q.put(event*100/num_events)  # Update the progress bar
                
                # Check if event already exists in calendar
                if check_event(f"{date}T{list(resolved_day.values())[j+1]}:00-06:00") == False:
                    continue

                service = build("calendar", "v3", credentials=creds)
                
                # Create event
                event = {
                    "summary": f"{list(resolved_day.keys())[j+1]} Prayer",
                    "description": "It's time to pray!",
                    "start": {
                        "dateTime": f"{date}T{list(resolved_day.values())[j+1]}:00-06:00",
                        "timeZone": "Canada/Central"
                    },
                    "end": {
                        "dateTime": f"{date}T{list(resolved_day.values())[j+1]}:00-06:00",
                        "timeZone": "Canada/Central"
                    }
                }

                event = service.events().insert(calendarId="primary", body=event).execute()

        except HttpError as error:
            show_error(f"An error occurred: {error}", quit=True)

    q.put(100)  # Update the progress bar to 100% when done