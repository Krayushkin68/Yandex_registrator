import os
import random
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from account import Account
from captcha import solve


def create_driver(proxy=None):
    options = webdriver.ChromeOptions()
    chrome_driver = os.getcwd() + r'\drivers\chromedriver.exe'

    capabilities = None
    if proxy:
        prox = Proxy()
        prox.proxy_type = ProxyType.MANUAL
        prox.http_proxy = proxy

        capabilities = webdriver.DesiredCapabilities.CHROME
        prox.add_to_capabilities(capabilities)

    driver = uc.Chrome(options=options, executable_path=chrome_driver, use_subprocess=True,
                       desired_capabilities=capabilities)
    driver.set_window_size(1024, 768)
    return driver


def register_mail(driver):
    url = r'https://mail.yandex.ru/'
    driver.get(url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="index-page-container"]/div/div[2]/div/div/div[4]/a[1]').click()
    time.sleep(random.random() + random.randint(0, 1))
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

    nophone_btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/'
                                                'div[3]/div/div[2]/div/div[1]/span')
    nophone_btn.click()
    time.sleep(random.random() + random.randint(0, 1))

    driver.execute_script("window.scrollTo(0, 300)")
    time.sleep(1)

    select = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/'
                                           'div/div[1]/div[1]/div[1]/span/select')
    time.sleep(random.random() + random.randint(0, 1))
    select = Select(select)
    select.select_by_index(1)
    time.sleep(random.random() + random.randint(0, 1))

    ans = driver.find_element(By.XPATH, '//*[@id="hint_answer"]')
    ans.send_keys(account.answer)
    time.sleep(random.random() + random.randint(0, 1))

    captcha = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/'
                                            'div[3]/div/div[2]/div[2]/div/div[1]/img')
    captcha_img = captcha.get_attribute('src')
    captcha_res = solve(captcha_img)
    if not captcha_res:
        driver.quit()

    captcha_input = driver.find_element(By.XPATH, '//*[@id="captcha"]')
    captcha_input.send_keys(captcha_res)
    time.sleep(random.random() + random.randint(0, 1))

    register_btn = driver.find_element(By.XPATH,
                                       '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[4]/span/button')
    register_btn.click()
    time.sleep(3)

    return account


def add_account_to_file(account, filename):
    with open(filename, 'a') as f:
        f.write(f'{account.login}@yandex.ru;{account.password}\n')


def register_api(driver, account):
    driver.get(r'https://developer.tech.yandex.ru/services/')

    try:
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
        time.sleep(7)

        try:
            enter3_btn = driver.find_element(By.XPATH,
                                             '//*[@id="root"]/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/form/div[3]/button')
            enter3_btn.click()
            time.sleep(5)
        except:
            pass
    except:
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
    cmp_name_input.send_keys(f'{account.name} project')
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
    phone_input.send_keys('+79' + ''.join([str(random.randint(0, 9)) for _ in range(9)]))
    time.sleep(random.random() + random.randint(0, 1))

    url_input = input_elements[4]
    url_input.send_keys(f'https://github.com/{account.name}')
    time.sleep(random.random() + random.randint(0, 1))

    driver.execute_script("window.scrollTo(0, 500)")
    time.sleep(2)

    descr_input = input_elements[5]
    descr_input.send_keys('Test api for static map')
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
    time.sleep(3)


if __name__ == '__main__':
    driver = create_driver()
    account = register_mail(driver)
    add_account_to_file(account, 'accounts.txt')
    # print(account)
    # account = Account()
    # account.name = 'Margaret'
    # account.lastname = 'Deaton'
    # account.login = 'Margaret-Deaton.233'
    # account.password = 'tCM00S2Wzt48M2ZI0zhL'

    register_api(driver, account)

    time.sleep(100)

    driver.quit()
