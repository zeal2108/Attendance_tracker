import streamlit as st
import psycopg2 as sql
import pandas as pd
from logic.attendance_logic import mark_entry, mark_exit, start_lunch, end_lunch, get_today_log, get_log_for_date
from db.database import init_db, reset_db
from datetime import datetime, timedelta
from assets.formatting import format_date_pretty

# Set page config as the first Streamlit command
st.set_page_config(page_title="Daily Help Attendance", page_icon="📋")

#Injecting CSS
with open("assets/styles.css", "r") as css_file:
    css = css_file.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Get password and database connection details from secrets
expected_password = st.secrets["database"]["password"]
#db_path = st.secrets["database"]["path"]
dev_password = st.secrets["database"]["dev_password"]
db_name=st.secrets["database"]["db_name"]
db_user=st.secrets["database"]["db_user"]
db_password=st.secrets["database"]["db_password"]
db_host=st.secrets["database"]["db_host"]
db_port=st.secrets["database"]["db_port"]


#Initializing the session states
if 'authentication' not in st.session_state:
     st.session_state['authentication'] = False
if 'pwd_input' not in st.session_state:
     st.session_state['pwd_input'] = ''
if 'reset_confirmed' not in st.session_state:
    st.session_state['reset_confirmed'] = False
if 'lunch_active' not in st.session_state:
    st.session_state['lunch_active'] = False
if 'entry_active' not in st.session_state:
    st.session_state['entry_active'] = False
if 'has_exited' not in st.session_state:
    st.session_state['has_exited'] = False
if 'current_date' not in st.session_state:
    st.session_state['current_date'] = datetime.now().strftime("%Y-%m-%d")


if not st.session_state['authentication']:
    if st.session_state.get('pwd_input', '') == '':
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("Login",use_container_width=True):
                @st.dialog("Enter Password")
                def ask_pwd_dialog():
                    u_pwd = st.text_input("Press enter to confirm ", type="password", key="dialog_pwd_input")
                    if st.button("Continue"):
                        if u_pwd:
                            st.session_state['pwd_input'] = u_pwd
                            st.rerun()
                        else:
                            st.error("Please Enter Password. ")


                ask_pwd_dialog()
    else:
        user_password = st.session_state["pwd_input"]
        if user_password == expected_password:
            st.session_state['authentication'] = True
            st.session_state['pwd_input'] = ''
            st.rerun()
        elif user_password != '' and user_password != expected_password:
            st.error("Invalid Password, Refresh the Page to Try Again !!. ")
            st.session_state['pwd_input'] = ''


