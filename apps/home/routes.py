import asyncio
import base64
import json
import webbrowser
import requests
import random
import string
from redis import StrictRedis
from apps.util.db_mongo import get_mongodb_database
from apps.myconstant import *
from apps.util.qbo_util import get_pagination_for_records
from flask import Flask
import urllib.parse
import boto3
import pdfkit


from flask import Flask, render_template, current_app, redirect, request, url_for, session, g, flash, jsonify, Response, make_response
from flask_login import login_required

from apps.authentication.forms import CreateJobForm, CreateauthcodeForm, CreateCustomerInfoForm
from apps.home import blueprint
from apps.home.models import JobExecutionStatus, Task, TaskExecutionStatus, TaskExecutionStep, ToolId, CustomerInfo, XeroQboTokens
from apps.home.models import MyobSettings
from apps.mmc_settings.all_settings import *
from apps.tasks.myob_to_qbo_task import read_myob_write_qbo_task, report_generation_task
redis = StrictRedis(host='localhost', port=6379, decode_responses=True)


@blueprint.route("/connect_output_tool")
def connect_output_tool():

    return render_template(
        "home/connect_output_tool.html"
    )


@blueprint.route("/conversion_underway")
def conversion_underway():
    job_id = redis.get('my_key')
    return render_template(
        "home/conversion_underway.html",
        job_id=job_id

    )


@blueprint.route("/startJobByID", methods=["POST"])
def startJobByID():
    print("isnide startjob by id")
    mail_send = sent_email_to_customer()
    print(mail_send)
    # final_report = final_report_email_to_customer()
    # print(final_report)
    # pdf_create=generate_pdf()
    # print(pdf_create,"created pdf file ")

    job_id = redis.get('my_key')
    print(job_id, "start job by id")
    # job_id = 1
    asyncio.run(read_myob_write_qbo_task(job_id))
    return render_template("home/conversion_underway.html")


@blueprint.route("/startReportGenerationByID", methods=["POST"])
def startReportGenerationByID():
    job_id = redis.get('my_key')
    print(job_id, "start job by id")
    # job_id = 1
    asyncio.run(report_generation_task(job_id))
    return "click report generation button"


@blueprint.route("/task_execution_details/<int:task_id>")
@login_required
def task_execution_details(task_id):
    task_steps = TaskExecutionStep.query.filter(
        TaskExecutionStep.task_id == task_id
    ).all()
    return render_template("home/task_execution_details.html", segment="task_steps", data=task_steps)


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


# @blueprint.route("/create_auth_code", methods=["GET", "POST"])
# def create_auth_code():
#     create_auth_code_form = CreateauthcodeForm(request.form)
#     if request.method == "GET":
#         return render_template(
#             "home/create_auth_token.html",
#             segment="jobs",
#             form=create_auth_code_form,
#         )

#     if request.method == "POST":
#         toolId = ToolId()

#         return redirect(
#             url_for(
#                 ".create_auth_code",
#                 tool_id=toolId.id,
#                 msg="Email created successfully!!!!.",
#                 success=True,
#             )
#         )


@blueprint.route("/xero-connect", methods=["GET", "POST"])
def xero_connect():

    client_id = XERO_CI
    client_secret = XERO_CS
    redirect_uri = XERO_REDIRECT
    # scope = "email%20profile%20openid%20accounting.reports.read%20payroll.employees%20payroll.employees.read%20accounting.settings%20accounting.transactions%20accounting.transactions.read%20accounting.contacts%20offline_access"
    scope = XERO_SCOPE
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
    print(auth_url)

    return redirect(auth_url)

    # return render_template('home/redirect_auth_url.html', auth_url1=auth_url)
    # return redirect(
    #             url_for(
    #                 ".redirect_auth_url",
    #                auth_url1=auth_url
    #             )
    #         )


@blueprint.route("/redirect_auth_url")
def redirect_auth_url():
    return render_template(
        "home/redirect_auth_url.html"
    )


@blueprint.route("/jobs/create", methods=["GET", "POST"])
@login_required
def create_job():
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(
            Tool.tool_type == "Input", Tool.account_type != "Delete")
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


@blueprint.route("/myob_settings")
@login_required
def myob_settings():
    myob_settings = MyobSettings.query.all()
    return render_template(
        "home/myob_settings.html", segment="myob_settings", data=myob_settings
    )


