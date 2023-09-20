import json
import logging
import traceback
from datetime import date

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo

logger = logging.getLogger(__name__)


def add_xero_item(job_id,task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_item -> add_xero_item")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        xero_items1 = dbname["xero_items"]

        x = xero_items1.find({"job_id":job_id})
        data1 = []
        for p1 in x:
            data1.append(p1)

        QuerySet = data1

        # d=[]
        # for i in range(0,len(data1)):
        #     if data1[i]['Name']=='Coping Tiles Mitered Edge per LM':
        #         d.append(data1[i])

        # QuerySet=d[0:10]

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        # API = item
        url = f"{base_url}/item?minorversion={minorversion}"

        for i in range(0, len(QuerySet)):
            print(QuerySet[i])
            print(i)
            _id = QuerySet[i]['_id']
            task_id = QuerySet[i]['task_id']
            
            QuerySet1 = {}

            if "Name" in QuerySet[i]:
                if (QuerySet[i]["Name"] != "") and (QuerySet[i]["Name"] is not None):
                    QuerySet1["Name"] = QuerySet[i]["Name"].replace(":","-")
                else:
                    QuerySet1["Name"] = QuerySet[i]["Code"].replace(":","-")
            else:
                QuerySet1["Name"] = QuerySet[i]["Code"].replace(":","-")

            QuerySet1["Sku"] = QuerySet[i]["Code"]
            if "Description" in QuerySet[i]:
                QuerySet1["Description"] = QuerySet[i]["Description"][0:1000]
                QuerySet1["PurchaseDesc"] = QuerySet[i]["Description"][0:1000]

            QuerySet1["InvStartDate"] = date.today().strftime("%Y-%m-%d")

            if QuerySet[i]["IsTrackedAsInventory"] == True:
                QuerySet1["Type"] = "NonInventory"
                QuerySet1["TrackQtyOnHand"] = False
                QuerySet3 = {}
                QuerySet4 = {}
                    
                for q1 in range(0, len(qbo_coa)):
                    for q2 in range(0,len(xero_coa)):
                        if QuerySet[i]["SalesDetails"] is not None:
                            if "UnitPrice" in QuerySet[i]["SalesDetails"][0]:
                                QuerySet1["UnitPrice"] = QuerySet[i]["SalesDetails"][0][
                                    "UnitPrice"
                                ]
                            
                            if "AccountCode" in QuerySet[i]["SalesDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if QuerySet[i]["SalesDetails"][0]["AccountCode"] == qbo_coa[q1]["AcctNum"]:
                                        print("Yes true")
                                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                                        QuerySet3["name"] = qbo_coa[q1]["Name"]
                                        break
                                else:
                                    if QuerySet[i]["SalesDetails"][0]["AccountCode"] == xero_coa[q2]["Code"]:
                                        if xero_coa[q2]["Name"] == qbo_coa[q1]["Name"]:
                                            QuerySet3["value"] = qbo_coa[q1]["Id"]
                                            QuerySet3["name"] = qbo_coa[q1]["Name"]
                                            break

                                    

                            else:
                                if qbo_coa[q1]["FullyQualifiedName"] == "Sales":
                                    QuerySet3["value"] = qbo_coa[q1]["Id"]
                                    QuerySet3["name"] = qbo_coa[q1]["Name"]
                                    break
                        else:
                            if qbo_coa[q1]["FullyQualifiedName"] == "Sales":
                                QuerySet3["value"] = qbo_coa[q1]["Id"]
                                QuerySet3["name"] = qbo_coa[q1]["Name"]
                                break



                    # for q1 in range(0, len(qbo_coa)):
                        if QuerySet[i]["PurchaseDetails"] is not None:
                            if "UnitPrice" in QuerySet[i]["PurchaseDetails"][0]:
                                QuerySet1["PurchaseCost"] = QuerySet[i]["PurchaseDetails"][
                                    0
                                ]["UnitPrice"]

                            if "COGSAccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if (
                                        QuerySet[i]["PurchaseDetails"][0]["COGSAccountCode"]
                                        == qbo_coa[q1]["AcctNum"]
                                    ):
                                        QuerySet4["value"] = qbo_coa[q1]["Id"]
                                        QuerySet4["name"] = qbo_coa[q1]["Name"]
                                        break
                                else:
                                    if QuerySet[i]["PurchaseDetails"][0]["COGSAccountCode"] == xero_coa[q2]["Code"]:
                                        if xero_coa[q2]["Name"] == qbo_coa[q1]["Name"]:
                                            QuerySet4["value"] = qbo_coa[q1]["Id"]
                                            QuerySet4["name"] = qbo_coa[q1]["Name"]
                                            break


                            elif "AccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if (
                                        QuerySet[i]["PurchaseDetails"][0]["AccountCode"]
                                        == qbo_coa[q1]["AcctNum"]
                                    ):
                                        QuerySet4["value"] = qbo_coa[q1]["Id"]
                                        QuerySet4["name"] = qbo_coa[q1]["Name"]
                                        break
                                else:
                                    if QuerySet[i]["PurchaseDetails"][0]["AccountCode"] == xero_coa[q2]["Code"]:
                                        if xero_coa[q2]["Name"] == qbo_coa[q1]["Name"]:
                                            QuerySet4["value"] = qbo_coa[q1]["Id"]
                                            QuerySet4["name"] = qbo_coa[q1]["Name"]
                                            break
                            else:
                                if qbo_coa[q1]["FullyQualifiedName"] == "Purchases":
                                    QuerySet4["value"] = qbo_coa[q1]["Id"]
                                    QuerySet4["name"] = qbo_coa[q1]["Name"]
                                    break

                        else:
                            if qbo_coa[q1]["FullyQualifiedName"] == "Purchases":
                                QuerySet4["value"] = qbo_coa[q1]["Id"]
                                QuerySet4["name"] = qbo_coa[q1]["Name"]

                    QuerySet1["IncomeAccountRef"] = QuerySet3
                    QuerySet1["ExpenseAccountRef"] = QuerySet4
                
            else:
                QuerySet1["Type"] = "Service"
                QuerySet3 = {}
                QuerySet4 = {}
                for j1 in range(0, len(xero_coa)):
                    if QuerySet[i]["SalesDetails"] is not None:
                        if "UnitPrice" in QuerySet[i]["SalesDetails"][0]:
                            QuerySet1["UnitPrice"] = QuerySet[i]["SalesDetails"][0][
                                "UnitPrice"
                            ]

                        for q1 in range(0, len(qbo_coa)):
                            if "AccountCode" in QuerySet[i]["SalesDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if (
                                        QuerySet[i]["SalesDetails"][0]["AccountCode"]
                                        == qbo_coa[q1]["AcctNum"]
                                    ):
                                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                                        QuerySet3["name"] = qbo_coa[q1]["Name"]
                                        break

                            else:
                                if qbo_coa[q1]["FullyQualifiedName"] == "Sales":
                                    QuerySet3["value"] = qbo_coa[q1]["Id"]
                                    QuerySet3["name"] = qbo_coa[q1]["Name"]
                                    break

                            if "COGSAccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if (
                                        QuerySet[i]["PurchaseDetails"][0][
                                            "COGSAccountCode"
                                        ]
                                        == qbo_coa[q1]["AcctNum"]
                                    ):
                                        QuerySet4["value"] = qbo_coa[q1]["Id"]
                                        QuerySet4["name"] = qbo_coa[q1]["Name"]
                                        break

                            elif "AccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if (
                                        QuerySet[i]["PurchaseDetails"][0]["AccountCode"]
                                        == qbo_coa[q1]["AcctNum"]
                                    ):
                                        QuerySet4["value"] = qbo_coa[q1]["Id"]
                                        QuerySet4["name"] = qbo_coa[q1]["Name"]
                                        break

                            else:
                                if qbo_coa[q1]["FullyQualifiedName"] == "Purchases":
                                    QuerySet4["value"] = qbo_coa[q1]["Id"]
                                    QuerySet4["name"] = qbo_coa[q1]["Name"]
                                    break

                        QuerySet1["IncomeAccountRef"] = QuerySet3
                        QuerySet1["ExpenseAccountRef"] = QuerySet4

                QuerySet1["Type"] = "Service"

            payload = json.dumps(QuerySet1)
            print(payload)
            id_or_name_value_for_error = QuerySet[i]["Name"] if "Name" in QuerySet[i] else QuerySet[i]['Code']
            post_data_in_qbo(url, headers, payload,xero_items1,_id, job_id,task_id, id_or_name_value_for_error)

            
    except Exception as ex:
        traceback.print_exc()
        


