import random
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from py_yandex_reg import logger
from py_yandex_reg import sms_activator
from py_yandex_reg.account import Account
from py_yandex_reg.captcha import solve
from py_yandex_reg.proxies import prepare_plugin


def create_driver(driver_path, hidden=False, proxy=None):
    base_driver = 'undetected'

    options = uc.ChromeOptions()
    # options.add_argument('--start-maximized')
    options.headless = hidden

    if proxy:
        if len(proxy) == 4:
            options.headless = False
            pluginfile = prepare_plugin(driver_path, proxy)
            options.add_extension(pluginfile)
            base_driver = 'standart'
        elif len(proxy) == 2:
            options.add_argument(f'--proxy-server={proxy[0]}:{proxy[1]}')

    if base_driver == 'undetected':
        driver = uc.Chrome(options=options, executable_path=driver_path, use_subprocess=True)
    else:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        if hidden:
            driver.minimize_window()
    time.sleep(2)
    return driver


def wait_and_click(driver, xpath, wait_time=5, sleep_time=2):
    try:
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        ActionChains(driver).move_to_element(driver.find_element(By.XPATH, xpath)).perform()
        try:
            WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        except Exception:
            driver.find_element(By.XPATH, xpath).click()
        time.sleep(sleep_time)
        return True
    except Exception:
        return False


def locate_and_input(driver, xpath, message, sleep_time=0.5):
    try:
        el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        ActionChains(driver).move_to_element(el).perform()
        el.send_keys(message)
        time.sleep(random.random() + random.randint(0, 1) + sleep_time)
        return True
    except Exception:
        return False


def get_text(driver, xpath):
    try:
        text_el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        ActionChains(driver).move_to_element(text_el).perform()
        return text_el.text
    except Exception:
        return False


def load_page(driver, url):
    try:
        driver.get(url)
        time.sleep(1)
        return True
    except Exception:
        return False


def register_mail(driver, smshub_token):
    logger.info('MAIL - Start account registration')

    url = r'https://mail.yandex.ru/'
    if not load_page(driver, url):
        raise Exception(f'Error loading page {url}')

    create_btn_xpath = '//*[@id="index-page-container"]/div/div[2]/div/div/div[4]/a[1]'
    if not wait_and_click(driver, create_btn_xpath):
        raise Exception('Error clicking "Create account"')

    account = Account()

    name_input_xpath = '//*[@id="firstname"]'
    if not locate_and_input(driver, name_input_xpath, account.name):
        raise Exception('Error input account name')

    lastname_input_xpath = '//*[@id="lastname"]'
    if not locate_and_input(driver, lastname_input_xpath, account.lastname):
        raise Exception('Error input account lastname')

    login_input_xpath = '//*[@id="login"]'
    if not locate_and_input(driver, login_input_xpath, account.login):
        raise Exception('Error input account login')

    pass_input_xpath = '//*[@id="password"]'
    if not locate_and_input(driver, pass_input_xpath, account.password):
        raise Exception('Error input account password')

    pass2_input_xpath = '//*[@id="password_confirm"]'
    if not locate_and_input(driver, pass2_input_xpath, account.password):
        raise Exception('Error input account password confirmation')

    phone = sms_activator.get_number(smshub_token)
    if phone:
        idx, phone = phone
        account.phone = phone
        logger.info('MAIL - Phone received')
    else:
        raise Exception('Getting SMS error')

    phone_input_xpath = '//*[@id="phone"]'
    if not locate_and_input(driver, phone_input_xpath, phone[1:]):
        sms_activator.set_status(sms_activator.TOKEN, idx, 'cancel')
        raise Exception('Error input phone number')

    send_btn_xpath = '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[2]/button'
    if not wait_and_click(driver, send_btn_xpath):
        sms_activator.set_status(sms_activator.TOKEN, idx, 'cancel')
        raise Exception('Error clicking "Confirm number"')

    send_text_xpath = '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[1]/span'
    send_text = get_text(driver, send_text_xpath)

    if not send_text:
        sms_activator.set_status(sms_activator.TOKEN, idx, 'cancel')
        raise Exception('Error getting text from "Send code" element')
    elif send_text != 'Минутку, код подтверждения отправлен на указанный номер':
        logger.info('MAIL - Waiting for code input field to appear')
        toggle_sms_xpath = '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/div[2]/div[1]/' \
                           'div/div/div[2]/div[3]/span'
        if not wait_and_click(driver, toggle_sms_xpath, wait_time=35):
            sms_activator.set_status(sms_activator.TOKEN, idx, 'cancel')
            raise Exception('Error clicking "Send SMS"')
        logger.info('MAIL - Input field appears')

    sms_activator.set_status(sms_activator.TOKEN, idx, 'send')
    logger.info('MAIL - SMS sent, waiting for code')
    code = sms_activator.get_code(sms_activator.TOKEN, idx)
    if not code:
        sms_activator.set_status(sms_activator.TOKEN, idx, 'cancel')
        raise Exception('Getting SMS error')
    sms_activator.set_status(sms_activator.TOKEN, idx, 'done')
    logger.info('MAIL - Code received')

    code_input_xpath = '//*[@id="phoneCode"]'
    if not locate_and_input(driver, code_input_xpath, code, 4):
        raise Exception('Error input received code')

    register_btn_xpath = '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[4]/span/button'
    if not wait_and_click(driver, register_btn_xpath):
        raise Exception('Error clicking "Register account"')

    logger.info('MAIL - Account registered successfully')

    return account


