import calendar


def get_last_friday_of_month(year, month):
    """Return the date of the last Friday in the month as an int."""
    # calendar_for_month is a 2D list of days of the month, grouped by week.
    # For example, December 2018 looks like this:
    # [[ 0,  0,  0,  0,  0,  1,  2],
    #  [ 3,  4,  5,  6,  7,  8,  9],
    #  [10, 11, 12, 13, 14, 15, 16],
    #  [17, 18, 19, 20, 21, 22, 23],
    #  [24, 25, 26, 27, 28, 29, 30],
    #  [31,  0,  0,  0,  0,  0,  0]]
    calendar_for_month = calendar.monthcalendar(year, month)

    # Iterate backwards through the weeks from the END (so taking the final week first).
    for week in reversed(calendar_for_month):
        # Each week is represented in this order: [mon, tue, wed, thu, fri, sat, sun].
        # So week[4] represents Friday.
        #
        # A value of 0 means that the current week doesn't contain Friday. That can
        # happen if the Friday of the current week actually lands in an adjacent month.
        #
        # As soon as we land on a week where Friday has a non-zero value, that must be
        # the last Friday in the month.
        if week[4] != 0:
            return week[4]
