from twocaptcha import TwoCaptcha


def solve(img_url):
    solver = TwoCaptcha(apiKey='b5261412e3c479060c259da67a7fc895', server='rucaptcha.com')
    try:
        result = solver.normal(img_url)
        return result.get('code')
    except Exception as e:
        print(e)
        return False

if __name__ == '__main__':
    url = r'https://ext.captcha.yandex.net/image?key=00Age07lyQVUy5IuLVccWqgP3HZgpAgc'
    res = solve(url)