from django.contrib.auth.backends import ModelBackend
from wavewhiz_app.models import Usuario

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        # Permite autenticar tanto por username quanto por email
        if email is None:
            email = username
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
