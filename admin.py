import streamlit as st
import pandas as pd
import numpy as np
import roster
import firestore
import meetings
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
from datetime import datetime
from wgpages import runAdmin
from wgpages import wg_chairemails


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


def updateroster(df):
    st.subheader('Update Roster')
    _df = df.copy()
    _df['Status'] = [roster.member_status(name) for name in _df['Name']]
    user_cat_input = st.multiselect(
        f'Name',
        _df['Name'].unique(),
    )
    if len(user_cat_input) > 0:
        _df = _df[_df['Name'].isin(user_cat_input)]
    if len(_df.index) == 1:
        st.dataframe(_df, hide_index=True)


def addnewPerson(df):
    _df = df.copy()
    with st.expander(label='Add a New Member', expanded=False):
        with st.form(key='AddUser', clear_on_submit=True):
            col1, col2 = st.columns([1,1])
            FirstName = col1.text_input('First Name')
            LastName = col2.text_input('Last Name')
            Email = st.text_input('E-mail')
            Affiliation = st.text_input('Affiliation')
            Employer = st.text_input('Employer')
            Type = st.selectbox('Type', options=roster.employertype())      
            if st.form_submit_button('Submit'):
                Status = 'O'
                Name = FirstName + ' ' + LastName
                new_user = pd.DataFrame({
                    'Affiliation': [Affiliation],
                    'E-mail': [Email],
                    'Employer': [Employer],
                    'First Name': [FirstName],
                    'Last Name': [LastName],
                    'Name': [Name],
                    'Status': [Status],
                    'Type': [Type],
                    'meeting': [None]
                    })
                _df = pd.concat([_df, new_user], ignore_index=True)
                # st.dataframe(_df)
                if firestore.set_roster(_df):
                    st.success('Saved')
                    # roster.refresh_df.clear()
                    roster.refresh_df()


def showroster(df):
    st.subheader('Committee Roster')
    _df = df.copy()
    _df['Status'] = [roster.member_status(name) for name in _df['Name']]
    col1, col2 = st.columns([8,2])
    col2.write('Apply filters to the Committee Roster')
    to_filter_columns = ('Name', 'Affiliation', 'Type', 'Status', 'E-mail')#st.multiselect("Filter dataframe on", df.columns)
    for column in to_filter_columns:
        user_cat_input = col2.multiselect(
            f"Filter on {column}",
            _df[column].unique(),
            #default=list(df[column].unique())
        )
        if len(user_cat_input) > 0:
            _df = _df[_df[column].isin(user_cat_input)]
    Height = int(35.2 * (12 + 1))
    col1.dataframe(_df, height=Height, hide_index=True, column_order=['Name', 'Affiliation', 'Type', 'Status', 'E-mail'], )
    col1.caption(f'Displaying {len(_df.index)} total rows')
    col1, col2, col3 = st.columns([8, 8, 8])
    if col2.button(label='Refresh Roster List'):
        roster.refresh_df()
        st.rerun()
    st.write('Send email to committee')
    col1, col2, col3, col4 = st.columns([.04, .18, .18, .60])
    email_votingmembers = roster.contact_list_votingmember()
    email_nonvotingmembers =roster.contact_list_notvotingmember()
    email_activemembers =roster.contact_list_activemember()
    email_all =roster.contact_list_all()
    col2.link_button(label='Voting Members', url=f"mailto:?to=stephen-norton@ieee.org;jschlick@hntb.com;heather.riebeling@aecom.com;brett.tharp@stvinc.com;eric.parsons@southwire.com&bcc={email_votingmembers}&subject=IEEE VT/OCS Standards Committee: ")
    col3.link_button(label='Active Members', url=f"mailto:?to=stephen-norton@ieee.org;jschlick@hntb.com;heather.riebeling@aecom.com;brett.tharp@stvinc.com;eric.parsons@southwire.com&bcc={email_activemembers}&subject=IEEE VT/OCS Standards Committee: ")
    if col4.button('All Members'):
        #col3.link_button(label='Try Email', url=f"mailto:?to=stephen-norton@ieee.org;jschlick@hntb.com;heather.riebeling@aecom.com;brett.tharp@stvinc.com;eric.parsons@southwire.com&bcc={email_all}subject=IEEE VT/OCS Standards Committee: ")
        st.warning('There are too many addressess to create an email automatically. Copy the list below.')
        st.link_button(label='Blank Email', url=f"mailto:?to=stephen-norton@ieee.org;jschlick@hntb.com;heather.riebeling@aecom.com;brett.tharp@stvinc.com;eric.parsons@southwire.com&subject=IEEE VT/OCS Standards Committee: ")
        st.caption('Voting Members')
        Path = f'''{email_votingmembers}'''
        st.code(Path, language="python")
        st.caption('Other Members')
        Path = f'''{email_nonvotingmembers}'''
        st.code(Path, language="python")


