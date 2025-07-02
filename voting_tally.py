import streamlit as st
import pandas as pd
import workinggroups
import firestore
import roster
from datetime import date


def attendingnextmeeting():
    st.subheader('Do you plan to attend our next meeting?')
    # st.write('\
    #     Firstly, we want to thank Toronto Transit Commission for hosting our next committee meeting on September 9th-10th!\
    #     ')
    st.write("\
        We have been approved to use on of APTA's rooms for our next committee meeting on July 2nd!\
        ")
    st.write('\
        We are asking you to let us know if and how you plan to attend, so we can be prepared for accomodating \
        the group.\
        ')
    st.write('\
        We are also still looking for room and meal sponsors, and meeting presenters. If you are interested in either, please [Contact the Officers](mailto:jschlick@hntb.com;heather.riebeling@aecom.com;brett.tharp@stvinc.com;eric.parsons@southwire.com).\
        ')
    st.caption('Please indicate if you plan to attend, and if so, if it will be in person or virtual.')
    with st.form(key='Future Attendance', clear_on_submit=False):
        existing_poll = firestore.get_existing_attendancepoll(st.session_state['name'])
        #st.text_input(label='WG Chair Nominee Full Name', value=existing_vote, key='P1628_name')
        st.selectbox(
            label = 'Do you plan on attending?',
            options = ['Yes, in person', 'Yes, virtually', 'No, not this time'],
            index=None,
            placeholder= "Select..." if existing_poll == '' else existing_poll,
            key='FutureAttendance')
        vote_label = 'Submit' if existing_poll == '' else 'Change Planned Attendance'
        if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
            if st.session_state.FutureAttendance == None:
                st.warning('Please make a selection')
            else:
                firestore.post_attendancepoll(st.session_state['name'], st.session_state.FutureAttendance)
                st.rerun()
    if existing_poll == 'Yes, in person':
        with st.container():
            st.write('Thank you for your attendance!')
            # st.subheader('Hotel booking information')
            # deldays = date(2024, 8, 20) - date.today()
            # if deldays.days > 0:
            #     st.caption('The booking link is setup for the full duration for both OCS/TPSS meetings. Please update the dates if you intend only to be there for one of the meetings, the rate should remain.')
            #     st.markdown(f"""
            #     Booking Link: [Hilton Group Code CDT92B](https://www.hilton.com/en/book/reservation/deeplink/?ctyhocn=YTOCSDT&groupCode=CDT92B&arrivaldate=2024-09-08&departuredate=2024-09-13&cid=OM,WW,HILTONLINK,EN,DirectLink&fromId=HILTONLINKDIRECT)
                
            #     The attendees can call 1-800-445-8667 or the hotel at 416-977-5000 and mention the group code CDT92B to make a booking as well.
            #     The cut-off date for the weblink is August 20th, 2024, so we have less than {deldays.days} days to book!
            #     """)
            # else:
            #     st.warning('The booking deadline has passed')
            #     st.caption('The booking link is setup for the full duration for both OCS/TPSS meetings. Please update the dates if you intend only to be there for one of the meetings, the rate should remain.')
            #     st.markdown(f"""
            #     Booking Link: [Hilton Group Code CDT92B](https://www.hilton.com/en/book/reservation/deeplink/?ctyhocn=YTOCSDT&groupCode=CDT92B&arrivaldate=2024-09-08&departuredate=2024-09-13&cid=OM,WW,HILTONLINK,EN,DirectLink&fromId=HILTONLINKDIRECT)
                
            #     The attendees can call 1-800-445-8667 or the hotel at 416-977-5000 and mention the group code CDT92B to make a booking as well.
            #     The cut-off date for the weblink has passed. It was August 20th, 2024! You may still try to coordinate through the hotel.
            #     """)
    elif existing_poll == 'Yes, virtually':
        st.write('Thank you for your attendance!')
    elif existing_poll == 'No, not this time':
        st.write('Thank you for letting us know.')

