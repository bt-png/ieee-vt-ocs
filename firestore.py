import streamlit as st
from datetime import datetime
import pandas as pd

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
        st.session_state.auth_warning = 'Error: Please try again later'

#---------nominations----------------
def get_existing_nomination(WG):
    try:
        doc_ref = db.collection(WG).document(st.session_state['name'])
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['nominee']
        return ''
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'

def get_nominations(WG):
    try:
        doc_ref = db.collection(WG).document('nominees')
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            df = pd.DataFrame.from_dict(data = val, orient='index')
            df.reset_index(drop=True, inplace=True)
        else:
            df = pd.DataFrame({
            'Current Nominees': [],
            'count': []
            })
        return df
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'

def post_nominations(df, WG):
    df['Index'] = df['Current Nominees']
    df = df.set_index('Index')
    df_dict = df.transpose().to_dict()
    try:
        doc_ref = db.collection(WG).document('nominees')
        doc_ref.set(df_dict)
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'

def submit_nomination(name, WG):
    #get_existing_nomination.clear()
    df = get_nominations(WG)
    previous = submit_nomination_ind(name, WG)
    if previous:
        if name == previous:
            return df
        else:
            df = remove_nominee(df, previous)
    df = post_nominee(df, name)
    post_nominations(df, WG)
    return df

def post_nominee(df, name):
    if df.empty:
        new_record = pd.DataFrame([{'Current Nominees':name, 'count':1}])
        df = pd.concat([df, new_record], ignore_index=True)
    else:
        if name in df['Current Nominees'].values:
            df.loc[df['Current Nominees'] == name, 'count'] += 1
        else:
            new_record = pd.DataFrame([{'Current Nominees':name, 'count':1}])
            df = pd.concat([df, new_record], ignore_index=True)
    return df
  
def remove_nominee(df, name):
    if not(df.empty) and name in df['Current Nominees'].values:
        i = df[df['Current Nominees'] == name].index[0]
        if df['count'].iloc[i] == 1:
            df.drop(index=i, inplace=True, errors='ignore')
        else:
            df.loc[df['Current Nominees'] == name, 'count'] -= 1
    return df

def submit_nomination_ind(name, WG):
    try:
        doc_ref = db.collection(WG).document(st.session_state['name'])
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            previousnominee = val['nominee']
            val['nominee'] = name.title()
            val['date'] = datetime.now()
            if name != previousnominee:
                doc_ref.set(val)
            return previousnominee
        else:
            doc_ref.set({
                'nominee': name.title(),
                'position': 'WG Chair Nomination',
                'workinggroup': WG,
                'nominator': st.session_state['name'],
                'date': datetime.now()
            })
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'

#---------schedule----------------
@st.cache_data
def get_schedule():
    try:
        doc_ref = db.collection('meetings').document('data')
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            df = pd.DataFrame.from_dict(data=val, orient='index')
            df.sort_values(by='number', ascending=True, inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'

def post_schedule(dfinput):
    df = dfinput.copy()
    df['Index'] = 'Meeting ' + df['number'].astype(str)
    df = df.set_index('Index')
    df_dict = df.transpose().to_dict()
    try:
        doc_ref = db.collection('meetings').document('data')
        doc_ref.set(df_dict)
        return True
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False

def archive_schedule():
    doc_ref = db.collection('roster').document('contactlist')
    doc = doc_ref.get()
    if doc.exists:
        val = doc.to_dict()
    doc_ref = db.collection('roster').document('contactlist_archive_20240529')
    doc_ref.set(val)

#---------roster----------------
@st.cache_data
def get_roster():
    doc_ref = db.collection('roster').document('contactlist')
    doc = doc_ref.get()
    if doc.exists:
        val = doc.to_dict()
        return val


def archive_roster():
    doc_ref = db.collection('roster').document('contactlist')
    doc = doc_ref.get()
    if doc.exists:
        val = doc.to_dict()
    doc_ref = db.collection('roster').document('contactlist_archive_20240529')
    doc_ref.set(val)


def set_roster(_dfinput):
    df = _dfinput.copy()
    df['Index'] = [str(last + ', ' + first) for last, first in zip(df['Last Name'], df['First Name'])]
    df = df.set_index('Index')
    df_dict = df.transpose().to_dict()
    try:
        doc_ref = db.collection('roster').document('contactlist')
        doc_ref.set(df_dict)
        return True
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False


#---------attendance----------------
def mark_in_attendance(fullname):
    try:
        doc_ref = db.collection('meetings').document(fullname)
        doc = doc_ref.get()
        if doc.exists:
            st.caption(f'{fullname} is already recorded as in attendance.')
        else:
            doc_ref.set({
                'Attendee': fullname,
                'Submitted': datetime.now(),
                'Submitted_By': st.session_state.user_info
            })
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'


def clear_in_attendance():
    try:
        doc_ref = db.collection('meetings')
        batch = db.batch()
        for doc in doc_ref.stream():
            if doc.id != 'data':
                batch.delete(doc.reference)
        batch.commit()
        return True
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False


@st.cache_data
def in_attendance():
    import roster
    df = pd.DataFrame({
        'Name': [],
        'Status': []
    })
    doc_ref = db.collection('meetings')
    for doc in doc_ref.stream():
        if doc.id != 'data':
            new_entry = pd.DataFrame([{'Name': doc.id, 'Status': roster.member_status(doc.id)}])
            df = pd.concat([df,new_entry], ignore_index=True)
    return df
