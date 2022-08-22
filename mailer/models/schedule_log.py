from mailer.extensions import db
from datetime import datetime



class Job_log(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    running_status =  db.Column(db.Boolean, default=True)
    campaign_id = db.Column(db.Integer)

    def __init__(self,started_at,end_time ,running_status, campaign_id):
        self.started_at = started_at
        self.end_time = end_time
        self.running_status = running_status
        self.campaign_id = campaign_id

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

