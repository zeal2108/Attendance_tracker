from datetime import datetime
from db import database
import streamlit as st
import pytz

from db.database import fetch_today_log

india_tz = pytz.timezone("Asia/Kolkata")

def get_today_date():
    return datetime.now(india_tz).strftime("%Y-%m-%d")

def get_current_time():
    return datetime.now(india_tz).strftime("%H:%M:%S")

def mark_entry(conn):
    st.write("Inside mark_entry")  # Debug message
    today = get_today_date()
    current_time = get_current_time()
    #existing = database.get_today_log(conn, today)

    #if existing is None:
    c = conn.cursor()
    c.execute("SELECT id FROM attendance WHERE date = ? AND type = 'main'", (today,))
    main_entry = c.fetchone()

    if not main_entry:
        database.insert_entry(conn, today, current_time, "main")
        st.write(f"Main entry marked for {today} at {current_time}")
    else:
        st.write("Main entry already exists, doing nothing")
    #else:
      #st.write("Entry already exists, doing nothing")  # Debug message


def start_lunch(conn):
    today = get_today_date()
    current_time = get_current_time()

    c = conn.cursor()
    c.execute("SELECT id FROM attendance WHERE date = ? AND type = 'main'", (today,))
    main_entry = c.fetchone()

    if not main_entry:
        st.write("No main entry market yet !!")
        return
    main_entry_id = main_entry[0]

    c.execute("SELECT id FROM attendance WHERE date = ? AND type ='lunch' AND parent_id = ? ", (today, main_entry_id))
    lunch_entry = c.fetchone()

    if not lunch_entry:
        database.insert_entry(conn, today, current_time, "lunch", parent_id = main_entry_id)
        st.write(f"Lunch Started for {today} at {current_time}")
    else:
        st.write("Lunch already started, doing nothing")

def end_lunch(conn):
    today = get_today_date()
    current_time = get_current_time()

    c = conn.cursor()
    c.execute("SELECT id FROM attendance WHERE date = ? AND type = 'main'", (today,))
    main_entry = c.fetchone()

    if not main_entry:
        st.write("No main entry market yet !!")
        return
    main_entry_id = main_entry[0]

    c.execute("SELECT id, entry_time FROM attendance WHERE date = ? AND type = 'lunch' AND parent_id = ? "
              "AND exit_time IS NULL", (today, main_entry_id))
    lunch_entry = c.fetchone()

    if lunch_entry:
        lunch_id, lunch_entry_time = lunch_entry
        database.update_exit(conn, lunch_id, current_time)
        st.write(f"Lunch ended for {today} at {current_time} (started at {lunch_entry_time}) ")
    else:
        st.write("doing nothing")

def mark_exit(conn):
    st.write("Inside mark_exit")  # Debug message
    today = get_today_date()
    current_time = get_current_time()
    c = conn.cursor()
    c.execute("SELECT id, entry_time FROM attendance WHERE date = ? AND type = 'main'"
              "AND exit_time IS NULL", (today,))
    main_entry = c.fetchone()

    if main_entry:
        main_entry_id, main_entry_time = main_entry
        database.update_exit(conn, main_entry_id, current_time)
        st.write(f"Exit marked for {today} at {current_time} (paired with entry at {main_entry_time})")
    else:
        st.write("No main entry to mark exit for today, or main exit already marked")
    #existing = database.get_today_log(conn, today)

    #if existing and existing[1] is None:
        #database.update_exit(conn, today, current_time)
        #st.write(f"Exit marked for {today} at {current_time}")  # Debug message
    #else:
        #st.write("No entry or already exited, doing nothing")  # Debug message

def get_today_log(conn):
    today = get_today_date()
    logs = fetch_today_log(conn, today)
    if logs:
        formatted_logs = []
        main_log = None
        lunch_log = None
        for log in logs:
            entry_id, entry_time, exit_time, entry_type, parent_id = log
            if entry_type == 'main':
                main_log = f"Main : Entry at {entry_time} | Exit at {exit_time if exit_time else 'Not Marked'}"
            elif entry_type == 'lunch' and parent_id:
                lunch_log = f"  Lunch: Entry at {entry_time} | Exit at {exit_time if exit_time else 'Not Marked'}"
        if main_log:
            formatted_logs.append(main_log)
        if lunch_log:
            formatted_logs.append(lunch_log)
        return "\n".join(formatted_logs)
    return None


def get_log_for_date(conn, date):
    """
    Retrieve the attendance log for a specific date as a formatted string.

    Args:
        conn: SQLite database connection
        date (str): Date in YYYY-MM-DD format

    Returns:
        str: Formatted log string for the specified date
    """
    logs = fetch_today_log(conn, date)
    if not logs:
        return f"No attendance records for {date}."

    log_text = []
    #main_hours, lunch_hours, work_hours = calculate_daily_work_hours(conn, date)

    for log in logs:
        entry_id, entry_time, exit_time, entry_type, parent_id= log
        if entry_type == "main":
            log_text.append(f"Main: Entry at {entry_time} | Exit at {exit_time if exit_time else 'Not Marked'}")
        elif entry_type == "lunch" and parent_id:
            log_text.append(f"  Lunch: Entry at {entry_time} | Exit at {exit_time if exit_time else 'Not Marked'}")

    # Add work hours summary
    #if main_hours is not None:
        #log_text.append(f"Main Duration: {main_hours:.2f} hours")
    #if lunch_hours is not None:
        #log_text.append(f"Lunch Duration: {lunch_hours:.2f} hours")
    #if work_hours is not None:
        #log_text.append(f"Work Hours (excluding lunch): {work_hours:.2f} hours")

    return "\n".join(log_text)

def get_full_history(conn):
    records = database.get_all_logs(conn, limit = 100)
    formatted = []
    for date, entry_time, exit_time, entry_type in records:
        if entry_type == 'main':
            formatted.append(f"{date} (Main): Entry at {entry_time} | Exit at {exit_time if exit_time 
            else 'Not Marked'}")
        elif entry_type == 'lunch':
            formatted.append(f"{date} (Lunch): Entry at {entry_time} | Exit at {exit_time if exit_time
            else 'Not Marked'}")
    return formatted

def get_monthly_history(conn, year_month):
    records = database.get_all_logs(conn, limit = 100)
    formatted = []
    for date, entry_time, exit_time, entry_type in records:
        if entry_type == 'main':
            formatted.append(f"{date} (Main): Entry at {entry_time} | Exit at {exit_time if exit_time 
            else 'Not Marked'}")
        elif entry_type == 'lunch':
            formatted.append(f"{date} (Lunch): Entry at {entry_time} | Exit at {exit_time if exit_time
            else 'Not Marked'}")
    return formatted if formatted else ["No attendance records for this month."]