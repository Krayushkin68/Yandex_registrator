from py_yandex_reg import YandexRegistrator

RUCAPTCHA_TOKEN = 'b5261412e3c479060c259da67a7fc895'
SMSHUB_TOKEN = '33391Ua3a055afde7b7da9dcb97391d732e8ce'

proxies = ['Selkrayuskhinml97:G6v8BcG@91.90.213.122:45785']

ya_reg = YandexRegistrator(rucaptcha_token=RUCAPTCHA_TOKEN, smshub_token=SMSHUB_TOKEN, savepath='accounts.json')
ya_reg.set_proxies(proxies)

# Used to register new mail and get an API key. Accounts will be automatically saved to "savepath".
ya_reg.generate_apis(count=1, hidden=True, use_proxy=True)

# Used to get an API key for accounts that do not have it. Accounts will be automatically saved to "savepath".
ya_reg.register_nontoken_accounts(hidden=True, use_proxy=True)

# Returns list of API keys in json format
print(ya_reg.get_api_tokens())

# Returns list of account in json format
print(ya_reg.get_accounts())
