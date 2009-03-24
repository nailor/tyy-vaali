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
        if request.user:
            # User might have logged through the admin interface,
            # don't change username
            return
        try:
            if 'HTTP_UID' in request.META and request.META['HTTP_UID']:
                username = request.META['HTTP_UID']
            else:
                username, domain = request.META['HTTP_MAIL'].split('@')
            user = User.objects.get(username=username)
            user.first_name = request.META['HTTP_DISPLAYNAME']
            user.last_name = request.META['HTTP_SN']
            request.__class__.user = user
        except User.DoesNotExist:
            content = 'You fail.'
            if settings.DEBUG:
                content = request.META.items()
            return HttpResponseForbidden(content)
