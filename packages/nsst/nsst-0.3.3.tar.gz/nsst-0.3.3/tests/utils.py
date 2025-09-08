import datetime


def hours_ago(n):
    return datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=n)
