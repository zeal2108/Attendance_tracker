from datetime import datetime
from db import database
import streamlit as st
import pytz

india_tz = pytz.timezone("Asia/Kolkata")

def get_today_date():
    return datetime.now(india_tz).strftime("%Y-%m-%d")

def get_current_time():
    return datetime.now(india_tz).strftime("%H:%M:%S")

def mark_entry(conn):
    st.write("Inside mark_entry")  # Debug message
    today = get_today_date()
    current_time = get_current_time()
    existing = database.get_today_log(conn, today)

    #if existing is None:
    database.insert_entry(conn, today, current_time)
    st.write(f"Entry marked for {today} at {current_time}")  # Debug message
    #else:
        #st.write("Entry already exists, doing nothing")  # Debug message

def mark_exit(conn):
    st.write("Inside mark_exit")  # Debug message
    today = get_today_date()
    current_time = get_current_time()
    existing = database.get_today_log(conn, today)

    if existing and existing[1] is None:
        database.update_exit(conn, today, current_time)
        st.write(f"Exit marked for {today} at {current_time}")  # Debug message
    else:
        st.write("No entry or already exited, doing nothing")  # Debug message

def get_today_log(conn):
    today = get_today_date()
    log = database.get_today_log(conn, today)
    if log:
        entry_time, exit_time = log
        return f"Entry: {entry_time} | Exit: {exit_time if exit_time else 'Still inside'}"
    return None

def get_full_history(conn):
    records = database.get_all_logs(conn)
    formatted = []
    for date, entry, exit in records:
        formatted.append(f"{date}: Entry at {entry} | Exit at {exit if exit else 'Not marked'}")
    return formatted