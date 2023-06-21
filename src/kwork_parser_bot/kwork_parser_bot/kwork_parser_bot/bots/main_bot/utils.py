import re


def validate_cron_string(cron_string):
    pattern = r"^(\*|\d{1,2}|\*/\d{1,2}|\d{1,2}-\d{1,2})(\s+(\*|\d{1,2}|\*/\d{1,2}|\d{1,2}-\d{1,2})){4}$"
    if re.match(pattern, cron_string):
        return True
    else:
        return False


def test_validate_cron_string():
    cron_string = "*/5 * * * *"
    if validate_cron_string(cron_string):
        return True
    else:
        raise ValueError(cron_string)