@blueprint.route("/connect_input_tool", methods=["GET", "POST"])
def connect_input_tool():
    create_customer_info_form = CreateCustomerInfoForm(request.form)
    if request.method == "GET":

        return render_template("home/connect_input_tool.html",
                               form=create_customer_info_form
                               )
    if request.method == "POST":
        # job_functions=['Customer','Supplier']
        job = Jobs()

        job_functions = ['Existing Chart of account', 'Chart of account', 'Customer', 'Supplier', 'Item', 'Job',
                         'Journal', 'Spend Money', 'Receive Money', 'Bank Transfer', 'Bill', 'Invoice', 'Payrun', 'Depreciation', 'AR-AP','Report']
        job.functions = "Existing Chart of account,Chart of account,Customer,Supplier,Item,Job,Journal,Spend Money,Receive Money,Bank Transfer,Bill,Invoice,Payrun,Depreciation,AR-AP,Report"

        # job_functions=['Item','Supplier']
        # job.functions = "Item,Supplier"
        length = 10
        job.name = ''.join(random.choice(
            string.ascii_letters + string.digits) for _ in range(length))
        print(job.name)
        job.description = ""
        job.input_account_id = 1
        job.output_account_id = 2
        job.start_date = ""
        job.end_date = ""
        db.session.add(job)
        db.session.commit()

        key_to_clear = 'my_key'
        redis.delete(key_to_clear)

        redis.set('my_key', job.id)
        print(redis.get('my_key'), "request data same function ")

        for fun in range(0, len(job_functions)):
            print('inside for loop', job.id)
            task = Task()
            task.function_name = job_functions[fun]
            task.job_id = job.id
            db.session.add(task)
            db.session.commit()
        # session.permanent = True
        # session['job_id_data']=job.id

        # print("---------session data print--------")
        # print(session['job_id_data'])

        customer_info = CustomerInfo()
        customer_info.job_id = job.id
        customer_info.Company = request.form["inputCompany"]
        customer_info.Email = request.form["inputEmail"]
        customer_info.First_Name = request.form["inputFirstName"]
        customer_info.Last_Name = request.form["inputLastName"]
        customer_info.start_date = request.form["start_date"]
        customer_info.end_date = request.form["end_date"]
        db.session.add(customer_info)
        db.session.commit()

        return redirect(
            url_for(
                ".xero_connect"


            )
        )


@blueprint.route("/xero_task_execution", methods=["GET", "POST"])
def xero_task_execution():
    if request.method == "GET":
        return render_template("home/xero_task_execution.html")


@blueprint.route("/create_auth_code", methods=["GET"])
def create_auth_code():
    client_id = XERO_CI
    client_secret = XERO_CS
    CLIENT_ID = f"{client_id}"
    CLIENT_SECRET = f"{client_secret}"
    clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
    encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
    auth_code = "%s" % encoded_u
    redirect_uri = XERO_REDIRECT
    auth_code1 = request.args.get("code")
    print(auth_code1)

    exchange_code_url = "https://identity.xero.com/connect/token"
    response = requests.post(exchange_code_url,
                             headers={'Authorization': "Basic" "  " + f'{auth_code}',
                                      'Content-Type': 'application/x-www-form-urlencoded'
                                      },
                             data={
                                 'grant_type': 'authorization_code',
                                 'code': f"{auth_code1}",
                                 'redirect_uri': f"{redirect_uri}"
                             })
    json_response = response.json()
    print(json_response)
    token_data = XeroQboTokens()

    print("inside xero auth code")
    print(redis.get('my_key'), "create auth routes")

    # print(session['job_id_data'])
    # print(session.get('job_id_data'))
    # if 'job_id_data' in session:
    #     print("inside session in auth code")

    token_data.job_id = redis.get('my_key')
    token_data.xero_access_token = response.json().get("access_token")
    token_data.xero_refresh_token = response.json().get("refresh_token")
    db.session.add(token_data)
    db.session.commit()

    abc = get_xerocompany_data()

    if abc == False:
        flash('Please enter a valid file name and select correct organisation', 'error')
        return redirect(
            url_for(
                ".connect_input_tool"
            )
        )
    else:
        return redirect("/connect_to_quickbooks")
    