def create_item_from_xero_invoice1(job_id,task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_item -> create_item_from_xero_invoice1")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        xero_invoice1 = dbname["xero_invoice"].find({"job_id":job_id})
        xero_invoice = []
        for p1 in xero_invoice1:
            xero_invoice.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        QuerySet = xero_invoice
        url = f"{base_url}/item?minorversion={minorversion}"

        arr1 = []

        for i in range(0, len(QuerySet)):
            for j in range(0, len(QuerySet[i]["Line"])):
                QuerySet1 = {"IncomeAccountRef": [], "ExpenseAccountRef": []}
                QuerySet1["Type"] = "NonInventory"
                QuerySet1["TrackQtyOnHand"] = False
                QuerySet2 = {}
                QuerySet3 = {}
                QuerySet1["Sku"] = QuerySet[i]["Line"][j]["AccountCode"]

                if "ItemCode" not in QuerySet[i]["Line"][j]:
                    for j1 in range(0, len(xero_coa)):
                        for j2 in range(0, len(qbo_coa)):
                            if ("Code" in xero_coa[j1]) and (
                                "AccountCode" in QuerySet[i]["Line"][j]
                            ):
                                if (
                                    QuerySet[i]["Line"][j]["AccountCode"]
                                    == xero_coa[j1]["Code"]
                                ):
                                    if (
                                        xero_coa[j1]["Name"]
                                        == qbo_coa[j2]["FullyQualifiedName"]
                                    ):
                                        QuerySet2["value"] = qbo_coa[j2]["Id"]
                                        QuerySet2["name"] = qbo_coa[j2]["Name"]
                                        QuerySet1["Name"] = qbo_coa[j2]["Name"]

                QuerySet1["IncomeAccountRef"] = QuerySet2
                QuerySet1["ExpenseAccountRef"] = QuerySet2

                # arr.append(QuerySet1)

                payload = json.dumps(QuerySet1)
                # print(payload)
                response = requests.request("POST", url, headers=headers, data=payload)

                if response.status_code == 401:
                    res1 = json.loads(response.text)
                    # res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]

                    add_job_status(job_id, res1, "error")
                elif response.status_code == 400:
                    res1 = json.loads(response.text)
                    add_job_status(job_id, res1, "error")

        # arr1=[]
        # for k3 in range(0, len(arr)):
        #     if arr[k3] not in arr1:
        #         arr1.append(arr[k3])
        #     else:
        #         pass

        # print(arr1)
        # print("---")

        # for k4 in range(0, len(arr1)):
        #     payload = json.dumps(arr1[k4])
        #     response = requests.request(
        #         "POST", url, headers=headers, data=payload)
        #     print(payload)
        #     print(response)
        #     print("--")

        #     if response.status_code == 401:
        #         res1 = json.loads(response.text)
        #         res2 = (res1['fault']['error'][0]['message']).split(";")[0]
        #         print(payload)
        #         print(response)
        #         print("--")

        #         add_job_status(job_id, res2, "error")
        #     elif response.status_code == 400:
        #         res1 = json.loads(response.text)
        #         print(payload)
        #         print(response)
        #         print("--")
        #         if 'Name' in arr1[k4]:
        #             res2 = (res1['Fault']['Error'][0]['Message'] +
        #                     ': {}'.format(arr1[k4]['Name']))
        #         else:
        #             res2 = (res1['Fault']['Error'][0]['Message'])
        #         add_job_status(job_id, res2, "error")

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_item -> create_item_from_xero_invoice1", ex)
        


def create_item_from_xero_purchase_order(job_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_item -> create_item_from_xero_purchase_order")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        xero_purchase_order1 = dbname["xero_purchase_order"]

        x = xero_purchase_order1.find({"job_id":job_id})
        data1 = []
        for p1 in x:
            data1.append(p1)
        QuerySet = data1

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        # API = item
        url = f"{base_url}/item?minorversion={minorversion}"

        arr = []
        arr1 = []
        for i in range(0, len(QuerySet)):
            if len(QuerySet[i]["Line"]) > 2:
                for j in range(0, len(QuerySet[i]["Line"])):
                    QuerySet1 = {"IncomeAccountRef": []}
                    QuerySet2 = {}
                    QuerySet3 = {}
                    if "ItemCode" not in QuerySet[i]["Line"][j]:
                        QuerySet1["Name"] = QuerySet[i]["Line"][j]["Acc_Name"]
                        QuerySet1["Type"] = "NonInventory"
                        QuerySet1["TrackQtyOnHand"] = False

                        for j1 in range(0, len(xero_coa)):
                            for j2 in range(0, len(qbo_coa)):
                                if ("Code" in xero_coa[j1]) and (
                                    "Acc_Name" in QuerySet[i]["Line"][j]
                                ):
                                    if (
                                        QuerySet[i]["Line"][j]["Acc_Name"]
                                        == xero_coa[j1]["Code"]
                                    ):
                                        if (
                                            xero_coa[j1]["Name"]
                                            == qbo_coa[j2]["FullyQualifiedName"]
                                        ):
                                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                                            QuerySet2["name"] = qbo_coa[j2]["Name"]
                                        else:
                                            pass

                        QuerySet1["IncomeAccountRef"] = QuerySet2
                        arr.append(QuerySet1)

            elif len(QuerySet[i]["Line"]) == 1:
                if "ItemCode" not in QuerySet[i]["Line"][0]:
                    QuerySet1["Name"] = QuerySet[i]["Line"][0]["Acc_Name"]
                    QuerySet1["Type"] = "NonInventory"
                    QuerySet1["TrackQtyOnHand"] = False

                    for j1 in range(0, len(xero_coa)):
                        for j2 in range(0, len(qbo_coa)):
                            if ("Code" in xero_coa[j1]) and (
                                "Acc_Name" in QuerySet[i]["Line"][0]
                            ):
                                if (
                                    QuerySet[i]["Line"][0]["Acc_Name"]
                                    == xero_coa[j1]["Code"]
                                ):
                                    if (
                                        xero_coa[j1]["Name"]
                                        == qbo_coa[j2]["FullyQualifiedName"]
                                    ):
                                        QuerySet2["value"] = qbo_coa[j2]["Id"]
                                        QuerySet2["name"] = qbo_coa[j2]["Name"]
                                    else:
                                        pass

                QuerySet1["IncomeAccountRef"] = QuerySet2
                arr.append(QuerySet1)
        for k3 in range(0, len(arr)):
            if arr[k3] not in arr1:
                arr1.append(arr[k3])
            else:
                pass

        for k4 in range(0, len(arr1)):
            payload = json.dumps(arr1[k4])
            response = requests.request("POST", url, headers=headers, data=payload)

            post_data_in_qbo(url, headers, payload,xero_purchase_order1,arr1[k4]["Name"], job_id, arr1[k4]["Name"])

            
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_item -> create_item_from_xero_purchase_order", ex)
        



def add_duplicate_item(job_id,task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_item -> add_duplicate_item")

        dbname = get_mongodb_database()

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        xero_items1 = dbname["xero_items"]

        x = xero_items1.find({"job_id":job_id})
        data1 = []
        for p1 in x:
            data1.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        qbo_item1 = dbname["QBO_Item"].find({"job_id":job_id})
        qbo_item = []
        for p21 in qbo_item1:
            qbo_item.append(p21)

        # API = item
        url = f"{base_url}/item?minorversion={minorversion}"

        a = data1

        b = []
        for i in range(0, len(a)):
            b.append(a[i]["Name"])
        a1 = {i: b.count(i) for i in b}

        b1 = []
        for i1 in a1.keys():
            if a1[i1] > 1:
                b1.append(i1)

        c1 = []

        # for j in range(0,len(b)):
        #     for i in range(0,len(QuerySet)):
        #         QuerySet1 = {}
        #         QuerySet3 = {}
        #         QuerySet4 = {}
        #         if b[j] == QuerySet[i]['Name']:
        #             QuerySet1["Name"] = QuerySet[i]["Name"] + "-" + QuerySet[i]["Code"]

        QuerySet = data1
        for i in range(0, len(QuerySet)):
            print(QuerySet[i])
            _id = QuerySet[i]['_id']
            task_id = QuerySet[i]['task_id']
            
            QuerySet1 = {}
            QuerySet3 = {}
            QuerySet4 = {}

            if QuerySet[i]["Name"] in b1:
                if QuerySet[i]["Name"] != "":
                    QuerySet1["Name"] = QuerySet[i]["Name"].replace(":","-") + "-" + QuerySet[i]["Code"]
                else:
                    QuerySet1["Name"] = QuerySet[i]["Code"].replace(":","-")
            else:
                QuerySet1["Name"] = QuerySet[i]["Name"].replace(":","-")

            QuerySet1["Sku"] = QuerySet[i]["Code"]
            if "Description" in QuerySet[i]:
                QuerySet1["Description"] = QuerySet[i]["Description"][0:1000]
                QuerySet1["PurchaseDesc"] = QuerySet[i]["Description"][0:1000]

            QuerySet1["InvStartDate"] = date.today().strftime("%Y-%m-%d")

            if QuerySet[i]["IsTrackedAsInventory"] == True:
                QuerySet1["Type"] = "NonInventory"
                QuerySet1["TrackQtyOnHand"] = False

                for q1 in range(0, len(qbo_coa)):
                    if QuerySet[i]["SalesDetails"] is not None:
                        if "UnitPrice" in QuerySet[i]["SalesDetails"][0]:
                            QuerySet1["UnitPrice"] = QuerySet[i]["SalesDetails"][0][
                                "UnitPrice"
                            ]
                        for j1 in range(0, len(xero_coa)):
                            if "AccountCode" in QuerySet[i]["SalesDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if (
                                        QuerySet[i]["SalesDetails"][0]["AccountCode"]
                                        == qbo_coa[q1]["AcctNum"]
                                    ):
                                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                                        QuerySet3["name"] = qbo_coa[q1]["Name"]
                            else:
                                if qbo_coa[q1]["FullyQualifiedName"] == "Sales":
                                    QuerySet3["value"] = qbo_coa[q1]["Id"]
                                    QuerySet3["name"] = qbo_coa[q1]["Name"]
                    else:
                        if qbo_coa[q1]["FullyQualifiedName"] == "Sales":
                            QuerySet3["value"] = qbo_coa[q1]["Id"]
                            QuerySet3["name"] = qbo_coa[q1]["Name"]

                for q1 in range(0, len(qbo_coa)):
                    if QuerySet[i]["PurchaseDetails"] is not None and QuerySet[i][
                        "PurchaseDetails"
                    ] != [{}]:
                        if "UnitPrice" in QuerySet[i]["PurchaseDetails"][0]:
                            QuerySet1["PurchaseCost"] = QuerySet[i]["PurchaseDetails"][
                                0
                            ]["UnitPrice"]

                        if "COGSAccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                            if "AcctNum" in qbo_coa[q1]:
                                if (
                                    QuerySet[i]["PurchaseDetails"][0]["COGSAccountCode"]
                                    == qbo_coa[q1]["AcctNum"]
                                ):
                                    QuerySet4["value"] = qbo_coa[q1]["Id"]
                                    QuerySet4["name"] = qbo_coa[q1]["Name"]

                        elif "AccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                            if "AcctNum" in qbo_coa[q1]:
                                if (
                                    QuerySet[i]["PurchaseDetails"][0]["AccountCode"]
                                    == qbo_coa[q1]["AcctNum"]
                                ):
                                    QuerySet4["value"] = qbo_coa[q1]["Id"]
                                    QuerySet4["name"] = qbo_coa[q1]["Name"]

                    else:
                        if qbo_coa[q1]["FullyQualifiedName"] == "Purchases":
                            QuerySet4["value"] = qbo_coa[q1]["Id"]
                            QuerySet4["name"] = qbo_coa[q1]["Name"]

                QuerySet1["ExpenseAccountRef"] = QuerySet4
                QuerySet1["IncomeAccountRef"] = QuerySet3

            else:
                QuerySet1["Type"] = "Service"

                for q1 in range(0, len(qbo_coa)):
                    if QuerySet[i]["SalesDetails"] is not None:
                        if "UnitPrice" in QuerySet[i]["SalesDetails"][0]:
                            QuerySet1["UnitPrice"] = QuerySet[i]["SalesDetails"][0][
                                "UnitPrice"
                            ]

                        for j1 in range(0, len(xero_coa)):
                            if "AccountCode" in QuerySet[i]["SalesDetails"][0]:
                                if "AcctNum" in qbo_coa[q1]:
                                    if (
                                        QuerySet[i]["SalesDetails"][0]["AccountCode"]
                                        == qbo_coa[q1]["AcctNum"]
                                    ):
                                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                                        QuerySet3["name"] = qbo_coa[q1]["Name"]
                            else:
                                if qbo_coa[q1]["FullyQualifiedName"] == "Sales":
                                    QuerySet3["value"] = qbo_coa[q1]["Id"]
                                    QuerySet3["name"] = qbo_coa[q1]["Name"]
                    else:
                        if qbo_coa[q1]["FullyQualifiedName"] == "Sales":
                            QuerySet3["value"] = qbo_coa[q1]["Id"]
                            QuerySet3["name"] = qbo_coa[q1]["Name"]

                for q1 in range(0, len(qbo_coa)):
                    if QuerySet[i]["PurchaseDetails"] is not None and QuerySet[i][
                        "PurchaseDetails"
                    ] != [{}]:
                        if "UnitPrice" in QuerySet[i]["PurchaseDetails"][0]:
                            QuerySet1["PurchaseCost"] = QuerySet[i]["PurchaseDetails"][
                                0
                            ]["UnitPrice"]

                        if "COGSAccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                            if "AcctNum" in qbo_coa[q1]:
                                if (
                                    QuerySet[i]["PurchaseDetails"][0]["COGSAccountCode"]
                                    == qbo_coa[q1]["AcctNum"]
                                ):
                                    QuerySet4["value"] = qbo_coa[q1]["Id"]
                                    QuerySet4["name"] = qbo_coa[q1]["Name"]

                        elif "AccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                            if "AcctNum" in qbo_coa[q1]:
                                if (
                                    QuerySet[i]["PurchaseDetails"][0]["AccountCode"]
                                    == qbo_coa[q1]["AcctNum"]
                                ):
                                    QuerySet4["value"] = qbo_coa[q1]["Id"]
                                    QuerySet4["name"] = qbo_coa[q1]["Name"]

                    else:
                        if qbo_coa[q1]["FullyQualifiedName"] == "Purchases":
                            QuerySet4["value"] = qbo_coa[q1]["Id"]
                            QuerySet4["name"] = qbo_coa[q1]["Name"]

                QuerySet1["Type"] = "Service"
                QuerySet1["IncomeAccountRef"] = QuerySet3
                QuerySet1["ExpenseAccountRef"] = QuerySet4

            payload = json.dumps(QuerySet1)
            print(payload)
            id_or_name_value_for_error = QuerySet[i]["Name"] if "Name" in QuerySet[i] else QuerySet[i]['Code']
            
            post_data_in_qbo(url, headers, payload,dbname["xero_items"],_id,job_id,task_id, id_or_name_value_for_error)

            
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_item -> add_duplicate_item", ex)
        
