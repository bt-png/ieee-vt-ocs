import streamlit as st
import smtplib
from email.mime.text import MIMEText
email_sender = st.secrets['Streamlit_email']
password = st.secrets['Streamlit_IEEE']

def passwordreset(email_receiver, new_password):
    body = "You'r new password is: " + new_password
    try:
        msg = MIMEText(body)
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = 'IEEE-VT-OCS New Temporary Password'

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, password)
        server.sendmail(email_sender, email_receiver, msg.as_string())
        server.quit
        st.sidebar.success('New password has been sent to your email, please login and then change.')
    except Exception as e:
        st.error(e)
    
def forgotusername(email_receiver, username):
    body = "You'r username is: " + username
    try:
        email_sender = st.secrets['Streamlit_email']
        msg = MIMEText(body)
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = 'IEEE-VT-OCS Forgotten Username'

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, st.secrets['Streamlit_IEEE'])
        server.sendmail(email_sender, email_receiver, msg.as_string())
        server.quit
        st.sidebar.success('Your username has been sent to your email, please use to login.')
    except Exception as e:
        st.error(e)