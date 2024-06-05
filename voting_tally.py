import streamlit as st
import pandas as pd
import workinggroups
import firestore
import roster


def nominations():
    st.subheader('Call for Nominations')
    st.write('\
        We have openings for the position of Working Group Chair \
        for two (2) of our committees, and are looking for nominations!\
        Each committee has a form below. Please use them to cast your nomination.\
        ')
    st.caption('Voting will take place at our next comittee meeting.')
    with st.expander('Nominate a candidate for P1628'):
        title = workinggroups.PARS_Title('P1628')
        scope = workinggroups.PARS_Scope('P1628')
        st.caption('Title: ' + title)
        st.caption('Scope: ' + scope)
        with st.form(key='Nomination form (P1628)', clear_on_submit=False):
            existing_vote = firestore.get_existing_nomination('P1628')
            #st.text_input(label='WG Chair Nominee Full Name', value=existing_vote, key='P1628_name')
            st.selectbox(
                label = 'WG Chair Nominee Full Name',
                options = roster.names(),
                index=None,
                placeholder= "Select nominee..." if existing_vote == '' else existing_vote,
                key='P1628_name')
            vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
            if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
                #if st.session_state.P1628_name == st.session_state['name']:
                #    st.error('You cannot nominate yourself!')
                if st.session_state.P1628_name == None:
                    st.warning('Please type a nominee...')
                else:
                    nomination_df = firestore.submit_nomination(st.session_state.P1628_name, 'P1628')
                    if existing_vote == '':
                        st.caption(f"Your nomination for '{st.session_state.P1628_name}' has been entered")
                    else:
                        st.caption(f"Your nomination has been revised, '{st.session_state.P1628_name}' has been entered")
                    show_nominations(nomination_df)

    with st.expander('Nominate a candidate for P3357'):
        title = workinggroups.PARS_Title('P3357')
        scope = workinggroups.PARS_Scope('P3357')
        st.caption('Title: ' + title)
        st.caption('Scope: ' + scope)
        with st.form(key='Nomination form (P3357)',clear_on_submit=False):
            existing_vote = firestore.get_existing_nomination('P3357')
            st.selectbox(
                label = 'WG Chair Nominee Full Name',
                options = roster.names(),
                index=None,
                placeholder= "Select nominee..." if existing_vote == '' else existing_vote,
                key='P3357_name')
            vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
            if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
                #if st.session_state.P3357_name == st.session_state['name']:
                #    st.error('You cannot nominate yourself!')
                if st.session_state.P3357_name == None:
                    st.warning('Please type a nominee...')
                else:
                    nomination_df = firestore.submit_nomination(st.session_state.P3357_name, 'P3357')
                    if existing_vote == '':
                        st.caption(f"Your nomination for '{st.session_state.P3357_name}' has been entered")
                    else:
                        st.caption(f"Your nomination has been revised, '{st.session_state.P3357_name}' has been entered")
                    show_nominations(nomination_df)
    with st.expander('Nominate a candidate for P3425'):
        title = workinggroups.PARS_Title('P3425')
        scope = workinggroups.PARS_Scope('P3425')
        st.caption('Title: ' + title)
        st.caption('Scope: ' + scope)
        with st.form(key='Nomination form (P3425)',clear_on_submit=False):
            existing_vote = firestore.get_existing_nomination('P3425')
            st.selectbox(
                label = 'WG Chair Nominee Full Name',
                options = roster.names(),
                index=None,
                placeholder= "Select nominee..." if existing_vote == '' else existing_vote,
                key='P3425_name')
            vote_label = 'Submit' if existing_vote == '' else 'Change Vote'
            if st.form_submit_button(label=vote_label,use_container_width=False,type='primary'):
                #if st.session_state.P3425_name == st.session_state['name']:
                #    st.error('You cannot nominate yourself!')
                if st.session_state.P3425_name == None:
                    st.warning('Please type a nominee...')
                else:
                    nomination_df = firestore.submit_nomination(st.session_state.P3425_name, 'P3425')
                    if existing_vote == '':
                        st.caption(f"Your nomination for '{st.session_state.P3425_name}' has been entered")
                    else:
                        st.caption(f"Your nomination has been revised, '{st.session_state.P3425_name}' has been entered")
                    show_nominations(nomination_df)


#@st.cache_data
def show_nominations(df):
    df = df.sort_values(by=['Current Nominees'], ascending=True)
    st.dataframe(data=df['Current Nominees'],
                 hide_index=True,
                 height=((min(len(df.index), 5) + 1) * 35 + 3),
                 use_container_width=True)
    st.warning('This form will be open until June 4th if you want to change your nomination.')


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
