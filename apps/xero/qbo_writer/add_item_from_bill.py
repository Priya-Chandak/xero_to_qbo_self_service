import json
import logging

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database

logger = logging.getLogger(__name__)


def add_xero_item_from_inv_bill(job_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_from_bill -> add_xero_item_from_inv_bill")

        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        Collection = db["xero_bill"]
        # Collection = db['xero_item_bill']

        x = Collection.find({"job_id": job_id})
        data1 = []
        for p1 in x:
            data1.append(p1)

        QuerySet = data1

        qbo_coa1 = db["QBO_COA"].find({"job_id": job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = db["xero_coa"].find({"job_id": job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        xero_item1 = db["xero_items"].find({"job_id": job_id})
        xero_item = []
        for p2 in xero_item1:
            xero_item.append(p2)

        # API = item
        url = f"{base_url}/item?minorversion={minorversion}"

        # for i in range(0, len(QuerySet)):
        #     for j1 in range(0,len(QuerySet[i]['Line'])):
        #         if "ItemCode" in QuerySet[i]['Line'][j1]:

        #             QuerySet1 = {}
        #             QuerySet3 = {}
        #             QuerySet4 = {}

        #             if ("AccountCode" in QuerySet[i]['Line'][j1]):
        #                 for k2 in range(0,len(xero_item)):
        #                     if QuerySet[i]['Line'][j1]['ItemCode'] == xero_item[k2]['Code']:
        #                         print(QuerySet[i]['Line'][j1]['ItemCode'])
        #                         QuerySet1["Name"] = xero_item[k2]['Name'] + "-" + QuerySet[i]['Line'][j1]['AccountCode']
        #                         QuerySet1["Sku"] = QuerySet[i]['Line'][j1]['ItemCode']
        #                         QuerySet1["Type"] = "NonInventory"
        #                         QuerySet1['TrackQtyOnHand'] = False
        #                     else:
        #                         print("inside name not found")
        #             else:
        #                 print("both missing ")

        #             for j in range(0, len(qbo_coa)):
        #                 for j11 in range(0, len(xero_coa)):
        #                     if ('Code' in xero_coa[j11]) and ('AccountCode' in QuerySet[i]['Line'][j1]):
        #                         if QuerySet[i]['Line'][j1]['AccountCode'] == xero_coa[j11]['Code']:
        #                             if xero_coa[j11]['Name']== qbo_coa[j]['FullyQualifiedName']:
        #                                 QuerySet3["value"] = qbo_coa[j]['Id']
        #                                 QuerySet3["name"] = qbo_coa[j]['Name']

        #             QuerySet1["ExpenseAccountRef"] = QuerySet3
        #             QuerySet1["IncomeAccountRef"] = QuerySet3

        for i in range(0, len(QuerySet)):
            if "ItemCode" not in QuerySet[i]:
                QuerySet1 = {}
                QuerySet3 = {}

                if "AccountCode" in QuerySet[i]:
                    for k2 in range(0, len(xero_item)):
                        if QuerySet[i]["ItemCode"] == xero_item[k2]["Code"]:
                            QuerySet1["Name"] = (
                                    xero_item[k2]["Name"] + "-" + QuerySet[i]["AccountCode"]
                            )
                            QuerySet1["Sku"] = QuerySet[i]["ItemCode"]
                            QuerySet1["Type"] = "NonInventory"
                            QuerySet1["TrackQtyOnHand"] = False

                for j in range(0, len(qbo_coa)):
                    for j11 in range(0, len(xero_coa)):
                        if ("Code" in xero_coa[j11]) and ("AccountCode" in QuerySet[i]):
                            if QuerySet[i]["AccountCode"] == xero_coa[j11]["Code"]:
                                if (
                                        xero_coa[j11]["Name"]
                                        == qbo_coa[j]["FullyQualifiedName"]
                                ):
                                    QuerySet3["value"] = qbo_coa[j]["Id"]
                                    QuerySet3["name"] = qbo_coa[j]["Name"]

                QuerySet1["ExpenseAccountRef"] = QuerySet3
                QuerySet1["IncomeAccountRef"] = QuerySet3

                payload = json.dumps(QuerySet1)
                response = requests.request("POST", url, headers=headers, data=payload)

                if response.status_code == 401:
                    res1 = json.loads(response.text)
                    res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
                    add_job_status(job_id, res2, "error")
                elif response.status_code == 400:
                    res1 = json.loads(response.text)
                    res2 = res1["Fault"]["Error"][0]["Message"]
                    add_job_status(job_id, res2, "error")

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_item_from_bill -> add_xero_item_from_inv_bill", ex)
