import streamlit as st
import pandas as pd
import roster
import firestore
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def run():
    st.header('Officers Administration Page')

    st.markdown('---')
    st.subheader('Nominations')
    st.caption('P1628')
    df_P1628 = firestore.get_nominations('P1628')
    st.dataframe(df_P1628, hide_index=True)
    st.caption('P3357')
    df_P3357 = firestore.get_nominations('P3357')
    st.dataframe(df_P3357, hide_index=True)
    st.markdown('---')
    st.subheader('Committee Roster')
    df_roster = roster.df
    st.dataframe(df_roster, hide_index=True, column_order=['Status', 'Name', 'Affiliation', 'E-mail'])

    st.markdown('---')
    st.subheader('Active Attendance')
    df_attendance = firestore.in_attendance()
    df_attendance = pd.merge(df_attendance, df_roster[['Name', 'Affiliation', 'E-mail']],  how='left', on='Name')
    _affiliations_count = df_attendance['Affiliation'].value_counts()
    if len(_affiliations_count) > 0:
        wordcloud = WordCloud(width=600, height=300, margin=10, prefer_horizontal=1, background_color=None).generate_from_frequencies(frequencies=_affiliations_count)
        plt.imshow(wordcloud.recolor(color_func=grey_color_func, random_state=3), interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt, use_container_width=False)
        _total_voting_members = len(df_roster[df_roster['Status'] == 'V'])
        _inattendance_voting_members = len(df_attendance[df_attendance['Status'] == 'Voting Member'])

        col1, col2, col3 = st.columns([20,10,10])
        col1.write(f'Total persons recorded in attendance: {len(df_attendance)}')
        col1.write(f'Total voting-members: {_total_voting_members}, in-attendance: {_inattendance_voting_members}')
        if col2.button('Refresh Attendance'): firestore.in_attendance.clear()
        col1, col2, col3 = st.columns([1,10,20])
        with col2:
            if roster.meets_quorum(_inattendance_voting_members, _total_voting_members):
                st.success('Quorum is met')
            else:
                st.warning('Quorum is not yet achieved')

        col1, col2, col3 = st.columns([1,10,10])
        df_member_attendance = pd.DataFrame({})
        df_member_attendance['Name'] = df_roster[df_roster['Status'] == 'V']['Name']
        df_member_attendance = pd.merge(df_attendance[df_attendance['Status'] == 'Voting Member'], df_member_attendance, how='outer', on='Name')
        df_member_attendance['Status'] = (df_member_attendance['Status'] == 'Voting Member')
        df_member_attendance.rename(columns={'Status': 'In Attendance'}, inplace=True)
        #df_member_attendance = pd.merge(df_member_attendance, df_roster[['Name', 'Affiliation', 'E-mail']],  how='left', on='Name')
        col2.caption(f"Voting Members: {_inattendance_voting_members}")
        col2.dataframe(df_member_attendance, hide_index=True,
                    column_order=['In Attendance', 'Name', 'Affiliation'],
                    column_config={
                        'Name': st.column_config.TextColumn(width='medium'),
                        'Affiliation': st.column_config.TextColumn(width='medium')
                    })
        df_nonmember_attendance = df_attendance[df_attendance['Status'] != 'Voting Member']
        #df_nonmember_attendance = pd.merge(df_nonmember_attendance, df_roster[['Name', 'Affiliation', 'E-mail']],  how='left', on='Name')
        col3.caption(f"Non-Voting Members, Non-Members, Staff: {len(df_nonmember_attendance)}")
        col3.dataframe(df_nonmember_attendance, hide_index=True,
                    column_order=['Name', 'Affiliation'],
                    column_config={
                        'Name': st.column_config.TextColumn(width='medium'),
                        'Affiliation': st.column_config.TextColumn(width='medium')
                    })

    #st.write(st.session_state.user_info)

    #roster.user_info(st.session_state.user_info)

    #roster.contact_list()
