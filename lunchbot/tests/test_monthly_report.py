from lunchbot.monthly_report import count_good_days, estimate_money_saved, get_distinct_users


def test_should_count_good_days_for_user():
    assert count_good_days([
        {"did_bring_lunch": True},
        {"did_bring_lunch": False},
        {"did_bring_lunch": True},
        {"did_bring_lunch": True},
    ]) == 3

    assert count_good_days([{"did_bring_lunch": False}]) == 0
    assert count_good_days([{"did_bring_lunch": True}]) == 1
    assert count_good_days([]) == 0


def test_should_estimate_money_saved():
    """Assume an average lunch cost of £5"""
    assert estimate_money_saved([
        {"did_bring_lunch": True},
        {"did_bring_lunch": False},
        {"did_bring_lunch": True},
        {"did_bring_lunch": True},
    ]) == 15

    assert estimate_money_saved([{"did_bring_lunch": False}]) == 0
    assert estimate_money_saved([{"did_bring_lunch": True}]) == 5
    assert estimate_money_saved([]) == 0


def test_should_identify_distinct_users():
    assert get_distinct_users([
        {"user_id": "AAA"},
        {"user_id": "BBB"},
        {"user_id": "CCC"},
        {"user_id": "AAA"},
        {"user_id": "CCC"},
        {"user_id": "DDD"}
    ]) == {"AAA", "BBB", "CCC", "DDD"}

    assert get_distinct_users([]) == set()
