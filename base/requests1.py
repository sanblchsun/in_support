import sqlite3
import logging

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_all_current_tel_chat(self):
        with self.connection:
            rows = self.cursor.execute("select virt_tel from virt_telefon").fetchall()
            result = []
            for row in rows:
                result.append(row[0])
            return result

    def add_new_chat(self, my_user_id, state, virt_tel, second_user_id=None):
        """Добавляем новую запись"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `virt_telefon` ('my_user_id', 'second_user_id', 'state', 'virt_tel') VALUES(?,?,?,?)",
                                       (my_user_id, second_user_id, state, virt_tel))

    def update_row(self, second_user_id: int, virt_tel: str):
        with self.connection:
            self.cursor.execute("update virt_telefon set second_user_id == ? where virt_tel == ?", (second_user_id, virt_tel))
            self.cursor.execute("update virt_telefon set state == ? where virt_tel == ?", ("in_chat", virt_tel))

    def get_virt_telefons_in_await_chat(self):
        with self.connection:
            rows = self.cursor.execute("SELECT virt_tel FROM virt_telefon WHERE state == ?", ('wait_chat',)).fetchall()
            result = []
            for row in rows:
                result.append(row[0])
            return result

    def chat_exists(self, virt_tel):
        """Проверяем, есть ли уже чат в базе"""
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `virt_telefon` WHERE virt_tel == ?", (virt_tel,)).fetchone()
            return bool(len(result))

    def get_my_user_id_from_base(self, virt_tel):
        with self.connection:
            res = self.cursor.execute('select my_user_id from virt_telefon where virt_tel == ?', (virt_tel,)).fetchone()
            result = res[0]
            return result

    def chat_delete(self, user_id):
        with self.connection:
            self.cursor.execute("delete from virt_telefon where my_user_id == ?", (user_id,))
            self.cursor.execute("delete from virt_telefon where second_user_id == ?", (user_id,))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


if __name__ == '__main__':
    sql_object = SQLighter('../db.db')
    # sql_object.chat_delete(1484233689)
    # sql_object.update_data(1111111111, '9950')
    rows1 = sql_object.get_virt_telefons_in_await_chat()
    print(rows1)

    sql_object.close()