@blueprint.route("/qbo_auth", methods=["GET", "POST"])
def qbo_auth():

    # CLIENT_ID = 'ABAngR99FX2swGqJy3xeHfeRfVtSJjHqlowjadjeGIg4W0mIdz'
    # CLIENT_SECRET = 'EC2abKy1uhHQcEpIDZy7EerH8i8hKl9gJ1ARGILE'

    # CLIENT_ID = 'ABpWOUWtcEG1gCun5dQbQNfc7dvyalw5qVF97AkJQcn5Lh09o6'
    # CLIENT_SECRET = 'LepyjXTADW592Dq5RYUP8UbGLcH5xtqDQhrf2xJN'

    # qtfy id client id and client secret

    CLIENT_ID = QBO_CI
    CLIENT_SECRET = QBO_CS

    # REDIRECT_URI = 'http://localhost:5000/data_access'

    REDIRECT_URI = QBO_REDIRECT

    # auth_url=f"https://accounts.intuit.com/app/sign-in?redirect_uri={REDIRECT_URI}&app_group=QBO&asset_alias=Intuit.accounting.core.qbowebapp&app_environment=prod"

    AUTHORIZATION_ENDPOINT = 'https://appcenter.intuit.com/connect/oauth2'
    TOKEN_ENDPOINT = 'https://oauth.platform.intuit.com/oauth2/v1/tokens'

    auth_url = f'{AUTHORIZATION_ENDPOINT}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=com.intuit.quickbooks.accounting&state=12345'
    # auth_url = f'{AUTHORIZATION_ENDPOINT}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=com.intuit.quickbooks.accounting&state={random_key}'

    print(auth_url, "print auth url ")
    webbrowser.open_new(auth_url)
    return redirect(auth_url, code=302)

    # url= urllib.parse.urlencode(auth_url)
    # print(url,"print auth url")
    # get_xerocompany_data()
    # window.location.replace(auth_url,"_self")
    # webbrowser.open_new(auth_url)
    # print(auth_url)

    # return redirect(url)

# @blueprint.route("/xerocompany_data", methods=["GET", "POST"])


def get_xerocompany_data():

    xero_company_name = CustomerInfo.query.filter(
        CustomerInfo.job_id == redis.get('my_key')).first()
    xero_access_token = XeroQboTokens.query.filter(
        XeroQboTokens.job_id == redis.get('my_key')).first()

    print(xero_company_name.Company, "print data company name ")

    print(xero_access_token.xero_access_token, "print data access token ")

    url = "https://api.xero.com/connections"
    payload = {}
    headers = {
        'Authorization': f'Bearer {xero_access_token.xero_access_token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    json_response = response.json()

    if response.status_code == 200:
        json_response = response.json()
        for entry in json_response:
            if entry["tenantName"].lower() == xero_company_name.Company.lower():
                print("inside true condition")
                token_data = XeroQboTokens.query.filter_by(
                    job_id=redis.get('my_key')).first()
                token_data.xero_company_id = entry["tenantId"]
                db.session.commit()
                return True
        return False
    else:
        return False

    # for i in range(0,len(json_response)):
    #     print(xero_company_name.Company,"inside")
    #     print(json_response[i]["tenantName"],"inside tennat name data")
    #     if json_response[i]["tenantName"] == xero_company_name.Company:
    #         print("inside tenant name data")
    #         token_data = XeroQboTokens.query.filter_by(job_id=redis.get('my_key')).first()
    #         print(token_data)
    #         token_data.xero_company_id=json_response[i]["tenantId"]
    #         db.session.commit()
    #         return True
    #     else:

    #         print("you enter file name and you get allow access file is different")
    #         return False


@blueprint.route("/data_access", methods=["GET", "POST"])
def data_access():

    token_endpoint = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

    # client_id = "ABAngR99FX2swGqJy3xeHfeRfVtSJjHqlowjadjeGIg4W0mIdz"
    # client_secret = "EC2abKy1uhHQcEpIDZy7EerH8i8hKl9gJ1ARGILE"
    CLIENT_ID1 = QBO_CI
    CLIENT_SECRET1 = QBO_CS
    # CLIENT_ID = 'ABpWOUWtcEG1gCun5dQbQNfc7dvyalw5qVF97AkJQcn5Lh09o6'
    # CLIENT_SECRET = 'LepyjXTADW592Dq5RYUP8UbGLcH5xtqDQhrf2xJN'
    redirect_uri = QBO_REDIRECT
    CLIENT_ID = f"{CLIENT_ID1}"
    CLIENT_SECRET = f"{CLIENT_SECRET1}"
    clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
    encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
    auth_code = "%s" % encoded_u
    authorization_code = request.args.get("code")
    realme_id = request.args.get("realmId")
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        'Authorization': "Basic" "  " + f'{auth_code}',
    }

    response = requests.post(token_endpoint, data=data, headers=headers)
    print(response.json())

    token_data = XeroQboTokens.query.filter_by(
        job_id=redis.get('my_key')).first()
    print(token_data)
    token_data.qbo_access_token = response.json().get("access_token")
    token_data.qbo_refresh_token = response.json().get("refresh_token")
    token_data.qbo_company_id = realme_id
    db.session.commit()

    if response.status_code == 200:

        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
        print(f"Access Token: {access_token}")
        print(f"refresh Token: {refresh_token}")
    else:
        print("Token failed data")

    return redirect(
        url_for(
            ".start_conversion"
        )
    )


