import datetime
import shutil

import pymysql


def convertToBinary(file_name):
    with open(file_name, 'rb') as file:
        binary_file = file.read()
        return binary_file


def convertToFile(binarydata, file_name):
    with open(file_name, 'wb') as file:
        file.write(binarydata)


def action(e_mail,
           firma,
           full_name,
           cont_telefon,
           description,
           host,
           port,
           user,
           password,
           database,
           files_list):
    try:
        con = pymysql.connect(host=host,
                              port=port,
                              user=user,
                              password=password,
                              database=database,
                              cursorclass=pymysql.cursors.DictCursor)
        try:
            with con.cursor() as cursor:
                select_sql = "SELECT id FROM users WHERE id_telegram='44908032948'"
                # select_sql = "SELECT * FROM requests"
                cursor.execute(select_sql)
                rows = cursor.fetchall()
                if len(rows) == 0:
                    sql_users = "INSERT INTO users (id_telegram) VALUES (%s)"
                    cursor.execute(sql_users, '44908032948')
                    select_sql = "SELECT id FROM users WHERE id_telegram='44908032948'"
                    cursor.execute(select_sql)
                    rows = cursor.fetchall()

                sql_requests = "INSERT INTO requests (user_id, full_name, firma, e_mail, telefon, description, date)" \
                               " VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_requests, (rows[0]['id'],
                                              full_name,
                                              firma,
                                              e_mail,
                                              cont_telefon,
                                              description,
                                              datetime.datetime.now()))
                select_sql1 = "SELECT MAX(id) FROM requests"
                cursor.execute(select_sql1)
                rows1 = cursor.fetchall()
                sql_attach = "INSERT INTO attach (id_requests, file) VALUES (%s, %s)"
                if len(files_list) != 0:
                    for file in files_list:
                        convert_file = convertToBinary(file)
                        cursor.execute(sql_attach, (rows1[0]['MAX(id)'], convert_file))
                con.commit()
        finally:
            con.close()
    except Exception as e:
        print(f'Ошибка запроса sql: {e}')
    finally:
        if len(files_list) != 0:
            str1 = str(files_list[0])
            path = str1[:str1.find('/', str1.find('/')+1)]
            shutil.rmtree(path, ignore_errors=False, onerror=None)
        pass

