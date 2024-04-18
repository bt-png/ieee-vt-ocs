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

import streamlit as st
import pandas as pd

def run():
    st.subheader('Upcoming Committee Meeting')
    show_upcoming()
    st.subheader('Recent Committee Meetings')
    show_recent()
    #if st.session_state["username"] =='btharp05':
    #    postnew = st.button('post')
    #    if postnew:
    #        post_newmeeting()
    #        print('posted')

@st.cache_data
def schedule():
    df = pd.DataFrame({
        'number': [],
        'location': [],
        'type': [],
        'start': [],
        'end': []
    })
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

def show_upcoming():
    df = schedule()
    df['time'] = df['start']
    st.dataframe(
        data=df.tail(1), 
        hide_index=True, 
        column_order=['number', 'location', 'type', 'start'],
        column_config={
            'start': st.column_config.DatetimeColumn(
                label='date',
                format='MMM D, YYYY'
            ),
        }
        )
    #'time': st.column_config.TimeColumn(
    #            label='start',
    #            format='hh:mm a z'
    #        )

def show_recent():
    df = schedule()
    df.drop(df.tail(1).index, inplace=True)
    st.dataframe(
        data=df.tail(3), 
        hide_index=True, 
        column_order=['number', 'location', 'start'],
        column_config={
            'start': st.column_config.DateColumn(
                label='start date',
                format='MMM D, YYYY'
            )
        }
        )

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