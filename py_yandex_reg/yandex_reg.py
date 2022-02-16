import json
import os
import random

from py_yandex_reg import logger
from py_yandex_reg import selenium_functions
from py_yandex_reg.account import Account
from py_yandex_reg.proxies import parse_proxy

DEFAULT_DRIVER_PATH = os.path.join(os.getcwd(), r'drivers\chromedriver.exe')


class YandexRegistrator:
    _driver_path = str()
    _rucaptcha_token = str()
    _smshub_token = str()
    _proxies = []
    _accounts = []

    def __init__(self, rucaptcha_token, smshub_token, driver_path=DEFAULT_DRIVER_PATH, savepath='accounts.json'):
        self._rucaptcha_token = rucaptcha_token
        self._smshub_token = smshub_token
        self._accounts_file = savepath
        self.set_driver_path(driver_path)

    def set_driver_path(self, path):
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if os.path.exists(path):
            self._driver_path = path
        else:
            raise Exception(f'Driver on path: "{path}" not found.\nPlease specify it with .set_driver_path() method.')

    def set_proxies(self, proxies):
        if isinstance(proxies, str):
            proxies = [proxies]
        for proxy in proxies:
            pproxy = parse_proxy(proxy)
            if pproxy:
                self._proxies.append(pproxy)

    def set_rucaptcha_token(self, token):
        self._rucaptcha_token = token

    def set_smshub_token(self, token):
        self._smshub_token = token

    def set_savepath(self, path):
        if os.path.exists(path):
            self._accounts_file = path
        else:
            logger.error(f'File "{path}" not found')
            return False

    def _prepare_proxy(self, use_proxy):
        if not use_proxy:
            return None

        if not self._proxies:
            logger.warning('Proxy list is empty. Will start without proxy. Use .set_proxies() method.')
            return None
        return random.choice(self._proxies)

    def register_mail(self, hidden=False, use_proxy=False):
        proxy = self._prepare_proxy(use_proxy)
        driver_created = False
        try:
            driver = selenium_functions.create_driver(self._driver_path, hidden, proxy)
            driver_created = True
            account = selenium_functions.register_mail(driver, self._smshub_token)
            driver.quit()
        except Exception as e:
            logger.error(f'Exception {e}')
            if driver_created:
                driver.quit()
            return False

        self._accounts.append(account)
        self._add_account_to_file(account)
        return account

    def register_api(self, account, hidden=False, use_proxy=False):
        proxy = self._prepare_proxy(use_proxy)
        driver_created = False
        try:
            driver = selenium_functions.create_driver(self._driver_path, hidden, proxy)
            driver_created = True
            need_auth = selenium_functions.is_authorize_needed(driver)
            if need_auth:
                selenium_functions.pass_authorize_form(driver, account)
            key = selenium_functions.register_api(driver, account, self._rucaptcha_token)
            driver.quit()
        except Exception as e:
            logger.error(f'Exception {e}')
            if driver_created:
                driver.quit()
            return False

        account.token = key
        self._update_account_in_file(account)
        return key

    def generate_api(self, hidden=False, use_proxy=False):
        proxy = self._prepare_proxy(use_proxy)
        driver_created = False
        try:
            driver = selenium_functions.create_driver(self._driver_path, hidden, proxy)
            driver_created = True
            account = selenium_functions.register_mail(driver, self._smshub_token)
            self._add_account_to_file(account)
            need_auth = selenium_functions.is_authorize_needed(driver)
            if need_auth:
                selenium_functions.pass_authorize_form(driver, account)
            key = selenium_functions.register_api(driver, account, self._rucaptcha_token)
            driver.quit()
        except Exception as e:
            logger.error(f'Exception {e}')
            if driver_created:
                driver.quit()
            return False

        account.token = key
        self._accounts.append(account)
        self._update_account_in_file(account)
        return account

    def generate_apis(self, count, hidden=False, use_proxy=False):
        counter = 0
        try_counter = 0
        new_accounts = []
        while counter < count:
            try_counter += 1
            logger.info(f'Try № {try_counter} - START')
            account = self.generate_api(hidden, use_proxy)
            if account:
                new_accounts.append(account)
                counter += 1
                logger.info(f'Try № {try_counter} - DONE')
            else:
                logger.info(f'Try № {try_counter} - FAIL')
        return new_accounts

    def get_api_tokens(self):
        tokens = [acc.token for acc in self._accounts if acc.token]
        return tokens

    def get_accounts(self):
        return self._accounts

    def _add_account_to_file(self, account):
        try:
            data = json.load(open(self._accounts_file, 'r'))
            data.append(account.to_json())
            json.dump(data, open(self._accounts_file, 'w'))
        except Exception:
            json.dump([account.to_json()], open(self._accounts_file, 'w'), indent=4)

    def _update_account_in_file(self, account):
        try:
            data = json.load(open(self._accounts_file, 'r'))
            for i in range(len(data)):
                if data[i]['login'] == account.login and data[i]['password'] == account.password:
                    data[i] = account.to_json()
                    break
            else:
                data.append(account.to_json())
            json.dump(data, open(self._accounts_file, 'w'), indent=4)
        except Exception:
            return False

    def load_accounts(self):
        if not self._accounts_file:
            logger.error('Accounts file is not set. Use .set_save_path() method')
            return False

        try:
            data = json.load(open(self._accounts_file, 'r'))
            for el in data:
                self._accounts.append(Account(el))
            logger.info(f'Inserted {len(data)} accounts')
            return True
        except Exception as e:
            logger.error(f'Exception {e.__str__()}')
            return False

    def save_tokens(self, path):
        tokens = [acc.token for acc in self._accounts if acc.token]
        if not os.path.exists(path):
            logger.error(f'File "{path}" not found')
            return False
        json.dump({"TOKENS": tokens}, open(path, 'w'))
