import streamlit as st
import pandas as pd
from datetime import datetime

### Firestore Authentication
import json
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
key_dict = json.loads(st.secrets['Firestorekey'])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)
##-End Firestore

def run():
    st.header('Committee Meetings')

import streamlit as st
import pandas as pd

def run():
    st.header('Committee Meetings')
    pull_entry()
    #if st.session_state["username"] =='btharp05':
    #    postnew = st.button('post')
    #    if postnew:
    #        post_newmeeting()
    #        print('posted')

#@st.cache_data
def pull_entry():
    val=[]
    doc_ref = db.collection('meetings')
    for doc in doc_ref.stream():
        items = doc.to_dict()
        items['start'] = dateonly(items['start'])
        items['end'] = dateonly(items['end'])
        val.append(items)
    st.dataframe(val, hide_index=True, column_order=('number', 'location', 'mtype', 'start'))

def dateonly(datetimeobject):
    return '%s/%s/%s' % (datetimeobject.month, datetimeobject.day, datetimeobject.year)

def post_newmeeting():
    submit_record(number = 63,
                  location = 'Cleveland',
                  mtype = 'Hybrid',
                  start = datetime(2024,6,5),
                  end = datetime(2024,6,5))

def submit_record(number, location, mtype, start, end):
    try:
        doc_ref = db.collection('meetings').document(str(number))
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            val['number'] = number
            val['location'] = location
            val['type'] = mtype
            val['start'] = start
            val['end'] = end
            doc_ref.set(val)
        else:
            doc_ref.set({
                'number': number,
                'location': location,
                'type': mtype,
                'start': start,
                'end': end,
            })
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'