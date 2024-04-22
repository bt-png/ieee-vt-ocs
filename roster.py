import streamlit as st
import pandas as pd
import firestore

val = firestore.get_roster()
df = pd.DataFrame.from_dict(data=val, orient='index')
df = df.sort_values('Last Name')

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