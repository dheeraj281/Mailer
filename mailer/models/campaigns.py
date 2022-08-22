from mailer.extensions import db
from datetime import datetime
from mailer.models.ab_users import Users
from mailer.utils.celery import crontab_parser


class Campaigns(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    crontab = db.Column(db.String(1000), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    # relational
    mailing_list = db.Column(db.Integer, db.ForeignKey('mailing_list.id')) # one to many relationship with table Mailing-list
    email_template = db.Column(db.Integer, db.ForeignKey("emails.id"))  # one to many relationship with table Emails
    owner = db.Column(db.Integer, db.ForeignKey(Users.id)) # Many to one relationship with table Ab_users


    def __init__(self, name):
        self.name = name

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

    @property
    def status(self):
        if self.is_active:
            return "Active"
        else:
            return "Inactive"

    @property
    def created(self):
        return self.created_on.strftime("%d %B, %Y")

    @property
    def schedule(self):
        return crontab_parser(self.crontab)


class Email(db.Model):
    __tablename__ = "emails"

    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(250))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    subject = db.Column(db.Text, nullable=False)
    email_body = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey(Users.id))
    is_favorite = db.Column(db.Boolean, default=False)
    # relational
    campaign = db.relationship('Campaigns', backref='Email_template', lazy='dynamic')

    def __init__(self, template_name, subject, email_body):
        self.template_name = template_name
        self.subject = subject
        self.email_body = email_body

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"{self.template_name}"
