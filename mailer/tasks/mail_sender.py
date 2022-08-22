import smtplib, logging, socket
from mailer import app
from email.mime.text import MIMEText
from validate_email import validate_email
from mailer.extensions import celery_app
from datetime import datetime
from mailer.models.schedule_log import Job_log

logger = logging.getLogger(__name__)


def send_emails(to, campid, subject, body):
    start_time = datetime.utcnow()
    gmail_user = app.config.get("GMAIL_USER")# mail id of our application
    gmail_password = app.config.get("GMAIL_PASSWORD")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "Mailers"
    failed_emails = []

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        #raise ValueError("this job is failed")
        smtp_server.login(gmail_user, gmail_password)
        for recvr in to:
            is_valid = validate_email(recvr, verify=True)
            if is_valid:
                msg['To'] = recvr
                try:
                    logger.info(f"Sending email to {recvr}")
                    smtp_server.sendmail(gmail_user, recvr, msg.as_string())
                except:
                    failed_emails.append(recvr)
            else:
                failed_emails.append(recvr)

        logger.info("Email sent successfully!")
        logger.info(f" Failed emails: {failed_emails}")
        smtp_server.close()
        new_log_entry = Job_log(start_time,datetime.utcnow(),True,campid)
        new_log_entry.add_to_db()
    except Exception as ex:
        logger.info("Something went wrong….", ex)
        new_log_entry = Job_log(start_time, datetime.utcnow(), False, campid)
        new_log_entry.add_to_db()


@celery_app.task(name="execute_campaign")
def execute_campaign(email_subject,email_body , recievers, campid):
    send_emails(to=recievers, campid=campid,subject=email_subject, body=email_body)
