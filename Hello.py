import streamlit as st
st.set_page_config(
        page_title='IEEE VT OCS Standards Committee',
        page_icon='🚊',
        layout='wide'
    )

import streamlit_authentication as st_auth
import firestore
config = firestore.openconfig()
auth = st_auth.authenticate(config)

import voting_tally as vt
import meetings
import workinggroups as wg
import board


## -------------------------------------------------------------------------------------------------
## Not logged in -----------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------

if 'user_info' not in st.session_state:
    col1,col2,col3 = st.columns([1,6,1])
    col2.header('IEEE VT OCS Standards Committee')
    col2.image(image='IMG_0079.jpg')
    #col2.button('test', on_click=testfun())
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
        ## Logged out
        st.session_state.clear()
        st.rerun()
    ## ---------------------------------------------------
    ## Logged in -----------------------------------------
    ## ---------------------------------------------------
    # Show user information
    st.sidebar.header('Hello ' + st.session_state.user_info +'!')
    with st.sidebar.expander('Update Profile', expanded=False):
        st_auth.resetpassword(auth, config)
        st_auth.updateuser(auth, config)
    st_auth.logout(auth)
    #st.write(st_auth.output(config))
    st.write(f'Welcome, {st.session_state["name"]}\.')
    #st.title('Some content')
    
    st.markdown('''---''')
    col1,col2,col3 = st.columns([1,6,1])
    with col2:
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
board.run()
