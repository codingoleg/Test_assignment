import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.utils import formataddr


def send_email(message) -> tuple:
    msg = MIMEText(message)
    msg['Subject'] = 'Mail Subject'
    msg['From'] = formataddr((os.environ['SMTP_NAME'], os.environ['SMTP_EMAIL']))

    try:
        with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ['SMTP_PORT']), timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(os.environ['SMTP_EMAIL'], os.environ['SMTP_PASSWORD'])
            server.sendmail(os.environ['SMTP_EMAIL'], os.environ['EMAIL'], msg.as_string())

        return True, None
    except (socket.gaierror, smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected, TimeoutError) as error:
        return False, str(error)

