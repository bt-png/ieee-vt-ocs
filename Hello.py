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
import admin
import roster

# -------------------------------------------------------------------------------------------------
# Not logged in -----------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------

if 'user_info' not in st.session_state:
    col1,col2,col3 = st.columns([1,6,1])
    col2.header('IEEE VT OCS Standards Committee')
    col2.image(image='IMG_0079.jpg')
    # col2.button('test', on_click=testfun())
    do_you_have_an_account = st.empty()
    do_you_have_an_account = st.sidebar.selectbox(label='Start here',options=('Sign in','Sign up','I forgot my password','I forgot my username'), key='mainone')
    if do_you_have_an_account == 'Sign in':
        user, status, username = st_auth.login(auth)
    elif do_you_have_an_account =='Sign up':
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
else:
    if st.session_state['authentication_status'] is None:
        # Logged out
        st.session_state.clear()
        st.rerun()
    # ---------------------------------------------------
    # Logged in -----------------------------------------
    # ---------------------------------------------------
    # Show Admin Link
    if st.session_state['username'] in ['btharp', '1schlick33', '1test']:
        st.sidebar.checkbox(label='Show Officer Page', key='admin_page')
    else:
        st.session_state['admin_page'] = False
    # Show user information
    st.sidebar.header('Hello ' + st.session_state.user_info + '!')

    with st.sidebar.expander('Update Profile', expanded=False):
        st_auth.resetpassword(auth, config)
        st_auth.updateuser(auth, config)
    st_auth.logout(auth)

    if st.session_state['admin_page']:
        admin.run()
        if (datetime.date(datetime.today()) == meetings.next_meeting_date()) or testing:
            meetings.attendance_manual()
        # Show Save Attendance Link
        if (st.session_state['username'] in ['btharp', '1schlick33', '1test']) and testing:
            if st.button('Save Attendance Record'):
                roster.post_meeting_attendance()
                #st.write('Save Attendance')\
            if st.button('Archive Roster'):
                firestore.archive_roster()
    else:
        st.markdown(f'#### Welcome, {st.session_state["name"]}\.')
        memberstatus = roster.member_status(st.session_state.user_info)
        if memberstatus is False:
            st.write('Your information could not be connected to the existing roster, please contact committee officers for help.')
        else:
        # st.markdown('''---''')
            st.write(f'Based on our attendance records of the last four (4) committee meetings, you are a {memberstatus}.')
            st.write(f'Our records indicate your preferred contact email address is {roster.user_email(st.session_state.user_info)}.')
            st.write(f'The affiliations we have on file are {roster.user_affiliations(st.session_state.user_info)}.')
            st.caption('If any of this information is incorrect, please contact your committee officers. They will help update the roster.')
        st.markdown('''---''')

        if (datetime.date(datetime.today()) == meetings.next_meeting_date()) or testing:
            col1,col2,col3 = st.columns([1,6,1])
            with col2:
                # Active meeting attendance
                st.subheader('Record Attendance of Comittee Meeting')
                meetings.attendance_statement()
            st.markdown('''---''')
        if (datetime.today() < datetime(year=2024, month=6, day=1)) or testing:
            col1,col2,col3 = st.columns([1,6,1])
            with col2:
                # Call for Nominations 4/22 through 6/1, 2024
                vt.run()
            st.markdown('''---''')
        col1,col2,col3 = st.columns([1,6,1])
        with col2:
            meetings.run()
        st.markdown('''---''')
        col1,col2,col3 = st.columns([1,6,1])
        with col2:
            wg.run()    
st.markdown('''---''')
officers.run()
