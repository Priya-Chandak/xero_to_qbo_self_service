import traceback

import requests

from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
import logging

def get_xero_purchase_order(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_purchase_order = dbname["xero_purchase_order"]
        payload, base_url, headers = get_settings_xero(job_id)

        purchase_order = []
        main_url1 = f"{base_url}/PurchaseOrders"
        response1 = requests.request("GET", main_url1, headers=headers, data=payload)
        r1 = response1.json()
        r2 = r1["PurchaseOrders"]
        no_of_records = len(r2)
        no_of_pages = (no_of_records // 100) + 1

        for pages in range(1, no_of_pages + 1):
            if start_date == "" and end_date == "":
                main_url = f"{base_url}/PurchaseOrders?page={pages}"
            else:
                y1 = int(start_date[0:4])
                m1 = int(start_date[5:7])
                d1 = int(start_date[8:])
                y2 = int(end_date[0:4])
                m2 = int(end_date[5:7])
                d2 = int(end_date[8:])
                main_url = f"{base_url}/PurchaseOrders?where=Date>=DateTime({y1},{m1},{d1}) AND Date<=DateTime({y2},{m2},{d2})"
            response = requests.request("GET", main_url, headers=headers, data=payload)
            JsonResponse = response.json()
            JsonResponse1 = JsonResponse["PurchaseOrders"]

            for i in range(0, len(JsonResponse1)):
                QuerySet = {"Line": []}
                QuerySet["job_id"] = job_id
                QuerySet["task_id"] = task_id
                QuerySet["error"] = None
                QuerySet["payload"] = None
                QuerySet["is_pushed"] = 0
                QuerySet["table_name"] = "xero_purchase_order"
                QuerySet["Number"] = JsonResponse1[i]["PurchaseOrderNumber"]
                QuerySet["Date"] = JsonResponse1[i]["DateString"]
                QuerySet["Supplier"] = JsonResponse1[i]["Contact"]["Name"]
                QuerySet["IsTaxInclusive"] = JsonResponse1[i]["LineAmountTypes"]
                QuerySet["Subtotal"] = JsonResponse1[i]["SubTotal"]
                QuerySet["TotalTax"] = JsonResponse1[i]["TotalTax"]
                QuerySet["TotalAmount"] = JsonResponse1[i]["Total"]
                QuerySet["Comment"] = JsonResponse1[i]["Reference"]
                QuerySet["IsDiscounted"] = JsonResponse1[i]["IsDiscounted"]

                for j in range(0, len(JsonResponse1[i]["LineItems"])):
                    QuerySet1 = {}
                    QuerySet1["BillQuantity"] = JsonResponse1[i]["LineItems"][j][
                        "Quantity"
                    ]
                    QuerySet1["UnitPrice"] = JsonResponse1[i]["LineItems"][j][
                        "UnitAmount"
                    ]
                    QuerySet1["DiscountPercent"] = JsonResponse1[i]["LineItems"][j][
                        "DiscountRate"
                    ]
                    QuerySet1["Total"] = JsonResponse1[i]["LineItems"][j]["LineAmount"]
                    QuerySet1["Acc_Name"] = JsonResponse1[i]["LineItems"][j][
                        "AccountCode"
                    ]
                    QuerySet1["taxcode"] = JsonResponse1[i]["LineItems"][j]["TaxType"]

                    QuerySet["Line"].append(QuerySet1)

                purchase_order.append(QuerySet)

        if dbname["xero_purchase_order"].count_documents({}) == no_of_records:
            pass
        else:
            xero_purchase_order.insert_many(purchase_order)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        traceback.print_exc()
