import streamlit as st
from logic.attendance_logic import mark_entry, mark_exit, get_today_log, get_full_history
from db.database import init_db
import sqlite3

# Get password and database path from secrets
expected_password = st.secrets["database"]["password"]
db_path = st.secrets["database"]["path"]

# User input for password
user_password = st.text_input("Enter Password", type="password")

if user_password == expected_password:
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        st.success("Access granted! Connected to the database.")

        # Initialize the database table
        init_db(conn)
        st.set_page_config(page_title="Daily Help Attendance", page_icon="📋")

        st.title("📋 Daily Help Attendance Tracker")
        st.write("Simple app to track Entry and Exit times.")

        col1, col2 = st.columns(2)

        with col1:
          if st.button('✅ Mark Entry', use_container_width=True):
            mark_entry(conn)

        with col2:
          if st.button('🏁 Mark Exit', use_container_width=True):
            mark_exit(conn)

        st.divider()

        today_log = get_today_log(conn)
        if today_log:
          st.info(today_log)
        else:
          st.info("No attendance marked for today yet.")

        st.divider()

        if st.checkbox('Show Full Attendance History'):
          full_history = get_full_history(conn)
          for record in full_history:
            st.write(record)

        conn.close()

    except Exception as e:
     st.error(f"Database error: {e}")

else:
 st.error("Incorrect password!")
