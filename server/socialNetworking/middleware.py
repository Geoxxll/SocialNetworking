from typing import Any
from django.urls import reverse
from django.http import HttpResponseRedirect

class TrailingSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, get_request):
        path = get_request.path_info
        if not path.endswith('/') and not path == '/':
            return HttpResponseRedirect(f'{path}/')
        else:
            return self.get_response(get_request)