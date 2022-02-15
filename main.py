import json
import logging
import os
import random
import sys
import time
import zipfile
from logging import StreamHandler, Formatter

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import sms_activator
from account import Account
from captcha import solve
from proxies import prepare_proxy, parse_proxy

logger = logging.getLogger(__name__)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s', datefmt='%d-%m-%y %H:%M:%S'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def create_driver(hidden=False, proxy=None):
    chrome_driver = os.getcwd() + r'\drivers\chromedriver.exe'
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.headless = hidden

    if proxy:
        proxy_res = parse_proxy(proxy)
        if len(proxy_res) == 4:
            options.headless = False
            pluginfile = 'drivers/proxy_auth_plugin.zip'
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                manifest_json, background_js = prepare_proxy(*proxy_res)
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            options.add_extension(pluginfile)
            driver = webdriver.Chrome(options=options, executable_path=chrome_driver)
            if hidden:
                driver.minimize_window()
        elif len(proxy_res) == 2:
            options.add_argument(f'--proxy-server={proxy_res[0]}:{proxy_res[1]}')
            driver = uc.Chrome(options=options, executable_path=chrome_driver, use_subprocess=True)
        else:
            logger.error(proxy_res)
    else:
        driver = uc.Chrome(options=options, executable_path=chrome_driver, use_subprocess=True)

    time.sleep(2)
    return driver


def register_mail(driver):
    url = r'https://mail.yandex.ru/'
    driver.get(url)
    time.sleep(1)

    btn = driver.find_element(By.XPATH, '//*[@id="index-page-container"]/div/div[2]/div/div/div[4]/a[1]')
    btn.click()
    time.sleep(2)

    account = Account()

    name_input = driver.find_element(By.XPATH, '//*[@id="firstname"]')
    name_input.send_keys(account.name)
    time.sleep(random.random() + random.randint(0, 1))

    lastname_input = driver.find_element(By.XPATH, '//*[@id="lastname"]')
    lastname_input.send_keys(account.lastname)
    time.sleep(random.random() + random.randint(0, 1))

    driver.execute_script("window.scrollTo(0, 100)")
    time.sleep(random.random() + random.randint(0, 1))

    login_input = driver.find_element(By.XPATH, '//*[@id="login"]')
    login_input.send_keys(account.login)
    time.sleep(random.random() + random.randint(0, 1))

    driver.execute_script("window.scrollTo(0, 100)")
    time.sleep(random.random() + random.randint(0, 1))

    pass_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    pass_input.send_keys(account.password)
    time.sleep(random.random() + random.randint(0, 1))

    pass2_input = driver.find_element(By.XPATH, '//*[@id="password_confirm"]')
    pass2_input.send_keys(account.password)
    time.sleep(random.random() + random.randint(0, 1))

    driver.execute_script("window.scrollTo(0, 200)")
    time.sleep(1)

    phone_input = driver.find_element(By.XPATH, '//*[@id="phone"]')
    phone = sms_activator.get_number(sms_activator.TOKEN)
    if phone:
        idx, phone = phone
        account.phone = phone
        phone_input.send_keys(phone[1:])
        logger.info('MAIL - Phone received')
        time.sleep(2)
    else:
        raise Exception('Getting SMS error')

    send_btn_xpath = '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[2]/button'
    send_btn = driver.find_element(By.XPATH, send_btn_xpath)
    send_btn.click()
    time.sleep(1)

    text_el_xpath = '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[1]/span'
    text_el = driver.find_element(By.XPATH, text_el_xpath)
    if text_el.text != 'Минутку, код подтверждения отправлен на указанный номер':
        logger.info('MAIL - Waiting for code input field to appear')
        toggle_sms_xpath = '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[2]/div[1]/' \
                           'div/div/div[2]/div[3]/span'
        WebDriverWait(driver, 35).until(EC.presence_of_element_located((By.XPATH, toggle_sms_xpath))).click()
        logger.info('MAIL - Input field appears')
    time.sleep(1)

    sms_activator.set_status(sms_activator.TOKEN, idx, 'send')
    logger.info('MAIL - SMS sent, waiting for code')
    code = sms_activator.get_code(sms_activator.TOKEN, idx)
    if not code:
        sms_activator.set_status(sms_activator.TOKEN, idx, 'cancel')
        raise Exception('Getting SMS error')
    sms_activator.set_status(sms_activator.TOKEN, idx, 'done')
    logger.info('MAIL - Code received')

    code_input = driver.find_element(By.XPATH, '//*[@id="phoneCode"]')
    code_input.send_keys(code)
    time.sleep(5)

    register_btn = driver.find_element(By.XPATH,
                                       '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[4]/span/button')
    register_btn.click()
    time.sleep(3)

    logger.info('MAIL - Account registered successfully')

    return account


def pass_authorize_form(driver, account):
    login_input = driver.find_element(By.XPATH, '//*[@id="passp-field-login"]')
    login_input.send_keys(f'{account.login}@yandex.ru')
    time.sleep(random.random() + random.randint(0, 1))

    enter_btn = driver.find_element(By.XPATH, '//*[@id="passp:sign-in"]')
    enter_btn.click()
    time.sleep(3)

    pass_input = driver.find_element(By.XPATH, '//*[@id="passp-field-passwd"]')
    pass_input.send_keys(account.password)
    time.sleep(random.random() + random.randint(0, 1))

    enter2_btn = driver.find_element(By.XPATH, '//*[@id="passp:sign-in"]')
    enter2_btn.click()
    time.sleep(5)

    try:
        skip_btn_xpath = '//*[@id="root"]/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/form/div[3]/button'
        enter3_btn = driver.find_element(By.XPATH, skip_btn_xpath)
        enter3_btn.click()
        time.sleep(5)
    except Exception:
        pass


