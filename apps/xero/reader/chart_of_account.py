import sys

import requests

from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
import logging


def get_coa(job_id, task_id):
    
    log_config1=log_config(job_id)
    try:
        logging.info('Inside GET XERO COA - Started')

        dbname = get_mongodb_database()
        xero_coa = dbname["xero_coa"]
        payload, base_url, headers = get_settings_xero(job_id)
        print(payload, base_url, headers)

        main_url = f"{base_url}/Accounts"
        print(main_url)

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        print(response1,"foa coa")
        if response1.status_code == 200:
            JsonResponse = response1.json()
            JsonResponse1 = JsonResponse["Accounts"]
            if len(JsonResponse1) > 0:
                arr = []

                for i in range(0, len(JsonResponse1)):
                    if JsonResponse1[i]["Status"] == "ACTIVE":

                        QuerySet = {"job_id": job_id, "task_id": task_id, "is_pushed": 0, "error": None,
                                    "AccountID": JsonResponse1[i]["AccountID"], "Name": JsonResponse1[i]["Name"],
                                    "payload": None, "Type": JsonResponse1[i]["Type"],
                                    "BankAccountType": JsonResponse1[i]["BankAccountType"],
                                    "TaxType": JsonResponse1[i]["TaxType"],
                                    "Status": JsonResponse1[i]["Status"], "table_name": "xero_coa"}
                        if "Code" in JsonResponse1[i]:
                            QuerySet["Code"] = JsonResponse1[i]["Code"]
                        else:
                            QuerySet["Code"] = None

                        arr.append(QuerySet)

                xero_coa.insert_many(arr)

            step_name = "Reading data from xero chart of account"
            write_task_execution_step(task_id, status=1, step=step_name)
            logging.info('Inside GET XERO COA - Completed')


    except Exception as ex:
        step_name = "Something went wrong"
        logging.error(ex, exc_info=True)

        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_archieved_coa(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        xero_coa = dbname["xero_archived_coa"]
        payload, base_url, headers = get_settings_xero(job_id)

        main_url = f"{base_url}/Accounts"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            JsonResponse = response1.json()
            JsonResponse1 = JsonResponse["Accounts"]
            if len(JsonResponse1) > 0:
                arr = []
                for i in range(0, len(JsonResponse1)):
                    if JsonResponse1[i]["Status"] == "ARCHIVED":

                        QuerySet = {"job_id": job_id, "task_id": task_id, "is_pushed": 0, "error": None,
                                    "AccountID": JsonResponse1[i]["AccountID"], "Name": JsonResponse1[i]["Name"],
                                    "payload": None, "Type": JsonResponse1[i]["Type"],
                                    "BankAccountType": JsonResponse1[i]["BankAccountType"],
                                    "TaxType": JsonResponse1[i]["TaxType"],
                                    "Status": JsonResponse1[i]["Status"], "table_name": "xero_coa"}
                        if "Code" in JsonResponse1[i]:
                            QuerySet["Code"] = JsonResponse1[i]["Code"]
                        else:
                            QuerySet["Code"] = None
                        arr.append(QuerySet)

                if len(arr)>0:
                    xero_coa.insert_many(arr)
                    step_name = "Reading xero archived coa successfully"
                    write_task_execution_step(task_id, status=1, step=step_name)
                else:
                    step_name = "No Data Available"
                    write_task_execution_step(task_id, status=1, step=step_name)

            else:
                step_name = "No Data Available"
                write_task_execution_step(task_id, status=1, step=step_name)

        else:
            step_name = "Access Token Expired"
            write_task_execution_step(task_id, status=0, step=step_name)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
