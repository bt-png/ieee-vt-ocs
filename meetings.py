import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit as st
import pandas as pd
import firestore
import roster


def lastname(name):
    first, *middle, last = name.split()
    return last


def run():
    df = schedule()
    st.subheader('Upcoming Committee Meeting')
    show_upcoming(df)
    st.subheader('Recent Committee Meetings')
    show_recent(df)


def schedule():
    return firestore.get_schedule()


def attendance_statement():
    if 'inattendance' not in st.session_state:
        st.session_state.inattendance = False

    if st.session_state.inattendance:
        # The message and nested widget will remain on the page
        st.write('Thank you! Your attendance has been recorded.')
        st.warning(f'Based on your previous attendance records, your status at this meeting is a {roster.member_status(st.session_state.user_info)}.')
    else:
        st.write(' \
                I acknowledge, that I am currently attending the committee meeting, \
                and I intend to actively participate for the full scheduled duration. \
                ')
        if st.button(label='Acknowledge'):
            st.session_state.inattendance = True
            firestore.mark_in_attendance(st.session_state.user_info)
            st.rerun()


def attendance_manual():
    df_attendance = firestore.in_attendance()
    fullroster = roster.member_names()
    listofmeetingattendees = df_attendance['Name'].tolist()
    notinattendance = list(set(fullroster).difference(listofmeetingattendees))
    notinattendance.sort(key=lastname)
    with st.form(key='Attendance', clear_on_submit=True):
        name = st.selectbox(
            label='Mark in Attendance',
            options=notinattendance,
            index=None,
            placeholder='Select a Name',
            key='mark_attendance_manual')
        if st.form_submit_button(label='Record', use_container_width=False):
            if " " in name:
                firestore.mark_in_attendance(name)
                st.caption(f'Attendance for {name} has been recorded as a {roster.member_status(name)}')
            else:
                st.rerun()
    #if st.button('Update Attendance'):
    #    firestore.in_attendance.clear()
    #    #attendance_status()


def next_meeting_date():
    test = False
    if test:
        return datetime.date(datetime.today())
    else:
        df = schedule()
        return datetime.date(df[~df['recorded']].head(1).start.tolist()[0])


def show_upcoming(dfinput):
    df = dfinput.copy()
    df['time'] = df['start']
    st.dataframe(
        data=df[~df['recorded']],
        hide_index=True,
        column_order=['number', 'location', 'type', 'start'],
        column_config={
            'start': st.column_config.DatetimeColumn(
                label='date',
                format='MMM D, YYYY'
            ),
            # 'time': st.column_config.TimeColumn(
            #     label='start',
            #     format='hh:mm a z'
            # )
        }
    )


def show_recent(dfinput):
    df = dfinput.copy()
    st.dataframe(
        data=df[df['recorded']].tail(6), 
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


def attendance_count(df, status):
    return df.loc[df['status'] == status, 'name'].count()


def attendance_status():
    df_attendance = firestore.in_attendance()
    attendeeslist = df_attendance['Name'].tolist()
    currentvotingmembership = roster.totals_votingmembers()
    inattendance_total = len(attendeeslist)
    inattendance_votingmembers = attendance_count(df_attendance, 'Voting Member')
    inattendance_nonvotingmembers = attendance_count(df_attendance, 'Non-Voting Member')
    inattendance_nonmembers = attendance_count(df_attendance, 'Non-Member')
    inattendance_staff = attendance_count(df_attendance, 'Staff Member')
    notattending = currentvotingmembership - inattendance_votingmembers
    quorum = roster.meets_quorum(inattendance_votingmembers, currentvotingmembership)
    text = ''
    st.write(f'There are currently {inattendance_total} total participants.')
    if quorum:
        st.success(f'Quorum has been achieved!  \n \
                   ({inattendance_votingmembers} of {currentvotingmembership} voting members are in attendance)')
    else:
        st.warning(f'Quorum has not been met.  \n \
                   (only {inattendance_votingmembers} of {currentvotingmembership} voting members are in attendance)')
