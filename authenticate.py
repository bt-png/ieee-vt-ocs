import json
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
#import streamlit_authenticator as stauth


key_dict = json.loads(st.secrets['Firestorekey'])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

def insert_user(first, last, email, password):
    #db = firestore.Client()
    username = last.lower() + first.lower()
    doc_ref = db.collection('users').document(username)
    doc_ref.set({
        'first': first.title(),
        'last': last.title(),
        'email': email,
    })
    item_ref = doc_ref.collection('private').document('private')
    item_ref.set({
        'password': password
    })

def get_user_doc(username):
    '''Returns the userdoc object'''
    return db.collection('users').document(username)

def get_user(username):
    '''If not found, the function will return None'''
    userdoc = get_user_doc(username)
    return userdoc.get().to_dict()

def get_user_email(username):
    return get_user(username)['email']

def fetch_all_users():
    users_ref = db.collection('users')
    for doc in users_ref.stream():
        st.write(doc.id, doc.to_dict())

def update_user_email(username, newemail):
    '''If the item is updated, returns success'''
    update = {'email': newemail}
    userdoc = get_user_doc(username)
    userdoc.set(update)
    user = get_user(userdoc)
    if newemail == get_user_email(user):
        st.success('Updated')
    else:
        st.warning('Update not successful')
    
def delete_user(username):
    '''Always returns None'''
    userdoc = get_user_doc(username)
    return userdoc.delete()
