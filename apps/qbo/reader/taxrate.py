import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database


def get_qbo_taxrate(job_id,task_id):
    try:
        db = get_mongodb_database()
        QBO_Taxrate = db["QBO_Taxrate"]
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db["QBO_Taxrate"].count_documents({'job_id':job_id})

        payload = f"select * from taxrate startposition {no_of_records} maxresults 1000"
        print(payload)
        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse["QueryResponse"]["TaxRate"]
        print(JsonResponse)
        arr = []
        for i in range(0, len(JsonResponse1)):
            QuerySet = {"job_id": job_id, "task_id": task_id, 'table_name': "QBO_Taxrate", 'error': None,
                        "is_pushed": 0}
            QuerySet["Name"] = JsonResponse1[i]["Name"]
            QuerySet["Description"] = JsonResponse1[i]["Description"]
            QuerySet["Id"] = JsonResponse1[i]["Id"]
            QuerySet["SpecialTaxType"] = JsonResponse1[i]["SpecialTaxType"]

            if "RateValue" in JsonResponse1[i]:
                QuerySet["Rate"] = JsonResponse1[i]["RateValue"]
            else:
                QuerySet["Rate"] = None

            arr.append(QuerySet)

        QBO_Taxrate.insert_many(arr)

        if JsonResponse["QueryResponse"]["maxResults"] < 1000:
            Break
        else:
            get_qbo_taxrate(job_id)

    except Exception as ex:
        traceback.print_exc()
        
