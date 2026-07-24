from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from common.messages import Messages
from common.constants import SecurityConstants

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.hashers import check_password

User = get_user_model()


class AuthService:
    
    #Registration
    @transaction.atomic
    def register(self, validated_data):

        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user
    
    #Login
    def login(self, validated_data):

        username = validated_data["username"]
        password = validated_data["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            raise AuthenticationFailed(
                Messages.INVALID_CREDENTIALS
            )

        tokens = self._generate_tokens(user)

        return {
            **tokens,
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.profile.display_name,
            }
        }
    
    #Profile
    def get_profile(self, user):

        return user.profile


    def update_profile(self, user, validated_data):

        profile = user.profile

        profile.display_name = validated_data.get(
            "display_name",
            profile.display_name
        )

        profile.theme = validated_data.get(
            "theme",
            profile.theme
        )

        profile.timezone = validated_data.get(
            "timezone",
            profile.timezone
        )

        profile.save()

        return profile


    #Refresh Token
    def refresh_token(self, validated_data):

        try:
            refresh = RefreshToken(validated_data["refresh"])

            return {
                "access": str(refresh.access_token)
            }

        except Exception:
            raise AuthenticationFailed(
                Messages.INVALID_REFRESH_TOKEN
            )

    def _generate_tokens(self, user):

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def _get_security(self, user):
        return user.security

    def _is_password_set(self, security, password_field):
        return bool(getattr(security, password_field))

    def _is_reset_scheduled(self, security, reset_field):
        reset_time = getattr(security, reset_field)
        if not reset_time:
            return False
        return timezone.now() < reset_time

    def _is_reset_expired(self, security, reset_field):
        reset_time = getattr(security, reset_field)
        if not reset_time:
            return False
        return timezone.now() >= reset_time

    def _clear_reset(self, security, reset_field):
        setattr(security, reset_field, None)
        security.save(update_fields=[reset_field])

    def _save_password(self, security, password_field, password):
        setattr(security, password_field, make_password(password))
        security.save(update_fields=[password_field])


    def change_login_password(self, user, validated_data):

        if not user.check_password(validated_data["old_password"]):
            return False

        user.set_password(validated_data["new_password"])
        user.save(update_fields=["password"])

        return True

def _set_security_password(self, user, password_field, reset_field, password):

    security = self._get_security(user)

    if not self._is_password_set(security, password_field):
        self._save_password(security, password_field, password)
        return True

    if self._is_reset_expired(security, reset_field):
        self._save_password(security, password_field, password)
        self._clear_reset(security, reset_field)
        return True

    return False

def _verify_security_password(self, user, password_field, reset_field, password):

    security = self._get_security(user)

    if not self._is_password_set(security, password_field):
        return False

    if self._is_reset_expired(security, reset_field):
        return False

    return check_password(
        password,
        getattr(security, password_field)
    )

def _change_security_password(self, user, password_field, reset_field, old_password, new_password):

    security = self._get_security(user)

    if not self._is_password_set(security, password_field):
        return False

    if self._is_reset_expired(security, reset_field):
        return False

    if not check_password(old_password, getattr(security, password_field)):
        return False

    self._save_password(security, password_field, new_password)
    self._clear_reset(security, reset_field)

    return True

def _forgot_security_password(self, user, password_field, reset_field, reset_duration):

    security = self._get_security(user)

    if not self._is_password_set(security, password_field):
        return False

    if self._is_reset_scheduled(security, reset_field):
        return False
    
    if self._is_reset_expired(security, reset_field):
        return False

    setattr(
        security,
        reset_field,
        timezone.now() + reset_duration
    )

    security.save(update_fields=[reset_field])

    return True

def set_lock_password(self, user, password):

    return self._set_security_password(
        user,
        "lock_password",
        "lock_password_reset_at",
        password
    )


def verify_lock_password(self, user, password):

    return self._verify_security_password(
        user,
        "lock_password",
        "lock_password_reset_at",
        password
    )


def change_lock_password(self, user, old_password, new_password):

    return self._change_security_password(
        user,
        "lock_password",
        "lock_password_reset_at",
        old_password,
        new_password
    )


def forgot_lock_password(self, user):

    return self._forgot_security_password(
        user,
        "lock_password",
        "lock_password_reset_at",
        SecurityConstants.LOCK_PASSWORD_RESET_DURATION
    )

def set_delete_password(self, user, password):

    return self._set_security_password(
        user,
        "delete_password",
        "delete_password_reset_at",
        password
    )


def verify_delete_password(self, user, password):

    return self._verify_security_password(
        user,
        "delete_password",
        "delete_password_reset_at",
        password
    )


def change_delete_password(self, user, old_password, new_password):

    return self._change_security_password(
        user,
        "delete_password",
        "delete_password_reset_at",
        old_password,
        new_password
    )


def forgot_delete_password(self, user):

    return self._forgot_security_password(
        user,
        "delete_password",
        "delete_password_reset_at",
        SecurityConstants.DELETE_PASSWORD_RESET_DURATION
    )


