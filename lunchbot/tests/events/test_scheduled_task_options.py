from lunchbot.events import ScheduledTaskOptions


def test_should_detect_when_dry_run_is_disabled():
    event = ScheduledTaskOptions.create_from_cloudwatch_event({"dry_run": False})
    assert not event.is_dry_run()


def test_should_detect_when_dry_run_is_enabled():
    event = ScheduledTaskOptions.create_from_cloudwatch_event({"dry_run": True})
    assert event.is_dry_run()


def test_should_enable_dry_run_by_default():
    event = ScheduledTaskOptions.create_from_cloudwatch_event({})
    assert event.is_dry_run()
