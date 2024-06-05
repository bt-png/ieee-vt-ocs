from math import ceil
import streamlit as st
import pandas as pd
import numpy as np
import firestore
import meetings
import webbrowser


roster_val = firestore.get_roster()
df = pd.DataFrame.from_dict(data=roster_val, orient='index')
df.sort_values(by='Last Name', ascending=True, inplace=True)
df.reset_index(drop=True, inplace=True)


#@st.cache_data
def names():
    return df['Name']


def lastname(name):
    first, *middle, last = name.split()
    return last


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


def user_email(FullName):
    return df['E-mail'].loc[df['Name'] == FullName].values[0]


def firstName(FullName):
    return df['First Name'].loc[df['Name'] == FullName].values[0]


def user_affiliations(FullName):
    affs = df['Affiliation'].loc[df['Name'] == FullName]
    return list_to_string(affs)


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
    else:
        return False


def meeting_attendance_record(FullName):
    allmeetings = meetings.schedule()
    allmeetings.drop(allmeetings.tail(1).index, inplace=True)
    allmeetings['Attended'] = False
    #allmeetings['Attended'] = allmeetings['number']
    txt = df['meeting'].loc[df['Name'] == FullName].copy()
    txt.reset_index(drop=True, inplace=True)
    _df = pd.DataFrame.from_dict(txt[0], orient='index')
    _df['Meeting'] = _df.index
    _df.rename(columns={0: 'Attended'}, inplace=True)
    for meet in allmeetings['number'].tail(4):
        if str(meet) not in _df['Meeting'].to_list():
            _newrow = pd.DataFrame({'Meeting': [str(meet)], 'Attended': [False]})
            _df = pd.concat([_df, _newrow], ignore_index=True)
    _df.reset_index(drop=True, inplace=True)
    _df.sort_values(by='Meeting', ascending=True, inplace=True)
    _df = _df.set_index(['Meeting'])
    _df = _df.tail(4)
    _df = _df.transpose()
    return _df

def list_to_string(list):
    str = ''
    for val in list:
        try:
            if len(val)>0:
                str += val + '; '
        except Exception:
            return str
    return str[:-2]

def contact_list_votingmember():
    email = df[df['Status'] == 'V']['E-mail'].loc[df['E-mail'].notnull()].to_numpy()
    return list_to_string(email)


def contact_list_notvotingmember():
    email = df[df['Status'] != 'V']['E-mail'].loc[df['E-mail'].notnull()].to_numpy()
    return list_to_string(email)


def contact_list_activemember():
    email = df[df['Status'] != 'O']['E-mail'].loc[df['E-mail'].notnull()].to_numpy()
    return list_to_string(email)


def contact_list_all():
    #email = df['E-mail'].loc[df['E-mail'].notnull()].to_csv(sep=";",index=False, lineterminator='\r\n')
    email = df['E-mail'].loc[df['E-mail'].notnull()].to_numpy()
    return list_to_string(email)


def totals_votingmembers():
    return df.loc[df['Status'] == 'V', 'Status'].count()


def meets_quorum(in_attendance, total_voting):
    if total_voting < 50:
        return in_attendance >= ceil(0.5*total_voting)
    else:
        return in_attendance >= max(ceil(0.1*total_voting), 26)


def postMeetingAttendanceToRoster(attendeelist, meetingnumber: int):
    # firestore.get_roster.clear()
    roster_val = firestore.get_roster()
    df_dict = pd.DataFrame.from_dict(data=roster_val, orient='index')
    df_dict['Index'] = df_dict['Name']
    df_dict = df_dict.set_index('Index')
    dict_attendance = df_dict.transpose().to_dict()
    for user in attendeelist:
        #if 'meeting' in dict_attendance[user]:
        try:
            dict_attendance[user]['meeting'].update({str(meetingnumber): True})
        except Exception:
            dict_attendance[user].update({'meeting': {str(meetingnumber): True}})
    df_r = pd.DataFrame.from_dict(data=dict_attendance, orient='index')
    return firestore.set_roster(df_r)


def postMeetingAttendanceToSchedule(attendeelist, meetingnumber: int):
    df_meetings = firestore.get_schedule()
    df_meetings['Index'] = df_meetings['number']
    df_meetings = df_meetings.set_index('Index')
    dict_attendance = df_meetings.transpose().to_dict()

    df_member_attendance = pd.DataFrame({})
    df_member_attendance['Name'] = df[df['Status'] == 'V']['Name']
    df_member_attendance['In Attendance'] = [user in attendeelist for user in df_member_attendance['Name']]
    df_member_attendance = df_member_attendance.set_index('Name')

    df_nonmember_attendance = []
    for user in attendeelist:
        if member_status(user) != 'Voting Member':
            df_nonmember_attendance.append(user)

    #if 'attendance' in dict_attendance[meetingnumber]:
    try:
        dict_attendance[meetingnumber]['attendance'].update(
            {'Voting Members': df_member_attendance.to_dict(),
             'Other Attendees': df_nonmember_attendance}
             )
    except Exception:
        dict_attendance[meetingnumber].update(
            {'attendance': {
                'Voting Members': df_member_attendance.to_dict(),
                'Other Attendees': df_nonmember_attendance
                }
            }
            )
    df_r = pd.DataFrame.from_dict(data=dict_attendance, orient='index')
    return firestore.post_schedule(df_r)


def post_meeting_attendance(activeMeeting):
    # firestore.in_attendance.clear()
    df_attendance = firestore.in_attendance()
    listofmeetingattendees = df_attendance['Name'].tolist()
    listofmeetingattendees.sort(key=lastname)

    PostUsers = postMeetingAttendanceToRoster(listofmeetingattendees, activeMeeting)
    PostSchedule = postMeetingAttendanceToSchedule(listofmeetingattendees, activeMeeting)

    if PostUsers and PostSchedule:
        if firestore.clear_in_attendance():
            st.success('Attendance Recorded Sucessfully')
        else:
            st.warning('User data posted, however attendance did not clear.')
    elif PostUsers and not PostSchedule:
        st.warning('User data posted to users, but not schedule.')
    elif PostSchedule and not PostUsers:
        st.warning('User data posted to schedule, but not users.')
    else:
        st.warning('No data was posted.')
    firestore.in_attendance.clear()
