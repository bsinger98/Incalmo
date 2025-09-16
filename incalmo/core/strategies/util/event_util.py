from incalmo.core.models.events import Event


def any_events_are_type(events: list[Event], event_type: type[Event]) -> bool:
    for event in events:
        if isinstance(event, event_type):
            return True
    return False
