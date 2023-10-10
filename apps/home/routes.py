import asyncio
import base64
import json
import os
import webbrowser
from pathlib import Path

import openpyxl
from flask import render_template, redirect, request, url_for
from flask.helpers import get_root_path
from flask_login import login_required
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename

from apps.authentication.forms import CreateAccountForm
from apps.authentication.forms import CreateJobForm, CreateSettingForm, CreateIdNameForm, \
    CreateEmailForm, CreateauthcodeForm
from apps.authentication.models import Users
from apps.home import blueprint
from apps.home.models import EntityDataReadDetails
from apps.home.models import JobExecutionStatus, Task, TaskExecutionStatus, TaskExecutionStep, ToolId
from apps.home.models import MyobSettings, QboSettings, XeroSettings, ToolSettings
from apps.mmc_settings.all_settings import *
from apps.tasks.myob_to_qbo_task import read_myob_write_qbo_task
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_pagination_for_records
from apps.util.qbo_util import retry_payload_for_xero_to_myob, \
    retry_payload_for_qbo_to_myob, retry_payload_for_excel_to_myob, retry_payload_for_xero_to_qbo, \
    retry_payload_for_myob_to_qbo, retry_payload_for_excel_to_reckon


@blueprint.route("/index")
@login_required
def index():
    # return render_template('home/index.html', segment='index')

    data = []

    all_files = [
        "all_bill",
        "all_invoices",
        "chart_of_account",
        "classified_COA",
        "combined_bill",
        "customer",
        "employee",
        "item",
        "item_bill",
        "item_invoice",
        "job",
        "journal",
        "misc_bill",
        "professional_bill",
        "received_money",
        "service_bill",
        "spend_money",
        "supplier",
        "taxcode",
        "trial_balance",
    ]

    for fname in all_files:
        edrd = EntityDataReadDetails()
        edrd.entity_name = fname
        edrd.last_read_count = 10
        data.append(edrd)

    return render_template("home/myob-entities.html", segment="myob", data=data)


@blueprint.route("/myob")
@login_required
def myob_entities():
    data = []

    all_files = [
        "all_bill",
        "all_invoices",
        "chart_of_account",
        "classified_COA",
        "combined_bill",
        "customer",
        "employee",
        "item",
        "item_bill",
        "item_invoice",
        "job",
        "journal",
        "misc_bill",
        "professional_bill",
        "received_money",
        "service_bill",
        "spend_money",
        "supplier",
        "taxcode",
        "trial_balance",
    ]

    for fname in all_files:
        edrd = EntityDataReadDetails()
        edrd.entity_name = fname
        edrd.last_read_count = 10
        data.append(edrd)

    return render_template("home/myob-entities.html", segment="myob", data=data)


@blueprint.route("/jobs")
@login_required
def jobs():
    page = request.args.get('page', 1, type=int)
    tool1 = aliased(Tool)
    tool2 = aliased(Tool)
    jobs = (
        db.session.query(
            Jobs,
            tool1.tool_name.label("input_tool"),
            tool2.tool_name.label("output_tool"),
        )
        .join(tool1, Jobs.input_account_id == tool1.id)
        .join(tool2, Jobs.output_account_id == tool2.id)
    )

    jobs_data = jobs.paginate(page=page, per_page=100)
    # jobs_data.items.reverse()

    return render_template("home/jobs.html", segment="jobs", jobs=jobs_data)


@blueprint.route("/tasks/<int:job_id>")
@login_required
def tasks_by_job(job_id):
    tasks = Task.query.filter(
        Task.job_id == job_id
    ).all()
    return render_template("home/tasks.html", segment="tasks", data=tasks, job_id=job_id)


@blueprint.route("/start_job/<int:job_id>")
@login_required
def start_job(job_id):
    # read_myob_write_qbo_task.apply_async(args=[job_id])
    tasks = Task.query.filter(
        Task.job_id == job_id
    ).all()
    return render_template("home/tasks.html", segment="tasks", data=tasks)


@blueprint.route("/startJobByID", methods=["POST"])
@login_required
def startJobByID():
    job_id = request.form['job_id']
    asyncio.run(read_myob_write_qbo_task(job_id))
    return json.dumps({'status': 'success'})


