import streamlit as st
import streamlit_authentication as st_auth
import voting_tally as vt

config = st_auth.openconfig()
auth = st_auth.authenticate(config)
## -------------------------------------------------------------------------------------------------
## Not logged in -----------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
if 'user_info' not in st.session_state:
    do_you_have_an_account = st.sidebar.selectbox(label='Start here',options=('Sign in','Sign up','I forgot my password','I forgot my username'), key='starthere')
    if do_you_have_an_account == 'Sign in':
        user, status, username = st_auth.login(auth)
    elif do_you_have_an_account =='Sign up':
        try:
            email, username, user = st_auth.register(auth)
            if email:
                st.sidebar.success('User registered successfully, please login')
                st_auth.saveconfig(config)
                st.sessionstate.starthere='Sign in'
                st.rerun()
        except Exception as e:
            st.sidebar.error(e)
    elif do_you_have_an_account == 'I forgot my password':
        try:
            username, email, new_random_password = st_auth.forgotpassword(auth)
            if username:
                st.sidebar.success('New password to be sent securely')
                # The developer should securely transfer the new password to the user.
                st_auth.saveconfig(config)
                st.sidebar.write('your new password is ' + new_random_password)
            elif username == False:
                st.sidebar.error('Username not found')
        except Exception as e:
            st.sidebar.error(e)
    elif do_you_have_an_account == 'I forgot my username':
        try:
            username, email = st_auth.forgotusername(auth)
            if username:
                st.sidebar.success('Username to be sent securely')
                st.sidebar.write('your username is ' + username)
                # The developer should securely transfer the username to the user.
            elif username == False:
                st.sidebar.error('Email not found')
        except Exception as e:
            st.sidebar.error(e)

    if 'authentication_status' in st.session_state:
        if st.session_state['authentication_status']:
            st.session_state.user_info = user
        elif st.session_state['authentication_status'] is False:
            st.sidebar.error('Username/password is incorrect')
        elif st.session_state['authentication_status'] is None:
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
    vt.run()
