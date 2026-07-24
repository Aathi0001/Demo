from datetime import timedelta

DEFAULT_DELETE_AFTER_HOURS = 48

DEFAULT_TIMEZONE = "Asia/Kolkata"

class SecurityConstants:

    LOCK_PASSWORD_RESET_DURATION = timedelta(hours=48)

    DELETE_PASSWORD_RESET_DURATION = timedelta(hours=48)

class PaginationConstants:

    PAGE_SIZE = 20
