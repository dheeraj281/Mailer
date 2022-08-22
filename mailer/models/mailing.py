from mailer.extensions import db


# Many to many relationship table between Reciepents and Mailing list table.
# This table is completely responsible to hold the relationship of entity.
recipients_from_mailing_list = db.Table('recipients_from_mailing_list',
                                        db.Column('mailing_list_id', db.Integer, db.ForeignKey('mailing_list.id')),
                                        db.Column('recipients_id', db.Integer, db.ForeignKey('recipients.id'))
                                        )


class Recipients(db.Model):
    __tablename__ = "recipients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    email = db.Column(db.String(250), unique=True)

    # Relational
    maling_list = db.relationship('MailingList', secondary=recipients_from_mailing_list, backref='recipients')

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()


class MailingList(db.Model):
    __tablename__ = "mailing_list"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    #relation
    owner = db.Column(db.Integer, db.ForeignKey('ab_user.id'))
    campaign = db.relationship('Campaigns', backref='_mailing_list',lazy='dynamic')


    def __init__(self, name):
        self.name = name

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"{self.name}"
