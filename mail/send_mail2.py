import smtplib
import email.message


def send():

    server = smtplib.SMTP('smtp.gmail.com:587')

    email_content = """
    <html>
    </html>
     
    """

    msg = email.message.Message()
    msg['Subject'] = 'Tutsplus Newsletter'


    msg['From'] = 'botsendto@gmail.com'
    msg['Reply-To'] = '2sunblch@gmail.com'
    msg['To'] = 'makosov.a@ininsys.ru'
    password = "Gnezdoviegoo"
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_content)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    # Login Credentials for sending the mail
    s.login(msg['From'], password)

    s.sendmail(msg['From'], [msg['To']], msg.as_string())


if __name__ == "__main__":
    send()