def nominations():
    st.subheader('Call for Committee Chair')
    st.write('\
        We have an opening for the position of IEEE VTS OCS Committee Chair\
        , and are looking for nominations!\
        You may self-nominate or nominate someone else to be considered as Chair of the Committee.\
        All nominees will be provided to the VTS Board of Governers for their selection.')
    st.caption('Nominations will be open for the next 2 weeks.')
    with st.expander('Nomination Form: Chair of Committee'):
        with st.form(key='Nomination form Chair of Committee', clear_on_submit=False):
            st.selectbox(
                label = 'Nominee Full Name',
                options = roster.member_names(),
                index=None,
                placeholder= "Select nominee...",
                key='Chair2025_name')
            st.text_area('Qualification Statement', height=450, key='Chair2025_qual', placeholder='Provide a paragraph of qualifications, working group contributions, and committee involvements for consideration by the VTS BoG.')
            vote_label = 'Submit'
            if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
                if st.session_state.Chair2025_name == None:
                    st.warning('Please type a nominee...')
                elif len(st.session_state.Chair2025_qual) < 20:
                    st.warning('Please provide a qualification statement')
                else:
                    nomination_success = firestore.submit_chair_nomination(st.session_state.Chair2025_name, st.session_state.Chair2025_qual)
                    if nomination_success:
                        st.caption(f"Your nomination for '{st.session_state.Chair2025_name}' has been entered")

    # st.subheader('Call for Nominations')
    # st.write('\
    #     We have an opening for the position of Working Group Chair \
    #     for three (3) of our committees, and are looking for nominations!\
    #     Each committee has a form below. Please use them to cast your nomination.\
    #     ')
    # st.caption('Voting will take place at our next comittee meeting.')
    # with st.expander('Nominate a candidate for P1628'):
    #     title = workinggroups.PARS_Title('P1628')
    #     scope = workinggroups.PARS_Scope('P1628')
    #     st.caption('Title: ' + title)
    #     st.caption('Scope: ' + scope)
    #     with st.form(key='Nomination form (P1628)', clear_on_submit=False):
    #         existing_vote = firestore.get_existing_nomination('P1628')
    #         #st.text_input(label='WG Chair Nominee Full Name', value=existing_vote, key='P1628_name')
    #         st.selectbox(
    #             label = 'WG Chair Nominee Full Name',
    #             options = roster.member_names(),
    #             index=None,
    #             placeholder= "Select nominee..." if existing_vote == '' else existing_vote,
    #             key='P1628_name')
    #         vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
    #         if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
    #             #if st.session_state.P1628_name == st.session_state['name']:
    #             #    st.error('You cannot nominate yourself!')
    #             if st.session_state.P1628_name == None:
    #                 st.warning('Please type a nominee...')
    #             else:
    #                 nomination_df = firestore.submit_nomination(st.session_state.P1628_name, 'P1628')
    #                 if existing_vote == '':
    #                     st.caption(f"Your nomination for '{st.session_state.P1628_name}' has been entered")
    #                 else:
    #                     st.caption(f"Your nomination has been revised, '{st.session_state.P1628_name}' has been entered")
    #                 show_nominations(nomination_df)

    # with st.expander('Nominate a candidate for P3357'):
    #     title = workinggroups.PARS_Title('P3357')
    #     scope = workinggroups.PARS_Scope('P3357')
    #     st.caption('Title: ' + title)
    #     st.caption('Scope: ' + scope)
    #     with st.form(key='Nomination form (P3357)',clear_on_submit=False):
    #         existing_vote = firestore.get_existing_nomination('P3357')
    #         st.selectbox(
    #             label = 'WG Chair Nominee Full Name',
    #             options = roster.member_names(),
    #             index=None,
    #             placeholder= "Select nominee..." if existing_vote == '' else existing_vote,
    #             key='P3357_name')
    #         vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
    #         if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
    #             #if st.session_state.P3357_name == st.session_state['name']:
    #             #    st.error('You cannot nominate yourself!')
    #             if st.session_state.P3357_name == None:
    #                 st.warning('Please type a nominee...')
    #             else:
    #                 nomination_df = firestore.submit_nomination(st.session_state.P3357_name, 'P3357')
    #                 if existing_vote == '':
    #                     st.caption(f"Your nomination for '{st.session_state.P3357_name}' has been entered")
    #                 else:
    #                     st.caption(f"Your nomination has been revised, '{st.session_state.P3357_name}' has been entered")
    #                 show_nominations(nomination_df)
    # with st.expander('Nominate a candidate for P3425'):
    #     title = workinggroups.PARS_Title('P3425')
    #     scope = workinggroups.PARS_Scope('P3425')
    #     st.caption('Title: ' + title)
    #     st.caption('Scope: ' + scope)
    #     with st.form(key='Nomination form (P3425)',clear_on_submit=False):
    #         existing_vote = firestore.get_existing_nomination('P3425')
    #         st.selectbox(
    #             label = 'WG Chair Nominee Full Name',
    #             options = roster.member_names(),
    #             index=None,
    #             placeholder= "Select nominee..." if existing_vote == '' else existing_vote,
    #             key='P3425_name')
    #         vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
    #         if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
    #             #if st.session_state.P3425_name == st.session_state['name']:
    #             #    st.error('You cannot nominate yourself!')
    #             if st.session_state.P3425_name == None:
    #                 st.warning('Please type a nominee...')
    #             else:
    #                 nomination_df = firestore.submit_nomination(st.session_state.P3425_name, 'P3425')
    #                 if existing_vote == '':
    #                     st.caption(f"Your nomination for '{st.session_state.P3425_name}' has been entered")
    #                 else:
    #                     st.caption(f"Your nomination has been revised, '{st.session_state.P3425_name}' has been entered")
    #                 show_nominations(nomination_df)