@blueprint.route("/retryPayload", methods=["POST"])
@login_required
def retryPayload():
    print("inside retry")
    dbname = get_mongodb_database()
    task_id = request.form['task_id']
    _id = request.form['_id']
    payload1 = request.form['payload']
    payload = json.loads(payload1)

    tool1 = aliased(Tool)
    tool2 = aliased(Tool)
    task_details = db.session.query(Task).get(task_id)
    job_id = task_details.job_id
    jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                     tool2.account_type.label(
                                                         'output_tool')
                                                     ).join(tool1, Jobs.input_account_id == tool1.id
                                                            ).join(tool2, Jobs.output_account_id == tool2.id
                                                                   ).filter(Jobs.id == job_id).first()

    function_name = task_details.function_name

    if output_tool == MYOB:
        if input_tool == EXCEL:
            payload1, base_url, headers = get_settings_myob(job_id)
            status = retry_payload_for_excel_to_myob(job_id, payload, _id, task_id, function_name)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})

        if input_tool == XERO:
            payload1, base_url, headers = get_settings_myob(job_id)
            status = retry_payload_for_xero_to_myob(job_id, payload, _id, task_id, function_name)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})

        if input_tool == QBO:
            payload1, base_url, headers = get_settings_myob(job_id)
            status = retry_payload_for_qbo_to_myob(job_id, payload, _id, task_id, function_name)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})

    if output_tool == QBO:
        if input_tool == XERO:
            base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
            status = retry_payload_for_xero_to_qbo(job_id, payload, _id, task_id, function_name)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})

        if input_tool == MYOB:
            base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
            status = retry_payload_for_myob_to_qbo(job_id, payload, _id, task_id)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})

    if output_tool == RECKON:
        if input_tool == EXCEL:
            payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)
            status = retry_payload_for_excel_to_reckon(job_id, payload, _id, task_id, function_name)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})


@blueprint.route("/task_execution_details/<int:task_id>")
@login_required
def task_execution_details(task_id):
    task_steps = TaskExecutionStep.query.filter(
        TaskExecutionStep.task_id == task_id
    ).all()
    return render_template("home/task_execution_details.html", segment="task_steps", data=task_steps)