def register_api(driver, account):
    driver.get(r'https://developer.tech.yandex.ru/services/')
    time.sleep(3)

    try:
        pass_authorize_form(driver, account)
    except Exception:
        pass

    logger.info('DEV - Authorized successfully')

    time.sleep(3)
    connect_btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/main/article/button')
    connect_btn.click()
    time.sleep(1)

    radio_btn = driver.find_element(By.XPATH, '//*[@id="uniq4"]')
    radio_btn.click()
    time.sleep(1)

    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div/div/section/footer/button[1]'))).click()
    time.sleep(2)

    iframe = driver.find_element(By.TAG_NAME, 'iframe')
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(iframe))
    input_elements = driver.find_elements(By.CLASS_NAME, 'input__control')

    cmp_name_input = input_elements[0]
    cmp_name_input.clear()
    cmp_name_input.send_keys(account.generate_company())
    time.sleep(random.random() + random.randint(0, 1))

    name_input = input_elements[1]
    name_input.clear()
    name_input.send_keys(f'{account.name} {account.lastname}')
    time.sleep(random.random() + random.randint(0, 1))

    login_input = input_elements[2]
    login_input.clear()
    login_input.send_keys(f'{account.login}@yandex.ru')
    time.sleep(random.random() + random.randint(0, 1))

    phone_input = input_elements[3]
    phone_input.send_keys(f'+{account.phone}')
    time.sleep(random.random() + random.randint(0, 1))

    url_input = input_elements[4]
    url_input.send_keys(f'https://github.com/{account.name}')
    time.sleep(random.random() + random.randint(0, 1))

    driver.execute_script("window.scrollTo(0, 500)")
    time.sleep(2)

    descr_input = input_elements[5]
    descr_input.send_keys(account.generate_phrase())
    time.sleep(random.random() + random.randint(0, 1))

    check = driver.find_elements(By.CLASS_NAME, 'checkbox__control')[2]
    check.click()
    time.sleep(random.random() + random.randint(0, 1))

    captcha_xpath = '/html/body/div/form/div[1]/div[2]/fieldset/div[14]/div/table/tbody/tr[2]/td[2]/div[1]/img'
    captcha = driver.find_element(By.XPATH, captcha_xpath)
    captcha_img = captcha.get_attribute('src')
    logger.info('DEV - Waiting for CAPTCHA to be solved')
    captcha_res = solve(captcha_img)
    if not captcha_res:
        raise Exception('CAPTCHA solving error')
    logger.info('DEV - CAPTCHA solved')

    captcha_input = input_elements[8]
    captcha_input.send_keys(captcha_res)
    time.sleep(random.random() + random.randint(0, 1))

    driver.switch_to.default_content()

    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div/div/section/footer/button[1]'))).click()
    time.sleep(3)

    logger.info('DEV - Waiting for YANDEX decision')
    btn_xpath = '/html/body/div[3]/div/div/div/section/footer/button[1]'
    WebDriverWait(driver, 35).until(EC.presence_of_element_located((By.XPATH, btn_xpath)))
    WebDriverWait(driver, 35).until(EC.element_to_be_clickable((By.XPATH, btn_xpath))).click()
    time.sleep(5)
    logger.info('DEV - YANDEX decision OK')

    key = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/main/article/section[2]/div/div/div/div[1]/div[2]')
    key = key.text

    logger.info(f'DEV - Key received - "{key}"')

    return key


def add_account_to_file(account, filename):
    try:
        data = json.load(open(filename, 'r'))
        data.append(account.to_json())
        json.dump(data, open(filename, 'w'))
    except Exception:
        json.dump([account.to_json()], open(filename, 'w'))


def get_api_keys_for_mails(filename, hidden=False, proxy=None):
    accounts = json.load(open(filename, 'r'))
    counter = 0
    for account in accounts:
        if account['TOKEN']:
            continue
        try:
            driver = create_driver(hidden=hidden, proxy=proxy)
            counter += 1
            logger.info(f'Try № {counter} - START')
            key = register_api(driver, Account(account))
            if key:
                account['TOKEN'] = key
                logger.info(f'Try № {counter} - DONE')
            driver.quit()
            time.sleep(2)
        except Exception as e:
            logger.info(f'Try № {counter} - FAIL')
            logger.exception(f'Exception "{e.__str__()}"', exc_info=False)
            driver.quit()
            time.sleep(2)
            continue
    json.dump(accounts, open(filename, 'w'))


def register_and_get_api(filename, hidden=False, proxy=None):
    counter = 0
    while True:
        counter += 1
        is_acc = False
        try:
            driver = create_driver(hidden=hidden, proxy=proxy)
            logger.info(f'Try № {counter} - START')
            account = register_mail(driver)
            is_acc = True
            key = register_api(driver, account)
            if key:
                account.token = key
                add_account_to_file(account, filename)
                logger.info(f'Try № {counter} - DONE')
            driver.quit()
            time.sleep(2)
        except Exception as e:
            logger.info(f'Try № {counter} - FAIL')
            logger.exception(f'Exception "{e.__str__()}"', exc_info=False)
            if is_acc:
                add_account_to_file(account, filename)
            driver.quit()
            time.sleep(2)


if __name__ == '__main__':
    # my_proxy = 'Selkrayuskhinml97:G6v8BcG@91.90.213.122:45785'
    my_proxy = None

    register_and_get_api('accounts.json', hidden=True, proxy=my_proxy)
    # get_api_keys_for_mails('accounts.json', hidden=False, proxy=my_proxy)
