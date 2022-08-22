from mailer.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    """ Creating Model class for users.
    This will make database table and columns to store user related data. """

    __tablename__ = "ab_user"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(250))
    lastname = db.Column(db.String(250))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(250))

    # Relational
    mailing_list = db.relationship('MailingList', backref='mailing_list_owner', lazy='dynamic')
    campaigns = db.relationship('Campaigns', backref='campaign_owner', lazy='dynamic')
    templates = db.relationship('Email', backref='template_owner', lazy='dynamic')

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"Username {self.firstname}"