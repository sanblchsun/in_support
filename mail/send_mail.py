import asyncio
import logging
import mimetypes
import os               # Функции для работы с операционной системой, не зависящие от используемой операционной системы
import smtplib          # Импортируем библиотеку по работе с SMTP
import sys
from configparser import ConfigParser
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from mail.html import get_html
import wget
from base.controlmysql import controlsql


#----------------------------------------------------------------------
async def send_email_with_attachment(e_mail,
                                     firma,
                                     full_name,
                                     cont_telefon,
                                     description,
                                     priority,
                                     message_id,
                                     http_to_attach=None
                                     ):
    """
    Send an email with an attachment
    """

    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "email.ini")
    header = 'Content-Disposition', 'attachment; filename="%s"' % http_to_attach

    # get the config
    if os.path.exists(config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
    else:
        print("Config not found! Exiting!")
        sys.exit(1)

    # extract server and from_addr from config
    host = cfg.get("smtp", "server")
    FROM = cfg.get("smtp", "from")
    password = cfg.get("smtp", "passwd")
    to_addrs = cfg.get("smtp", "to_addrs")

    # create the message
    msg = MIMEMultipart()
    msg["From"] = FROM
    msg["To"] = e_mail
    msg['Reply-To'] = e_mail
    msg["Subject"] = "Новая заявка"
    msg["Date"] = formatdate(localtime=True)

    # msg["To"] = ', '.join(e_mail)
    # msg["cc"] = ', '.join(cc_emails)

    html = get_html(e_mail, firma, full_name, cont_telefon, description, priority)

    if html:
        msg.attach(MIMEText(html, "html"))

    files_list = []
    if http_to_attach is not None:
        for key_iter in http_to_attach.keys():
            path = f'documents/{http_to_attach[key_iter][0]}/{http_to_attach[key_iter][1]}'
            try:
                os.makedirs(path)
            except OSError:
                logging.info(f"Создать директорию %s не удалось: {path}")
            pahh_file = wget.download(key_iter,
                                      f'documents/{http_to_attach[key_iter][0]}/'
                                      f'{http_to_attach[key_iter][1]}/'
                                      f'{http_to_attach[key_iter][2]}')
            files_list.append(pahh_file)
        process_attachement(msg, files_list)

    server = smtplib.SMTP(host)
    server.starttls()
    server.login(FROM, password)
    server.sendmail(FROM, to_addrs, msg.as_string())
    server.quit()

    await controlsql(e_mail=e_mail,
                     firma=firma,
                     full_name=full_name,
                     cont_telefon=cont_telefon,
                     description=description,
                     priority=priority,
                     message_id=message_id,
                     fils_list=files_list)


    #==========================================================================================================================

def process_attachement(msg, files):                        # Функция по обработке списка, добавляемых к сообщению файлов
    for f in files:
        if os.path.isfile(f):                               # Если файл существует
            attach_file(msg,f)                              # Добавляем файл к сообщению
        elif os.path.exists(f):                             # Если путь не файл и существует, значит - папка
            dir = os.listdir(f)                             # Получаем список файлов в папке
            for file in dir:                                # Перебираем все файлы и...
                attach_file(msg,f+"/"+file)                 # ...добавляем каждый файл к сообщению

def attach_file(msg, filepath):                             # Функция по добавлению конкретного файла к сообщению
    filename = os.path.basename(filepath)                   # Получаем только имя файла
    ctype, encoding = mimetypes.guess_type(filepath)        # Определяем тип файла на основе его расширения
    if ctype is None or encoding is not None:               # Если тип файла не определяется
        ctype = 'application/octet-stream'                  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)                 # Получаем тип и подтип
    # if maintype == 'text':                                  # Если текстовый файл
    #     with open(filepath) as fp:                          # Открываем файл для чтения
    #         file = MIMEText(fp.read(), _subtype=subtype)    # Используем тип MIMEText
    #         fp.close()                                      # После использования файл обязательно нужно закрыть
    # elif maintype == 'image':                               # Если изображение
    #     with open(filepath, 'rb') as fp:
    #         file = MIMEImage(fp.read(), _subtype=subtype)
    #         fp.close()
    # elif maintype == 'audio':                               # Если аудио
    #     with open(filepath, 'rb') as fp:
    #         file = MIMEAudio(fp.read(), _subtype=subtype)
    #         fp.close()
    # else:                                                   # Неизвестный тип файла
    #     with open(filepath, 'rb') as fp:
    #         file = MIMEBase(maintype, subtype)              # Используем общий MIME-тип
    #         file.set_payload(fp.read())                     # Добавляем содержимое общего типа (полезную нагрузку)
    #         fp.close()
    #         encoders.encode_base64(file)                    # Содержимое должно кодироваться как Base64

    with open(filepath, 'rb') as fp:
        file = MIMEBase(maintype, subtype)              # Используем общий MIME-тип
        file.set_payload(fp.read())                     # Добавляем содержимое общего типа (полезную нагрузку)
        fp.close()
        encoders.encode_base64(file)                    # Содержимое должно кодироваться как Base64

    file.add_header('Content-Disposition', 'attachment', filename=filename) # Добавляем заголовки
    msg.attach(file)                                        # Присоединяем файл к сообщению


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_email_with_attachment(e_mail='dffdvfd@fd.ru',
                               firma="фирма",
                               full_name='Иван',
                               cont_telefon='49834889',
                               description='Ура!')
    )
    loop.close()
