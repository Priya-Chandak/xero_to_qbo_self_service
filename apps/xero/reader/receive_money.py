import sys

import requests

from apps.home.data_util import get_job_details
from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
import time
import logging

def get_xero_receive_money(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()

        xero_receive_money = dbname["xero_receive_money"]
        xero_receive_prepayment = dbname["xero_receive_prepayment"]
        xero_receive_overpayment = dbname["xero_receive_overpayment"]

        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/BankTransactions"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/BankTransactions?where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["BankTransactions"]
            if len(r2) > 0:
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                receive_money = []
                receive_prepayment = []
                receive_overpayment = []

                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        url = f"{base_url}/BankTransactions?page={pages}"
                    else:
                        url = f"{base_url}/BankTransactions?page={pages}&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

                    print(url)
                    response = requests.request("GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    time.sleep(1)
                    JsonResponse1 = JsonResponse["BankTransactions"]

                    for i in range(0, len(JsonResponse1)):
                        if (
                                JsonResponse1[i]["Status"] != "DELETED"
                                and JsonResponse1[i]["Status"] != "VOIDED"
                        ):
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["payload"] = None

                            # QuerySet['Name'] = JsonResponse1[i]['Contact']['Name']
                            QuerySet["Date"] = JsonResponse1[i]["DateString"]
                            QuerySet["LineAmountTypes"] = JsonResponse1[i]["LineAmountTypes"]
                            QuerySet["HasAttachments"] = JsonResponse1[i]["HasAttachments"]
                            QuerySet["TotalAmount"] = JsonResponse1[i]["Total"]
                            QuerySet["IsReconciled"] = JsonResponse1[i]["IsReconciled"]
                            QuerySet["Status"] = JsonResponse1[i]["Status"]
                            if "TotalTax" in JsonResponse1[i]:
                                QuerySet["TotalTax"] = JsonResponse1[i]["TotalTax"]
                            if "SubTotal" in JsonResponse1[i]:
                                QuerySet["SubTotal"] = JsonResponse1[i]["SubTotal"]
                            if "BankAccount" in JsonResponse1[i]:
                                QuerySet["BankAccountID"] = JsonResponse1[i]["BankAccount"][
                                    "AccountID"
                                ]
                                QuerySet["BankAccountName"] = JsonResponse1[i]["BankAccount"][
                                    "Name"
                                ]
                            if "Contact" in JsonResponse1[i]:
                                QuerySet["ContactName"] = JsonResponse1[i]["Contact"]["Name"]
                            if "Type" in JsonResponse1[i]:
                                QuerySet["Type"] = JsonResponse1[i]["Type"]
                            if "BankTransactionID" in JsonResponse1[i]:
                                QuerySet["BankTransactionID"] = JsonResponse1[i][
                                    "BankTransactionID"
                                ]

                            if "Reference" in QuerySet:
                                QuerySet["Reference"] = JsonResponse1[i]["Reference"]
                            else:
                                pass

                            for j in range(0, len(JsonResponse1[i]["LineItems"])):
                                QuerySet1 = {}

                                if "Description" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Description"] = JsonResponse1[i]["LineItems"][j][
                                        "Description"
                                    ]
                                if "UnitAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Unit_Price"] = JsonResponse1[i]["LineItems"][j][
                                        "UnitAmount"
                                    ]
                                if "AccountCode" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["AccountCode"] = JsonResponse1[i]["LineItems"][j][
                                        "AccountCode"
                                    ]
                                if "LineAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["LineAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "LineAmount"
                                    ]
                                if "TaxAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["TaxAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "TaxAmount"
                                    ]
                                if "Quantity" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Quantity"] = JsonResponse1[i]["LineItems"][j][
                                        "Quantity"
                                    ]
                                if "ItemCode" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["ItemCode"] = JsonResponse1[i]["LineItems"][j][
                                        "ItemCode"
                                    ]
                                if "TaxType" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["TaxType"] = JsonResponse1[i]["LineItems"][j][
                                        "TaxType"
                                    ]
                                else:
                                    QuerySet1["TaxType"] = None

                                if "Reference" in JsonResponse1[i]:
                                    QuerySet["Reference"] = JsonResponse1[i]["Reference"]
                                else:
                                    QuerySet["Reference"] = None

                                if ("Tracking" in JsonResponse1[i]["LineItems"][j]) and len(
                                        JsonResponse1[i]["LineItems"][j]["Tracking"]
                                ) > 0:
                                    if (
                                            JsonResponse1[i]["LineItems"][j]["Tracking"] != {}
                                    ) and (
                                            JsonResponse1[i]["LineItems"][j]["Tracking"] is not None
                                    ):
                                        QuerySet1["TrackingName"] = JsonResponse1[i][
                                            "LineItems"
                                        ][j]["Tracking"][0]["Option"]
                                        QuerySet1["TrackingID"] = JsonResponse1[i]["LineItems"][
                                            j
                                        ]["Tracking"][0]["TrackingCategoryID"]
                                    else:
                                        QuerySet1["TrackingName"] = None
                                        QuerySet1["TrackingID"] = None
                                else:
                                    QuerySet1["TrackingName"] = None
                                    QuerySet1["TrackingID"] = None

                                QuerySet["Line"].append(QuerySet1)

                            if JsonResponse1[i]["Type"] == "RECEIVE":
                                QuerySet["table_name"] = "xero_receive_money"
                                receive_money.append(QuerySet)
                            if JsonResponse1[i]["Type"] == "RECEIVE-PREPAYMENT":
                                QuerySet["table_name"] = "xero_receive_prepayment"
                                receive_prepayment.append(QuerySet)
                            if JsonResponse1[i]["Type"] == "RECEIVE-OVERPAYMENT":
                                QuerySet["table_name"] = "xero_receive_overpayment"
                                receive_overpayment.append(QuerySet)

                if len(receive_money) > 0:
                    xero_receive_money.insert_many(receive_money)

                if len(receive_prepayment) > 0:
                    xero_receive_prepayment.insert_many(receive_prepayment)

                if len(receive_overpayment) > 0:
                    xero_receive_overpayment.insert_many(receive_overpayment)

                step_name = "Reading data from xero receive money"
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