if st.session_state['authentication']:
    try:
        # Connect to the database
        conn = sql.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        st.success("Welcome! Connected to the database.")

        # Initialize the database
        init_db(conn)

        today = datetime.now().strftime("%Y-%m-%d")
        if today != st.session_state['current_date']:
            st.session_state['has_entered'] = False
            st.session_state['lunch_active'] = False
            st.session_state['has_exited'] = False

        # Check if an entry-exit pair already exists for today
        c = conn.cursor()
        c.execute("SELECT * FROM attendance WHERE date = %s AND type = 'main' AND id IS NOT NULL AND entry_time "
                  "IS NOT NULL AND exit_time IS NOT NULL",(today,))
        if c.fetchone():
            st.session_state['has_exited'] = True
            st.session_state['has_entered'] = False
            st.session_state['lunch_active'] = False
        else:
            # Check if an entry exists for today
            c.execute("SELECT * FROM attendance WHERE date = %s AND type = 'main'", (today,))
            if c.fetchone():
                st.session_state['has_entered'] = True
            # Check if an active lunch record exists for today
            c.execute("SELECT * FROM attendance WHERE date = %s AND type = 'lunch' AND exit_time IS NULL", (today,))
            if c.fetchone():
                st.session_state['lunch_active'] = True
            else:
                st.session_state['lunch_active'] = False

        # Proceed with the app's UI
        st.title("📋 Daily Help Attendance Tracker")
        st.write("Simple app to track Entry and Exit times.")

        left_col, right_col = st.columns(2)

        with left_col:
            #disable_entry = st.session_state['has_exited']
            if st.button('✅ Mark Entry', use_container_width=True, key="mark_entry_btn"):
                st.session_state['entry_active'] = True
                mark_entry(conn)


            disable_exit = not st.session_state['entry_active'] or st.session_state['lunch_active']
            if st.button('🏁 Mark Exit', use_container_width=True, key="mark_exit_btn", disabled=disable_exit):
                mark_exit(conn)
                #st.session_state['entry_active'] = False
                st.session_state['lunch_active'] = False
                c = conn.cursor()
                c.execute(
                    "SELECT * FROM attendance WHERE date = %s AND type = 'main' AND entry_time IS NOT NULL AND exit_time IS NOT NULL",
                    (today,))
                if c.fetchone():
                    st.session_state['has_exited'] = True
                st.rerun()

        with right_col:
            today = datetime.now().strftime("%Y-%m-%d")
            c.execute(
                "SELECT entry_time FROM attendance WHERE date = %s AND type = 'main' ORDER BY entry_time DESC LIMIT 1",
                (today,))
            main_entry = c.fetchone()
            #disable_exit = not st.session_state['entry_active'] or main_entry is None #or st.session_state['has_exited']
            if st.button('🍴 Start Lunch', use_container_width=True, key="start_lunch_btn"):
                start_lunch(conn)
                st.session_state['lunch_active'] = True
                st.rerun()
                    #st.success("Lunch Started")
            c.execute(
                "SELECT entry_time FROM attendance WHERE date = %s AND type = 'main' ORDER BY entry_time DESC LIMIT 1",
                (today,))
            main_entry = c.fetchone()
            if st.button('🍽️ End Lunch', use_container_width=True, key="end_lunch_btn"):
                end_lunch(conn)
                st.session_state['lunch_active'] = False
                st.rerun()
                #st.success("Lunch ended.")

        st.divider()
        today_log = get_today_log(conn)
        if today_log:
            st.markdown(f"**Today's Log:**<br>{today_log.replace('\n', '<br>')}", unsafe_allow_html=True)
            #st.info(f"Today's Log: \n {today_log}")
        else:
            st.info("No attendance marked for today yet !!")

        with st.sidebar:

            st.header("Additional Options")

            with st.expander("View Log for Specific Date"):
                current_year = datetime.now().year
                current_month = datetime.now().month
                selected_date = st.date_input("Select a date", value = datetime.now(), min_value = datetime(current_year, 1, 1),
                max_value = datetime.now())
                selected_date_str = selected_date.strftime("%Y-%m-%d")
                date_log = get_log_for_date(conn, selected_date_str)
                st.write(f"Log for {format_date_pretty(selected_date_str)} : ")
                for log in date_log.split("\n"):
                    st.info(log)

            st.divider()

            st.subheader("Export Attendance Data")
            export_option = st.radio("Export Range", ["Last 6 months","All Data"])
            if export_option == "Last 6 months":
                start_date = (datetime.now() - timedelta(days = 180)).strftime("%Y-%m-%d")
            else:
                start_date = None
            if st.button("Download as CSV"):

               if start_date:
                 c.execute("SELECT date, entry_time, exit_time, type FROM attendance WHERE date >= %s ORDER BY date", (start_date,))
                 records = c.fetchall()
               else:
                 c.execute("SELECT date, entry_time, exit_time, type FROM attendance ORDER BY date")
                 records = c.fetchall()

               df = pd.DataFrame(records, columns =["DATE ", "ENTRY ", "EXIT ", "ENTRY TYPE "])
               df["EXIT "] = df["EXIT "].fillna("Not Marked")
               csv = df.to_csv(index = False, float_format = "%.2f")

               st.download_button(
               label = "Download CSV File",
               data = csv,
               file_name = "attendance_data.csv",
               mime = "text/csv"
               )

            with st.expander("Reset Attendance Data"):
                dev_input = st.text_input("Enter Master Control Key", type="password")
                if dev_input == dev_password:
                    st.info("Confirm Reset ( all saved records will be removed )")
                    if st.button("Confirm"):
                        reset_db(conn)
                        st.session_state['reset_confirmed'] = True
                        st.warning("Resetting all attendance data...")
                        st.success("Attendance data has been reset!")
                        st.rerun()

                elif dev_input != "" and dev_input != dev_password:
                   st.error("Invalid Key Entered, Try Again !!")

        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")
else:
    pass



