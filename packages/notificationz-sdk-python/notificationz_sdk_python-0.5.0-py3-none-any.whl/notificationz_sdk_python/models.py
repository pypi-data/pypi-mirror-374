from enum import Enum

class notification_destinations(Enum):
    telegram = "telegram"
    email = "email"

class tag(Enum):
    error = "ERROR"
    success = "SUCCESS"
    warning = "WARNING"