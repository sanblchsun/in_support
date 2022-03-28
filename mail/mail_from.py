
import yagmail


def send_email(subject, body_text, html, imag, to_emails, bb_c):
    # yag = yagmail.SMTP("2sunblch@gmail.com", "Utplj8061goo")
    yag = yagmail.SMTP(user='logovopost@yandex.ru',
                       password='Utplj8061log',
                       host='smtp.yandex.ru',
                       port='465')
    yag.send(to=to_emails, subject=subject,
             contents=body_text, attachments=imag)

    print("Email sent successfully")


if __name__ == "__main__":
    emails = ["logovopost@yandex.ru"]
    bb_c = "makosov.a@ininsys.ru"
    subject = "Test email from Python"
    body_text = [
        "Hello Mike! Here is a picture I took last week:",
        {'photo.jpg': 'PictureForMike'}
    ]
    imag = ['./1.txt']
    html = '<a href="hhtps://pypi.python.org/pypi/sky">Click me!</a>'
    send_email(subject, body_text, html, imag, emails, bb_c)
