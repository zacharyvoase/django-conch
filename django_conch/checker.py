from twisted.cred import checkers, error, credentials
from twisted.internet import defer
from twisted.python import failure
from zope.interface import implements

from django.contrib.auth.models import User, check_password


class DjangoSuperuserCredChecker:
    implements(checkers.ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)

    user_queryset = User.objects.filter(is_superuser=True)

    def passwordMatched(self, matched, user):
        if matched:
            return user.username
        return failure.Failure(error.UnauthorizedLogin())

    def requestAvatarId(self, credentials):
        try:
            user = self.user_queryset.get(username=credentials.username)
            return defer.maybeDeferred(
                check_password,
                credentials.password,
                user.password).addCallback(self.passwordMatched, user)
        except User.DoesNotExist:
            return defer.fail(error.UnauthorizedLogin())
