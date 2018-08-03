# Sample Lambda events based on real API Gateway events, triggered by Slack API POSTing to the
# event handler endpoint.
#
# Only `body` is included to keep fixtures concise. None of the request handling logic depends
# on `headers`, `requestContext` or other metadata normally included in API Gateway events.

import json


yes_message_event = {
    'body': json.dumps({
        "token": "secret",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "message",
            "user": "U12345678",
            "text": "yes",  # Important! This is what makes it a "yes" message.
            "client_msg_id": "1f4c8752-1b0d-41ab-8b18-e245b3290e3f",
            "ts": "1530889991.000380",
            "channel": "C12345678",
            "event_ts": "1530889991.000380",
            "channel_type": "channel"
        },
        "type": "event_callback",
        "event_id": "E12345678",
        "event_time": 1530889991,
        "authed_users": ["U12345678"]
    })
}

no_message_event = {
    'body': json.dumps({
        "token": "secret",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "message",
            "user": "U12345678",
            "text": "no",   # Note the "no" message, which differentiates this fixture.
            "client_msg_id": "1f4c8752-1b0d-41ab-8b18-e245b3290e3f",
            "ts": "1530889991.000380",
            "channel": "C12345678",
            "event_ts": "1530889991.000380",
            "channel_type": "channel"
        },
        "type": "event_callback",
        "event_id": "E12345678",
        "event_time": 1530889991,
        "authed_users": ["U12345678"]
    })
}
