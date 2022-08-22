from contextlib import contextmanager
from mailer import app, db
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Iterator
from croniter import croniter
from pytz import timezone as pytz_timezone, UnknownTimeZoneError
import logging

logger = logging.getLogger(__name__)


@contextmanager
def session_scope(nullpool: bool):
    """Provide a transactional scope around a series of operations."""
    database_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if nullpool:
        engine = create_engine(database_uri, poolclass=NullPool)
        session_class = sessionmaker()
        session_class.configure(bind=engine)
        session = session_class()
    else:
        session = db.session()
        session.commit()  # HACK

    try:
        yield session
        session.commit()
    except SQLAlchemyError as ex:
        session.rollback()
        raise
    finally:
        session.close()



def cron_schedule_window(cron: str,timezone="Asia/Kolkata") -> Iterator[datetime]:

    time_now = datetime.now(tz=dt_timezone.utc)
    try:
        tz = pytz_timezone(timezone)
    except UnknownTimeZoneError:
        # fallback to default timezone
        tz = pytz_timezone("UTC")
        logger.warning("Timezone %s was invalid. Falling back to 'UTC'", timezone)
    utc = pytz_timezone("UTC")
    # convert the current time to the user's local time for comparison
    time_now = time_now.astimezone(tz)
    start_at = time_now - timedelta(seconds=1)
    stop_at = time_now + timedelta(seconds=59)
    crons = croniter(cron, start_at)
    for schedule in crons.all_next(datetime):
        if schedule >= stop_at:
            break
        # convert schedule back to utc
        yield schedule.astimezone(utc).replace(tzinfo=None)


def crontab_parser(crontab):
    min, hour, day, month, weekday = crontab.split(" ")
    timeformat = "AM"

    if "/" in min:
        return f"Every {min.split('/')[1]} Minutes"

    if day == "*" and month == "*" and weekday == "*":
        if hour=="*" and min == "*":
            return "Every Minute"
        elif hour != "*" and int(hour) > 12:
            hour = int(hour) - 12
            timeformat = "PM"
            return f"At {hour}: {min} {timeformat} everyday"

    if weekday == "0":
        week_day = "Sunday"
    elif weekday == "1":
        week_day = "Monday"
    elif weekday == "2":
        week_day = "Tuesday"
    elif weekday == "3":
        week_day = "Wednesday"
    elif weekday == "4":
        week_day = "Thursday"
    elif weekday == "5":
        week_day = "Friday"
    elif weekday == "6":
        week_day = "Saturday"

    if hour != "*":
        if int(hour) > 12:
            hour = int(hour) - 12
            timeformat = "PM"

        return f"Every {week_day} at {hour}: {min} {timeformat}"
