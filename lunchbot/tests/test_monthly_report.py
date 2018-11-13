import datetime

from lunchbot.monthly_report import count_good_days, estimate_money_saved, get_distinct_users, \
    count_distinct_days, get_monthly_stats, get_winners, summarise_winners


def _get_timestamp(year, month, day):
    """Get a timestamp in a realistic DB format. Utility function for tests below"""
    return datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp()


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
    """Assume an average saving of £4"""
    assert estimate_money_saved([
        {"did_bring_lunch": True},
        {"did_bring_lunch": False},
        {"did_bring_lunch": True},
        {"did_bring_lunch": True},
    ]) == 12

    assert estimate_money_saved([{"did_bring_lunch": False}]) == 0
    assert estimate_money_saved([{"did_bring_lunch": True}]) == 4
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


def test_should_count_distinct_days():
    assert count_distinct_days([
        {"timestamp": _get_timestamp(2018, 1, 1)},
        {"timestamp": _get_timestamp(2018, 1, 1)},
        {"timestamp": _get_timestamp(2018, 1, 2)},
        {"timestamp": _get_timestamp(2018, 1, 2)},
        {"timestamp": _get_timestamp(2018, 1, 2)},
        {"timestamp": _get_timestamp(2018, 1, 3)},
    ]) == 3

    assert count_distinct_days([]) == 0


def test_should_get_monthly_stats():
    records = [
        # On 1st Jan 2018, Alice brings lunch and Bob doesn't
        {
            "user_id": "Alice",
            "timestamp": _get_timestamp(2018, 1, 1),
            "did_bring_lunch": True
        },
        {
            "user_id": "Bob",
            "timestamp": _get_timestamp(2018, 1, 1),
            "did_bring_lunch": False
        },

        # On 2nd Jan 2018, only Bob replies. Assume Alice didn't bring lunch
        {
            "user_id": "Bob",
            "timestamp": _get_timestamp(2018, 1, 2),
            "did_bring_lunch": False
        },

        # On 4th Jan 2018, both brought lunch
        {
            "user_id": "Alice",
            "timestamp": _get_timestamp(2018, 1, 4),
            "did_bring_lunch": True
        },
        {
            "user_id": "Bob",
            "timestamp":_get_timestamp(2018, 1, 4),
            "did_bring_lunch": True
        },
    ]

    users = [
        {"id": "Alice", "name": "alice"},
        {"id": "Bob", "name": "bob"},
    ]

    assert get_monthly_stats(records, users) == [
        {"name": "alice", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
        {"name": "bob", "good_days": 1, "total_days": 3, "estimated_money_saved": 4},
    ]


def test_should_identify_winners():
    stats = [
        {"name": "alice", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
        {"name": "bob", "good_days": 1, "total_days": 3, "estimated_money_saved": 4},
    ]
    assert get_winners(stats) == ["alice"]

    stats = [
        {"name": "alice", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
        {"name": "bob", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
    ]
    assert get_winners(stats) == ["alice", "bob"]


def test_should_summarise_winners():
    assert summarise_winners(["alice"]) == "our winner for the month is\n:tada: alice :tada:"
    assert summarise_winners(["alice", "bob"]) == "our winners for the month are\n:tada: alice and bob :tada:"