def showfutureattendance():
    st.subheader('Next meeting Attendance')
    df_poll = firestore.future_attendee_list()
    df_poll['Attending'] = ['Yes' in x for x in df_poll['Attendance Poll']]
    inattendance_total = df_poll[(df_poll['Attending'] == True)]['Attending'].count()
    inperson_total = df_poll[(df_poll['Attendance Poll'] == 'Yes, in person')]['Attending'].count()
    st.write(f'There are currently {inattendance_total} total participants planning to attend, {inperson_total} of which are planning to attend in person.')
    
    # attendee_list = df_poll[df_poll['Attendance Poll'] == 'Yes, in person']['Name'].to_list()
    # attendee_list.sort()
    # txt = ''
    # for name in attendee_list:
    #     txt += name
    #     if len(attendee_list) == 2:
    #         if name == attendee_list[1]:
    #             txt += ' and '
    #     if len(attendee_list) > 2:
    #         if name == attendee_list[-2]:
    #             txt += ' and '
    #         elif name != attendee_list[-1]:
    #             txt += ', '
    # st.caption('List of planned in-person attendee\'s')
    # st.write(txt)
    
    currentvotingmembership = roster.totals_votingmembers()
    inattendance_votingmembers = df_poll[(df_poll['Attending'] == True) & (df_poll['Status'] == 'Voting Member')]['Attending'].count()
    quorum = roster.meets_quorum(inattendance_votingmembers, currentvotingmembership)
    
    col1, col2 = st.columns([4, 2])
    col1.caption('Expected Quorum')
    if quorum:
        col1.success(f'Quorum may be achieved, {roster.quorum_required(currentvotingmembership)} required.  \n \
                   ({inattendance_votingmembers} of {currentvotingmembership} voting members are planning to attend)')
    else:
        col1.warning(f'Quorum may not be met, {roster.quorum_required(currentvotingmembership)} required.  \n \
                   (only {inattendance_votingmembers} of {currentvotingmembership} voting members are planning to attend)')
    col1, col2 = st.columns([4, 2])
    col1.caption('Polling Results')
    col1.dataframe(df_poll, hide_index=True, column_order=['Name', 'Attendance Poll', 'Status'])
    main_list = np.setdiff1d(roster.member_names(),df_poll['Name'].to_list())
    with col2.form(key='ADMIN Future Attendance', clear_on_submit=True):
        st.write('Manual RSVP on behalf of attendee')
        st.caption("Only those not yet RSVP'd will show in this drop down")
        st.selectbox(
            label = 'Attendee Name',
            options = main_list,
            index=None,
            placeholder= "Select...",
            key='ADMINFutureAttendee')
        st.selectbox(
            label = 'Does the attendee plan on attending?',
            options = ['Yes, in person', 'Yes, virtually', 'No, not this time'],
            index=None,
            placeholder= "Select...",
            key='ADMINFutureAttendance')
        vote_label = 'Submit Attendance'
        if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
            if st.session_state.ADMINFutureAttendance == None:
                st.warning('Please make a selection')
            else:
                firestore.post_attendancepoll(st.session_state.ADMINFutureAttendee, st.session_state.ADMINFutureAttendance)
                st.rerun()


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


def showMeetingAttendanceActive(df_roster):
    if (datetime.date(datetime.today()) == meetings.next_meeting_date()) or testing:
        showattendance(df_roster)
        meetings.attendance_manual()
        # Show Save Attendance Link
        if st.session_state['username'] in ['btharp']:
            with st.expander(label='Record Meeting Attendance', expanded=False):
                col1, col2 = st.columns([1,1])
                meetingnumber = col1.number_input('Meeting Number')
                if col2.button('Save Attendance Record'):
                    roster.post_meeting_attendance(int(meetingnumber))
                roster.postUpdatedMemberStatus()
                if testing:
                    if st.button('Archive Roster'):
                        firestore.archive_roster()


