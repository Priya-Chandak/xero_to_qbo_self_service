import traceback

import requests

from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import  write_task_execution_step,update_task_execution_status
import sys


def get_xero_bank_transfer(job_id, task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        Collection = dbname["xero_bank_transfer"]
        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/BankTransfers"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/BankTransfers?where=Date>=DateTime({y1},{m1},{d1}) AND Date<=DateTime({y2},{m2},{d2})"

        print(main_url)
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        print(response1)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["BankTransfers"]
            if len(r2) > 0:
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 1000) + 1
                print(no_of_pages)
                arr = []
                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        url = f"{base_url}/BankTransfers?page={pages}"
                    else:
                        url = f"{base_url}/BankTransfers?page={pages}&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"
                    
                    print(url)
                    response = requests.request("GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["BankTransfers"]
                    
                    for i in range(0, len(JsonResponse1)):
                        QuerySet = {"job_id": job_id, "task_id": task_id, "is_pushed": 0, "error": None,"payload": None,
                                    "table_name": "xero_bank_transfer",
                                    "FromAccountName": JsonResponse1[i]["FromBankAccount"]["Name"]}

                        if "Code" in JsonResponse1[i]["FromBankAccount"]:
                            QuerySet["FromAccountID"] = JsonResponse1[i]["FromBankAccount"][
                                "Code"
                            ]
                        QuerySet["ToAccountName"] = JsonResponse1[i]["ToBankAccount"]["Name"]
                        if "Code" in JsonResponse1[i]["ToBankAccount"]:
                            QuerySet["ToAccountID"] = JsonResponse1[i]["ToBankAccount"]["Code"]
                        QuerySet["TransferNumber"] = JsonResponse1[i]["BankTransferID"]
                        QuerySet["Date"] = JsonResponse1[i]["DateString"]
                        QuerySet["Amount"] = JsonResponse1[i]["Amount"]
                        if 'Reference' in JsonResponse1[i]:
                            QuerySet["Memo"] = JsonResponse1[i]["Reference"]

                        arr.append(QuerySet)
                        print(len(arr))
                   
                    Collection.insert_many(arr)
                    print("Added")

                
    except Exception as ex:
        import traceback
        traceback.print_exc()
        
