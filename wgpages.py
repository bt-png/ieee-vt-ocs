import streamlit as st
import pandas as pd
from datetime import date, time, datetime
from workinggroups import PARS, PARS_Title, PARS_Scope
from firestore import wg_get, wg_register, wg_unregister, wg_assign_chair, wg_unassign_chair, wg_push_schedule
from officers import officerlist
from roster import member_names, searchname, user_affiliations, contact_list


def list_to_string(list):
    str = ''
    for val in list:
        try:
            if len(val)>0:
                str += val + '; '
        except Exception:
            return str
    return str[:-2]


@st.cache_data
def get_wglist():
    return PARS()['Project Number'].to_list()


@st.cache_data
def get_df():
    dict = {}
    for wg in get_wglist():
        dict[wg] = wg_get(wg)
    return dict


def ischair(val, user):
    if df_wg[val] is None:
        return False
    if user in df_wg[val].get('WG Chair'):
        return True


def wgchair(val):
    if df_wg[val] is not None:
        return df_wg[val]['WG Chair']
    return ['Not Assigned']


def wgmeeting(val):
    if df_wg[val] is not None:
        if 'Next Meeting' in df_wg[val]:
            return df_wg[val]['Next Meeting']
    return 'Not Assigned'


def registered(val, user):
    if df_wg[val] is None:
        return False
    # if ischair(val, user):
    #     return True
    if user in df_wg[val].get('Volunteers'):
        return True


def generateCheckbox(val):
    # ADD FEATURE - 
    # if chair, default is checked
    if 'wg_page_'+val not in st.session_state:
        if ischair(val, st.session_state["name"]):
            st.session_state['wg_page_'+val] = True
    st.checkbox(label=val, key='wg_page_'+val)


def runSidebar():
    with st.sidebar:
        st.write('WG Pages')
        [generateCheckbox(val) for val in get_wglist()]


@st.fragment
def showscope(val):
    # if 'wg_scope_'+val not in st.session_state:
    #     st.session_state['wg_scope_'+val] = False
    # if st.session_state['wg_scope_'+val]:
    st.caption('Scope: ' + PARS_Scope(val))
    st.session_state['wg_scope_'+val] = False
    # else:
    #     if st.button(label='Show PAR Scope', key='wg_scope_btn_'+val):
    #         st.session_state['wg_scope_'+val] = True
    #         st.rerun()


def showtitle(val):
    st.subheader('Working Group ' + val)
    st.write('WG Chair: ' + list_to_string(wgchair(val)))
    st.write('Title: ' + PARS_Title(val))


# def showmeeting(val):
#     date_val = wgmeeting(val)
#     if type(date_val) is datetime:
#         st.write(date_val)
#     else:
#         st.write('Next meeting not yet scheduled.')


def register_user(val, user):
    if wg_register(user, val):
        get_df.clear()
        st.rerun()


def remove_user(val, user):
    if wg_unregister(user, val):
        get_df.clear()
        st.rerun()


def assignchair_user(val, user):
    if wg_assign_chair(user, val):
        get_df.clear()
        st.rerun()


def rescindchair_user(val, user):
    if wg_unassign_chair(user, val):
        get_df.clear()
        st.rerun()


# def push_wg_schedule(wg, date_time):
#     if wg_push_schedule(date_time, wg):
#         get_df.clear()
#         st.rerun()


# def update_wgschedule(wg):
#     showmeeting(wg)
#     st.write('Update Next WG Meeting')
#     st.caption('Reference')
    
#     col1, col2, col3 = st.columns([1,1,1])
#     date_val = col1.date_input(
#         'Next WG Date', value='default_value_today',
#         key='wg_scheduledate_'+wg, label_visibility='collapsed')
#     # time_val = col1.time_input(
#     #     'Next WG Time', value='now',
#     #     key='wg_scheduletime_'+wg, label_visibility='collapsed')
#     time_val = time(12,0,0)
#     datetime_val = datetime.combine(date_val, time_val)
#     st.write(datetime.now())
#     st.write(datetime_val)
#     if col3.button('Submit', key='wg_schedule_btn_'+wg):
#         # datetimeval = datetime.strptime(val.isoformat(), '%Y-%m-%d')
        
