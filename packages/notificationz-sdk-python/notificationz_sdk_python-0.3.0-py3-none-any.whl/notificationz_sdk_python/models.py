from enum import Enum
class notification_destination(Enum):
    telegram = "telegram"
    email = "email"

class tag(Enum):
    error = "ERROR"
    success = "SUCCESS"
    warning = "WARNING"