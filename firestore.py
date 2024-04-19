import streamlit as st
from datetime import datetime
### Firestore Authentication
import json
import yaml
from yaml.loader import SafeLoader
from google.cloud import firestore
from google.oauth2 import service_account
key_dict = json.loads(st.secrets['Firestorekey'])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

#---------login----------------
#@st.cache_data
def openconfig():
    doc_ref = db.collection('roster').document('login')
    doc = doc_ref.get()
    conf = doc.to_dict()
    return conf

def saveconfig(conf):
    try:
        doc_ref = db.collection('roster').document('login')
        doc_ref.set(conf)
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'

#---------nominations----------------
#@st.cache_data
def get_existing_nomination(WG):
    try:
        doc_ref = db.collection(WG).document(st.session_state['name'])
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['nominee']
        return ''
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'

#@st.cache_data
def get_nominations(df, WG):
    try:
        doc_ref = db.collection(WG)
        for doc in doc_ref.stream():
            val = doc.to_dict()
            if df.empty:
                df.loc[len(df.index)] = [val['nominee'], 0]
            else:
                if val['nominee'] in df['Current Nominees'].values:
                    df.loc[df['Current Nominees'] == val['nominee'], 'count'] += 1
                else:
                    df.loc[len(df.index)] = [val['nominee'], 0]
        return df
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'

def submit_nomination(name, WG):
    try:
        doc_ref = db.collection(WG).document(st.session_state['name'])
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            val['nominee'] = name
            val['date'] = datetime.now()
            doc_ref.set(val)
        else:
            doc_ref.set({
                'nominee': name.title(),
                'position': 'WG Chair Nomination',
                'workinggroup': WG,
                'nominator': st.session_state['name'],
                'date': datetime.now()
            })
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'

#---------schedule----------------
@st.cache_data
def get_schedule(df):
    doc_ref = db.collection('meetings')
    for doc in doc_ref.stream():
        items = doc.to_dict()
        df.loc[len(df.index)] = [
            items['number'], 
            items['location'],
            items['type'],
            items['start'],
            items['end']
        ]
    return df

#---------roster----------------
@st.cache_data
def get_roster():
    doc_ref = db.collection('roster').document('contactlist')
    doc = doc_ref.get()
    if doc.exists:
        val = doc.to_dict()
        return val