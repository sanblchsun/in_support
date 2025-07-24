from datetime import datetime


def get_html(description=' ',
             priority=' ',
             comment_from_bot='----------',
             status_request=' ',
             number_request=' '):
    html = f"""
<i><b>Описание проблемы:</b></i>
<code>{description}</code>
<i><b>Приоритет заявки:</b></i>
<code>{priority}</code>
<i><b>Hомер заявки №:</b></i>
<code>{number_request}</code>
"""
 # 1c integrated
# <i><b>Статус заявки:</b></i>
# <code>{status_request}</code>
# <i><b>Комментарии от бота:</b></i>
# <code>{comment_from_bot}</code>
# 1c integrated
    return html

