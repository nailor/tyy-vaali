from django.contrib.auth.models import User

class ShibbolethBackend(object):
    "Authenticate against Tse/Utu Shibboleth."

    def authenticate(self, request):
        """Authenticate user against the data from Shibboleth.

        Tse provides HTTP_UID in the response, Utu provides HTTP_MAIL
        in form of username@utu.fi.

        """
        if 'HTTP_UID' in request.META and request.META['HTTP_UID']:
            username = request.META['HTTP_UID']
        else:
            username, domain = request.META['HTTP_MAIL'].split('@')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if not user.first_name or user.last_name:
            user.first_name = request.META['HTTP_DISPLAYNAME']
            user.last_name = request.META['HTTP_SN']
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
