import streamlit as st
from streamlit.logger import get_logger
from streamlit_gsheets import GSheetsConnection

#import pyrebase

#Firebase Authentication
#firebase = pyrebase.initialize_app(st.secrets['firebaseConfig'])
#auth = firebase.auth()
#db = firebase.database()


import authenticate as auth

LOGGER = get_logger(__name__)
UserDoc = None

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
    with st.expander('Sign Up'):
        Login = st.form('Login', clear_on_submit=True)
        firstname = Login.text_input('First Name')
        lastname = Login.text_input('Last Name')
        email = Login.text_input('email address')
        password = Login.text_input('password')
        LoginSubmit = Login.form_submit_button('Join')
        if LoginSubmit:
            auth.insert_user(firstname, lastname, email, password)
    
    with st.expander('User Info'):
        User = st.form('user')
        username = User.text_input('User Name')
        UserSubmit = User.form_submit_button('Check')
        UserDoc = auth.get_user_doc(username)
        AuthUser = auth.get_user(UserDoc)
        st.write(auth.get_user_email(AuthUser))
        with st.form('change email'):
            newemail = st.text_input('new email')
            if st.form_submit_button('Submit'):
                auth.update_user_email(UserDoc, newemail)
    
    with st.expander('All Users'):
        Update = st.button('Run')
        if Update:
            auth.fetch_all_users()

def gsheets():
    conn = st.connection('gsheets', type=GSheetsConnection)
    data = conn.read(
        worksheet='Attendance',
        ttl=0,
        )
    st.dataframe(data)
    
def sample():
    st.write('test sample')
    
if __name__ == '__main__':
    run()
    #gsheets()
    #adduser()
    #showusers()
