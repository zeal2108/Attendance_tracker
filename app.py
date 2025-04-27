import streamlit as st
from logic.attendance_logic import mark_entry, mark_exit, get_today_log, get_full_history

st.set_page_config(page_title="Daily Help Attendance", page_icon="📋")

st.title("📋 Daily Help Attendance Tracker")
st.write("Simple app to track Entry and Exit times.")

col1, col2 = st.columns(2)

with col1:
    if st.button('✅ Mark Entry', use_container_width=True):
        mark_entry()

with col2:
    if st.button('🏁 Mark Exit', use_container_width=True):
        mark_exit()

st.divider()

today_log = get_today_log()
if today_log:
    st.info(today_log)
else:
    st.info("No attendance marked for today yet.")

st.divider()

if st.checkbox('Show Full Attendance History'):
    full_history = get_full_history()
    for record in full_history:
        st.write(record)