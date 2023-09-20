from sqlalchemy.orm import aliased

from apps import db
from apps.home.models import Jobs, Tool
from apps.mmc_settings.get_myob import get_myob_settings
from apps.mmc_settings.get_myob_ledger import get_myobledger_settings
from apps.mmc_settings.get_qbo import get_qbo_settings
from apps.mmc_settings.get_xero import get_xero_settings
from apps.mmc_settings.post_myob import post_myob_settings
from apps.mmc_settings.post_myob_ledger import post_myobledger_settings
from apps.mmc_settings.post_qbo import post_qbo_settings
from apps.mmc_settings.post_xero import post_xero_settings
from apps.mmc_settings.get_reckon import get_reckon_settings
from apps.mmc_settings.post_reckon import post_reckon_settings
from apps.myconstant import *


def get_settings_qbo(job_id):
    """get_settings_qbo is for QBO Account (Any-Input or Output)"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)
    
    # jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label('input_tool'),output_data.account_type.label('output_tool')).join(input_data, Jobs.input_account_id == input_data.id).join(output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()
    jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label('input_tool'),
                                                    output_data.account_type.label('output_tool')
                                                    ).join(input_data, Jobs.input_account_id == input_data.id
                                                        ).join(output_data, Jobs.output_account_id == output_data.id
                                                                ).filter(Jobs.id == job_id).first()
    
 

    if (input_tool==QBO):
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_qbo_settings(job_id)
        return base_url, headers, company_id, minorversion, get_data_header,report_headers
       
    elif (output_tool==QBO):
        base_url, headers, company_id, minorversion, get_data_header,report_headers = post_qbo_settings(job_id)
        return base_url, headers, company_id, minorversion, get_data_header,report_headers


def get_settings_myob(job_id):
    """get_settings_myob is for Rest of the Accounts (MYOB,MYOBLEDGER,XERO) (Any-Input or Output)"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)

    jobs, input_tool, output_tool = db.session.query(
        Jobs,
        input_data.account_type.label("input_tool"),
        output_data.account_type.label("output_tool")).join(input_data, Jobs.input_account_id == input_data.id).join(
        output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()

    if input_tool == MYOB:
        payload, base_url, headers = get_myob_settings(job_id)
        return payload, base_url, headers
    elif output_tool == MYOB:
        payload, base_url, headers = post_myob_settings(job_id)
        return payload, base_url, headers

    if input_tool == MYOBLEDGER:
        payload, base_url, headers = get_myobledger_settings(job_id)
        return payload, base_url, headers

    elif output_tool == MYOBLEDGER:
        payload, base_url, headers = post_myobledger_settings(job_id)
        return payload, base_url, headers


def get_settings_myobledger(job_id):
    """get_settings_myob is for Rest of the Accounts (MYOB,MYOBLEDGER,XERO) (Any-Input or Output)"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)

    # jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label('input_tool'),output_data.account_type.label('output_tool')).join(input_data, Jobs.input_account_id == input_data.id).join(output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()
    jobs, input_tool, output_tool = (
        db.session.query(
            Jobs,
            input_data.account_type.label("input_tool"),
            output_data.account_type.label("output_tool"),
        )
            .join(input_data, Jobs.input_account_id == input_data.id)
            .join(output_data, Jobs.output_account_id == output_data.id)
            .filter(Jobs.id == job_id)
            .first()
    )

    if input_tool == MYOBLEDGER:
        payload, base_url, headers = get_myobledger_settings(job_id)
        return payload, base_url, headers

    elif output_tool == MYOBLEDGER:
        payload, base_url, headers = post_myobledger_settings(job_id)
        return payload, base_url, headers


def get_settings_xero(job_id):
    """get_settings_myob is for Rest of the Accounts (MYOB,MYOBLEDGER,XERO) (Any-Input or Output)"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)

    jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label("input_tool"),
                                                     output_data.account_type.label("output_tool"), ).join(input_data,
                                                                                                           Jobs.input_account_id == input_data.id).join(
        output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()

    if input_tool == XERO:
        payload, base_url, headers = get_xero_settings(job_id)
        return payload, base_url, headers

    elif output_tool == XERO:
        payload, base_url, headers = post_xero_settings(job_id)
        return payload, base_url, headers


def get_settings_reckon(job_id):
    """get_settings reckon"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)

    jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label("input_tool"),
                                                     output_data.account_type.label("output_tool"), ).join(input_data,
                                                                                                           Jobs.input_account_id == input_data.id).join(
        output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()

    if input_tool == RECKON:
        payload, base_url, headers,book,post_headers,get_headers = get_reckon_settings(job_id)
        return payload, base_url, headers,book,post_headers,get_headers

    if output_tool == RECKON:
        payload, base_url, headers,book,post_headers,get_headers = post_reckon_settings(job_id)
        return payload, base_url, headers,book,post_headers,get_headers
