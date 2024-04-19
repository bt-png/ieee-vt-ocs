import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit as st
import pandas as pd
import firestore

def run():
    st.subheader('Upcoming Committee Meeting')
    show_upcoming()
    st.subheader('Recent Committee Meetings')
    show_recent()

@st.cache_data
def schedule():
    df = pd.DataFrame({
        'number': [],
        'location': [],
        'type': [],
        'start': [],
        'end': []
    })
    return firestore.get_schedule(df)

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
