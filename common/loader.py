# -- coding: utf-8--
import settings

APPS = settings.APPS

def load_url_handlers():
    handlers = list()
    for app in APPS:
        urls = __import__(app)
        for url in urls.url_handlers:
            handlers.append(url)
    return handlers

