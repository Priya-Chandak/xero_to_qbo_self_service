import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database


def get_accountright_item_invoice(job_id):
    try:
        db = get_mongodb_database()
        Collection = db["accountright_item_invoice"]
        start_date, end_date = get_job_details(job_id)
        payload, base_url, headers = get_settings_myob(job_id)
        no_of_records = db["accountright_item_invoice"].count_documents({})

        if start_date == "" and end_date == "":
            url = f"{base_url}/Sale/Invoice/Item?$top=100&$skip={no_of_records}"
        else:
            url = f"{base_url}/Sale/Invoice/Item?$filter=Date ge datetime'{start_date[0:10]}' and Date le datetime'{end_date[0:10]}'"

        response = requests.request("GET", url, headers=headers, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse["Items"]

        arr = []

        for i in range(0, len(JsonResponse1)):
            QuerySet1 = {}
            QuerySet1['job_id']=job_id
            QuerySet1 = JsonResponse1["Items"][i]
            arr.append(QuerySet1)

        Collection.insert_many(arr)

        if JsonResponse["NextPageLink"] is not None:
            get_accountright_item_invoice(job_id)

        else:
            Break

    except Exception as ex:
        traceback.print_exc()
        


def get_classified_invoice(job_id):
    try:
        db = get_mongodb_database()
        single_item_invoice = db["single_item_invoice"]
        multiple_item_invoice = db["multiple_item_invoice"]

        item_invoice1 = db["item_invoice"].find({"job_id": job_id})
        Q1 = []

        for i in item_invoice1:
            Q1.append(i)

        single = []
        multiple = []

        for p1 in range(0, len(Q1)):
            if len(Q1[p1]["Item"]) == 1:
                single.append(Q1[p1])
            elif len(Q1[p1]["Item"]) > 1:
                multiple.append(Q1[p1])
            else:
                pass

        single_item_invoice.insert_many(single)
        multiple_item_invoice.insert_many(multiple)

    except Exception as ex:
        traceback.print_exc()
        
