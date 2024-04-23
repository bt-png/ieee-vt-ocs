import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit as st
import pandas as pd
import firestore

#@st.cache_data
def run():
    df = schedule()
    st.subheader('Upcoming Committee Meeting')
    show_upcoming(df)
    st.subheader('Recent Committee Meetings')
    show_recent(df)

@st.cache_data
def schedule():
    return firestore.get_schedule()

def show_upcoming(dfinput):
    df = dfinput.copy()
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

def show_recent(dfinput):
    df = dfinput.copy()
    st.dataframe(df)
    df.drop(df.tail(1).index, inplace=True)
    st.dataframe(
        data=df.tail(3), 
        hide_index=True, 
        column_order=['link', 'number', 'location', 'start'],
        column_config={
            'start': st.column_config.DateColumn(
                label='start date',
                format='MMM D, YYYY'
            ),
            'link': st.column_config.LinkColumn(
                label='',
                display_text='Minutes'
            )
        }
        )

def dateonly(datetimeobject):
    return '%s/%s/%s' % (datetimeobject.month, datetimeobject.day, datetimeobject.year)
