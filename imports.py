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
    file = st.file_uploader(label='image')
    if file is not None:
        try:
            # Create account
            doc_ref = db.collection('uploads').document('mainimage')
            doc = doc_ref.get()
            if doc.exists:
                val = doc.to_dict()
                val['image'] = file
                doc_ref.set(val)
            else:
                doc_ref.set({
                    'image': file
                })
        except Exception as error:
            print(error)
            st.session_state.auth_warning = 'Error: Please try again later'