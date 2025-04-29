import streamlit as st
import sqlite3
import pandas as pd
from logic.attendance_logic import mark_entry, mark_exit, start_lunch, end_lunch, get_today_log, get_full_history, get_monthly_history
from db.database import init_db, reset_db
from datetime import datetime, timedelta

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

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button('✅ Mark Entry', use_container_width=True):
                st.write("Mark Entry button clicked!")  # Debug message
                mark_entry(conn)


        with col2:
            if st.button('🍴 Start Lunch', use_container_width=True):
                start_lunch(conn)
                st.success("Lunch Started")


        with col3:
            if st.button('🍽️ End Lunch', use_container_width=True):
                end_lunch(conn)
                st.success("Lunch ended.")


        with col4:
            if st.button('🏁 Mark Exit', use_container_width=True):
                st.write("Mark Exit button clicked!")  # Debug message
                mark_exit(conn)


        st.divider()
        today_log = get_today_log(conn)
        if today_log:
            st.markdown(f"**Today's Log:**<br>{today_log.replace('\n', '<br>')}", unsafe_allow_html=True)
            #st.info(f"Today's Log: \n {today_log}")
        else:
            st.info("No attendance marked for today yet !!")

        with st.sidebar:
            st.header("Additional Options")

            with st.expander("Month-Wise Attendance History"):
                current_year = datetime.now().year
                current_month = datetime.now().month
                months = [f"{current_year}-{str(m).zfill(2)}" for m in range(1, current_month+1)]
                selected_month = st.selectbox("Select Month", months, index=len(months)-1)
                monthly_history = get_monthly_history(conn, selected_month)
                for record in monthly_history:
                  st.write(record)

            st.divider()

            if st.checkbox('Show Full Attendance History'):
              full_history = get_full_history(conn)
              for record in full_history:
                 st.write(record)

            st.divider()

            st.subheader("Export Attendance Data")
            export_option = st.radio("Export Range", ["Last 6 months","All Data"])
            if export_option == "Last 6 months":
                start_date = (datetime.now() - timedelta(days = 180)).strftime("%Y-%m-%d")
            else:
                start_date = None
            if st.button("Download as CSV"):

               if start_date:
                 records = conn.execute("SELECT date, entry_time, exit_time FROM attendance WHERE date >= ? ORDER BY date", (start_date,)).fetchall()
               else:
                 records = conn.execute("SELECT date, entry_time, exit_time FROM attendance ORDER BY date").fetchall()

               df = pd.DataFrame(records, columns =["DATE ", "ENTRY ", "EXIT "])
               df["EXIT "] = df["EXIT "].fillna("Not Marked")
               csv = df.to_csv(index = False, float_format = "%.2f")

               st.download_button(
               label = "Download CSV File",
               data = csv,
               file_name = "attendance_data.csv",
               mime = "text/csv"
               )
        # Close the connection
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")
else:
    st.error("Incorrect password!")



