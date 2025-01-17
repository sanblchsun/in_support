import asyncio
import sys
import time
from brom import *
from configparser import ConfigParser


@staticmethod
def connect1c():
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "settings.ini")

    # get the config
    if os.path.exists(config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
    else:
        print("Config not found! Exiting!")
        sys.exit(1)

    url_to_base = cfg.get("connect", "urlToBase")
    login = cfg.get("connect", "login")
    passwd = cfg.get("connect", "passwd")

    try:
        klient = БромКлиент(
            f"{url_to_base}", f"{login}", f"{passwd}"
        )
    except Exception as e:
        print(e)
        exit(1)
    return klient


async def get_where_number(num, count=500):
    klient = connect1c()

    textRequest = klient.СоздатьЗапрос(f"""
            ВЫБРАТЬ ПЕРВЫЕ {count}
                Инцидент.Дата КАК Дата,
                Инцидент.Состояние.Наименование КАК СостояниеНаименование,
                Инцидент.Описание КАК Описание,
                Инцидент.Номер КАК Номер
            ИЗ
                Документ.Инцидент КАК Инцидент
            
            ГДЕ Инцидент.Номер = "{num}"
        """)

    res = textRequest.Выполнить()

    for item in res:
        print(f"""
Дата: 
    {item.Дата}
Номер: 
    {item.Номер}
Состояние: 
    {item.СостояниеНаименование}
Описание: 
    {item.Описание}""")
    print("==========================================================================")


async def get_count(count=500):
    klient = connect1c()

    textRequest = klient.СоздатьЗапрос(f"""
            ВЫБРАТЬ ПЕРВЫЕ {count}
                Инцидент.Дата КАК Дата,
                Инцидент.Состояние.Наименование КАК СостояниеНаименование,
                Инцидент.Описание КАК Описание,
                Инцидент.Номер КАК Номер
            ИЗ
                Документ.Инцидент КАК Инцидент
            
            УПОРЯДОЧИТЬ ПО
                Дата УБЫВ
        """)

    res = textRequest.Выполнить()

    for item in res:
        print(f"""
Дата: 

    {item.Дата}
Номер: 
    {item.Номер}
Состояние: 
    {item.СостояниеНаименование}
Описание: 
    {item.Описание}""")
        print("==========================================================================")


async def set_brom(description):
    klient = connect1c()

    docObject = klient.Документы.Инцидент.СоздатьДокумент()

    # Заполняем реквизиты
    docObject.Дата = datetime.today()
    docObject.ТемаОбращения = "Новая заявка"
    docObject.Клиент = klient.Справочники.Клиенты.НайтиПоНаименованию("РИБП")
    docObject.Описание = description

    # докОбъект.КонтактноеЛицо   = клиент.Справочники.Пользователи.НайтиПоНаименованию("Александрова Алена")
    # докОбъект.Приоритет        = клиент.Справочники.Приоритеты.НайтиПоНаименованию("Низкий")
    # докОбъект.Состояние        = клиент.Справочники.СостоянияИнцидентов.НайтиПоНаименованию("00. Новая заявка")
    # докОбъект.Ответственный    = клиент.Справочники.Сотрудники.НайтиПоНаименованию("Макосов Александр Александрович")
    # докОбъект.Услуга           = клиент.Справочники.Услуги.НайтиПоНаименованию("01. Рабочие места пользователей")
    # докОбъект.КомпонентаУслуги = клиент.Справочники.СоставУслуг.НайтиПоНаименованию("01.01 Установка и настройка ЭЦП")
    # докОбъект.Тип              = клиент.Справочники.ИТ_ТипыИнцидентов.НайтиПоНаименованию("Запрос на обслуживание")

    # Записываем состояние объекта в режиме проведения
    docObject.Записать()
    # Получаем ссылку на созданный документ
    docLink = docObject.Ссылка
    print(docLink.Номер)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(get_count(2))
    end = time.time()
    print("The time of execution of above program is :",
              (end - start) * 10 ** 3, "ms")
