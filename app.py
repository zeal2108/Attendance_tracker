import streamlit as st
import sqlite3
import pandas as pd
from logic.attendance_logic import mark_entry, mark_exit, get_today_log, get_full_history, get_monthly_history
from db.database import init_db, reset_db
from datetime import datetime

# Set page config as the first Streamlit command
st.set_page_config(page_title="Daily Help Attendance", page_icon="📋")

# Get password and database path from secrets
expected_password = st.secrets["database"]["password"]
db_path = st.secrets["database"]["path"]

# User input for password
user_password = st.text_input("Enter Password", type="password")

if user_password == expected_password:
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path, check_same_thread=False)
        st.success("Access granted! Connected to the database.")

        # Initialize the database table
        init_db(conn)

        # Proceed with the app's UI
        st.title("📋 Daily Help Attendance Tracker")
        st.write("Simple app to track Entry and Exit times.")

        if st.button("Reset Attendance Data"):
            st.warning("Resetting all attendance data...")
            reset_db(conn)
            st.success("Attendance data has been reset!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button('✅ Mark Entry', use_container_width=True):
                st.write("Mark Entry button clicked!")  # Debug message
                mark_entry(conn)
                  # Force UI refresh

        with col2:
            if st.button('🏁 Mark Exit', use_container_width=True):
                st.write("Mark Exit button clicked!")  # Debug message
                mark_exit(conn)


        st.divider()

        today_log = get_today_log(conn)
        if today_log:
            st.info(today_log)
        else:
            st.info("No attendance marked for today yet.")

        st.divider()

        st.subheader("Monthly Attendance History")
        current_year = datetime.now().year
        current_month = datetime.now().month
        months = [f"{current_year}-{str(m).zfill(2)}" for m in range(1, current_month+1)]
        selected_month = st.selectbox("Select Month", months, index=len(months)-1)
        monthly_history = get_monthly_history(conn, selected_month)
        for record in monthly_history:
            st.write(record)

        if st.checkbox('Show Full Attendance History'):
            full_history = get_full_history(conn)
            for record in full_history:
                st.write(record)

        # Close the connection
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")
else:
    st.error("Incorrect password!")



