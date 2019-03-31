from lunchbot import monthly_report
from lunchbot.test_utils import get_timestamp


def test_should_count_good_days_for_user():
    assert 3 == monthly_report.count_good_days(
        [
            {"did_bring_lunch": True},
            {"did_bring_lunch": False},
            {"did_bring_lunch": True},
            {"did_bring_lunch": True},
        ]
    )

    assert 0 == monthly_report.count_good_days([{"did_bring_lunch": False}])
    assert 1 == monthly_report.count_good_days([{"did_bring_lunch": True}])
    assert 0 == monthly_report.count_good_days([])


def test_should_estimate_money_saved():
    """Assume an average saving of £4"""
    assert 12 == monthly_report.estimate_money_saved(
        [
            {"did_bring_lunch": True},
            {"did_bring_lunch": False},
            {"did_bring_lunch": True},
            {"did_bring_lunch": True},
        ]
    )

    assert 0 == monthly_report.estimate_money_saved([{"did_bring_lunch": False}])
    assert 4 == monthly_report.estimate_money_saved([{"did_bring_lunch": True}])
    assert 0 == monthly_report.estimate_money_saved([])


def test_should_identify_distinct_users():
    assert {"AAA", "BBB", "CCC", "DDD"} == monthly_report.get_distinct_users(
        [
            {"user_id": "AAA"},
            {"user_id": "BBB"},
            {"user_id": "CCC"},
            {"user_id": "AAA"},
            {"user_id": "CCC"},
            {"user_id": "DDD"},
        ]
    )

    assert set() == monthly_report.get_distinct_users([])


def test_should_count_distinct_days():
    assert 3 == monthly_report.count_distinct_days(
        [
            {"timestamp": get_timestamp(2018, 1, 1)},
            {"timestamp": get_timestamp(2018, 1, 1)},
            {"timestamp": get_timestamp(2018, 1, 2)},
            {"timestamp": get_timestamp(2018, 1, 2)},
            {"timestamp": get_timestamp(2018, 1, 2)},
            {"timestamp": get_timestamp(2018, 1, 3)},
        ]
    )

    assert 0 == monthly_report.count_distinct_days([])


def test_should_get_monthly_stats():
    records = [
        # On 1st Jan 2018, Alice brings lunch and Bob doesn't
        {
            "user_id": "Alice",
            "timestamp": get_timestamp(2018, 1, 1),
            "did_bring_lunch": True,
        },
        {
            "user_id": "Bob",
            "timestamp": get_timestamp(2018, 1, 1),
            "did_bring_lunch": False,
        },
        # On 2nd Jan 2018, only Bob replies. Assume Alice didn't bring lunch
        {
            "user_id": "Bob",
            "timestamp": get_timestamp(2018, 1, 2),
            "did_bring_lunch": False,
        },
        # On 4th Jan 2018, both brought lunch
        {
            "user_id": "Alice",
            "timestamp": get_timestamp(2018, 1, 4),
            "did_bring_lunch": True,
        },
        {
            "user_id": "Bob",
            "timestamp": get_timestamp(2018, 1, 4),
            "did_bring_lunch": True,
        },
    ]

    users = [{"id": "Alice", "name": "alice"}, {"id": "Bob", "name": "bob"}]

    assert [
        {"name": "alice", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
        {"name": "bob", "good_days": 1, "total_days": 3, "estimated_money_saved": 4},
    ] == monthly_report.get_monthly_stats(records, users)


def test_should_identify_winners():
    stats = [
        {"name": "alice", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
        {"name": "bob", "good_days": 1, "total_days": 3, "estimated_money_saved": 4},
    ]
    assert ["alice"] == monthly_report.get_winners(stats)

    stats = [
        {"name": "alice", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
        {"name": "bob", "good_days": 2, "total_days": 3, "estimated_money_saved": 8},
    ]
    assert ["alice", "bob"] == monthly_report.get_winners(stats)


def test_should_summarise_winners():
    assert (
        "our winner for the month is\n:tada: alice :tada:"
        == monthly_report.summarise_winners(["alice"])
    )
    assert (
        "our winners for the month are\n:tada: alice and bob :tada:"
        == monthly_report.summarise_winners(["alice", "bob"])
    )
