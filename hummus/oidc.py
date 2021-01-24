from mozilla_django_oidc.auth import OIDCAuthenticationBackend


# This subclass of the mozilla-django-oidc authentication backend
# updates the user's real name from the OIDC claims. See the example in
# mozilla-django-oidc's documentation.
class HummusOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(HummusOIDCAuthenticationBackend, self).create_user(claims)
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.save()
        return user

    def update_user(self, user, claims):
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.save()
        return user