def showMeetingAttendanceRecord():
    # if st.session_state['username'] in ['btharp']:
    with st.expander(label='View Prior Meeting Attendance', expanded=False):
        _df = meetings.schedule()
        _df.drop(_df[~_df['recorded']].index, inplace=True)
        meetingID = st.selectbox(
            label='Meeting Number',
            options=_df['number'].values, 
        )
        attendance = _df[_df['number']==meetingID]['attendance'].values[0]
        col1, col2 = st.columns([1,1])
        with col1:
            # st.write(attendance.get('Voting Members').get('In Attendance'))
            st.subheader('Voting Membership Attendance')
            _dfMembersInAttendance = pd.DataFrame(
                data=attendance.get('Voting Members').get('In Attendance').items(),
                columns=['Surname Ordered', 'In Attendance'])
            _dfMembersInAttendance['In Attendance'] = ['Yes' if att else 'No' for att in _dfMembersInAttendance['In Attendance']]
            _dfMembersInAttendance['sort'] = [roster.searchname(name) for name in _dfMembersInAttendance['Surname Ordered']]
            _dfMembersInAttendance['Affiliations'] = [roster.user_affiliations(name) for name in _dfMembersInAttendance['Surname Ordered']]
            _dfMembersInAttendance.sort_values(by='sort', inplace=True)
            st.dataframe(
                data=_dfMembersInAttendance,
                column_order=['Surname Ordered', 'Affiliations', 'In Attendance'],
                hide_index=True)
        with col2:
            st.subheader('Additional Attendees')
            _dfOthersInAttendance = pd.DataFrame(
                data=attendance.get('Other Attendees'),
                columns=['Surname Ordered'])
            _dfOthersInAttendance['sort'] = [roster.searchname(name) for name in _dfOthersInAttendance['Surname Ordered']]
            _dfOthersInAttendance['Affiliations'] = [roster.user_affiliations(name) for name in _dfOthersInAttendance['Surname Ordered']]
            _dfOthersInAttendance.sort_values(by='sort', inplace=True)
            st.dataframe(
                data=_dfOthersInAttendance,
                column_order=['Surname Ordered', 'Affiliations'],
                hide_index=True)


def meetingAttendance(df_roster):
    st.markdown('---')
    st.subheader('Meeting Attendance')
    showMeetingAttendanceActive(df_roster)
    showMeetingAttendanceRecord()


def showWorkingGroupRoster(df_roster):
    st.markdown('---')
    col1, col2 = st.columns([1,1])
    col1.subheader('Working Groups')
    email_wgchairs = wg_chairemails()
    col2.link_button(label='Email WG Chairs', url=f"mailto:?to={email_wgchairs}&cc=stephen-norton@ieee.org;jschlick@hntb.com;heather.riebeling@aecom.com;brett.tharp@stvinc.com;eric.parsons@southwire.com&subject=IEEE VT/OCS Standards Committee: WG Chairs")
    with st.expander(label='View Working Group Rosters', expanded=False):
        runAdmin()


