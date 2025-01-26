import streamlit as st
from datetime import datetime
st.set_page_config(
        page_title='IEEE VT OCS Standards Committee',
        page_icon='🚊',
        layout='wide'
    )

testing = False
import streamlit_authentication as st_auth
import firestore
config = firestore.openconfig()
auth = st_auth.authenticate(config)

import voting_tally as vt
import meetings
import workinggroups as wg
import officers
from officers import officerlist
import admin
import roster
import wgpages


def home():
    col1, col2, col3 = st.columns([1, 6, 1])
    col2.header('IEEE VT OCS Standards Committee')
    col2.image(image='IMG_0079.jpg')
    # col2.button('test', on_click=testfun())
    do_you_have_an_account = st.empty()
    do_you_have_an_account = st.sidebar.selectbox(label='Start here',options=('Sign in', 'Sign up', 'I forgot my password', 'I forgot my username'), key='mainone')
    if do_you_have_an_account == 'Sign in':
        user, status, username = st_auth.login(auth)
    elif do_you_have_an_account == 'Sign up':
        email, username, user = st_auth.register(auth, config)
    elif do_you_have_an_account == 'I forgot my password':
        username, email, new_random_password = st_auth.forgotpassword(auth, config)
    elif do_you_have_an_account == 'I forgot my username':
        username, email = st_auth.forgotusername(auth)
    if 'authentication_status' in st.session_state:
        if st.session_state['authentication_status']:
            st.session_state.user_info = user
        elif st.session_state['authentication_status'] is False:
            st.sidebar.error('Username/password is incorrect')
        elif st.session_state['authentication_status'] is None and do_you_have_an_account == 'Sign in':
            st.sidebar.warning('Please enter your username and password')


def memberwelcome():
    st.markdown(f'#### Welcome, {st.session_state["name"]}\.')
    st.session_state.memberstatus = roster.member_status(st.session_state.user_info)
    if st.session_state.memberstatus is False:
        st.write('Your information could not be connected to the existing roster, please contact committee officers for help.')
    else:
    # st.markdown('''---''')
        try:
                st.write(f'Your membership status is recorded as: {st.session_state.memberstatus}')
                st.caption('Per our Policies and Procedures, voting membership is based on attendance of 2 of the last 4 committee meetings and participating in votes.')
                col1,col2,col3 = st.columns([1,4,4])
                col2.dataframe(roster.meeting_attendance_record(st.session_state.user_info), hide_index=False)
                st.write(f'Our records indicate your preferred contact email address is {tmp_email} \
                with {roster.user_affiliations(st.session_state.user_info)} as your affiliation.')
                st.caption('If any of this information is incorrect, please contact your committee officers. They will help update the roster.')
        except Exception:
                st.warning('Your attendance records could not be matched. Please contact your committee officers to update the roster.')
                return False
    st.markdown('''---''')
    return True


def meetingattendance():
    if (datetime.date(datetime.today()) == meetings.next_meeting_date()) or testing:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            # Active meeting attendance
            st.subheader('Record Attendance of Comittee Meeting')
            meetings.attendance_statement()
        st.markdown('''---''')


def pollfutureattendance():
    if (datetime.today() < datetime(year=2024, month=9, day=9)) or testing:
    # if (datetime.date(datetime.today()) < meetings.next_meeting_date()) or testing:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            vt.attendingnextmeeting()
        st.markdown('''---''')


def nominations():
    if (datetime.today() < datetime(year=2024, month=9, day=9)) or testing:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            # Call for Nominations 4/22 through 6/4, 2024
            vt.nominations()
        st.markdown('''---''')


def voting():
    if False:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.subheader('Call for Vote')
            if st.session_state.memberstatus == 'Voting Member':
                st.write('\
                    We are now open for voting, please use the form below to cast your vote.\
                    ')
                vt.vote('P1628', ['Cynthia', 'Andrew'])
                vt.vote('P3357', ['bilal', 'brett', 'pandas'])
            else:
                st.write('A voting membership status is required to vote based on our committee policies and procedures. Voting status is \
                            determined by attending at least 2 of the past 4 committee meetings.')
        st.markdown('''---''')


def officerpage():
    admin.run()
 

def workinggrouppages():
    wgpages.run()


def viewmeetings():
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        meetings.run()
    st.markdown('''---''')


def viewworkinggroups():
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        wg.run()


# -------------------------------------------------------------------------------------------------
# Not logged in -----------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------

if 'user_info' not in st.session_state:
    home()
else:
    if st.session_state['authentication_status'] is None:
        # Logged out
        st.session_state.clear()
        st.rerun()
    if 'WG_page' not in st.session_state:
        st.session_state['WG_page'] = False
    # ---------------------------------------------------
    # Logged in -----------------------------------------
    # ---------------------------------------------------
    # Show Admin Link
    if st.session_state['username'] in officerlist():
        st.sidebar.checkbox(label='Show Officer Page', key='admin_page')
    else:
        st.session_state['admin_page'] = False
       
    if st.session_state['admin_page']:
        officerpage()
    else:
        if memberwelcome():
                meetingattendance()
                pollfutureattendance()
                nominations()
                voting()
                workinggrouppages()
                viewmeetings()
                viewworkinggroups()
    # Show user information
    with st.sidebar.expander('Update Login', expanded=False):
        st_auth.resetpassword(auth, config)
        #st_auth.updateuser(auth, config)
    st_auth.logout(auth)
st.markdown('''---''')
officers.run()
