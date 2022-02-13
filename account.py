import random
import secrets
import string

import names


class Account:
    def __init__(self):
        self.name = names.get_first_name()
        self.lastname = names.get_last_name()
        self.login = self.create_login()
        self.password = self.create_password()
        self.answer = self.create_answer()

    def __str__(self):
        return f'{self.login}@yandex.ru {self.password}'

    def create_login(self):
        symbols = ['.', '-']
        login = self.name + random.choice(symbols) + self.lastname + random.choice(symbols) + \
                str(random.randint(0, 1000))
        return login

    def create_password(self):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(20))
        return password

    def create_answer(self):
        return names.get_full_name()
