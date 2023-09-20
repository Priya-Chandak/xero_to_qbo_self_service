import traceback
from ast import Break

import requests

from apps.home.data_util import get_job_details, add_job_status
from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database


def get_accountright_bank_transfer(job_id):
    try:
        start_date, end_date = get_job_details(job_id)
        db = get_mongodb_database()
        Collection = db["accountright_bank_transfer"]

        payload, base_url, headers = get_settings_myob(job_id)
        no_of_records = db["accountright_bank_transfer"].count_documents({})
        if start_date == "" and end_date == "":
            url = f"{base_url}/Banking/TransferMoneyTxn?$top=100&$skip={no_of_records}"
        else:
            url = f"{base_url}/Banking/TransferMoneyTxn?$filter=Date ge datetime'{start_date[0:10]}' and Date le datetime'{end_date[0:10]}'"
        response = requests.request("GET", url, headers=headers, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse["Items"]

        arr = []
        for i in range(0, len(JsonResponse1)):
            QuerySet = {}
            QuerySet['job_id']=job_id
            QuerySet = JsonResponse["Items"][i]

            arr.append(QuerySet)

        Collection.insert_many(arr)

        if JsonResponse["NextPageLink"] is not None:
            get_accountright_bank_transfer(job_id)

        else:
            Break

    except Exception as ex:
        traceback.print_exc()
        
