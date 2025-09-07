import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def send_plain_email(sender_name, sender_email, sender_password, receiver_email, subject, body, smtp_server, smtp_port):
    
    message = MIMEText(body, "plain")
    message["From"] = formataddr((sender_name, sender_email))
    message["To"] = receiver_email
    message["Subject"] = subject

    try:
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    except Exception as e:
        raise