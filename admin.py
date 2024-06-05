import streamlit as st
import pandas as pd
import roster
import firestore
import meetings
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
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


def showattendance(df_roster):
    st.markdown('---')
    st.subheader('Active Attendance')
    df_attendance = firestore.in_attendance()
    df_attendance = pd.merge(df_attendance, df_roster[['Name', 'Affiliation', 'E-mail']],  how='left', on='Name')
    _affiliations_count = df_attendance['Affiliation'].value_counts()
    #
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
    col1, col2, col3 = st.columns([1, 10, 20])
    with col2:
        if roster.meets_quorum(_inattendance_voting_members, _total_voting_members):
            st.success('Quorum is met')
        else:
            st.warning('Quorum is not yet achieved')
    if col3.button('Refresh Attendance'):
    #    firestore.in_attendance.clear()
        st.rerun()
    col1, col2, col3 = st.columns([1, 10, 10])
    df_member_attendance = pd.DataFrame({})
    df_member_attendance['Name'] = df_roster[df_roster['Status'] == 'V']['Name']
    df_member_attendance = pd.merge(df_attendance[df_attendance['Status'] == 'Voting Member'], df_member_attendance, how='outer', on='Name')
    df_member_attendance['Status'] = (df_member_attendance['Status'] == 'Voting Member')
    df_member_attendance.rename(columns={'Status': 'In Attendance'}, inplace=True)
    df_member_attendance['Last Name'] = [lastname(name) for name in df_member_attendance['Name']]
    df_member_attendance = df_member_attendance.sort_values(by=['Last Name'])
    # df_member_attendance = pd.merge(df_member_attendance, df_roster[['Name', 'Affiliation', 'E-mail']],  how='left', on='Name')
    col2.caption(f"Voting Members: {_inattendance_voting_members}")
    col2.dataframe(
        df_member_attendance, hide_index=True,
        column_order=['In Attendance', 'Name', 'Affiliation'],
        column_config={
            'Name': st.column_config.TextColumn(width='medium'),
            'Affiliation': st.column_config.TextColumn(width='medium')
            }
        )
    df_nonmember_attendance = df_attendance[df_attendance['Status'] != 'Voting Member']
    # df_nonmember_attendance = pd.merge(df_nonmember_attendance, df_roster[['Name', 'Affiliation', 'E-mail']],  how='left', on='Name')
    df_nonmember_attendance['Last Name'] = [lastname(name) for name in df_nonmember_attendance['Name']]
    df_nonmember_attendance = df_nonmember_attendance.sort_values(by=['Last Name'])
    col3.caption(f"Non-Voting Members, Non-Members, Staff: {len(df_nonmember_attendance)}")
    col3.dataframe(
        df_nonmember_attendance, hide_index=True,
        column_order=['Name', 'Affiliation'],
        column_config={
            'Name': st.column_config.TextColumn(width='medium'),
            'Affiliation': st.column_config.TextColumn(width='medium')
            }
        )


def run():
    st.header('Officers Administration Page')
    st.markdown('---')
    shownominations()
    df_roster = roster.df
    showroster(df_roster)
    if (datetime.date(datetime.today()) == meetings.next_meeting_date()) or testing:
        showattendance(df_roster)
        meetings.attendance_manual()
    # Show Save Attendance Link
    if st.session_state['username'] in ['btharp']:
        col1, col2 = st.columns([1,1])
        meetingnumber = col1.number_input('Meeting Number')
        if col2.button('Save Attendance Record'):
            roster.post_meeting_attendance(int(meetingnumber))
        if False:
            if st.button('Archive Roster'):
                firestore.archive_roster()