@blueprint.route("/conversion_report/<int:job_id>")
def conversion_report(job_id):
    dbname = get_mongodb_database()
    job_id = redis.get('my_key')
    print(job_id, type(job_id))
    function_name = ["Chart of Account", "Supplier", "Customer", "Item", "Spend Money",
                     "Receive Money", "Bank Transfer", "Journal", "Invoice", "Bill", "Invoice Payment", "Bill Payment"]
    table_name = [dbname['xero_classified_coa'], dbname['xero_supplier'], dbname['xero_customer'], dbname['xero_items'], dbname['xero_spend_money'], dbname['xero_receive_money'],
                  dbname['xero_bank_transfer'], dbname['xero_manual_journal'], dbname['xero_invoice'], dbname['xero_bill'], dbname['xero_invoice_payment'], dbname['xero_bill_payment']]

    condition1 = {"job_id": f"{job_id}"}
    print(condition1)
    condition2 = {"job_id": f"{job_id}", "is_pushed": 1}
    condition3 = {"job_id": f"{job_id}", "is_pushed": 0}

    all_data = []
    pushed_data = []
    unpushed_data = []
    s1 = []
    f1 = []
    for k in range(0, len(table_name)):
        print(k)

        all_data1 = table_name[k].count_documents(condition1)
        pushed_data1 = table_name[k].count_documents(condition2)
        unpushed_data1 = table_name[k].count_documents(condition3)
        all_data.append(all_data1)
        pushed_data.append(pushed_data1)
        unpushed_data.append(unpushed_data1)
        if all_data1 != 0:
            success = pushed_data1/all_data1*100
            fail = unpushed_data1/all_data1*100
            s1.append(success)
            f1.append(fail)

        else:
            success = 0
            fail = 0
            s1.append(success)
            f1.append(fail)

        if all_data1 == 0:
            all_data1 = 100
    # return jsonify(all_data,function_name);
    return render_template("home/conversion_report.html", function_name=function_name, data1=all_data, data2=pushed_data, data3=unpushed_data, success=s1, fail=f1, job_id=job_id)


