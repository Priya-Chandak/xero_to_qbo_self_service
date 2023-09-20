# -*- encoding: utf-8 -*-

from apps import db
from datetime import datetime


class EntityDataReadDetails(db.Model):
    __tablename__ = "entity_data_read_details"

    id = db.Column(db.Integer, primary_key=True)
    entity_name = db.Column(db.String(64), unique=True)
    last_read_count = db.Column(db.Integer)


class Jobs(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    myob_account = db.Column(db.String(255), nullable=True)
    xero_account = db.Column(db.String(255), nullable=True)
    input_account_id = db.Column(db.Integer)
    output_account_id = db.Column(db.Integer)
    qbo_account = db.Column(db.String(255))
    start_date = db.Column(db.String(255), nullable=True)
    end_date = db.Column(db.String(255), nullable=True)
    functions = db.Column(db.String(255), nullable=True)
    filename = db.Column(db.String(1024))
    is_successful = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean(), default=True)


class JobExecutionStatus(db.Model):
    __tablename__ = "job_execution_status"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer)
    start_time = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.Integer, default=3)


class JobDataCount(db.Model):
    __tablename__ = "job_data_count"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer)
    input_records = db.Column(db.Integer)
    output_records = db.Column(db.Integer)


class MyobSettings(db.Model):
    __tablename__ = "myob_settings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))
    client_id = db.Column(db.String(655))
    client_secret = db.Column(db.String(655))
    access_token = db.Column(db.String(5000))
    refresh_token = db.Column(db.String(5000))
    company_file_uri = db.Column(db.String(255))
    company_file_id = db.Column(db.String(255))
    is_active = db.Column(db.Boolean(), default=True)


class QboSettings(db.Model):
    __tablename__ = "qbo_settings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))
    company_id = db.Column(db.String(255))
    client_id = db.Column(db.String(625))
    client_secret = db.Column(db.String(625))
    user_agent = db.Column(db.String(255))
    base_url = db.Column(db.String(255))
    minor_version = db.Column(db.String(255))
    access_token = db.Column(db.String(5000))
    refresh_token = db.Column(db.String(5000))
    is_active = db.Column(db.Boolean(), default=True)


class XeroSettings(db.Model):
    __tablename__ = "xero_settings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))
    xero_tenant_id = db.Column(db.String(255))
    client_id = db.Column(db.String(625))
    client_secret = db.Column(db.String(625))
    scopes = db.Column(db.String(1000))
    re_directURI = db.Column(db.String(1000))
    state = db.Column(db.String(255))
    access_token = db.Column(db.String(5000))
    refresh_token = db.Column(db.String(2000))
    is_active = db.Column(db.Boolean(), default=True)


class Tool(db.Model):
    __tablename__ = "tool"

    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(1264))
    keys = db.Column(db.String(5255))
    account_type = db.Column(db.String(255))
    tool_type = db.Column(db.String(255))
    is_active = db.Column(db.Boolean(), default=True)


class ToolSettings(db.Model):
    __tablename__ = "tool_settings"

    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("tool.id"))
    keys = db.Column(db.Text)
    values = db.Column(db.Text)
    added_on = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    function_name = db.Column(db.String(1264))
    is_successful = db.Column(db.Integer, default=3)
    read = db.Column(db.Integer, default=3)
    write = db.Column(db.Integer, default=3)


class ToolId(db.Model):
    __tablename__="ToolId"
    id = db.Column(db.Integer, primary_key=True)
    Email =db.Column(db.String(1264))
    client_id = db.Column(db.String(625))
    client_secret = db.Column(db.String(625))

class Authdata(db.Model):
    __tablename__="Auth_data"
    id = db.Column(db.Integer, primary_key=True)
    auth_data = db.Column(db.String(1264))

class TaskExecutionStatus(db.Model):
    __tablename__ = "task_execution_status"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    created_at = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.Integer, default=2)


class TaskExecutionStep(db.Model):
    __tablename__ = "task_execution_steps"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    created_at = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.Integer, default=2)
    step = db.Column(db.String(500))
    error = db.Column(db.String(2000))
