from apps.util.log_file import log_config
import logging

import requests

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database

from apps.util.log_file import log_config
import logging


def get_qbo_invoice_for_payments(job_id, task_id):
    log_config1=log_config(job_id)
    try:

        logging.info("Started executing xero -> qbowriter -> Get All QBO Invoice")

        db1 = get_mongodb_database()
        QBO_Invoice = db1['QBO_Invoice']
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = QBO_Invoice.count_documents({"job_id": job_id})
        remaining_records = 1000
        while remaining_records >= 1000:
            payload = (
                f"select * from invoice startposition {no_of_records} maxresults 1000"
            )
            response = requests.request("POST", url, headers=get_data_header, data=payload)
            if response and response.status_code == 200:
                api_response = response.json()
                items = api_response["QueryResponse"]["Invoice"]
                if len(items) > 0:

                    items_output = []
                    for item in items:
                        item["job_id"] = job_id
                        item["task_id"] = task_id
                        item["table_name"] = 'QBO_Invoice'
                        item["error"] = None
                        item["is_pushed"] = 0
                        items_output.append(item)

                    db1['QBO_Invoice'].insert_many(items_output)
                    no_of_records = no_of_records + api_response["QueryResponse"]["maxResults"]
                    remaining_records = api_response["QueryResponse"]["maxResults"]


    except Exception as ex:
        logging.error(ex, exc_info=True)


def get_qbo_bill_for_payments(job_id, task_id):
    log_config1=log_config(job_id)
    try:

        logging.info("Started executing xero -> qbowriter -> Get All QBO Bill")

        db1 = get_mongodb_database()
        QBO_Bill = db1['QBO_Bill']
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = QBO_Bill.count_documents({"job_id": job_id})
        remaining_records = 1000
        while remaining_records >= 1000:
            payload = (
                f"select * from bill startposition {no_of_records} maxresults 1000"
            )
            response = requests.request("POST", url, headers=get_data_header, data=payload)
            if response and response.status_code == 200:
                api_response = response.json()
                items = api_response["QueryResponse"]["Bill"]
                if len(items) > 0:

                    items_output = []
                    for item in items:
                        item["job_id"] = job_id
                        item["task_id"] = task_id
                        item["table_name"] = 'QBO_Bill'
                        item["error"] = None
                        item["is_pushed"] = 0
                        items_output.append(item)

                    db1['QBO_Bill'].insert_many(items_output)
                    no_of_records = no_of_records + api_response["QueryResponse"]["maxResults"]
                    remaining_records = api_response["QueryResponse"]["maxResults"]


    except Exception as ex:
        logging.error(ex, exc_info=True)