@blueprint.route("/conversion_report_data/<int:job_id>")
def conversion_report_data(job_id):
    dbname = get_mongodb_database()

    job_id = redis.get('my_key')
    # print(job_id,type(job_id))

    function_name = ["Existing COA", "Chart of Account", "Supplier", "Customer", "Item", "Spend Money",
                     "Receive Money", "Bank Transfer", "Journal", "Invoice", "Bill", "Invoice Payment", "Bill Payment"]
    table_name = [dbname['existing_coa'], dbname['xero_classified_coa'], dbname['xero_supplier'], dbname['xero_customer'], dbname['xero_items'], dbname['xero_spend_money'], dbname['xero_receive_money'],
                  dbname['xero_bank_transfer'], dbname['xero_manual_journal'], dbname['xero_invoice'], dbname['xero_bill'], dbname['xero_invoice_payment'], dbname['xero_bill_payment']]

    condition1 = {"job_id": f"{job_id}"}
    # print(condition1)
    condition2 = {"job_id": f"{job_id}", "is_pushed": 1}
    condition3 = {"job_id": f"{job_id}", "is_pushed": 0}

    company_info = CustomerInfo.query.filter(
        CustomerInfo.job_id == redis.get('my_key')).first()
    print(company_info, "print company_info data")

    all_data = []
    pushed_data = []
    unpushed_data = []
    s1 = []
    f1 = []
    for k in range(0, len(table_name)):
        # print(k)

        all_data1 = table_name[k].count_documents(condition1)
        pushed_data1 = table_name[k].count_documents(condition2)
        unpushed_data1 = table_name[k].count_documents(condition3)
        all_data.append(all_data1)
        pushed_data.append(pushed_data1)
        unpushed_data.append(unpushed_data1)
        if all_data1 != 0:
            success = pushed_data1/all_data1*100
            fail = unpushed_data1/all_data1*100
            s1.append(success)
            f1.append(fail)

        else:
            success = 0
            fail = 0
            s1.append(success)
            f1.append(fail)

        if all_data1 == 0:
            all_data1 = 100

    data_list = []

    # print(function_name)
    # print(s1)
    # print(f1)

    for i in range(len(function_name)):
        item_dict = {
            "company_name": company_info.Company,
            "customer_email": company_info.Email,
            "start_date": company_info.start_date,
            "end_date": company_info.end_date, }

        item_dict['function_name'] = function_name[i]
        item_dict['values'] = s1[i]

        data_list.append(item_dict)

    return jsonify({'data': data_list})


@blueprint.route("/start_conversion", methods=["GET", "POST"])
def start_conversion():

    if request.method == "GET":
        return render_template("home/start_conversion.html")


@blueprint.route("/Xero_file_error")
def Xero_file_error():

    return render_template(
        "home/Xero_file_error.html"
    )


@blueprint.route("/records/<int:task_id>/<function_name>")
def records(task_id, function_name):
    dbname = get_mongodb_database()
    page = request.args.get('page', 1, type=int)
    input_tool = 1

    if input_tool == 1:
        if function_name == 'AR-AP':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["AR"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Archieved Chart of account':

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_classified_archived_coa"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Chart of account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_classified_coa"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Existing Chart of account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["existing_coa"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Deleted Chart Of Account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_deleted_coa"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Archieved Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_archived_customer_in_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Archieved Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_archived_supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_customer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_supplier"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_items"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Job':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_job"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_spend_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_receive_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice CreditNote':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_creditnote"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill VendorCredit':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_vendorcredit"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice Credit Memo Refund':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_credit_memo_refund_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill Credit Memo Refund':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_supplier_credit_cash_refund"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Journal':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_manual_journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_invoice_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_bill_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["xero_bank_transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

# @blueprint.route("/connect_to_qbo")
# def connect_to_qbo():

#     node_app_url=NODE_APP_URL

#     response=requests.get(node_app_url)

#     return Response(response.content, content_type=response.headers['content-type'])

# #@blueprint.route('/connect_to_quickbooks', defaults={'path': ''})
# @blueprint.route('/connect_to_quickbooks')
# def connect_to_quickbooks():
#     # Define the URL of the Node.js app, including the port number
#     node_app_url = f'http://localhost:6000/connect_to_quickbooks'

#     # Make a request to the Node.js app
#     response = requests.get(node_app_url)

#     # Return the response from the Node.js app to the client
#     return Response(response.content, content_type=response.headers['content-type'])


# @blueprint.route("/callback")
# def callback():

#     node_app_url = f'http://localhost:6000/callback'

#     # Make a request to the Node.js app
#     response = requests.get(node_app_url)

#     # Return the response from the Node.js app to the client
#     return Response(response.content, content_type=response.headers['content-type'])

# @blueprint.route("/connected")
# def connected():

#     node_app_url=NODE_APP_URL+'/connected'

#     response=requests.get(node_app_url)

#     return Response(response.content, content_type=response.headers['content-type'])


# @blueprint.route("/api_call")
# def api_call():

#     node_app_url=NODE_APP_URL+'/api_call'

#     response=requests.get(node_app_url)

#     return Response(response.content, content_type=response.headers['content-type'])

@blueprint.route("/customerinfo_email", methods=["GET", "POST"])
def get_customerinfo_email():

    customer_info_data = CustomerInfo.query.filter(
        CustomerInfo.job_id == redis.get('my_key')).first()

    print(customer_info_data.Email, "customer info email")
    customer_email = customer_info_data.Email

    return customer_email


@blueprint.route("/sent_email_to_customer", methods=["GET", "POST"])
def sent_email_to_customer():
    # Specify your AWS access key and secret key directly
    aws_access_key_id = aws_access_key_id1
    aws_secret_access_key = aws_secret_access_key1
    region_name = region_name1
    # Initialize Boto3 SQS client with the credentials
    sqs = boto3.client('sqs', region_name=region_name, aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)
    ses = boto3.client('ses', region_name=region_name, aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)
    queue_url = Queue_URI

    customer_info_data = CustomerInfo.query.filter(
        CustomerInfo.job_id == redis.get('my_key')).first()

    file_name = customer_info_data.Company
    first_name = customer_info_data.First_Name
    start_date = customer_info_data.start_date
    end_date = customer_info_data.end_date

    subject = f"Check Status of {file_name} from {start_date} to {end_date}"
    conversion_report_link = f"https://mmc.vishleshak.io/conversion_report/{redis.get('my_key')}"
    html_body = f"<html><body><p>Dear {first_name},</p><p>I hope this email finds you well. I wanted to provide you with an update on the status of the file named <strong>{file_name}</strong> that you are associated with. To view the progress and details, please click on the following link:</p><p><a href=\"{conversion_report_link}\">Check Status</a></p>    <p>This link will redirect you to a page where you can check the status of <strong>{file_name}</strong> between the specified start date of <strong>{start_date}</strong> and the end date of <strong>{end_date}</strong>.</p><p>Thank you</p><p>Best regards,<br>Ankit Mehta<br></body></html>"
    recipient = get_customerinfo_email()

    response = ses.send_email(
        Source='ankit@mmcconvert.com',
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': html_body}
            }
        }
    )

    sqs.send_message(QueueUrl=queue_url, MessageBody=subject)

    return response


