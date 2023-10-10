import asyncio
import base64
import json
import webbrowser

from flask import render_template, redirect, request, url_for
from flask_login import login_required

from apps.authentication.forms import CreateJobForm, CreateauthcodeForm
from apps.home import blueprint
from apps.home.models import JobExecutionStatus, Task, TaskExecutionStatus, TaskExecutionStep, ToolId
from apps.home.models import MyobSettings
from apps.mmc_settings.all_settings import *
from apps.tasks.myob_to_qbo_task import read_myob_write_qbo_task


@blueprint.route("/startJobByID", methods=["POST"])
@login_required
def startJobByID():
    job_id = request.form['job_id']
    asyncio.run(read_myob_write_qbo_task(job_id))
    return json.dumps({'status': 'success'})


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


@blueprint.route("/create_auth_code", methods=["GET", "POST"])
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


@blueprint.route("/xero-connect", methods=["GET", "POST"])
def xero_connect():
    client_id = "BDDDE967BCF943098B8A44E164AE1A74"
    client_secret = "JVCy3rDSvqkMelGOxJenpLkdiAgRgiHcXLe6GJZ79IAKXv_l"
    redirect_uri = "http://127.0.0.1:5000/"
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
    if request.method == "GET":
        return render_template("home/connect_input_tool.html")
    if request.method == "POST":
        return redirect(
            url_for(
                ".xero_connect"
            )
        )


@blueprint.route("/xero_task_execution", methods=["GET", "POST"])
def xero_task_execution():
    if request.method == "GET":
        return render_template("home/xero_task_execution.html")
