import json
import logging

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database

import logging


def add_xero_tax(job_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_taxrate -> add_xero_tax")

        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/taxservice/taxcode?minorversion={minorversion}"

        xero_tax = db["xero_tax"]

        x = xero_tax.find({"job_id": job_id})

        data = []
        for k in x:
            data.append(k)

        QuerySet1 = data

        for i in range(0, len(QuerySet1)):
            QuerySet2 = {"TaxRateDetails": []}
            QuerySet3 = {}

            QuerySet2["TaxCode"] = QuerySet1[i]["TaxType"]
            QuerySet3["TaxRateName"] = QuerySet1[i]["Name"]
            QuerySet3["RateValue"] = QuerySet1[i]["TaxRate"]
            QuerySet3["TaxAgencyId"] = "1"
            QuerySet3["TaxApplicableOn"] = "Sales"

            QuerySet2["TaxRateDetails"].append(QuerySet3)

            payload = json.dumps(QuerySet2)
            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = ((res1["fault"]["error"][0]["message"]).split(";")[0]).split(
                    "="
                )[1] + ": Please Update the Access Token"
                add_job_status(job_id, res2, "error")
            elif response.status_code == 400:
                res1 = json.loads(response.text)
                res2 = res1["Fault"]["Error"][0]["Message"] + ": {}".format(
                    QuerySet1[i]["Name"]
                )
                add_job_status(job_id, res2, "error")

    except Exception as ex:
        logging.error(ex, exc_info=True)