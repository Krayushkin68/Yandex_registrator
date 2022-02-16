import names
import random
import secrets
import string


class Account:
    def __init__(self, json=None):
        if json:
            self.name = json['name']
            self.lastname = json['lastname']
            self.login = json['login']
            self.password = json['password']
            self.phone = json.get('phone')
            self.answer = json['answer']
            self.token = json['TOKEN']
        else:
            self.name = names.get_first_name()
            self.lastname = names.get_last_name()
            self.login = self.create_login()
            self.password = self.create_password()
            self.phone = None
            self.answer = self.create_answer()
            self.token = False

    def __str__(self):
        return f'{self.login}@yandex.ru {self.password}'

    def to_json(self):
        return {"name": self.name,
                "lastname": self.lastname,
                "login": self.login,
                "password": self.password,
                'phone': self.phone,
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

    def generate_phrase(self):
        first = ["Home made", "Customly created", "Fully interactive", "Testing project"]
        second = ["project", "program", "session", "live map", "user friendly agent", "randomly generated",
                  "highly perfomanced"]
        third = ["playing a game", "watching map", "talking", "registration", "advising"]
        return random.choice(first) + " " + random.choice(second) + " for " + random.choice(third)

    def generate_company(self):
        add = ['Company', 'Co', 'Project', 'Startup', 'Enc']
        return self.lastname + random.choice(add)
