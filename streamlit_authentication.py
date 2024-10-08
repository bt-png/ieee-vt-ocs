import streamlit as st
import streamlit_authenticator as stauth #pip install streamlit-authenticator
import firestore
import emailclient

def authenticate(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )
    return authenticator

def login(auth):
    user, status, username = auth.login(location='sidebar', max_login_attempts=5)
    return user, status, username

def logout(auth):
    return auth.logout(location='sidebar')

def resetpassword(auth, conf):
    if st.session_state["authentication_status"]:
        try:
            if auth.reset_password(username=st.session_state["username"]):
                st.sidebar.success('Password modified successfully')
                firestore.saveconfig(conf)
        except Exception as e:
            st.sidebar.error(e)

def updateuser(auth,conf):
    if st.session_state["authentication_status"]:
        try:
            fieldval = {'Form name':'Update user details', 'Field': 'Name or Email'}
            if auth.update_user_details(username=st.session_state["username"], fields=fieldval):
                st.sidebar.success('Entries updated successfully')
                firestore.saveconfig(conf)
        except Exception as e:
            st.sidebar.error(e)

def register(auth, conf):
    try:
        fieldval = {'Form name':'Create Account', 'Name': 'Full Name'}
        email, username, user = auth.register_user(location='sidebar', pre_authorization=False, fields=fieldval)
        if email:
            st.sidebar.success('User created successfully')
            firestore.saveconfig(conf)
            st.session_state['name'] = user
            st.session_state['authentication_status'] = True
            st.session_state['username'] = username
            st.session_state['user_info'] = user
            st.rerun()
        return email, username, user
    except Exception as e:
        st.sidebar.error(e)

def forgotpassword(auth, conf):
    try:
        username, email, new_random_password = auth.forgot_password(location='sidebar')
        if username:
            firestore.saveconfig(conf)
            emailclient.passwordreset(email, new_random_password)
            return username, email, new_random_password
        elif username == False:
            st.sidebar.error('Username not found')
    except Exception as e:
        st.sidebar.error(e)

def forgotusername(auth):
    try:
        username, email = auth.forgot_username(location='sidebar')
        if username:
            emailclient.forgotusername(email, username)
            return username, email
        elif username == False:
            st.sidebar.error('Email not found')
    except Exception as e:
        st.sidebar.error(e)
    