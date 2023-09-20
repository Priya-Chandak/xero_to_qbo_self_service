import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database


def get_south_qbo_taxrate(job_id):
    try:
        db = get_mongodb_database()
        QBO_TAX_SA = db["QBO_TAX_SA"]
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db["QBO_TAX_SA"].count_documents({})

        payload = f"select * from taxrate startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse["QueryResponse"]["TaxRate"]

        arr = []
        for i in range(0, len(JsonResponse1)):
            QuerySet = {}

            QuerySet["Name"] = JsonResponse1[i]["Name"]
            QuerySet["Description"] = JsonResponse1[i]["Description"]
            QuerySet["Id"] = JsonResponse1[i]["Id"]
            QuerySet["SpecialTaxType"] = JsonResponse1[i]["SpecialTaxType"]

            if "RateValue" in JsonResponse1[i]:
                QuerySet["MainRate"] = JsonResponse1[i]["RateValue"]
            else:
                QuerySet["MainRate"] = None

            for j in range(0, len(JsonResponse1[i]["EffectiveTaxRate"])):
                if "RateValue" in JsonResponse1[i]["EffectiveTaxRate"][j]:
                    QuerySet[f"Rate{j + 1}"] = JsonResponse1[i]["EffectiveTaxRate"][j][
                        "RateValue"
                    ]
                    QuerySet[f"Date{j + 1}"] = JsonResponse1[i]["EffectiveTaxRate"][j][
                        "EffectiveDate"
                    ][0:10]
                if "EndDate" in JsonResponse1[i]["EffectiveTaxRate"][j]:
                    QuerySet[f"EndDate{j + 1}"] = JsonResponse1[i]["EffectiveTaxRate"][
                        j
                    ]["EndDate"][0:10]

            arr.append(QuerySet)

        QBO_TAX_SA.insert_many(arr)

        if JsonResponse["QueryResponse"]["maxResults"] < 1000:
            Break
        else:
            get_south_qbo_taxrate(job_id)

    except Exception as ex:
        traceback.print_exc()
        
