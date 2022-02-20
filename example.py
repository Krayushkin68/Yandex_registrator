import json

from py_yandex_reg import YandexRegistrator

config = json.load(open('config.json', 'r'))
RUCAPTCHA_TOKEN = config['RUCAPTCHA_TOKEN']
SMSHUB_TOKEN = config['SMSHUB_TOKEN']
proxies = config['proxies']

ya_reg = YandexRegistrator(rucaptcha_token=RUCAPTCHA_TOKEN, smshub_token=SMSHUB_TOKEN, savepath='accounts.json')

# Use proxies in str or list in these formats:
# With auth    - "username:password@host:port"
# Without auth - "host:port"
ya_reg.set_proxies(proxies)

# Used to register new mail and get an API key. Accounts will be automatically saved to "savepath".
ya_reg.generate_apis(count=1, hidden=True, use_proxy=False)

# Used to get an API keys for accounts from "savepath" that don't have it. Keys will be automatically saved to file.
# ya_reg.register_nontoken_accounts(hidden=False, use_proxy=False)

# Returns list of API keys in json format
print(ya_reg.get_api_tokens())

# Returns list of account in json format
print(ya_reg.get_accounts())
