from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from mailer.extensions import db
from mailer.models.campaigns import Campaigns, Email
from mailer.models.mailing import MailingList, Recipients
from mailer.models.schedule_log import Job_log
from datetime import datetime, tzinfo
from dateutil import tz
import pytz
import logging
base = Blueprint("base", __name__)


@base.route("/")
def main_view():

    return redirect(url_for('base.base_view'))


@base.route("/welcome")
@login_required
def base_view():
    camps = []
    log_entires = []
    local_zone = tz.tzlocal()
    all_camp = Campaigns.query.filter_by(owner=current_user.id,is_active=True).all()
    for camp in all_camp:
        camp_run = Job_log.query.filter_by(campaign_id=camp.id).order_by(Job_log.end_time.desc()).first()
        if camp_run:
            camps.append({"name":camp.name,"last_run_time":camp_run.started_at.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%b %d %Y %I:%M%p')})
        else:
            camps.append({"name": camp.name,"last_run_time":None})
    templates = Email.query.filter_by(is_favorite=True,owner=current_user.id)
    log_entires  = get_log_entries()
    return render_template("home.html", title="Home", active_campaigns=camps,templates=templates,log_entires=log_entires[0:5])


@base.route("/mailing-list", methods=["GET", "POST"])
@login_required
def mailing_list():
    """ Mailing list is a name of the group of emails of people who shares the same traits.
     Used for targeting customers for pur campaign """

    if request.method == "POST":
        name = request.form.get("mailing_list_name")
        new_mailing_list = MailingList(name)
        new_mailing_list.owner = current_user.id
        new_mailing_list.add_to_db()
        return redirect(url_for("base.mailing_list"))
    all_mailing_list = MailingList.query.filter_by(owner=current_user.id).all()
    return render_template("mailing.html", title="Mailing list", page_title="Mailing List",
                           mailing_list=all_mailing_list)


@base.route("/delete/mailing-list", methods=["POST"])
@login_required
def delete_mailing_list():
    if request.method == "POST":
        for item in request.values:
            list_item = MailingList.query.filter_by(id=int(item)).first()
            rcpnts = list_item.recipients
            all_camp = Campaigns.query.filter_by(owner=current_user.id).all()
            for camp in all_camp:
                if camp._mailing_list == list_item:
                    flash("Some mailing list linked to a campaign can't be deleted. first delete the campaign.")
                    return redirect(url_for('base.mailing_list'))
            if list_item.owner != current_user.id:
                abort(403)
            for rcp in rcpnts:
                list_item.recipients.remove(rcp) # deleting all the related recipents from relationship table before deleting mailing list.
            db.session.delete(list_item)
        db.session.commit()
    return redirect(url_for('base.mailing_list'))


@base.route("/mailing-list/<int:mailing_list_id>/recipients", methods=["GET", "POST"])
@login_required
def reciepents(mailing_list_id):
    mailing_list = MailingList.query.filter_by(id=int(mailing_list_id)).first()
    page_title = f"Recipients of {mailing_list.name}"
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        existing_id = Recipients.query.filter_by(email=email).first()
        if existing_id: # if the reciepents id already exist in db.
            mailing_list.recipients.append(existing_id) # don't add duplicate data. Just create a relationship with the new mailing list.
        else:
            new_reciepents = Recipients(name, email)
            mailing_list.recipients.append(new_reciepents)
        mailing_list.add_to_db()
        return redirect(url_for("base.reciepents", mailing_list_id=mailing_list_id))

    all_receipents = mailing_list.recipients
    return render_template("recipients.html", title="Recipients", page_title=page_title,
                           Recipients=all_receipents, list_id=mailing_list_id)


@base.route("/delete/reciepent", methods=["POST"])
@login_required
def delete_reciepents():
    list_id = request.args.get("list_id")
    if request.method == "POST":
        mailing_list = MailingList.query.filter_by(id=int(list_id)).first()
        for item in request.form:
            list_item = Recipients.query.filter_by(id=int(item)).first()
            mailing_list.recipients.remove(list_item)
        db.session.commit()
    return redirect(url_for('base.reciepents', mailing_list_id=list_id))


@base.route("/email_template", methods=["GET", "POST"])
@login_required
def email_template():
    if request.method == "POST":
        template_name = request.form.get("template_name")
        email_subject = request.form.get("subject")
        email_body = request.form.get("emailbody")
        new_template = Email(template_name, email_subject, email_body)
        new_template.owner = current_user.id
        new_template.add_to_db()
        return redirect(url_for("base.email_template"))

    templates = Email.query.filter_by(owner=current_user.id).all()
    return render_template("email_template.html", title="Email Templates", page_title="Email Templates",
                           templates=templates)

@base.route("/favorite/<int:template_id>",methods=["GET"])
@login_required
def favorite_template(template_id):

    item = Email.query.filter_by(id=int(template_id)).first()
    if item.owner == current_user.id:
        if item.is_favorite:
            item.is_favorite = False
        else:
            item.is_favorite = True
        item.add_to_db()
    return redirect(url_for("base.email_template"))



@base.route("/delete_template/<int:template_id>",methods=["GET"])
def delete_template(template_id):
    item = Email.query.filter_by(id=int(template_id)).first()
    if item.owner != current_user.id:
        abort(403)
    all_camp = Campaigns.query.filter_by(owner=current_user.id).all()
    for camp in all_camp:
        if camp.Email_template == item:
            flash("This template is linked to a campaign can't be deleted. first delete the campaign.")
            return redirect(url_for('base.email_template'))
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('base.email_template'))


@base.route("/campaign/logs", methods=["GET", "POST"])
@login_required
def job_logs():
    log_entires = get_log_entries()
    return render_template("joblogs.html",title="logs", log_entires=log_entires)




def get_log_entries():
    log_entires = []
    camp_logs = Job_log.query.order_by(Job_log.end_time.desc()).all()
    local_zone = tz.tzlocal()
    for logs in camp_logs:
        camp_id = logs.campaign_id
        camp = Campaigns.query.filter_by(id=camp_id).first()

        if camp!=None and camp.owner == current_user.id:
            log_entires.append({"id": logs.id,
                                "campaign": camp.name,
                                "start_time": logs.started_at.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%b %d %Y %I:%M%p'),
                                "end_time": logs.end_time.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%b %d %Y %I:%M%p'),
                                "status": "Success" if logs.running_status else "Failed"})
    return log_entires