@blueprint.route("/records/<int:task_id>/<function_name>")
@login_required
def records(task_id, function_name):
    dbname = get_mongodb_database()
    page = request.args.get('page', 1, type=int)

    tool1 = aliased(Tool)
    tool2 = aliased(Tool)
    task_details = db.session.query(Task).get(task_id)
    job_id = task_details.job_id
    jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                     tool2.account_type.label(
                                                         'output_tool')
                                                     ).join(tool1, Jobs.input_account_id == tool1.id
                                                            ).join(tool2, Jobs.output_account_id == tool2.id
                                                                   ).filter(Jobs.id == job_id).first()

    print(input_tool, '===================')

    if input_tool == XERO:
        if function_name == 'Archieved Chart of account':
            if output_tool == QBO:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "xero_classified_archived_coa"])
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)
            if output_tool == MYOB:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "xero_archived_coa"])
                data1 = []
                for i in data:
                    data1.append(i)

                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

        if function_name == 'Chart of account':
            if output_tool == QBO:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "xero_classified_coa"])
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

            if output_tool == MYOB:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "xero_coa"])
                data1 = []
                for i in data:
                    data1.append(i)

                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

        if function_name == 'Existing Chart of account':
            if output_tool == MYOB:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "existing_coa_myob"])
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

            if output_tool == QBO:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "existing_coa"])
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

        if function_name == 'Deleted Chart Of account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_deleted_coa"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Archieved Customer':
            if output_tool == MYOB:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "xero_archived_customer"])
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

            if output_tool == QBO:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "xero_archived_customer_in_invoice"])
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

        if function_name == 'Archieved Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_archived_supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_customer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_items"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Job':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_job"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_spend_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_receive_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice CreditNote':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_creditnote"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill VendorCredit':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_vendorcredit"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice Credit Memo Refund':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_credit_memo_refund_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill Credit Memo Refund':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_supplier_credit_cash_refund"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Journal':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_manual_journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_invoice_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_bill_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

            # bill_payment = dbname["xero_bill_payment"].find(
            #     {"task_id": task_id})
            # data = []
            # for i in bill_payment:
            #     data.append(i)
            # return render_template("home/records.html", data=data)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "xero_bank_transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

    if input_tool == QBO:
        if output_tool == MYOB:
            if function_name == 'Chart of account':
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                                dbname[
                                                                                                                    "QBO_COA"])
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                       total_records=total_records, successful_count=successful_count,
                                       error_count=error_count)

        if function_name == 'Existing Chart of account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "existing_coa_myob"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Archieved Chart of account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_ARCHIVED_COA"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Archieved Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_ARCHIVED_CUSTOMER"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Archieved Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_ARCHIVED_VENDOR"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Customer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Item"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Job':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Class"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Spend_Money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Received_Money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Journal':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Bill_Payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "QBO_Bank_Transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

    if input_tool == MYOB:
        if function_name == 'Chart of account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "classified_coa"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Employee':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "employee"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "customer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "items"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Job':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "job"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "myob_spend_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "received_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "service_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "final_bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Journal':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "invoice_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "bill_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "bank_transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

    if input_tool == DELETE:
        if function_name == 'Chart of account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "chart_of_account"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "customer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "item"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Job':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "job"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "myob_spend_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "received_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "service_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "all_bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Journal':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "invoice_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bill Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "bill_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "bank_transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

    if input_tool == EXCEL and output_tool == MYOB:

        if function_name == 'COA':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_chart_of_account"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_customer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_item"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Job':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_job"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bills':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer return':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_creditnote"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier return':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_vendorcredit"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_spend_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_receive_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_bank_transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Journals':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_invoice_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_bill_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

    if input_tool == EXCEL and output_tool == RECKON:
        if function_name == 'account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_chart_of_account"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_contact"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_contact"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Employee':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_employee"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_item"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bills':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Customer payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_invoice_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Supplier Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_bill_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Journals':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_bank_transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_spend_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_receive_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

        if function_name == 'Credit Memo':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(task_id,
                                                                                                            dbname[
                                                                                                                "excel_reckon_creditnote"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page,
                                   total_records=total_records, successful_count=successful_count,
                                   error_count=error_count)

    records_data = jobs.paginate(page=page, per_page=50)
    return render_template("home/records.html", segment="records", records=records_data)


@blueprint.route("/job_execution_status/<int:job_id>")
@login_required
def Job_Execution_Status(job_id):
    job_execution_status = JobExecutionStatus.query.filter(
        JobExecutionStatus.job_id == job_id
    )
    return render_template(
        "home/job_status.html",
        segment="job_execution_status",
        data=job_execution_status,
    )


@blueprint.route("/task_execution_status/<int:job_id>")
@login_required
def Task_Execution_Status(task_id):
    task_execution_status = TaskExecutionStatus.query.filter(
        TaskExecutionStatus.task_id == task_id
    )
    return render_template(
        "home/job_status.html",
        segment="task_execution_status",
        data=task_execution_status,
    )


@blueprint.route("/delete_job_page", methods=["GET", "POST"])
@login_required
def delete_job_page():
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(Tool.tool_type == "Input", Tool.account_type == "Delete")
        # qbo_settings = QboSeCreateJobFormttings.query.all()
        output_settings = Tool.query.filter(Tool.tool_type == "Output")
        return render_template(
            "home/delete_job_page.html",
            segment="jobs",
            input_settings=input_settings,
            output_settings=output_settings,
            form=create_job_form,
        )

    if request.method == "POST":
        input_type = 'delete'

        # if account_type != EXCEL:
        if (
                request.form["output_account_id"] == "None"
        ):
            return redirect(
                url_for(
                    ".delete_job_page",
                    msg="Input account and output account are the mandatory fields!!!!.",
                    success=True,
                )
            )

        if len(request.form.getlist("mycheckbox")) == 0:
            return redirect(
                url_for(
                    ".delete_job_page",
                    msg="Please select atleast one function!!!!.",
                    success=True,

                )
            )

        # elif (request.form['myob_account'] is not None and request.form['xero_account'] == 'None') or (request.form['myob_account'] == 'None' and request.form['xero_account'] is not None):
        job = Jobs()
        fn = request.form.getlist('mycheckbox')
        job.functions = ",".join(fn)
        job.name = request.form["name"]
        job.description = request.form["description"]
        job.input_account_id = request.form["input_account_id"]
        job.output_account_id = request.form["output_account_id"]
        job.start_date = request.form["start_date"]
        job.end_date = request.form["end_date"]
        # TODO: Create job and tasks in same transaction, rollback if anything fails
        db.session.add(job)
        db.session.commit()
        # read_myob_write_qbo_task.apply_async(args=[job.id])
        for fun in range(0, len(fn)):
            task = Task()
            task.function_name = fn[fun]
            task.job_id = job.id
            db.session.add(task)
            db.session.commit()
        return redirect(
            url_for(
                ".tasks_by_job",
                job_id=job.id,
                msg="Job created successfully!!!!.",
                success=True,
            )
        )


@blueprint.route("/create_id_name_page", methods=["GET", "POST"])
@login_required
def create_id_name_page():
    create_id_name_form = CreateIdNameForm(request.form)
    if request.method == "GET":
        return render_template(
            "home/create_id_name.html",
            segment="jobs",
            form=create_id_name_form,
        )

    if request.method == "POST":
        toolId = ToolId()
        toolId.Email = request.form["name"]
        toolId.client_id = request.form["client_id"]
        toolId.client_secret = request.form["client_secret"]
        db.session.add(toolId)
        db.session.commit()
        return redirect(
            url_for(
                ".create_auth_token",
                tool_id=toolId.id,
                msg="Email created successfully!!!!.",
                success=True,
            )
        )


@blueprint.route("/Reckon_job_page", methods=["GET", "POST"])
@login_required
def Reckon_job_page():
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(Tool.tool_type == "Input", Tool.account_type == "Excel")
        # qbo_settings = QboSeCreateJobFormttings.query.all()
        output_settings = Tool.query.filter(Tool.tool_type == "Output", Tool.account_type == "Reckon")
        return render_template(
            "home/create_job.html",
            segment="jobs",
            input_settings=input_settings,
            output_settings=output_settings,
            form=create_job_form,
        )

    if request.method == "POST":
        input_type = 'Excel'

        job_id = upload_file(request)
        return redirect(
            url_for(
                ".tasks_by_job",
                job_id=job_id,
                msg="Job created successfully!!!!.",
                success=True,
            )
        )


@blueprint.route("/create_auth_code", methods=["GET", "POST"])
@login_required
def create_auth_code():
    create_auth_code_form = CreateauthcodeForm(request.form)
    if request.method == "GET":
        return render_template(
            "home/create_auth_token.html",
            segment="jobs",
            form=create_auth_code_form,
        )

    if request.method == "POST":
        toolId = ToolId()

        return redirect(
            url_for(
                ".create_auth_code",
                tool_id=toolId.id,
                msg="Email created successfully!!!!.",
                success=True,
            )
        )


@blueprint.route("/onclickauth", methods=["GET", "POST"])
@login_required
def onclickauth():
    client_id = "BDDDE967BCF943098B8A44E164AE1A74"
    client_secret = "JVCy3rDSvqkMelGOxJenpLkdiAgRgiHcXLe6GJZ79IAKXv_l"
    redirect_uri = "https://www.mmcconvert.com"
    scope = "offline_access accounting.transactions"

    CLIENT_ID = f"{client_id}"
    CLIENT_SECRET = f"{client_secret}"
    clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
    encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
    auth_code = "%s" % encoded_u

    auth_url = ('''https://login.xero.com/identity/connect/authorize?''' +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&client_secret=''' + client_secret +
                '''&redirect_uri=''' + redirect_uri +
                '''&scope=''' + scope +
                '''&state=123456''')

    webbrowser.open_new(auth_url)
    return redirect(
        url_for(
            ".create_auth_code"
        )
    )


@blueprint.route("/choice_email_page", methods=["GET", "POST"])
@login_required
def choice_email_page():
    choice_email_page_form = CreateEmailForm(request.form)
    if request.method == "GET":
        email_settings = ToolId.query.all()

        return render_template(
            "home/choice_email_name.html",
            segment="jobs",
            email_settings=email_settings,
            form=choice_email_page_form,
        )

    if request.method == "POST":
        toolId = ToolId()
        return redirect(
            url_for(
                ".create_auth_code",
                client_id=toolId.client_id,
                client_secret=toolId.client_secret,

            )
        )


# @blueprint.route("/id_select_page", methods=["GET", "POST"])
# @login_required
# def id_select_page():
#     create_idselect_form = CreateSelectidForm(request.form)
#     if request.method == "GET":

#         return render_template(
#             "home/delete_job_page.html",
#             segment="jobs",
#             form=create_idselect_form,
#         )

#     if request.method == "POST":


@blueprint.route("/jobs/create", methods=["GET", "POST"])
@login_required
def create_job():
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(Tool.tool_type == "Input", Tool.account_type != "Delete")
        # qbo_settings = QboSeCreateJobFormttings.query.all()
        output_settings = Tool.query.filter(Tool.tool_type == "Output")
        return render_template(
            "home/create_job.html",
            segment="jobs",
            input_settings=input_settings,
            output_settings=output_settings,
            form=create_job_form,
        )

    if request.method == "POST":
        input_type = Tool.query.filter(
            Tool.id == request.form["input_account_id"]
        ).first()
        account_type = input_type.account_type

        if account_type != EXCEL:
            if (request.form["input_account_id"] == "None") and (
                    request.form["output_account_id"] == "None"
            ):
                return redirect(
                    url_for(
                        ".create_job",
                        msg="Input account and output account are the mandatory fields!!!!.",
                        success=True,
                    )
                )

            if len(request.form.getlist("mycheckbox")) == 0:
                return redirect(
                    url_for(
                        ".create_job",
                        msg="Please select atleast one function!!!!.",
                        success=True,
                    )
                )

            # elif (request.form['myob_account'] is not None and request.form['xero_account'] == 'None') or (request.form['myob_account'] == 'None' and request.form['xero_account'] is not None):
            job = Jobs()
            fn = request.form.getlist('mycheckbox')
            job.functions = ",".join(fn)
            job.name = request.form["name"]
            job.description = request.form["description"]
            job.input_account_id = request.form["input_account_id"]
            job.output_account_id = request.form["output_account_id"]
            job.start_date = request.form["start_date"]
            job.end_date = request.form["end_date"]
            # TODO: Create job and tasks in same transaction, rollback if anything fails
            db.session.add(job)
            db.session.commit()
            # read_myob_write_qbo_task.apply_async(args=[job.id])
            for fun in range(0, len(fn)):
                task = Task()
                task.function_name = fn[fun]
                task.job_id = job.id
                db.session.add(task)
                db.session.commit()
            return redirect(
                url_for(
                    ".tasks_by_job",
                    job_id=job.id,
                    msg="Job created successfully!!!!.",
                    success=True,
                )
            )
        else:
            job_id = upload_file(request)
            return redirect(
                url_for(
                    ".tasks_by_job",
                    job_id=job_id,
                    msg="Job created successfully!!!!.",
                    success=True,
                )
            )


@blueprint.route("/myob_settings")
@login_required
def myob_settings():
    myob_settings = MyobSettings.query.all()
    return render_template(
        "home/myob_settings.html", segment="myob_settings", data=myob_settings
    )


@blueprint.route("/qbo_settings")
@login_required
def qbo_settings():
    settings = QboSettings.query.all()
    return render_template(
        "home/qbo_settings.html", segment="qbo_settings", data=settings
    )


@blueprint.route("/xero_settings")
@login_required
def xero_settings():
    xero_settings = XeroSettings.query.all()
    return render_template(
        "home/xero_settings.html", segment="xero_settings", data=xero_settings
    )


@blueprint.route("/tool")
@login_required
def tool():
    tool = Tool.query.all()
    return render_template("home/tool.html", segment="tool", data=tool)


@blueprint.route("/tool/create", methods=["GET", "POST"])
@login_required
def create_tool():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_tool.html",
            segment="settings",
            data=data,
            form=create_setting_form,
            MYOB_KEY=MYOB_KEY,
            QBO_KEY=QBO_KEY,
            XERO_KEY=XERO_KEY,
            MYOBLEDGER_KEY=MYOBLEDGER_KEY,
            EXCEL_KEY=EXCEL_KEY,
            DELETE_KEY=DELETE_KEY,
            RECKON_KEY=RECKON_KEY
        )
    if request.method == "POST":
        setting = Tool(**request.form)
        db.session.add(setting)
        db.session.commit()
        return redirect(
            url_for(".tool", msg="Tool created successfully!!!!.", success=True)
        )


@blueprint.route("/tool/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_tool(id):
    if request.method == "GET":
        tool = Tool.query.filter(Tool.id == id).first()
        if tool:
            return render_template("home/edit_tool.html", tool=tool)

    if request.method == "POST":
        tool = Tool.query.filter(Tool.id == request.form["id"]).first()
        tool.tool_name = request.form["tool_name"]
        tool.keys = request.form["keys"]
        tool.account_type = request.form["account_type"]
        # tool.tool_type = request.form["tool_type"]
        db.session.commit()
        return redirect(
            url_for(".tool", msg="Tool updated successfully!!!!.", success=True)
        )


@blueprint.route("/tool_settings")
@login_required
def tool_settings():
    tool_settings = ToolSettings.query.all()
    return render_template(
        "home/tool_settings.html", segment="tool_settings", data=tool_settings
    )


@blueprint.route("/tool_settings/create/<int:id>", methods=["GET", "POST"])
@login_required
def create_tool_settings(id):
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        tool = Tool.query.filter(Tool.id == id).first()
        tool_xero_type = Tool.query.filter(Tool.account_type == "Xero").first()
        tool_settings = ToolSettings.query.filter(
            ToolSettings.tool_id == id).all()
        key_list = tool.keys.split(",")
        return render_template(
            "home/create_tool_settings.html",
            zip=zip,
            len=len,
            segment="settings",
            tool=tool,
            toolsettings=tool_settings,
            data=key_list,
            tool_xero_type=tool_xero_type,
            form=create_setting_form,
        )
    if request.method == "POST":
        tool = Tool.query.filter(Tool.id == id).first()
        key_list = tool.keys.split(",")
        for i in range(0, len(key_list)):
            tool_settings = ToolSettings.query.filter(
                ToolSettings.tool_id == id, ToolSettings.keys == key_list[i].strip(
                )
            ).first()

            if tool_settings is not None:
                tool_settings.keys = key_list[i].strip()
                tool_settings.values = request.form[key_list[i]].strip()
                db.session.commit()

            else:
                setting = ToolSettings()
                setting.tool_id = id
                setting.keys = key_list[i].strip()
                setting.values = request.form[key_list[i]].strip()
                db.session.add(setting)
                db.session.commit()
        return redirect(
            url_for(
                ".tool", msg="Tool setting created successfully!!!!.", success=True)
        )


@blueprint.route("/myob_settings/create", methods=["GET", "POST"])
@login_required
def create_setting():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_myob_setting.html",
            segment="settings",
            data=data,
            form=create_setting_form,
        )
    if request.method == "POST":
        setting = MyobSettings(**request.form)
        db.session.add(setting)
        db.session.commit()
        return render_template(
            "home/myob_settings.html", msg="Setting created successfully.", success=True
        )


@blueprint.route("/myob_settings/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_myob_setting(id):
    if request.method == "GET":
        myob = MyobSettings.query.filter(MyobSettings.id == id).first()
        if myob:
            return render_template("home/edit_myob_setting.html", myob=myob)

    if request.method == "POST":
        myob = MyobSettings.query.filter(
            MyobSettings.id == request.form["id"]).first()
        myob.name = request.form["name"]
        myob.client_id = request.form["client_id"]
        myob.company_file_id = request.form["company_file_id"]
        myob.username = request.form["username"]
        myob.client_secret = request.form["client_secret"]
        myob.access_token = request.form["access_token"]
        myob.password = request.form["password"]
        myob.company_file_uri = request.form["company_file_uri"]
        myob.refresh_token = request.form["refresh_token"]
        db.session.commit()
        return redirect(
            url_for(
                ".myob_settings", msg="Setting updated successfully!!!!.", success=True
            )
        )


@blueprint.route("/qbo_settings/create", methods=["GET", "POST"])
@login_required
def create_qbo_setting():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_qbo_setting.html",
            segment="qbo_settings",
            data=data,
            form=create_setting_form,
        )

    if request.method == "POST":
        setting = QboSettings(**request.form)
        db.session.add(setting)
        db.session.commit()

        return redirect(
            url_for(
                ".qbo_settings", msg="Setting Created Successfully!!!!.", success=True
            )
        )


@blueprint.route("/qbo_settings/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_qbo_setting(id):
    if request.method == "GET":
        qbo = QboSettings.query.filter(QboSettings.id == id).first()
        if qbo:
            return render_template("home/edit_qbo_setting.html", qbo=qbo)

    if request.method == "POST":
        qbo = QboSettings.query.filter(
            QboSettings.id == request.form["id"]).first()
        qbo.name = request.form["name"]
        qbo.client_id = request.form["client_id"]
        qbo.client_secret = request.form["client_secret"]
        qbo.minor_version = request.form["minor_version"]
        qbo.username = request.form["username"]
        qbo.company_id = request.form["company_id"]
        qbo.user_agent = request.form["user_agent"]
        qbo.access_token = request.form["access_token"]
        qbo.password = request.form["password"]
        qbo.base_url = request.form["base_url"]
        qbo.refresh_token = request.form["refresh_token"]
        db.session.commit()
        return redirect(
            url_for(
                ".qbo_settings", msg="Setting updated successfully!!!!.", success=True
            )
        )


@blueprint.route("/xero_settings/create", methods=["GET", "POST"])
@login_required
def create_xero_setting():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_xero_setting.html",
            segment="xero_settings",
            data=data,
            form=create_setting_form,
        )

    if request.method == "POST":
        setting = XeroSettings(**request.form)
        db.session.add(setting)
        db.session.commit()

        return redirect(
            url_for(
                ".xero_settings", msg="Setting created successfully!!!!.", success=True
            )
        )


@blueprint.route("/xero_settings/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_xero_setting(id):
    if request.method == "GET":
        xero = XeroSettings.query.filter(XeroSettings.id == id).first()
        if xero:
            return render_template("home/edit_xero_setting.html", xero=xero)

    if request.method == "POST":
        xero = XeroSettings.query.filter(
            XeroSettings.id == request.form["id"]).first()
        xero.name = request.form["name"]
        xero.client_id = request.form["client_id"]
        xero.xero_tenant_id = request.form["xero_tenant_id"]
        xero.username = request.form["username"]
        xero.password = request.form["password"]
        xero.client_secret = request.form["client_secret"]
        xero.re_directURI = request.form["re_directURI"]
        xero.access_token = request.form["access_token"]
        xero.scopes = request.form["scopes"]
        xero.state = request.form["state"]
        xero.refresh_token = request.form["refresh_token"]
        db.session.commit()
        return redirect(
            url_for(
                ".xero_settings", msg="Setting updated successfully!!!!.", success=True
            )
        )


@blueprint.route("/myob/entity/<entity_name>")
@login_required
def myob_entity_details(entity_name):
    data_from_db = None
    columns = None
    parent_path = Path(__file__).parent
    filepath = "{}/{}.json".format(parent_path, entity_name)

    with open(filepath, "r") as f:
        data_from_db = json.load(f)

    if data_from_db is not None:
        columns = list(data_from_db[0].keys())

    return render_template(
        "home/myob-entities-data.html",
        segment="myob",
        data=data_from_db,
        columns=columns,
        entity_name=entity_name,
    )


@blueprint.route("/<template>")
@login_required
def route_template(template):
    try:
        if not template.endswith(".html"):
            template += ".html"

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template("home/page-404.html"), 404

    except:
        return render_template("home/page-500.html"), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None


@blueprint.route("/users")
@login_required
def list_users():
    users = Users.query.all()
    return render_template("home/users.html", segment="users", data=users)


@blueprint.route("/register", methods=["GET", "POST"])
@login_required
def register():
    create_account_form = CreateAccountForm(request.form)
    if create_account_form and request.method == "POST":
        email = request.form["email"]
        # Check usename exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template(
                "home/register.html",
                msg="Email is already registered",
                success=False,
                form=create_account_form,
            )

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return redirect(
            url_for(
                ".list_users", msg="User added successfully!!!!.", success=True
            )
        )
    else:
        return render_template("home/register.html", form=create_account_form, user=None)


@blueprint.route("/users/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if request.method == "GET":
        user = Users.query.filter(Users.id == user_id).first()
        create_account_form = CreateAccountForm()
        if user:
            # create_account_form.data["first_name"] = user.first_name
            # create_account_form.data["last_name"] = user.last_name
            # create_account_form.data["email"] = user.email
            return render_template("home/register.html", form=create_account_form, user=user)

    create_account_form = CreateAccountForm(request.form)
    if create_account_form and request.method == "POST":
        # Check usename exists
        user_from_db = Users.query.filter_by(
            email=request.form["email"]).first()
        user_id = user_from_db.id
        # else we can create the user
        user = Users(**request.form)
        if user_id is None:
            db.session.add(user)
            return redirect(
                url_for(
                    ".list_users", msg="User added successfully!!!!.", success=True
                )
            )
        else:
            user_from_db.first_name = user.first_name if user_from_db.first_name != user.first_name else user_from_db.first_name
            user_from_db.last_name = user.last_name if user_from_db.last_name != user.last_name else user_from_db.last_name
            user_from_db.email = user.email if user_from_db.email != user.email else user_from_db.email
            user_from_db.password = user.password if user_from_db.password != user.password else user_from_db.password
            db.session.flush()
            db.session.commit()
        return redirect(
            url_for(
                ".list_users", msg="User updated successfully!!!!.", success=True
            )
        )
    else:
        return render_template("home/register.html", form=create_account_form)


@blueprint.route("/getInputAccountType", methods=["POST"])
@login_required
def getInputAccountType():
    input_type = request.form['input_type']
    input_type = Tool.query.filter(
        Tool.id == input_type
    ).first()
    return json.dumps({'account_type': input_type.account_type})
    # return jsonify(input_type)


@blueprint.route("/getToolType", methods=["POST"])
@login_required
def getToolType():
    xero_tool = Tool.query.filter(
        Tool.account_type == "Xero"
    ).all()
    return render_template("home/create_tool_settings.html", xero_tool=xero_tool)
    # return json.dumps({'account_type': xero_tool})


@blueprint.route("/upload")
@login_required
def upload_file(request):
    basedir = os.path.abspath(os.path.dirname(__file__))
    uploaded_file = request.files['excelfile']
    job = Jobs()
    job.name = request.form["name"]
    job.description = request.form["description"]
    job.input_account_id = request.form["input_account_id"]
    job.output_account_id = request.form["output_account_id"]
    job.filename = uploaded_file.filename
    # TODO: Create job and tasks in same transaction, rollback if anything fails
    db.session.add(job)
    db.session.commit()
    filename = f'{job.id}' + '_' + secure_filename(uploaded_file.filename)
    print(get_root_path('apps'))
    if filename != "":
        # uploaded_file.save('app/files/',filename)

        uploaded_file.save(os.path.join(get_root_path('apps'), 'files/', filename))
    path = os.path.join(get_root_path('apps'), 'files/', filename)
    print(path)
    data1 = openpyxl.load_workbook(path)
    sheets = data1.sheetnames
    print(sheets)

    # fn = request.form.getlist('mycheckbox')
    # job.functions = ",".join(fn)

    for fun in range(0, len(sheets)):
        task = Task()
        task.function_name = sheets[fun]
        task.job_id = job.id
        db.session.add(task)
        db.session.commit()
    return job.id

    # save_path = "/uploads"apps/home/files
    # file_name = "abc.xlsx"
    # completeName = os.path.join(save_path, file_name)
    # file1 = open(completeName, "w")
    # file1.write("file information")
    # file1.close()
    # print("file created")
    # return send_from_directory(app.config['UPLOAD_PATH'],filename)
