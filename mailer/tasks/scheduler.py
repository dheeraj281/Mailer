from mailer.extensions import celery_app
from mailer.models.campaigns import Campaigns
from mailer.utils.celery import session_scope, cron_schedule_window
from mailer.tasks.mail_sender import execute_campaign
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="email.scheduler")
def scheduler() -> None:
    """
    Celery beat main scheduler for emails.
    """

    with session_scope(nullpool=True) as session:
        active_schedules = session.query(Campaigns).filter(Campaigns.is_active == True).all() # selecting active campaings

        for active_schedule in active_schedules:
            for schedule in cron_schedule_window(active_schedule.crontab):
                logger.info(
                    "Scheduling campaign %s eta: %s", active_schedule.name, schedule
                )
                async_options = {"eta": schedule}
                email = active_schedule.Email_template
                mailing_list = active_schedule._mailing_list
                rcvrs = mailing_list.recipients
                rcvrs = [rcp.email for rcp in rcvrs]
                execute_campaign.apply_async((email.subject,email.email_body,rcvrs,active_schedule.id),**async_options)
