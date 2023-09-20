import traceback

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


def get_taxrate(job_id):
    try:
        dbname = get_mongodb_database()
        Collection = dbname["xero_taxrate"]
        payload, base_url, headers = get_settings_xero(job_id)

        main_url = f"{base_url}/TaxRates"
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        r1 = response1.json()
        r2 = r1["TaxRates"]
        no_of_records = len(r2)
        no_of_pages = (no_of_records // 100) + 1

        arr = []
        for pages in range(1, no_of_pages + 1):
            url = f"{base_url}/TaxRates?page={pages}"
            response = requests.request("GET", url, headers=headers, data=payload)
            JsonResponse = response.json()
            JsonResponse1 = JsonResponse["TaxRates"]

            for i in range(0, len(JsonResponse1)):
                QuerySet = {}
                QuerySet["job_id"] = job_id
                QuerySet["Name"] = JsonResponse1[i]["Name"]
                QuerySet["TaxType"] = JsonResponse1[i]["TaxType"]
                QuerySet["TaxName"] = JsonResponse1[i]["TaxComponents"][0]["Name"]
                QuerySet["TaxRate"] = JsonResponse1[i]["TaxComponents"][0]["Rate"]
                arr.append(QuerySet)

        if dbname["xero_taxrate"].count_documents({}) == no_of_records:
            pass
        else:
            Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()
        
