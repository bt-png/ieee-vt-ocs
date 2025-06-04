import streamlit as st


def officerlist():
    # Username of Officers
    return ['btharp', 'schlick33', 'ucme4me', 'iccswusn', 'hriebeling', 'proder']


def run():
    st.caption(
                "In Memoriam - Steve Norton  \n"
                "interim Chairperson, Vice Chairperson - John Schlick - [jschlick@hntb.com](mailto:jschlick@hntb.com)  \n"
                "Secretary - Heather Riebeling - [heather.riebeling@aecom.com](mailto:heather.riebeling@aecom.com)  \n"
                "Recording Secretary - Brett Tharp - [brett.tharp@stvinc.com](mailto:brett.tharp@stvinc.com)  \n"
                "Media Chair - Eric Parsons - [eric.parsons@southwire.com](mailto:eric.parsons@southwire.com)  \n"
                "[Contact the Officers](mailto:jschlick@hntb.com;heather.riebeling@aecom.com;brett.tharp@stvinc.com;eric.parsons@southwire.com)"
    )
    st.page_link(page='https://vtsociety.org/committee/overhead-contact-systems-standards-committee', label='IEEE VT/OCS')
    st.page_link(page='https://ieee-sa.imeetcentral.com/vts-ocs-sc/home', label='IEEE SA Committee Workspace')
    
