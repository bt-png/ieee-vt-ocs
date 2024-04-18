import streamlit as st
import pandas as pd

def run():
    st.subheader('Working Groups')
    dfPARS = PARS()
    dfPARS = dfPARS[dfPARS['Project Status'] == 'Draft Development']
    dfSt = Standards()
    st.caption('Active PARS')
    st.dataframe(data=dfPARS,
                 hide_index=True,
                 height = ((min(len(dfPARS.index),5) + 1) * 35 + 3),
                 column_order=['Project Number', 'Expiration PAR Date', 'Project Title'],
                 column_config={
                     'Project Number': 'Ref',
                     'Expiration PAR Date': st.column_config.DateColumn(
                         label='Expiration',
                         format='MMM DD, YYYY'
                     )
                 },
                 use_container_width=True
                 )
    
    st.caption('WG Published Standards')
    st.dataframe(data=dfSt.style.apply(color_coding, axis=1),
                 hide_index=True,
                 height = ((min(len(dfSt.index),5) + 1) * 35 + 3),
                 column_order=['Standard Number', 'Year', 'Project Title', 'Status'],
                 column_config={
                     'Standard Number': st.column_config.TextColumn(label='Ref'),
                     'Year': st.column_config.TextColumn(label='Published')
                 },
                 use_container_width=True
                 )

@st.cache_data
def PARS():
    df = pd.read_csv('ParsReport.CSV')
    return df

@st.cache_data
def Standards():
    df = pd.read_csv('ParsStandardReport.CSV')
    df.loc[df['Status'] == 'Completed', 'Status'] = 'Active'
    df.loc[df['Status'] == 'Inactive Reserved', 'Status'] = 'Inactive'
    df = df.sort_values(by=['Standard Number'])
    return df

@st.cache_data
def PARS_Title(WG):
    df = PARS()
    item = df.loc[df['Project Number'] == WG, 'Project Title'].item()
    return item

@st.cache_data
def PARS_Scope(WG):
    df = PARS()
    item = df.loc[df['Project Number'] == WG, 'Scope'].item()
    return item

def color_coding(row):
    return ['background-color:grey'] * len(row) if row['Status'] == 'Inactive' else ['background-color:black']*len(row)