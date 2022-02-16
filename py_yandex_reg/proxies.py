import os
import zipfile

from py_yandex_reg import logger


def prepare_proxy(proxy_host, proxy_port, proxy_user, proxy_pass):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_host, proxy_port, proxy_user, proxy_pass)
    return manifest_json, background_js


def prepare_plugin(driver_path, proxy):
    pluginfile = os.path.join(os.path.dirname(driver_path), 'proxy_auth_plugin.zip')
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        manifest_json, background_js = prepare_proxy(*proxy)
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return pluginfile


def parse_proxy(proxy):
    try:
        if '@' in proxy:
            creds, addr = proxy.strip().split('@')
            proxy_user, proxy_pass = creds.split(':')
            proxy_host, proxy_port = addr.split(':')
            return proxy_host, proxy_port, proxy_user, proxy_pass
        else:
            proxy_host, proxy_port = proxy.split(':')
            return proxy_host, proxy_port
    except Exception:
        logger.error(f'Error parsing proxy "{proxy}". Use format: "user:pass@host:port"')
        return False
