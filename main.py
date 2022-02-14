import json
import os
import random
import time
import zipfile

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import sms_activator
from account import Account
from captcha import solve
from proxies import prepare_proxy


def create_driver(hidden=False, proxy=None):
    chrome_driver = os.getcwd() + r'\drivers\chromedriver.exe'
    options = uc.ChromeOptions()
    options.headless = hidden

    if proxy:
        pluginfile = 'drivers/proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            manifest_json, background_js = prepare_proxy(proxy)
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)
        driver = webdriver.Chrome(options=options, executable_path=chrome_driver)
    else:
        driver = uc.Chrome(options=options, executable_path=chrome_driver, use_subprocess=True)

    # driver.set_window_size(1024, 768)
    driver.maximize_window()
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
        time.sleep(4)
    else:
        raise Exception('Getting SMS error')

    send_btn = driver.find_element(By.XPATH,
                                   '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[2]/button')
    send_btn.click()
    time.sleep(1)

    text_el = driver.find_element(By.XPATH,
                                  '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[1]/span')
    if text_el.text != 'Минутку, код подтверждения отправлен на указанный номер':
        WebDriverWait(driver, 35).until(EC.presence_of_element_located((By.XPATH,
                                                                        '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div[3]/span'))).click()

    # time.sleep(35)
    # sms_btn = driver.find_element(By.XPATH,
    #                               '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div[3]/span')
    # sms_btn.click()
    time.sleep(1)

    sms_activator.set_status(sms_activator.TOKEN, idx, 'send')
    code = sms_activator.get_code(sms_activator.TOKEN, idx)
    if not code:
        sms_activator.set_status(sms_activator.TOKEN, idx, 'cancel')
        raise Exception('Getting SMS error')
    sms_activator.set_status(sms_activator.TOKEN, idx, 'done')

    code_input = driver.find_element(By.XPATH, '//*[@id="phoneCode"]')
    code_input.send_keys(code)
    time.sleep(5)

    register_btn = driver.find_element(By.XPATH,
                                       '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[4]/span/button')
    register_btn.click()
    time.sleep(3)

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
        enter3_btn = driver.find_element(By.XPATH,
                                         '//*[@id="root"]/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/form/div[3]/button')
        enter3_btn.click()
        time.sleep(5)
    except:
        pass


def register_api(driver, account):
    driver.get(r'https://developer.tech.yandex.ru/services/')
    time.sleep(3)

    try:
        pass_authorize_form(driver, account)
    except Exception:
        pass

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

    captcha = driver.find_element(By.XPATH,
                                  '/html/body/div/form/div[1]/div[2]/fieldset/div[14]/div/table/tbody/tr[2]/td[2]/div[1]/img')
    captcha_img = captcha.get_attribute('src')
    captcha_res = solve(captcha_img)
    if not captcha_res:
        driver.quit()

    captcha_input = input_elements[8]
    captcha_input.send_keys(captcha_res)
    time.sleep(random.random() + random.randint(0, 1))

    driver.switch_to.default_content()

    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div/div/section/footer/button[1]'))).click()
    time.sleep(25)

    try:
        btn = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/section/footer/button[1]')
        btn.click()
        time.sleep(3)
    except Exception:
        return None

    key = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/main/article/section[2]/div/div/div/div[1]/div[2]')
    key = key.text
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
    for account in accounts:
        if account['TOKEN']:
            continue
        try:
            driver = create_driver(hidden=hidden, proxy=proxy)
            key = register_api(driver, Account(account))
            if key:
                print(key)
                account['TOKEN'] = key
            else:
                print('Getting API fails')
            driver.quit()
            time.sleep(2)
        except Exception as e:
            print('Getting API fails')
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
            account = register_mail(driver)
            is_acc = True
            print(f'Try № {counter}: account registered')
            key = register_api(driver, account)
            if key:
                print(f'Try № {counter}: key recieved - "{key}"\n')
                account.token = key
            else:
                print(f'Try № {counter}: FAIL\n')
            add_account_to_file(account, filename)
            driver.quit()
            time.sleep(2)
        except Exception:
            print(f'Try № {counter}: FAIL\n')
            if is_acc:
                add_account_to_file(account, filename)
            driver.quit()
            time.sleep(2)


if __name__ == '__main__':
    my_proxy = 'Selkrayuskhinml97:G6v8BcG@91.90.213.122:45785'
    # my_proxy = None

    # get_api_keys_for_mails('accounts.json', hidden=False, proxy=my_proxy)

    register_and_get_api('accounts.json', hidden=False, proxy=my_proxy)
