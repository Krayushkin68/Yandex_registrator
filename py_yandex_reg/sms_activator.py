import time

import requests


def get_number(token):
    params = {
        'api_key': token,
        'action': 'getNumber',
        'service': 'ya',
    }
    url = 'http://smshub.org/stubs/handler_api.php'
    r = requests.get(url, params=params)
    if r.status_code == 200:
        msg = r.content.decode()
        idx = msg.split(':')[1]
        phone_number = msg.split(':')[2]
        return idx, phone_number
    return False


def set_status(token, idx, status):
    """
    Cтатусы
    8 - Отменить активацию
    1 - Сообщить, что SMS отправлена (необязательно)
    Для активации со статусом 1:
    8 - Отменить активацию
    Сразу после получения кода:
    3 - Запросить еще одну смс
    6 - Подтвердить SMS-код и завершить активацию
    Для активации со статусом 3:
    6 - Подтвердить SMS-код и завершить активацию
    """

    if status == 'send':
        status = 1
    elif status == 'cancel':
        status = 8
    elif status == 'done':
        status = 6

    params = {
        'api_key': token,
        'action': 'setStatus',
        'status': status,
        'id': idx,
    }
    url = 'http://smshub.org/stubs/handler_api.php'
    requests.get(url, params=params)


def get_code(token, idx):
    params = {
        'api_key': token,
        'action': 'getStatus',
        'id': idx,
    }
    url = 'http://smshub.org/stubs/handler_api.php'

    loop_time = 5
    max_retries = 20
    while max_retries:
        r3 = requests.get(url, params=params)
        if r3.status_code == 200:
            msg = r3.content.decode()
            if msg.startswith('STATUS_OK'):
                code = msg.split(':')[1]
                return code
        max_retries -= 1
        time.sleep(loop_time)
    set_status(token, idx, 'cancel')
    return False
