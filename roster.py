import streamlit as st
import pandas as pd
import firestore

val = firestore.get_roster()
df = pd.DataFrame.from_dict(data=val, orient='index')
df.sort_values(by='Last Name', ascending=True, inplace=True)
df.reset_index(drop=True, inplace=True)

@st.cache_data
def names():
    return df['Name']

def match_user(txt):
    val = txt.title()
    firstnames = df.loc[df['First Name'].str.startswith(val), 'Name']
    lastnames = df.loc[df['Last Name'].str.startswith(val), 'Name']
    df_search = pd.concat([firstnames, lastnames], ignore_index=True)
    return df_search

def match_user_key(key):
    df_search = match_user(st.session_state[key])
    st.dataframe(df_search, hide_index=True, use_container_width=True)

def user_info(FullName):
    st.dataframe(df.loc[df['Name'] == FullName])

def member_status(FullName):
    txt = df['Status'].loc[df['Name'] == FullName].values
    if txt == 'V':
        return 'Voting Member'
    elif txt == 'P':
        return 'Non-Voting Member'
    elif txt == 'O':
        return 'Non-Member'
    elif txt == 'S':
        return 'Staff Member'

def contact_list():
    #email = df['E-mail'].loc[df['E-mail'].notnull()].to_csv(sep=";",index=False, lineterminator='\r\n')
    email = df['E-mail'].loc[df['E-mail'].notnull()].to_numpy()
    email = email.tolist()
    st.write(email, unsafe_allow_html=True)
