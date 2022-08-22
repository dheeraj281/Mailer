from flask import Blueprint, request, render_template,redirect,abort,url_for
from flask_login import current_user,login_required
from datetime import datetime
from mailer.extensions import db
from mailer.models.campaigns import Campaigns, Email
from mailer.models.mailing import MailingList
from mailer.models.schedule_log import Job_log

campaigns = Blueprint("campaigns", __name__)

import pdb

@login_required
@campaigns.route("/campaigns", methods=["GET", "POST"])
def create_campaign():
    if request.method == 'POST':
        c_name = request.form.get('camp_name')
        mailing_list_id = request.form.get('malinglist')
        schedule_crontab = request.form.get('crontab_schedule')
        template_id = request.form.get("template")

        mailing_list = MailingList.query.filter_by(id=int(mailing_list_id)).first()
        email_template = Email.query.filter_by(id=int(template_id)).first()

        new_campaign = Campaigns(c_name)
        new_campaign.owner = current_user.id
        new_campaign.mailing_list = mailing_list.id
        new_campaign.email_template = email_template.id
        new_campaign.crontab = schedule_crontab
        new_campaign.add_to_db()
        return redirect(url_for('campaigns.create_campaign'))

    mailing_list = MailingList.query.filter_by(owner=current_user.id).all()
    templates =  Email.query.filter_by(owner=current_user.id).all()
    all_camp = Campaigns.query.filter_by(owner=current_user.id).all()
    return render_template("campaigns.html",page_title= "campaigns",
                           title="campaigns",
                           mailing_list=mailing_list,
                           templates=templates,
                           cmp_list=all_camp,

                           )


@login_required
@campaigns.route("/<int:camp_id>/delete_campaign", methods=["GET"])
def delete_campaign(camp_id):
    item = Campaigns.query.filter_by(id=int(camp_id)).first()
    related_logs = Job_log.query.filter_by(campaign_id=item.id).all()
    if item.owner != current_user.id:
        abort(403)
    for logs in related_logs:
        db.session.delete(logs)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('campaigns.create_campaign'))

@login_required
@campaigns.route("/<int:camp_id>/change_status", methods=["GET"])
def change_status(camp_id):

    item = Campaigns.query.filter_by(id=int(camp_id)).first()

    if item.owner != current_user.id:
        abort(403)

    status = item.is_active
    item.is_active = False if status else True

    db.session.commit()
    return redirect(url_for('campaigns.create_campaign'))