from django.contrib.auth.models import User

class ShibbolethBackend(object):
    "Authenticate against Tse/Utu Shibboleth."

    def authenticate(self, request=request):
        """Authenticate user against the data from Shibboleth.

        Tse provides HTTP_UID in the response, Utu provides HTTP_MAIL
        in form of username@utu.fi.

        """
        try:
            if 'HTTP_UID' in request.META and request.META['HTTP_UID']:
                username = request.META['HTTP_UID']
            else:
                username, domain = request.META['HTTP_MAIL'].split('@')
            user = User.objects.get(username=username)
            user.first_name = request.META['HTTP_DISPLAYNAME']
            user.last_name = request.META['HTTP_SN']
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            User.objects.get(username=user_id)
        except User.DoesNotExist:
            return None
