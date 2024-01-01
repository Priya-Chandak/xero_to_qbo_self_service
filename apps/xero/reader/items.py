import sys

import requests

from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
import logging

def get_items(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        dbname = get_mongodb_database()
        Collection = dbname["xero_items"]
        payload, base_url, headers = get_settings_xero(job_id)

        main_url = f"{base_url}/Items"
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["Items"]
            if len(r2) > 0:
                no_of_records = len(r2)
                # no_of_pages = (no_of_records // 100)+1
                no_of_pages = 1
                arr = []
                for pages in range(1, no_of_pages + 1):
                    url = f"{base_url}/Items?page={pages}"
                    response = requests.request("GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["Items"]

                    for i in range(0, len(JsonResponse1)):
                        QuerySet = {"SalesDetails": [], "PurchaseDetails": []}
                        QuerySet["job_id"] = job_id
                        QuerySet["table_name"] = "xero_items"
                        QuerySet["task_id"] = task_id
                        QuerySet["error"] = None
                        QuerySet["payload"] = None

                        QuerySet["is_pushed"] = 0

                        PurchaseDetails = {}
                        SalesDetails = {}
                        if "Name" in JsonResponse1[i]:
                            QuerySet["Name"] = JsonResponse1[i]["Name"]
                        QuerySet["Code"] = JsonResponse1[i]["Code"]

                        if "Description" in JsonResponse1[i]:
                            QuerySet["Description"] = JsonResponse1[i]["Description"]
                        if "IsTrackedAsInventory" in JsonResponse1[i]:
                            QuerySet["IsTrackedAsInventory"] = JsonResponse1[i][
                                "IsTrackedAsInventory"
                            ]
                        QuerySet["IsSold"] = JsonResponse1[i]["IsSold"]
                        QuerySet["IsPurchased"] = JsonResponse1[i]["IsPurchased"]

                        if "QuantityOnHand" in JsonResponse1[i]:
                            QuerySet["QuantityOnHand"] = JsonResponse1[i]["QuantityOnHand"]

                        if JsonResponse1[i]["SalesDetails"] != {}:
                            if "AccountCode" in JsonResponse1[i]["SalesDetails"]:
                                SalesDetails["AccountCode"] = JsonResponse1[i]["SalesDetails"][
                                    "AccountCode"
                                ]

                            if "UnitPrice" in JsonResponse1[i]["SalesDetails"]:
                                SalesDetails["UnitPrice"] = JsonResponse1[i]["SalesDetails"][
                                    "UnitPrice"
                                ]
                            if "TaxType" in JsonResponse1[i]["SalesDetails"]:
                                SalesDetails["TaxType"] = JsonResponse1[i]["SalesDetails"][
                                    "TaxType"
                                ]

                        if JsonResponse1[i]["PurchaseDetails"] != {}:
                            if "AccountCode" in JsonResponse1[i]["PurchaseDetails"]:
                                PurchaseDetails["COGSAccountCode"] = JsonResponse1[i][
                                    "PurchaseDetails"
                                ]["AccountCode"]
                            elif "COGSAccountCode" in JsonResponse1[i]["PurchaseDetails"]:
                                PurchaseDetails["COGSAccountCode"] = JsonResponse1[i][
                                    "PurchaseDetails"
                                ]["COGSAccountCode"]

                            if "UnitPrice" in JsonResponse1[i]["PurchaseDetails"]:
                                PurchaseDetails["UnitPrice"] = JsonResponse1[i][
                                    "PurchaseDetails"
                                ]["UnitPrice"]
                            if "TaxType" in JsonResponse1[i]["PurchaseDetails"]:
                                PurchaseDetails["TaxType"] = JsonResponse1[i][
                                    "PurchaseDetails"
                                ]["TaxType"]

                        QuerySet["SalesDetails"].append(SalesDetails)
                        QuerySet["PurchaseDetails"].append(PurchaseDetails)

                        arr.append(QuerySet)

                if len(arr) > 0:
                    Collection.insert_many(arr)

                step_name = "Reading data from xero items"
                write_task_execution_step(task_id, status=1, step=step_name)

    except Exception as ex:
        step_name = "Something went wrong"
        logging.error(ex, exc_info=True)
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
