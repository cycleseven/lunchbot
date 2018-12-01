import datetime


def get_timestamp(year, month, day):
    """Get a timestamp in a realistic DB format. Utility function for tests below"""
    return datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp()
