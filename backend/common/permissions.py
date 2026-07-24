from rest_framework.permissions import IsAuthenticated


class AuthenticatedPermission(IsAuthenticated):
    pass
