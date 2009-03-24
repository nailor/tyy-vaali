from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.models import User

class ShibbolethMiddleware(object):
    """
    Middleware that checks that the user authenticated via Shibboleth
    is the user we actually want.
    """
    def process_request(self, request):
        """Authenticate user against the data from Shibboleth.

        Tse provides uid in the response, Utu provides mail in form of
        username@utu.fi.

        """
        try:
            if 'uid' in request.META:
                username = request.META['uid']
            else:
                username, domain = request.META['mail'].split('@')
            user = User.objects.get(username=username)
            request.__class__.user = user
        except User.DoesNotExist:
            content = 'You fail.'
            if settings.DEBUG:
                content = content + dir(request.META)
            return HttpResponseForbidden(content)