#         push_wg_schedule(wg, datetime_val)


def register(val):
    if st.button(label='Self-Register to Participate', key='wg_register_btn_'+val):
        register_user(val, st.session_state['name'])


def registersomeone(val, user):
    disabled = False
    if registered(val, user): disabled = True
    if st.button('Register User', disabled=disabled, key='wg_register_btn_admin_'+val):
        register_user(val, user)


def removesomeone(val, user):
    disabled = True
    if registered(val, user): disabled = False
    if st.button('Remove User', disabled=disabled, key='wg_unregister_btn_admin_'+val):
        remove_user(val, user)


def assignchair(val, user):
    if st.session_state['username'] == 'btharp':
        disabled = False
        if ischair(val, user):
            if st.button('Revoke WG Chair', disabled=disabled, key='wg_chair_btn_admin_r_'+val):
                rescindchair_user(val, user)
        else:
            if st.button('Assign WG Chair', disabled=disabled, key='wg_chair_btn_admin_'+val):
                assignchair_user(val, user)


def updatewgRoster(val):
    st.write(val)
    if (ischair(val, st.session_state["name"])) or (st.session_state['username'] in officerlist()):
        selectuser = st.selectbox(
                label='Update WG Roster:',
                options=member_names().to_list(),
                index=None,
                placeholder='Select..',
                key='wg_admin_user_' + val
            )
        if selectuser is not None:
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                registersomeone(val, selectuser)
            with col2:
                removesomeone(val, selectuser)
            if st.session_state['username'] in officerlist():
                with col3:
                    assignchair(val, selectuser)


def wgroster(val):
    if df_wg[val] is not None:
        _df = pd.DataFrame(
                data=df_wg[val]['Volunteers'],
                columns=['Volunteers'])
        _df['sort'] = [searchname(name) for name in _df['Volunteers']]
        _df['Affiliations'] = [user_affiliations(name) for name in _df['Volunteers']]
        # _df['E-mail'] = [user_email(name) for name in _df['Surname Ordered']]
        _df.sort_values(by='sort', inplace=True)
        return _df


def show_wgroster(val):
    st.write('Working Group Roster')
    # st.caption('Names orderd by Surname')
    df = wgroster(val)
    # col1, col2 = st.columns([6,4])
    st.dataframe(
        data=df,
        column_order=['Volunteers', 'Affiliations'],
        hide_index=True)
    if 'Volunteers' in df_wg[val]:
        email_list = contact_list(df_wg[val]['Volunteers'])
        if len(email_list) > 0:
            st.link_button(label='Email WG Members', url=f"mailto:?bcc={email_list}&subject=IEEE VT/OCS WG {val}: ")
        

def wgchair_view(val):
    show_wgroster(val)
    # show_wgschedule(wg)
    # update_wgschedule(wg)
    updatewgRoster(val)


def generateContent(val):
    if 'wg_page_' + val not in st.session_state:
        return
    if st.session_state['wg_page_'+val] == False:
        return
    showtitle(val)
    showscope(val)
    if ischair(val, st.session_state["name"]):
        st.subheader('WG Administration View')
        wgchair_view(val)
    elif registered(val, st.session_state["name"]):
        st.write("""
                 Thank you for volunteering to be a part of this working group. 
                 Your name and e-mail is made available to the working group chair 
                 for purposes of working on this Standard.
                 """)
        # showmeeting(val)
        col1, col2 = st.columns([7,3])
        email_list = contact_list(df_wg[val]['WG Chair'])
        if len(email_list) > 0:
            col1.link_button(label='Email WG Chair', url=f"mailto:?to={email_list}&subject=IEEE VT/OCS WG {val}: ")
        if col2.button(label='Rescind Registration', key='wg_btn_rescind_'+val):
            remove_user(val, st.session_state["name"])
    else:
        register(val)
    
    st.markdown('---')


def runMain():
    # st.write(df_wg)
    [generateContent(val) for val in get_wglist()]


def run():
    global df_wg
    df_wg = get_df()
    runSidebar()
    runMain()


def runAdmin():
    global df_wg
    df_wg = get_df()
    for wg in get_wglist():
        showtitle(wg)
        st.write('WG Chair: ' + list_to_string(wgchair(wg)))
        wgchair_view(wg)
