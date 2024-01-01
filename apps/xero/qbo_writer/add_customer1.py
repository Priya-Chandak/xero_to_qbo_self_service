import json
import logging

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database

logger = logging.getLogger(__name__)


def add_xero_customer(job_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_customer1 -> add_xero_customer")

        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/customer?minorversion={minorversion}"

        Collection = db["xero_customer"]

        x = Collection.find({"job_id": job_id})
        data1 = []
        for k in x:
            data1.append(k)

        QuerySet1 = data1

        for i in range(0, len(QuerySet1)):
            QuerySet01 = {}
            QuerySet2 = {}
            QuerySet3 = {}
            QuerySet4 = {}
            QuerySet5 = {}

            QuerySet01["CompanyName"] = QuerySet1[i]["DisplayName"]
            QuerySet01["DisplayID"] = QuerySet1[i]["Id"]
            QuerySet01["Addresses"] = [QuerySet2]
            if "BillAddr" in QuerySet1[i]:
                if QuerySet1[i]["BillAddr"] is not None:
                    QuerySet2["Street"] = QuerySet1[i]["BillAddr"]["Line1"]
                    QuerySet2["City"] = QuerySet1[i]["BillAddr"]["City"]
                    if "Country" in QuerySet1[i]["BillAddr"]:
                        QuerySet2["Country"] = QuerySet1[i]["BillAddr"]["Country"]
                    else:
                        QuerySet2["Country"] = ""
                    if "CountrySubDivisionCode" in QuerySet1[i]["BillAddr"]:
                        QuerySet2["State"] = QuerySet1[i]["BillAddr"][
                            "CountrySubDivisionCode"
                        ]
                    else:
                        QuerySet2["State"] = ""
                    if "PrimaryPhone" in QuerySet1[i]:
                        QuerySet2["Phone1"] = QuerySet1[i]["PrimaryPhone"][
                            "FreeFormNumber"
                        ]
                    else:
                        QuerySet2["Phone1"] = ""
                else:
                    QuerySet2["Street"] = None
                    QuerySet2["City"] = None
                    QuerySet2["Country"] = None
                    QuerySet2["State"] = None
                    QuerySet2["Phone1"] = None

            else:
                pass
            if "Notes" in QuerySet1[i]:
                QuerySet01["Notes"] = QuerySet1[i]["Notes"]
            else:
                QuerySet01["Notes"] = ""
            if "Fax" in QuerySet1[i]:
                QuerySet2["Fax"] = QuerySet1[i]["Fax"]["FreeFormNumber"]
            else:
                QuerySet2["Fax"] = ""

            if "PrimaryEmailAddr" in QuerySet1[i]:
                QuerySet2["Email"] = QuerySet1[i]["PrimaryEmailAddr"]["Address"]
            else:
                QuerySet2["Email"] = ""
            if "WebAddr" in QuerySet1[i]:
                QuerySet2["Website"] = QuerySet1[i]["WebAddr"]["URI"]
            else:
                QuerySet2["Website"] = ""
            QuerySet2["ContactName"] = QuerySet1[i]["PrintOnCheckName"][0:110]
            QuerySet01["SellingDetails"] = QuerySet3
            QuerySet3["ABN"] = "41 824 753 556"
            QuerySet3["Taxcode"] = QuerySet4
            QuerySet4["UID"] = "db47ef71-1549-4f22-b21d-c1ff26f4c516"
            QuerySet3["FreightTaxCode"] = QuerySet5
            QuerySet5["UID"] = "db47ef71-1549-4f22-b21d-c1ff26f4c516"

            payload = json.dumps(QuerySet01)

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = ((res1["fault"]["error"][0]["message"]).split(";")[0]).split(
                    "="
                )[1] + ": Please Update the Access Token"
                add_job_status(job_id, res2, "error")
            elif response.status_code == 400:
                res1 = json.loads(response.text)
                res2 = (res1["Fault"]["Error"][0]["Message"]) + " : {}".format(
                    QuerySet01[i]["Name"]
                )
                add_job_status(job_id, res2, "error")

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_customer1 -> add_xero_customer", ex)
