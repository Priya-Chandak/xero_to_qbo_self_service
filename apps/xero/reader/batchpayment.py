import traceback

import requests

from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
import logging

def get_xero_invoice_batchpayment(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_invoice_batchpayment = dbname["xero_invoice_batchpayment"]
        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/BatchPayments"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/BatchPayments?where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["BatchPayments"]
            if len(r2) > 0:
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                invoice_batchpayment = []

                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        main_url = f"{base_url}/BatchPayments?page={pages}"
                    else:
                        y1 = int(start_date[0:4])
                        m1 = int(start_date[5:7])
                        d1 = int(start_date[8:])
                        y2 = int(end_date[0:4])
                        m2 = int(end_date[5:7])
                        d2 = int(end_date[8:])
                        main_url = f"{base_url}/BatchPayments?page={pages}&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

                    response = requests.request("GET", main_url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["BatchPayments"]

                    for i in range(0, len(JsonResponse1)):
                        JsonResponse1["job_id"]: job_id
                        JsonResponse1["task_id"]: task_id
                        JsonResponse1["is_pushed"]: 0
                        JsonResponse1["table_name"]: "xero_invoice_batchpayment"
                        if JsonResponse1[i]["Type"] == "RECBATCH":
                            invoice_batchpayment.append(JsonResponse1[i])

                    if len(invoice_batchpayment) > 0:
                        xero_invoice_batchpayment.insert_many(invoice_batchpayment)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        traceback.print_exc()


def get_xero_bill_batchpayment(job_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_bill_batchpayment = dbname["xero_bill_batchpayment"]
        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/BatchPayments"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/BatchPayments?where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["BatchPayments"]
            if len(r2) > 0:
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                bill_batchpayment = []

                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        main_url = f"{base_url}/BatchPayments?page={pages}"
                    else:
                        y1 = int(start_date[0:4])
                        m1 = int(start_date[5:7])
                        d1 = int(start_date[8:])
                        y2 = int(end_date[0:4])
                        m2 = int(end_date[5:7])
                        d2 = int(end_date[8:])
                        main_url = f"{base_url}/BatchPayments?page={pages}&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

                    response = requests.request("GET", main_url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["BatchPayments"]

                    for i in range(0, len(JsonResponse1)):
                        if JsonResponse1[i]["Type"] == "PAYBATCH":
                            bill_batchpayment.append(JsonResponse1[i])

                    if len(bill_batchpayment) > 0:
                        xero_bill_batchpayment.insert_many(bill_batchpayment)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        traceback.print_exc()
