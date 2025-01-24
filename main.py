import google_api as g_api

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import queue

from available_dates import date_range, formatted_date, formatted_last_day
import messagebox


def submit_dates():
    start_date = start_date_entry.entry.get()
    end_date = end_date_entry.entry.get()

    # Check if the end date is after the start date
    if int(end_date[-2:]) < int(start_date[-2:]):
        messagebox.show_error("Invalid date range. End date precede start date.")
        return

    # Check if the dates are within the available range, then process
    if start_date in date_range and end_date in date_range:

        q = queue.Queue()

        # Execute google calendar API in a separate thread
        thread = threading.Thread(target=lambda: g_api.add_events(int(start_date[-2:]), int(end_date[-2:]), q))
        thread.start()
        update_progress(q)

    else:
        messagebox.show_error(f"Invalid date range. Dates must be within {formatted_date} to {formatted_last_day}.")
        

# Progress bar function
def update_progress(q):
    # Check if there's anything in the queue
    try:
        # We block here until there's something in the queue
        progress_value = q.get_nowait()  # Don't block, get the value if available
        progress["value"] = progress_value

    except queue.Empty:
        progress_value = None

    # Keep updating the progress if there's new information in the queue
    if progress["value"] < 100:
        root.after(100, update_progress, q)  # Check again in 100 ms
    else:
        messagebox.show_info("Events added successfully.")
        return


# Create the main window
root = tk.Tk()
root.title("Calender Prayer Times")
root.geometry("300x150")

# Create a style object
style = ttk.Style()

# ENTER REQUEST FOR DATES

date_label = ttk.Label(root, text="Select a start and end date:")
date_label.place(x=20, y=0, width=240, height=30)

start_date_entry = ttk.DateEntry(root, width=12,)
start_date_entry.place(x=20, y=30, width=240, height=30)

end_date_entry = ttk.DateEntry(root, width=12,)
end_date_entry.place(x=20, y=70, width=240, height=30)

date_submit_button = ttk.Button(root, text="Enter", bootstyle=SUCCESS, command=submit_dates)
date_submit_button.place(x=20, y=110, width=80, height=30)

progress = ttk.Progressbar(root, length=200, mode='determinate', bootstyle=SUCCESS)
progress.place(x=110, y=110, width=150, height=30)
    

# Start the main loop
root.mainloop()