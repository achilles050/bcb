from rest_framework.authentication import SessionAuthentication
from django.utils.deprecation import MiddlewareMixin


class DisableCSRF(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

# class DisableCSRF(object):
#     def process_request(self, request):
#         setattr(request, '_dont_enforce_csrf_checks', True)
#         return


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