def is_authorize_needed(driver):
    url = r'https://developer.tech.yandex.ru/services/'
    if not load_page(driver, url):
        raise Exception(f'Error loading page {url}')

    login_input_xpath = '//*[@id="passp-field-login"]'
    try:
        driver.find_element(By.XPATH, login_input_xpath)
        return True
    except Exception:
        return False


def pass_authorize_form(driver, account):
    logger.info('DEV - Start authorization')

    login_input_xpath = '//*[@id="passp-field-login"]'
    if not locate_and_input(driver, login_input_xpath, f'{account.login}@yandex.ru'):
        raise Exception('Error input login')

    signin_btn_xpath = '//*[@id="passp:sign-in"]'
    if not wait_and_click(driver, signin_btn_xpath):
        raise Exception('Error clicking "Sign In"')

    pass_input_xpath = '//*[@id="passp-field-passwd"]'
    if not locate_and_input(driver, pass_input_xpath, account.password):
        raise Exception('Error input password')

    signin2_btn_xpath = '//*[@id="passp:sign-in"]'
    if not wait_and_click(driver, signin2_btn_xpath, sleep_time=4):
        raise Exception('Error clicking "Sign In 2"')

    skip_btn_xpath = '//*[@id="root"]/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/form/div[3]/button'
    if not wait_and_click(driver, skip_btn_xpath, sleep_time=4):
        pass

    logger.info('DEV - Authorized successfully')


def fill_iframe(driver, account, rucaptcha_token):
    logger.info('DEV - Start filling the form')

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

    descr_input = input_elements[5]
    ActionChains(driver).move_to_element(descr_input).perform()
    descr_input.send_keys(account.generate_phrase())
    time.sleep(random.random() + random.randint(0, 1))

    check = driver.find_elements(By.CLASS_NAME, 'checkbox__control')[2]
    ActionChains(driver).move_to_element(check).perform()
    check.click()
    time.sleep(random.random() + random.randint(0, 1))

    captcha_xpath = '/html/body/div/form/div[1]/div[2]/fieldset/div[14]/div/table/tbody/tr[2]/td[2]/div[1]/img'
    captcha = driver.find_element(By.XPATH, captcha_xpath)
    ActionChains(driver).move_to_element(captcha).perform()
    captcha_img = captcha.get_attribute('src')
    logger.info('DEV - Waiting for CAPTCHA to be solved')
    captcha_res = solve(captcha_img, rucaptcha_token)
    if not captcha_res:
        raise Exception('CAPTCHA solving error')
    logger.info('DEV - CAPTCHA solved')

    captcha_input = input_elements[8]
    ActionChains(driver).move_to_element(captcha_input).perform()
    captcha_input.send_keys(captcha_res)
    time.sleep(random.random() + random.randint(0, 1))

    driver.switch_to.default_content()


def register_api(driver, account, rucaptcha_token):
    connect_btn_xpath = '//*[@id="root"]/div/div[2]/main/article/button'
    if not wait_and_click(driver, connect_btn_xpath):
        raise Exception('Error clicking "Connect API"')

    radio_btn_xpath = '//*[@id="uniq4"]'
    if not wait_and_click(driver, radio_btn_xpath):
        raise Exception('Error clicking radio button')

    continue_btn_xpath = '/html/body/div[3]/div/div/div/section/footer/button[1]'
    if not wait_and_click(driver, continue_btn_xpath):
        raise Exception('Error clicking "Continue"')

    try:
        fill_iframe(driver, account, rucaptcha_token)
    except Exception as e:
        print(e)
        raise Exception('Error filling iframe')

    confirm_btn_xpath = '/html/body/div[3]/div/div/div/section/footer/button[1]'
    if not wait_and_click(driver, confirm_btn_xpath, wait_time=20, sleep_time=5):
        raise Exception('Error clicking "Confirm"')

    logger.info('DEV - Waiting for YANDEX decision')

    btn_api_xpath = '/html/body/div[3]/div/div/div/section/footer/button[1]'
    if not wait_and_click(driver, btn_api_xpath, wait_time=35, sleep_time=5):
        logger.info('DEV - YANDEX decision DECLINE')
        raise Exception('Error connecting API')

    logger.info('DEV - YANDEX decision ACCEPT')

    key_xpath = '//*[@id="root"]/div/div[2]/main/article/section[2]/div/div/div/div[1]/div[2]'
    key = get_text(driver, key_xpath)
    if not key:
        raise Exception('Error getting API key')

    logger.info(f'DEV - Key received - "{key}"')

    return key
