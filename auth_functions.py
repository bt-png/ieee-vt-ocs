import json
import streamlit as st

from google.cloud import firestore
from google.oauth2 import service_account

key_dict = json.loads(st.secrets['Firestorekey'])

creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

## -------------------------------------------------------------------------------------------------
## Firebase Auth API -------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------

def sign_in_with_email_and_password(email, password):
    users_ref = db.collection('users')
    for doc in users_ref.stream():
        val = doc.to_dict()
        if val['email'] == email:
            if val['password'] == password:
                return doc.id
            else:
                return None

def get_account_info(id_token):
    return db.collection('users').document(id_token).get().to_dict()

#def send_email_verification(id_token):
#    request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(st.secrets['FIREBASE_WEB_API_KEY'])
#   headers = {"content-type": "application/json; charset=UTF-8"}
#    data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": id_token})
#    request_object = requests.post(request_ref, headers=headers, data=data)
#    raise_detailed_error(request_object)
#    return request_object.json()

#def send_password_reset_email(email):
    #request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(st.secrets['FIREBASE_WEB_API_KEY'])
    #headers = {"content-type": "application/json; charset=UTF-8"}
    #data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
    #request_object = requests.post(request_ref, headers=headers, data=data)
    #raise_detailed_error(request_object)
    #return request_object.json()

#def create_user_with_email_and_password(email, password):
#    request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={0}".format(st.secrets['FIREBASE_WEB_API_KEY'])
#    headers = {"content-type": "application/json; charset=UTF-8" }
#    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
#    request_object = requests.post(request_ref, headers=headers, data=data)
#    raise_detailed_error(request_object)
#    return request_object.json()

def delete_user_account(id_token):
    return db.collection('users').document(id_token).delete()

#def raise_detailed_error(request_object):
    #try:
    #    request_object.raise_for_status()
    #except requests.exceptions.HTTPError as error:
    #    raise requests.exceptions.HTTPError(error, request_object.text)

## -------------------------------------------------------------------------------------------------
## Authentication functions ------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------

def sign_in(email:str, password:str) -> None:
    try:
        # Attempt to sign in with email and password
        id_token = sign_in_with_email_and_password(email,password)
        
        if id_token is None:
            st.session_state.auth_warning = 'Error: Use a valid email and password'
        else:
            # Get account information
            user_info = get_account_info(id_token)

            # Save user info to session state and rerun
            st.session_state.user_info = user_info
            st.rerun()

    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'


def create_account(email:str, password:str, firstname:str, lastname:str) -> None:
    try:
        # Create account
        username = lastname.lower() + firstname.lower()
        doc_ref = db.collection('users').document(username)
        if doc_ref.get().exists:
            st.session_state.auth_warning = 'Error: User already registered!'
            exit
        else:
            doc_ref.set({
                'first': firstname.title(),
                'last': lastname.title(),
                'email': email,
                'password': password
            })
            sign_in(email, password)
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'


#def reset_password(email:str) -> None:
    #try:
    #    send_password_reset_email(email)
    #    st.session_state.auth_success = 'Password reset link sent to your email'
    
    #except requests.exceptions.HTTPError as error:
    #    error_message = json.loads(error.args[1])['error']['message']
    #    if error_message in {"MISSING_EMAIL","INVALID_EMAIL","EMAIL_NOT_FOUND"}:
    #        st.session_state.auth_warning = 'Error: Use a valid email'
    #    else:
    #        st.session_state.auth_warning = 'Error: Please try again later'    
    
    #except Exception:
    #    st.session_state.auth_warning = 'Error: Please try again later'


def sign_out() -> None:
    st.session_state.clear()
    st.session_state.auth_success = 'You have successfully signed out'


def delete_account(password:str) -> None:
    try:
        # Confirm email and password by signing in (and save id_token)
        id_token = sign_in_with_email_and_password(st.session_state.user_info['email'],password)
        
        if id_token is None:
            st.session_state.auth_warning = 'Error: Use a valid email and password'
        else:
            # Attempt to delete account
            delete_user_account(id_token)
            st.session_state.clear()
            st.session_state.auth_success = 'You have successfully deleted your account'
    except Exception as error:
        print(error)
        st.session_state.auth_warning = 'Error: Please try again later'

def fetch_all_users():
    users_ref = db.collection('users')
    for doc in users_ref.stream():
        st.write(doc.id, doc.to_dict())

