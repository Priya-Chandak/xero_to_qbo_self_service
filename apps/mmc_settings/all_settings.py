from sqlalchemy.orm import aliased

from apps import db
from apps.home.models import Jobs, Tool
from apps.mmc_settings.get_qbo import get_qbo_settings
from apps.mmc_settings.get_xero import get_xero_settings
from apps.mmc_settings.post_qbo import post_qbo_settings
from apps.mmc_settings.post_xero import post_xero_settings
from apps.myconstant import *


def get_settings_qbo(job_id):
    """get_settings_qbo is for QBO account (Any-Input or Output)"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)

    # jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label('input_tool'),output_data.account_type.label('output_tool')).join(input_data, Jobs.input_account_id == input_data.id).join(output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()
    jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label('input_tool'),
                                                     output_data.account_type.label('output_tool')
                                                     ).join(input_data, Jobs.input_account_id == input_data.id
                                                            ).join(output_data, Jobs.output_account_id == output_data.id
                                                                   ).filter(Jobs.id == job_id).first()

    if (input_tool == QBO):
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_qbo_settings(job_id)
        return base_url, headers, company_id, minorversion, get_data_header, report_headers

    elif (output_tool == QBO):
        base_url, headers, company_id, minorversion, get_data_header, report_headers = post_qbo_settings(job_id)
        return base_url, headers, company_id, minorversion, get_data_header, report_headers


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
