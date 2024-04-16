import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth #pip install streamlit-authenticator

def openconfig():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def authenticate(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )
    return authenticator

def login(auth):
    return auth.login(location='sidebar', max_login_attempts=5)

def logout(auth):
    return auth.logout(location='sidebar')

def resetpassword(auth, conf):
    if st.session_state["authentication_status"]:
        try:
            if auth.reset_password(username=st.session_state["username"]):
                st.sidebar.success('Password modified successfully')
                saveconfig(conf)
        except Exception as e:
            st.sidebar.error(e)

def updateuser(auth,conf):
    if st.session_state["authentication_status"]:
        try:
            if auth.update_user_details(st.session_state["username"]):
                st.sidebar.success('Entries updated successfully')
                saveconfig(conf)
        except Exception as e:
            st.sidebar.error(e)

def register(auth):
    return auth.register_user(location='sidebar', pre_authorization=False)

def forgotpassword(auth):
    return auth.forgot_password(location='sidebar')

def forgotusername(auth):
    return auth.forgot_username(location='sidebar')

def saveconfig(conf):
    with open('config.yaml', 'w') as file:
        yaml.dump(conf, file, default_flow_style=False)
    
def output(conf):
    return conf