def syncloginroster():
    if st.session_state['username'] in ['btharp']:
        st.markdown('---')
        col1, col2 = st.columns([1,1])
        with col1:
            st.subheader('User Login Database Errors')
            _df = pd.DataFrame(firestore.openconfig()['credentials']['usernames'])
            _df = _df.filter(items=['name', 'email'], axis=0).transpose()
            _df['Member Status'] = [roster.member_status(fn) for fn in _df['name']]
            st.write('Users Not Registered')
            st.dataframe(_df[_df['Member Status'] == 'Not Registered'])    
            # fnlogin = st.selectbox(
            #     label='Revise Information for:',
            #     options=_df[_df['Member Status'] == 'Not Registered'].index,
            #     index=None,
            #     placeholder='Select..',
            #     key='updateloginname'
            # )
            # if st.session_state['updateloginname'] is not None:
            #     with st.form(key='updatelogin', clear_on_submit=True):
            #         st.write('Update Login')
            #         # changes = ['Affiliation', 'E-mail', 'Employer']
            #         name = st.text_input('Name', placeholder='')                   
            #         # email = st.text_input('E-mail', placeholder=roster.user_email(st.session_state['updaterostername']))
            #         # employer = st.text_input('Employer', placeholder=roster.user_employer(st.session_state['updaterostername']))
            #         if st.form_submit_button('Update'):
            #             pass
            #         #     updates = 0
            #         #     if len(affiliate) > 0:
            #         #         updates += 1
            #         #         firestore.set_roster_update(roster.searchname(fn), 'Affiliation', affiliate)
            #         #     if len(email) > 0:
            #         #         updates += 1
            #         #         firestore.set_roster_update(roster.searchname(fn), 'E-mail', email)
            #         #     if len(employer) > 0:
            #         #         updates += 1
            #         #         firestore.set_roster_update(roster.searchname(fn), 'Employer', employer)
            #         #     if updates > 0:
            #         #         roster.refresh_df()
        with col2:
            st.subheader('Update Roster Database')
            fnroster = st.selectbox(
                label='Revise Information for:',
                options=roster.df['Name'].to_list(),
                index=None,
                placeholder='Select..',
                key='updaterostername'
            )
            if st.session_state['updaterostername'] is not None:
                with st.form(key='updateroster', clear_on_submit=True):
                    st.write('Update Roster')
                    # changes = ['Affiliation', 'E-mail', 'Employer']
                    affiliate = st.text_input('Affiliation', placeholder=roster.user_affiliations(st.session_state['updaterostername']))
                    try:
                        idx = roster.employertype().index(roster.user_employertype(st.session_state['updaterostername']))
                    except Exception:
                        idx = None
                    companytype = st.selectbox(
                        'Employer Type',
                        options=roster.employertype(),
                        index=idx) 
                    #st.text_input('Employer Type', placeholder=roster.user_affiliations(st.session_state['updaterostername']))  
                    email = st.text_input('E-mail', placeholder=roster.user_email(st.session_state['updaterostername']))
                    employer = st.text_input('Employer', placeholder=roster.user_employer(st.session_state['updaterostername']))
                    if st.session_state['username'] in ['btharp']:
                        revisename = st.text_input('Database Saved Name!', placeholder=st.session_state['updaterostername'])
                    if st.form_submit_button('Update'):
                        updates = 0
                        if len(affiliate) > 0:
                            updates += 1
                            firestore.set_roster_update(roster.searchname(st.session_state['updaterostername']), 'Affiliation', affiliate)
                        if len(companytype) > 0:
                            if companytype != roster.user_employertype(st.session_state['updaterostername']):
                                updates += 1
                                firestore.set_roster_update(roster.searchname(st.session_state['updaterostername']), 'Type', companytype)
                        if len(email) > 0:
                            updates += 1
                            if email == " ":
                                firestore.set_roster_update(roster.searchname(st.session_state['updaterostername']), 'E-mail', np.nan)
                            else:
                                firestore.set_roster_update(roster.searchname(st.session_state['updaterostername']), 'E-mail', email)
                        if len(employer) > 0:
                            updates += 1
                            firestore.set_roster_update(roster.searchname(st.session_state['updaterostername']), 'Employer', employer)
                        if st.session_state['username'] in ['btharp']:
                            if len(revisename) > 0:
                                updates += 1
                                if st.session_state['updaterostername'] != revisename:
                                    firestore.changename(
                                        st.session_state['updaterostername'], roster.searchname(st.session_state['updaterostername']),
                                        revisename, roster.searchname(revisename)
                                        )
                        # if updates > 0:
                            # roster.refresh_df.clear()
                            # roster.refresh_df()


def run():
    st.header('Officers Administration Page')
    if (datetime.date(datetime.today()) <= meetings.next_meeting_date()) or testing:
       st.markdown('---')
       showfutureattendance()
    if False:
        st.markdown('---')
        shownominations()
    df_roster = roster.df
    showroster(df_roster)
    addnewPerson(df_roster)
    syncloginroster()
    meetingAttendance(df_roster)
    showWorkingGroupRoster(df_roster)
