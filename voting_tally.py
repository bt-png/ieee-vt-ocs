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
    st.subheader('Call for Nominations')
    st.write('\
        We have openings for the position of Working Group Chair \
        for two (2) of our committees, and are looking for nominations!\
        Each committee has a form below. Please use them to cast your nomination.\
        ')
    st.caption('Voting will take place at our next comittee meeting.')
    with st.expander('Nominate a candidate for P1628'):
        st.caption('Recommended Practice for Maintenance of Direct Current (DC) Overhead Contact Systems for Transit Systems')
        #st.write("Submit your nomination")
        with st.form(key='Nomination form (P1628)',clear_on_submit=False):
            existing_vote = pull_existing_vote('P1628')
            st.text_input(label='Nominee Full Name', value=existing_vote, key='P1628_name')
            vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
            if st.form_submit_button(label=vote_label,use_container_width=True,type='primary'):
                if st.session_state.P1628_name == st.session_state['name']:
                    st.error('You cannot nominate yourself!')
                else:
                    submit_entry(st.session_state.P1628_name, 'P1628')
                    if existing_vote == '':
                        st.caption(f"Your nomination for '{st.session_state.P1628_name}' has been entered")
                    else:
                        st.caption(f"Your nomination has been revised, '{st.session_state.P1628_name}' has been entered")
                    pull_entry('P1628')
                    st.warning('This form will be open until July 1st if you want to change your nomination.')
                
    with st.expander('Nominate a candidate for P3357'):
        st.caption('Recommended Practice for Grounding Overhead Contact System (OCS) Poles and Supports on Light Rail Transit Systems')
        #st.write("Submit your nomination")
        with st.form(key='Nomination form (P3357)',clear_on_submit=False):
            existing_vote = pull_existing_vote('P3357')
            st.text_input(label='Nominee Full Name', value=existing_vote, key='P3357_name')
            vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
            if st.form_submit_button(label=vote_label,use_container_width=True,type='primary'):
                if st.session_state.P3357_name == st.session_state['name']:
                    st.error('You cannot nominate yourself!')
                else:
                    submit_entry(st.session_state.P3357_name, 'P3357')
                    if existing_vote == '':
                        st.caption(f"Your nomination for '{st.session_state.P3357_name}' has been entered")
                    else:
                        st.caption(f"Your nomination has been revised, '{st.session_state.P3357_name}' has been entered")
                    pull_entry('P3357')
                    st.warning('This form will be open until July 1st if you want to change your nomination.')

def pull_existing_vote(WG):
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
def pull_entry(WG):
    df = pd.DataFrame({
        'Current Nominees': [],
        'count': []
    })
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
    df = df.sort_values(by=['Current Nominees'], ascending=True)
    st.dataframe(data=df['Current Nominees'], hide_index=True)

#@st.cache_data
def submit_entry(name, WG):
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
