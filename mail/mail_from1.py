# Импортируем библиотеку по работе с SMTP
import smtplib
# Функции для работы с операционной системой, не зависящие от используемой операционной системы
import os

# Добавляем необходимые подклассы - MIME-типы
# Импорт класса для обработки неизвестных MIME-типов, базирующихся на расширении файла
import mimetypes
# Импортируем энкодер
from email import encoders
from email.mime.base import MIMEBase                        # Общий тип
from email.mime.text import MIMEText                        # Текст/HTML
from email.mime.image import MIMEImage                      # Изображения
from email.mime.audio import MIMEAudio                      # Аудио
# Многокомпонентный объект
from email.mime.multipart import MIMEMultipart


def send_email(addr_to, msg_subj, msg_text, files):
    addr_from = "2sunblch@gmail.com"                         # Отправитель
    password = "Utplj8061goo"                                  # Пароль

    msg = MIMEMultipart()                                   # Создаем сообщение
    msg['From'] = addr_from                              # Адресат
    msg['To'] = addr_to                                # Получатель
    msg['Subject'] = msg_subj                               # Тема сообщения

    body = msg_text                                         # Текст сообщения
    # Добавляем в сообщение текст
    msg.attach(MIMEText(body, 'plain'))

    process_attachement(msg, files)

    #======== Этот блок настраивается для каждого почтового провайдера отдельно ===============================================
    server = smtplib.SMTP('smtp.gmail.com', 587)        # Создаем объект SMTP
    # Начинаем шифрованный обмен по TLS
    server.starttls()
    server.login(addr_from, password)                   # Получаем доступ
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()                                       # Выходим
    #==========================================================================================================================


# Функция по обработке списка, добавляемых к сообщению файлов
def process_attachement(msg, files):
    for f in files:
        if os.path.isfile(f):                               # Если файл существует
            # Добавляем файл к сообщению
            attach_file(msg, f)
        # Если путь не файл и существует, значит - папка
        elif os.path.exists(f):
            # Получаем список файлов в папке
            dir = os.listdir(f)
            for file in dir:                                # Перебираем все файлы и...
                # ...добавляем каждый файл к сообщению
                attach_file(msg, f + "/" + file)


# Функция по добавлению конкретного файла к сообщению
def attach_file(msg, filepath):
    # Получаем только имя файла
    filename = os.path.basename(filepath)
    # Определяем тип файла на основе его расширения
    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:               # Если тип файла не определяется
        # Будем использовать общий тип
        ctype = 'application/octet-stream'
    # Получаем тип и подтип
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':                                  # Если текстовый файл
        with open(filepath) as fp:                          # Открываем файл для чтения
            # Используем тип MIMEText
            file = MIMEText(fp.read(), _subtype=subtype)
            # После использования файл обязательно нужно закрыть
            fp.close()
    elif maintype == 'image':                               # Если изображение
        with open(filepath, 'rb') as fp:
            file = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
    elif maintype == 'audio':                               # Если аудио
        with open(filepath, 'rb') as fp:
            file = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
    else:                                                   # Неизвестный тип файла
        with open(filepath, 'rb') as fp:
            # Используем общий MIME-тип
            file = MIMEBase(maintype, subtype)
            # Добавляем содержимое общего типа (полезную нагрузку)
            file.set_payload(fp.read())
            fp.close()
            # Содержимое должно кодироваться как Base64
            encoders.encode_base64(file)
    file.add_header('Content-Disposition', 'attachment',
                    filename=filename)  # Добавляем заголовки
    # Присоединяем файл к сообщению
    msg.attach(file)


if __name__ == "__main__":
    # Использование функции send_email()
    addr_to = "logovopost@yandex.ru"                                # Получатель
    files = [                                     # Список файлов, если вложений нет, то files=[]

        "attach/"]                                       # Если нужно отправить все файлы из заданной папки, нужно указать её

    send_email(addr_to, "Тема сообщения", "Текст сообщения", files)
