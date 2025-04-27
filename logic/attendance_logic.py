from datetime import datetime
from db import database


def get_today_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


def mark_entry(conn):
    today = get_today_date()
    current_time = get_current_time()
    existing = database.get_today_log(conn, today)

    if existing is None:
        database.insert_entry(conn, today, current_time)
    else:
        # Already exists, do nothing
        pass


def mark_exit(conn):
    today = get_today_date()
    current_time = get_current_time()
    existing = database.get_today_log(conn, today)

    if existing and existing[1] is None:
        database.update_exit(conn, today, current_time)
    else:
        # No entry or already exited
        pass


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