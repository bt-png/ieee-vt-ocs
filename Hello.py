import streamlit as st
from streamlit.logger import get_logger
from streamlit_gsheets import GSheetsConnection

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
        initial_sidebar_state="collapsed",
    )
    Voting = st.expander('Open Working Group Chair Positions')
    Voting.write('Nominate a candidate')
    P1628 = Voting.container()
    P1628.write("Vote Now")
    P3357 = Voting.container()
    P3357.write("Vote Now")
    Attendance = st.expander('Record attendance')
    AttendanceForm = Attendance.form(key='form_attendance')
    col1, col2, col3 = AttendanceForm.columns([3, 1, 1])

    lastname = col1.text_input(
        'Last Name',
        key='name',
    )
    AttendanceForm.form_submit_button(label="Submit")

def gsheets():
    conn = st.connection('gsheets', type=GSheetsConnection)
    data = conn.read()
    st.dataframe(data)
    
def sample():
    st.write('test sample')
    
if __name__ == '__main__':
    run()
    gsheets()
