from caldav import DAVClient, Calendar
from src import logger

from src.model.event import Event


def authenticate_caldav(url: str, username: str, password: str) -> DAVClient:
    return DAVClient(url, username=username, password=password)


def add_to_caldav(
    url: str, username: str, password: str, calendar_name: str, events: list[Event]
):
    with authenticate_caldav(url, username, password) as client:
        principal = client.principal()
        ## The principals calendars can be fetched like this:
        calendars: list[Calendar] = principal.calendars()

        calendar: Calendar = [cal for cal in calendars if cal.name == calendar_name][0]
        if not calendar:
            logger.error(f"Calendar '{calendar_name}' not found.")
            raise ValueError(f"Calendar '{calendar_name}' not found.")

        events = [event for event in events if not event.in_calendar]
        if not events:
            return

        for event in events:
            try:
                logger.info(
                    f"Adding event {event.summary} to CalDAV calendar '{calendar_name}'"
                )
                calendar.add_event(
                    dtstart=event.start, dtend=event.end, summary=event.summary
                )
                event.save_to_caldav()
            except Exception as e:
                logger.error(f"Failed to add event {event.summary} to CalDAV: {e}")
                raise e
