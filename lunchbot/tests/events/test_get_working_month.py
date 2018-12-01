from lunchbot.events import LunchbotMessageEvent
from lunchbot.test_utils import get_timestamp


def test_should_return_working_month():
    # November 1st 2018 is a Thursday early on in the month, nothing special about it.
    # So here, the working month is equal to the calendar month.
    event = LunchbotMessageEvent({
        "ts": get_timestamp(2018, 11, 1)
    })
    assert "11/2018" == event.get_working_month()

    # October 30th 2018 is a Tuesday after payday has already passed. So it should
    # count towards the *November* working month, not October!
    event = LunchbotMessageEvent({
        "ts": get_timestamp(2018, 10, 30)
    })
    assert "11/2018" == event.get_working_month()

    # December 31st should get assigned to January next year, it's after payday.
    # This test is important to verify that assignment to the next month "loops
    # around" to 1 (rather than 13).
    event = LunchbotMessageEvent({
        "ts": get_timestamp(2018, 12, 31)
    })
    assert "1/2019" == event.get_working_month()
