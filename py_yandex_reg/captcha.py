from twocaptcha import TwoCaptcha


def solve(img_url, token):
    solver = TwoCaptcha(apiKey=token, server='rucaptcha.com')
    try:
        result = solver.normal(img_url)
        return result.get('code')
    except Exception as e:
        print(e)
        return False
