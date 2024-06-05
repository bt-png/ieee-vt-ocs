import streamlit as st
import pandas as pd
import roster
import firestore
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
import meetings
from datetime import datetime

testing = False

def lastname(name):
    try:
        first, *middle, last = name.split()
    except Exception:
        last = name
    return last


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def showroster(df):
    st.subheader('Committee Roster')
    _df = df.copy()
    _df['Status'] = [roster.member_status(name) for name in _df['Name']]
    st.dataframe(_df, hide_index=True, column_order=['Status', 'Name', 'Affiliation', 'E-mail'])
    st.write('Send email to committee')
    col1, col2, col3, col4 = st.columns([.04, .18, .18, .60])
    email_votingmembers = roster.contact_list_votingmember()
    email_nonvotingmembers =roster.contact_list_notvotingmember()
    email_activemembers =roster.contact_list_activemember()
    email_all =roster.contact_list_all()
    col2.link_button(label='Voting Members', url=f"mailto:?to={email_votingmembers}&subject=IEEE VT/OCS Standards Committee: ")
    col3.link_button(label='Active Members', url=f"mailto:?to={email_activemembers}&subject=IEEE VT/OCS Standards Committee: ")
    if col4.button('All Members'):
        #col3.link_button(label='Try Email', url=f"mailto:?to={email_all}subject=IEEE VT/OCS Standards Committee: ")
        st.warning('There are too many addressess to create an email automatically. Copy the list below.')
        st.link_button(label='Blank Email', url=f"mailto:?subject=IEEE VT/OCS Standards Committee: ")
        Path = f'''{email_all}'''
        st.code(Path, language="python")


def shownominations():
    st.subheader('Nominations')
    st.caption('P1628')
    df_P1628 = firestore.get_nominations('P1628')
    st.dataframe(df_P1628, hide_index=True)
    st.caption('P3357')
    df_P3357 = firestore.get_nominations('P3357')
    st.dataframe(df_P3357, hide_index=True)
    st.caption('P3425')
    df_P3425 = firestore.get_nominations('P3425')
    st.dataframe(df_P3425, hide_index=True)
    st.markdown('---')


def showvotes():
    if False:
        st.subheader('Votes Cast')
        st.caption('P1628')
        df_P1628 = firestore.get_nominations('Vote_P1628')
        st.dataframe(df_P1628, hide_index=True)
        st.caption('P3357')
        df_P3357 = firestore.get_nominations('Vote_P3357')
        st.dataframe(df_P3357, hide_index=True)
        st.markdown('---')


def run():
    st.header('Officers Administration Page')
    st.markdown('---')
    shownominations()
    df_roster = roster.df
    showroster(df_roster)
