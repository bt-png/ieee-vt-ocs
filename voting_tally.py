import streamlit as st
import pandas as pd

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
    col1,col2,col3 = st.columns([1,4,1])
    col2.subheader('Calling Nominations')
    col2.write('\
        We have two (2) openings for the position of Working Group Chair \
        and are looking for nominations!!.\
        Use the below form to submit your nomination.\
        ')
    col2.caption('Voting will take place at our next comittee meeting.')
    with col2.expander('Nominate a candidate for P1628'):
        #st.caption('Current Nominations')
        
        st.write("Submit your nomination")
        with st.form(key='Nomination form (P1628)',clear_on_submit=False):
            st.text_input(label='Full Name',key='P1628_name')
            if st.form_submit_button(label='Submit',use_container_width=True,type='primary'):
                submit_entry(st.session_state.P1628_name, 'P1628')
                st.caption(f"Your nomination for '{st.session_state.P1628_name}' has been entered")
                pull_entry('P1628')
                st.warning('This form will be open until July 1st if you want to change your nomination.') 
    with col2.expander('Nominate a candidate for P3357'):
        st.write("P3357 - ")
        st.caption('Current Nominations')

#@st.cache_data
def pull_entry(WG):
    aname=[]
    acount=[]
    doc_ref = db.collection(WG)
    for doc in doc_ref.stream():
        val = doc.to_dict()
        aname.append(val['name'])
        acount.append(val['count'])
    df = pd.DataFrame({'Current Nominees': aname, 'count': acount})
    df = df.sort_values(by=['count'], ascending=False)
    st.dataframe(data=df['Current Nominees'], hide_index=True)

#@st.cache_data
def submit_entry(name, WG):
    try:
        # Create account
        doc_ref = db.collection(WG).document(name)
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            #print(val)
            val['nominators'].append(st.session_state['name'])
            val['count'] += 1
            doc_ref.set(val)
            #print(val)
        else:
            doc_ref.set({
                'name': name.title(),
                'position': 'WG Chair Nomination',
                'workinggroup': WG,
                'count': 1,
                'nominators': [st.session_state['name']]
            })
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'
