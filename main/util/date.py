from datetime import datetime, timedelta

def has_passed_29_days(date: datetime):
  raw_now_date = datetime.now().strftime("%Y-%m-%d")

  now_date = datetime.strptime(raw_now_date, "%Y-%m-%d")
  target_date = datetime.strptime(date, "%Y-%m-%d")

  difference = (target_date - now_date).days

  return difference > 29

def current_time():
  raw_now = datetime.now()
  now = raw_now.strftime("%Y-%m-%d")
  return now

