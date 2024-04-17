import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth #pip install streamlit-authenticator

### Firestore Authentication
import json
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
key_dict = json.loads(st.secrets['Firestorekey'])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

def openconfig():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def saveconfig(conf):
    with open('config.yaml', 'w') as file:
        yaml.dump(conf, file, default_flow_style=False)

def openconfig_firebase():
    doc_ref = db.collection('yaml').document('users')
    doc = doc_ref.get()
    val = doc.to_dict()
    conf = val['yaml']
    return conf

def saveconfig_firebase(conf):
    try:
        doc_ref = db.collection('yaml').document('users')
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            val['yaml'] = conf
            doc_ref.set(val)
        else:
            doc_ref.set({
                'yaml': conf
            })
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'

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
                #saveconfig(conf)
                saveconfig_firebase(conf)
        except Exception as e:
            st.sidebar.error(e)

def updateuser(auth,conf):
    if st.session_state["authentication_status"]:
        try:
            fieldval = {'Form name':'Update user details', 'Field': 'Name or Email'}
            if auth.update_user_details(username=st.session_state["username"], fields=fieldval):
                st.sidebar.success('Entries updated successfully')
                #saveconfig(conf)
                saveconfig_firebase(conf)
        except Exception as e:
            st.sidebar.error(e)

def register(auth):
    return auth.register_user(location='sidebar', pre_authorization=False)

def forgotpassword(auth):
    return auth.forgot_password(location='sidebar')

def forgotusername(auth):
    return auth.forgot_username(location='sidebar')
    
def output(conf):
    return conf
