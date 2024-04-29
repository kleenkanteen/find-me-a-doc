from datetime import datetime


# Checks if the given date is x days apart from today
def has_passed_30_days_since(date: datetime):
    raw_now_date = datetime.now().strftime("%Y-%m-%d")

    now_date = datetime.strptime(raw_now_date, "%Y-%m-%d")
    target_date = datetime.strptime(date, "%Y-%m-%d")

    difference = (now_date - target_date).days

    return difference >= 30


def current_time():
    raw_now = datetime.now()
    now = raw_now.strftime("%Y-%m-%d")
    return now