#@st.cache_data
def show_nominations(df):
    df = df.sort_values(by=['Current Nominees'], ascending=True)
    st.dataframe(data=df['Current Nominees'],
                 hide_index=True,
                 height=((min(len(df.index), 5) + 1) * 35 + 3),
                 use_container_width=True)
    st.warning('This form will be open until September 8th if you want to change your nomination.')


def vote(WG, names):
    with st.expander('Vote for ' + WG + ' chair!', expanded=True):
        title = workinggroups.PARS_Title(WG)
        scope = workinggroups.PARS_Scope(WG)
        st.caption('Title: ' + title)
        st.caption('Scope: ' + scope)
        existing_vote = firestore.get_existing_nomination('Vote_' + WG)
        if len(existing_vote)>0:
            st.success(f"Your nomination for '{existing_vote}' has been entered")
        else:
            with st.form(key='Vote form (' + WG + ')', clear_on_submit=False):
                st.selectbox(
                    label='WG Chair for ' + WG,
                    options=names,
                    index=None,
                    placeholder="Select your vote...", #if existing_vote == '' else existing_vote,
                    key=WG + 'Vote_name')
                vote_label = 'Submit' #if existing_vote == '' else 'Change Vote'
                if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
                    #if st.session_state.P1628_name == st.session_state['name']:
                    #    st.error('You cannot nominate yourself!')
                    #elif st.session_state.P1628_name == None:
                    #    st.warning('Please type a nominee...')
                    #else:
                    firestore.submit_nomination(st.session_state[WG + 'Vote_name'], 'Vote_' + WG)
                    st.rerun()
                    #if existing_vote == '':
                    #st.caption(f"Your nomination for '{st.session_state[WG + 'Vote_name']}' has been entered")
                    #else:
                    #    st.caption(f"Your nomination has been revised, '{st.session_state.P1628_name}' has been entered")
                    # show_nominations(nomination_df)
