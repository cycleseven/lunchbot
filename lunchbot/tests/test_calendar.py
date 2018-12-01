from lunchbot.calendar import get_last_friday_of_month


def test_get_last_friday_of_month():
    assert 28 == get_last_friday_of_month(2018, 12)
    assert 30 == get_last_friday_of_month(2018, 11)
    assert 26 == get_last_friday_of_month(2018, 10)
    assert 28 == get_last_friday_of_month(2018, 9)
