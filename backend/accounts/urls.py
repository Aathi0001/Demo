from django.urls import path

from accounts.views.register_view import RegisterView
from accounts.views.login_view import LoginView
from accounts.views.refresh_view import RefreshView
from accounts.views.logout_view import LogoutView

from accounts.views.profile_view import ProfileView
from accounts.views.change_password_view import ChangePasswordView

from accounts.views.set_lock_password_view import SetLockPasswordView
from accounts.views.verify_lock_password_view import VerifyLockPasswordView
from accounts.views.change_lock_password_view import ChangeLockPasswordView
from accounts.views.forgot_lock_password_view import ForgotLockPasswordView

from accounts.views.set_delete_password_view import SetDeletePasswordView
from accounts.views.verify_delete_password_view import VerifyDeletePasswordView
from accounts.views.change_delete_password_view import ChangeDeletePasswordView
from accounts.views.forgot_delete_password_view import ForgotDeletePasswordView


urlpatterns = [

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("profile/", ProfileView.as_view(), name="profile"),

    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    path("lock-password/set/", SetLockPasswordView.as_view(), name="set-lock-password"),
    path("lock-password/verify/", VerifyLockPasswordView.as_view(), name="verify-lock-password"),
    path("lock-password/change/", ChangeLockPasswordView.as_view(), name="change-lock-password"),
    path("lock-password/forgot/", ForgotLockPasswordView.as_view(), name="forgot-lock-password"),

    path("delete-password/set/", SetDeletePasswordView.as_view(), name="set-delete-password"),
    path("delete-password/verify/", VerifyDeletePasswordView.as_view(), name="verify-delete-password"),
    path("delete-password/change/", ChangeDeletePasswordView.as_view(), name="change-delete-password"),
    path("delete-password/forgot/", ForgotDeletePasswordView.as_view(), name="forgot-delete-password"),
]

