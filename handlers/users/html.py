from datetime import datetime


def get_html(description=' ',
             priority=' '):
    html = f"""
<i><b>Описание проблемы:</b></i>
<code>{description}</code>
<i><b>Приоритет заявки:</b></i>
<code>{priority}</code>
"""
    return html

