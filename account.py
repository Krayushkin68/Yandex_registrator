import random
import secrets
import string

import names


class Account:
    def __init__(self, json=None):
        if json:
            self.name = json['name']
            self.lastname = json['lastname']
            self.login = json['login']
            self.password = json['password']
            self.answer = json['answer']
            self.token = json['TOKEN']
        else:
            self.name = names.get_first_name()
            self.lastname = names.get_last_name()
            self.login = self.create_login()
            self.password = self.create_password()
            self.answer = self.create_answer()
            self.token = False

    def __str__(self):
        return f'{self.login}@yandex.ru {self.password}'

    def to_json(self):
        return {"name": self.name,
                "lastname": self.lastname,
                "login": self.login,
                "password": self.password,
                "answer": self.answer,
                "TOKEN": self.token}


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
