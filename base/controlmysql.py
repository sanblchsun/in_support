import logging
import os
import sys
from configparser import ConfigParser

from base.mysqlrequests import action


async def controlsql(e_mail,
                     firma,
                     full_name,
                     cont_telefon,
                     description,
                     message_id,
                     fils_list=[]):
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, 'mysql.ini')
    if os.path.exists(config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
    else:
        logging.info('Config mysql not found')
        sys.exit(1)
    host = cfg.get("connect", "host")
    port = int(cfg.get("connect", "port"))
    user = cfg.get("connect", "user")
    password = cfg.get("connect", "password")
    database = cfg.get("connect", "database")

    action(e_mail=e_mail,
           firma=firma,
           full_name=full_name,
           cont_telefon=cont_telefon,
           description=description,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
           message_id=message_id,
            files_list=fils_list)

