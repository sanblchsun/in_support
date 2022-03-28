
import os
import smtplib
import sys
from configparser import ConfigParser
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


def send_email(subject, body_text, to_emails, cc_emails="", bcc_emails=""):
    """
    Send an email
    """

    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "email.ini")

    if os.path.exists(config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
    else:
        print("Config not found! Exiting!")
        sys.exit(1)

    host = cfg.get("smtp", "server")
    from_addr = cfg.get("smtp", "from_addr")

    # create the message
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    if body_text:
        msg.attach(MIMEText(body_text))

    msg["To"] = ', '.join(to_emails)
    # msg["cc"] = ', '.join(cc_emails)

    FROM = "logovopost@yandex.ru"
    password = "Utplj8061log"
    # emails = to_emails + cc_emails + bcc_emails
    emails = to_emails
    server = smtplib.SMTP(host)
    server.ehlo()
    server.starttls()
    server.login(FROM, password)
    server.sendmail(from_addr, emails, msg.as_string())
    server.quit()


if __name__ == "__main__":
    emails = ["logovopost@yandex.ru"]
    cc_emails = ["test@moskom-proekt.ru"]
    bcc_emails = ["makosov.a@ininsys.ru"]
    subject = "Test email from Python"
    body_text = "Python rules them all!"
    send_email(subject, body_text, emails)