@blueprint.route("/create_final_report", methods=["GET", "POST"])
def create_final_report():
    cust_data = []
    supp_data = []
    if request.method == "GET":
        dbname = get_mongodb_database()

        cust_data1 = dbname["xero_report_customer"].count_documents(
            {"job_id": redis.get('my_key')})

        supp_data1 = dbname["xero_report_customer"].count_documents(
            {"job_id": redis.get('my_key')})

        cust_data.append(cust_data1)
        supp_data.append(supp_data1)

        return render_template("home/final_conversion_report.html", cust_data=cust_data, supp_data=supp_data)


# @blueprint.route("/generate_pdf", methods=["GET", "POST"])
# def generate_pdf():
#     rendered_template = render_template('create_final_report.html')

#     pdf = pdfkit.from_string(rendered_template, False)

#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = 'inline; filename=output.pdf'

#     return response


@blueprint.route("/final_report_email_to_customer", methods=["GET", "POST"])
def final_report_email_to_customer():
    cust_data = []
    supp_data = []
    aws_access_key_id = aws_access_key_id1
    aws_secret_access_key = aws_secret_access_key1
    region_name = region_name1
    sqs = boto3.client('sqs', region_name=region_name, aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)
    ses = boto3.client('ses', region_name=region_name, aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)
    queue_url = Queue_URI

    customer_info_data = CustomerInfo.query.filter(
        CustomerInfo.job_id == redis.get('my_key')).first()

    file_name = customer_info_data.Company

    subject = f"Check Status of Final Report  {file_name}"

    dbname = get_mongodb_database()

    cust_data1 = dbname["xero_report_customer"].count_documents(
        {"job_id": redis.get('my_key')})

    supp_data1 = dbname["xero_report_customer"].count_documents(
        {"job_id": redis.get('my_key')})

    cust_data.append(cust_data1)
    supp_data.append(supp_data1)

   
    create_final_report_response = render_template("home/final_conversion_report.html", cust_data=cust_data, supp_data=supp_data)


    if isinstance(create_final_report_response, Response):
        
        create_final_report_content = create_final_report_response.data.decode('utf-8')
    else:
        create_final_report_content = str(create_final_report_response)

    recipient = get_customerinfo_email()

    response = ses.send_email(
        Source='ankit@mmcconvert.com',
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': create_final_report_content}
            }
        }
    )

    sqs.send_message(QueueUrl=queue_url, MessageBody=subject)

    return response
