from py_yandex_reg import YandexRegistrator

RUCAPTCHA_TOKEN = 'b5261412e3c479060c259da67a7fc895'
SMSHUB_TOKEN = '33391Ua3a055afde7b7da9dcb97391d732e8ce'

proxies = []

ya_reg = YandexRegistrator(rucaptcha_token=RUCAPTCHA_TOKEN, smshub_token=SMSHUB_TOKEN)
ya_reg.set_proxies('Selkrayuskhinml97:G6v8BcG@91.90.213.122:45785')
ya_reg.generate_apis(count=1, hidden=False, use_proxy=False)
print(ya_reg.get_api_tokens())

# TODO: scrolling in minimized view or resizing
# TODO: register api for non token accounts
