import json
import logging

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database

import logging



def get_list_of_items_from_qbo(job_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> get_list_of_items_from_qbo")

        dbname = get_mongodb_database()

        qbo_item1 = dbname["QBO_Item"].find({"job_id":job_id})
        qbo_item = []
        for p1 in qbo_item1:
            qbo_item.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        qbo_item_for_invoice = dbname["qbo_item_for_invoice"]

        arr = []
        for i in range(0, len(qbo_item)):
            QuerySet1 = {}
            QuerySet1["Name"] = qbo_item[i]["Name"].replace(":","-")

            if "Sku" in qbo_item[i]:
                QuerySet1["Code"] = qbo_item[i]["Sku"].replace(":","-")
            else:
                QuerySet1["Code"] = "NA"

            for j in range(0, len(qbo_coa)):
                QuerySet1["acc_name"] = qbo_coa[j]["FullyQualifiedName"]

                if qbo_item[i]["IncomeAccountRef"]["value"] == qbo_coa[j]["Id"]:
                    if "AcctNum" in qbo_coa[j]:
                        QuerySet1["acc_no"] = qbo_coa[j]["AcctNum"]
                        QuerySet1["DisplayName"] = (
                            qbo_item[i]["Name"] + "-" + qbo_coa[j]["AcctNum"]
                        )

                    else:
                        QuerySet1["acc_no"] = None
                        QuerySet1["DisplayName"] = qbo_item[i]["Name"]

            arr.append(QuerySet1)

        if len(arr) > 0:
            qbo_item_for_invoice.insert_many(arr)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        


def get_list_of_items_from_xero_invoice(job_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> get_list_of_items_from_xero_invoice")

        dbname = get_mongodb_database()

        xero_invoice1 = dbname["xero_open_invoice"].find({"job_id":job_id})
        xero_invoice = []
        for p1 in xero_invoice1:
            xero_invoice.append(p1)

        new_items_for_xero_invoice = dbname["new_items_for_xero_invoice"]

        arr = []
        for i in range(0, len(xero_invoice)):
            for j in range(0, len(xero_invoice[i]["Line"])):
                QuerySet1 = {}
                if (
                    "ItemCode" in xero_invoice[i]["Line"][j]
                    and "AccountCode" in xero_invoice[i]["Line"][j]
                ):
                    QuerySet1["Code"] = xero_invoice[i]["Line"][j]["ItemCode"]
                    QuerySet1["acc_no"] = xero_invoice[i]["Line"][j]["AccountCode"]

                    if "Name" in xero_invoice[i]["Line"][j]:
                        QuerySet1["Name"] = xero_invoice[i]["Line"][j]["Name"].replace(":","-")
                        QuerySet1["DisplayName"] = (
                            QuerySet1["Name"] + "-" + QuerySet1["acc_no"]
                        ).replace(":","-")

                if QuerySet1 not in arr:
                    arr.append(QuerySet1)

        if len(arr) > 0:
            new_items_for_xero_invoice.insert_many(arr)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        


def create_item_xero_open_invoice_accountcode(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> create_item_xero_invoice_accountcode")

        dbname = get_mongodb_database()

        (
            base_url,
            headers,
            company_id,
            minorversion,
            get_data_header,
            report_headers,
        ) = get_settings_qbo(job_id)
        url = f"{base_url}/item?minorversion={minorversion}"

        invoices1 = dbname["xero_open_invoice"].find({"job_id":job_id})
        invoices = []
        for p1 in invoices1:
            invoices.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        # items1 = dbname['new_items_for_xero_invoice']

        arr = []
        for i in range(0, len(invoices)):
            for j in range(0, len(invoices[i]["Line"])):
                if "ItemCode" not in invoices[i]["Line"][j]:
                    if "AccountCode" in invoices[i]["Line"][j]:
                        if invoices[i]["Line"][j]["AccountCode"] not in arr:
                            arr.append(invoices[i]["Line"][j]["AccountCode"])

        print(arr)
        for p in range(0, len(arr)):
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for j2 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[j2]:
                    if arr[p] == qbo_coa[j2]["AcctNum"]:
                        QuerySet1["Name"] = (
                            qbo_coa[j2]["FullyQualifiedName"] + "-" + qbo_coa[j2]["AcctNum"]
                        ).replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]

                        if arr[p] == qbo_coa[j2]["AcctNum"]:
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]
                        elif (
                            arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip()
                        ):
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]

                    elif arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip():
                        QuerySet1["Name"] = qbo_coa[j2]["FullyQualifiedName"].replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]
                        QuerySet2["value"] = qbo_coa[j2]["Id"]
                        QuerySet2["name"] = qbo_coa[j2]["Name"]

                QuerySet1["IncomeAccountRef"] = QuerySet2
                QuerySet1["ExpenseAccountRef"] = QuerySet2

            payload = json.dumps(QuerySet1)
            print(payload)
            
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
          
    except Exception as ex:
        logging.error(ex, exc_info=True)

        

def create_item_xero_open_creditnote_accountcode(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> create_item_xero_creditnote_accountcode")

        dbname = get_mongodb_database()

        (
            base_url,
            headers,
            company_id,
            minorversion,
            get_data_header,
            report_headers,
        ) = get_settings_qbo(job_id)
        url = f"{base_url}/item?minorversion={minorversion}"

        invoices1 = dbname["xero_open_creditnote"].find({"job_id":job_id})
        invoices = []
        for p1 in invoices1:
            invoices.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        # items1 = dbname['new_items_for_xero_invoice']

        arr = []
        for i in range(0, len(invoices)):
            for j in range(0, len(invoices[i]["Line"])):
                if "ItemCode" not in invoices[i]["Line"][j] or ("ItemCode" in invoices[i]["Line"][j] and invoices[i]["Line"][j]['ItemCode']==None):
                    if "AccountCode" in invoices[i]["Line"][j]:
                        if invoices[i]["Line"][j]["AccountCode"] not in arr:
                            arr.append(invoices[i]["Line"][j]["AccountCode"])

        for p in range(0, len(arr)):
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for j2 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[j2]:
                    if arr[p] == qbo_coa[j2]["AcctNum"]:
                        QuerySet1["Name"] = (
                            qbo_coa[j2]["FullyQualifiedName"] + "-" + qbo_coa[j2]["AcctNum"]
                        ).replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]

                        if arr[p] == qbo_coa[j2]["AcctNum"]:
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]
                            break
                        elif (
                            arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip()
                        ):
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]
                            break

                    elif arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip():
                        QuerySet1["Name"] = qbo_coa[j2]["FullyQualifiedName"].replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]
                        QuerySet2["value"] = qbo_coa[j2]["Id"]
                        QuerySet2["name"] = qbo_coa[j2]["Name"]

                QuerySet1["IncomeAccountRef"] = QuerySet2
                QuerySet1["ExpenseAccountRef"] = QuerySet2

            payload = json.dumps(QuerySet1)
            print(payload)
            
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
          
    except Exception as ex:
        logging.error(ex, exc_info=True)


def create_item_from_xero_open_invoice_acccode_itemcode(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> create_item_from_xero_open_invoice_acccode_itemcode")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        qbo_item1 = dbname["QBO_Item"].find({"job_id":job_id})
        qbo_item = []
        for p1 in qbo_item1:
            qbo_item.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        xero_invoice1 = dbname["xero_open_invoice"].find({"job_id":job_id})
        xero_invoice = []
        for p1 in xero_invoice1:
            xero_invoice.append(p1)

        url = f"{base_url}/item?minorversion={minorversion}"

        arr1 = []
        arr2 = []
        arr3 = []

        for i2 in range(0, len(qbo_item)):
            if "Sku" in qbo_item[i2]:
                QuerySet = {}

                QuerySet["ItemCode"] = qbo_item[i2]["Sku"]
                for j2 in range(0, len(qbo_coa)):
                    if "IncomeAccountRef" in qbo_item[i2]:
                        if (
                            qbo_item[i2]["IncomeAccountRef"]["value"]
                            == qbo_coa[j2]["Id"]
                        ):
                            if "AcctNum" in qbo_coa[j2]:
                                QuerySet["AccountCode"] = qbo_coa[j2]["AcctNum"]
                            else:
                                QuerySet["AccountCode"] = "NA"

                arr1.append(QuerySet)

        for i1 in range(0, len(xero_invoice)):
            for j1 in range(0, len(xero_invoice[i1]["Line"])):
                if (
                    "ItemCode" in xero_invoice[i1]["Line"][j1]
                    and "AccountCode" in xero_invoice[i1]["Line"][j1]
                ):
                    QuerySet = {}
                    QuerySet["ItemCode"] = xero_invoice[i1]["Line"][j1]["ItemCode"]

                    QuerySet["AccountCode"] = xero_invoice[i1]["Line"][j1][
                        "AccountCode"
                    ]
                    arr2.append(QuerySet)

        for k in range(0, len(arr2)):
            if arr2[k] in arr1:
                pass
            else:
                if arr2[k] not in arr3:
                    arr3.append(arr2[k])

        QuerySet = arr3
        for i in range(0, len(QuerySet)):
            QuerySet1 = {}
            QuerySet3 = {}
            QuerySet4 = {}

            for i2 in range(0, len(qbo_item)):
                if "Sku" in qbo_item[i2]:
                    if QuerySet[i]["ItemCode"] == qbo_item[i2]["Sku"]:
                        if qbo_item[i2]["Name"] != "":
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Name"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )
                        else:
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Sku"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )
            
            if QuerySet[i]["ItemCode"] !=None:
                QuerySet1["Sku"] = (
                    QuerySet[i]["ItemCode"] + "-" + QuerySet[i]["AccountCode"]
                    ).replace(":","-")
                QuerySet1["Name"] = (
                    QuerySet[i]["ItemCode"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                ).replace(":","-")
            else:
                QuerySet1["Sku"] = (
                    QuerySet[i]["AccountCode"]
                    ).replace(":","-")
                QuerySet1["Name"] = (
                    QuerySet[i]["AccountCode"]
                ).replace(":","-")
            


            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for q1 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[q1]:
                    if QuerySet[i]["AccountCode"] == qbo_coa[q1]["AcctNum"]:
                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                        QuerySet3["name"] = qbo_coa[q1]["Name"]

            QuerySet1["ExpenseAccountRef"] = QuerySet3
            QuerySet1["IncomeAccountRef"] = QuerySet3

            payload = json.dumps(QuerySet1)
            response = requests.request("POST", url, headers=headers, data=payload)
            
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
           
    except Exception as ex:
        logging.error(ex, exc_info=True)
        

def create_item_from_xero_open_creditnote_acccode_itemcode(job_id,task_id):
    
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> create_item_from_xero_open_creditnote_acccode_itemcode")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        qbo_item1 = dbname["QBO_Item"].find({"job_id":job_id})
        qbo_item = []
        for p1 in qbo_item1:
            qbo_item.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        xero_invoice1 = dbname["xero_open_creditnote"].find({"job_id":job_id})
        xero_invoice = []
        for p1 in xero_invoice1:
            xero_invoice.append(p1)

        url = f"{base_url}/item?minorversion={minorversion}"

        arr1 = []
        arr2 = []
        arr3 = []

        for i2 in range(0, len(qbo_item)):
            if "Sku" in qbo_item[i2]:
                QuerySet = {}

                QuerySet["ItemCode"] = qbo_item[i2]["Sku"]
                for j2 in range(0, len(qbo_coa)):
                    if "IncomeAccountRef" in qbo_item[i2]:
                        if (
                            qbo_item[i2]["IncomeAccountRef"]["value"]
                            == qbo_coa[j2]["Id"]
                        ):
                            if "AcctNum" in qbo_coa[j2]:
                                QuerySet["AccountCode"] = qbo_coa[j2]["AcctNum"]
                            else:
                                QuerySet["AccountCode"] = "NA"

                arr1.append(QuerySet)

        for i1 in range(0, len(xero_invoice)):
            for j1 in range(0, len(xero_invoice[i1]["Line"])):
                if (
                    "ItemCode" in xero_invoice[i1]["Line"][j1]
                    and "AccountCode" in xero_invoice[i1]["Line"][j1]
                ):
                    QuerySet = {}
                    QuerySet["ItemCode"] = xero_invoice[i1]["Line"][j1]["ItemCode"]

                    QuerySet["AccountCode"] = xero_invoice[i1]["Line"][j1][
                        "AccountCode"
                    ]
                    arr2.append(QuerySet)

        for k in range(0, len(arr2)):
            if arr2[k] in arr1:
                pass
            else:
                if arr2[k] not in arr3:
                    arr3.append(arr2[k])

        QuerySet = arr3
        for i in range(0, len(QuerySet)):
            QuerySet1 = {}
            QuerySet3 = {}
            QuerySet4 = {}

            for i2 in range(0, len(qbo_item)):
                if "Sku" in qbo_item[i2]:
                    if QuerySet[i]["ItemCode"] == qbo_item[i2]["Sku"]:
                        if qbo_item[i2]["Name"] != "":
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Name"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )
                        else:
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Sku"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )

            if QuerySet[i]["ItemCode"] !=None:
                QuerySet1["Sku"] = (
                    QuerySet[i]["ItemCode"] + "-" + QuerySet[i]["AccountCode"]
                ).replace(":","-")
                QuerySet1["Name"] = (
                    QuerySet[i]["ItemCode"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                ).replace(":","-")

            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for q1 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[q1]:
                    if QuerySet[i]["AccountCode"] == qbo_coa[q1]["AcctNum"]:
                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                        QuerySet3["name"] = qbo_coa[q1]["Name"]

            QuerySet1["ExpenseAccountRef"] = QuerySet3
            QuerySet1["IncomeAccountRef"] = QuerySet3

            payload = json.dumps(QuerySet1)
            response = requests.request("POST", url, headers=headers, data=payload)
            
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
           
    except Exception as ex:
        logging.error(ex, exc_info=True)
        


def create_item_from_xero_open_bill_acccode_itemcode(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> create_item_from_xero_open_invoice_acccode_itemcode")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        qbo_item1 = dbname["QBO_Item"].find({"job_id":job_id})
        qbo_item = []
        for p1 in qbo_item1:
            qbo_item.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        xero_invoice1 = dbname["xero_open_bill"].find({"job_id":job_id})
        xero_invoice = []
        for p1 in xero_invoice1:
            xero_invoice.append(p1)

        url = f"{base_url}/item?minorversion={minorversion}"

        arr1 = []
        arr2 = []
        arr3 = []

        for i2 in range(0, len(qbo_item)):
            if "Sku" in qbo_item[i2]:
                QuerySet = {}

                QuerySet["ItemCode"] = qbo_item[i2]["Sku"]
                for j2 in range(0, len(qbo_coa)):
                    if "IncomeAccountRef" in qbo_item[i2]:
                        if (
                            qbo_item[i2]["IncomeAccountRef"]["value"]
                            == qbo_coa[j2]["Id"]
                        ):
                            if "AcctNum" in qbo_coa[j2]:
                                QuerySet["AccountCode"] = qbo_coa[j2]["AcctNum"]
                            else:
                                QuerySet["AccountCode"] = "NA"

                arr1.append(QuerySet)

        for i1 in range(0, len(xero_invoice)):
            for j1 in range(0, len(xero_invoice[i1]["Line"])):
                if (
                    "ItemCode" in xero_invoice[i1]["Line"][j1]
                    and "AccountCode" in xero_invoice[i1]["Line"][j1]
                ):
                    QuerySet = {}
                    QuerySet["ItemCode"] = xero_invoice[i1]["Line"][j1]["ItemCode"]

                    QuerySet["AccountCode"] = xero_invoice[i1]["Line"][j1][
                        "AccountCode"
                    ]
                    arr2.append(QuerySet)

        for k in range(0, len(arr2)):
            if arr2[k] in arr1:
                pass
            else:
                if arr2[k] not in arr3:
                    arr3.append(arr2[k])

        QuerySet = arr3
        for i in range(0, len(QuerySet)):
            QuerySet1 = {}
            QuerySet3 = {}
            QuerySet4 = {}

            for i2 in range(0, len(qbo_item)):
                if "Sku" in qbo_item[i2]:
                    if QuerySet[i]["ItemCode"] == qbo_item[i2]["Sku"]:
                        if qbo_item[i2]["Name"] != "":
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Name"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )
                        else:
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Sku"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )

            QuerySet1["Sku"] = (
                QuerySet[i]["ItemCode"] + "-" + QuerySet[i]["AccountCode"]
            ).replace(":","-")
            QuerySet1["Name"] = (
                QuerySet[i]["ItemCode"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
            ).replace(":","-")

            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for q1 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[q1]:
                    if QuerySet[i]["AccountCode"] == qbo_coa[q1]["AcctNum"]:
                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                        QuerySet3["name"] = qbo_coa[q1]["Name"]

            QuerySet1["ExpenseAccountRef"] = QuerySet3
            QuerySet1["IncomeAccountRef"] = QuerySet3

            payload = json.dumps(QuerySet1)
            response = requests.request("POST", url, headers=headers, data=payload)
            
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
           
    except Exception as ex:
        logging.error(ex, exc_info=True)


def create_item_xero_bill_accountcode(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_bill -> create_item_xero_invoice_accountcode")

        dbname = get_mongodb_database()

        (
            base_url,
            headers,
            company_id,
            minorversion,
            get_data_header,
            report_headers,
        ) = get_settings_qbo(job_id)
        url = f"{base_url}/item?minorversion={minorversion}"

        invoices1 = dbname["xero_open_bill"].find({"job_id":job_id})
        invoices = []
        for p1 in invoices1:
            invoices.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        # items1 = dbname['new_items_for_xero_invoice']

        arr = []
        for i in range(0, len(invoices)):
            for j in range(0, len(invoices[i]["Line"])):
                if "ItemCode" not in invoices[i]["Line"][j]:
                    if "AccountCode" in invoices[i]["Line"][j]:
                        if invoices[i]["Line"][j]["AccountCode"] not in arr:
                            arr.append(invoices[i]["Line"][j]["AccountCode"])

        for p in range(0, len(arr)):
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for j2 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[j2]:
                    if arr[p] == qbo_coa[j2]["AcctNum"]:
                        QuerySet1["Name"] = (
                            qbo_coa[j2]["FullyQualifiedName"] + "-" + qbo_coa[j2]["AcctNum"]
                        ).replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]

                        if arr[p] == qbo_coa[j2]["AcctNum"]:
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]
                        elif (
                            arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip()
                        ):
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]

                    elif arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip():
                        QuerySet1["Name"] = qbo_coa[j2]["FullyQualifiedName"].replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]
                        QuerySet2["value"] = qbo_coa[j2]["Id"]
                        QuerySet2["name"] = qbo_coa[j2]["Name"]

                QuerySet1["IncomeAccountRef"] = QuerySet2
                QuerySet1["ExpenseAccountRef"] = QuerySet2

            payload = json.dumps(QuerySet1)
            print(payload)
            
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
          
    except Exception as ex:
        logging.error(ex, exc_info=True)


def create_item_xero_open_vendorcredit_accountcode(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> create_item_xero_invoice_accountcode")

        dbname = get_mongodb_database()

        (
            base_url,
            headers,
            company_id,
            minorversion,
            get_data_header,
            report_headers,
        ) = get_settings_qbo(job_id)
        url = f"{base_url}/item?minorversion={minorversion}"

        invoices1 = dbname["xero_open_vendorcredit"].find({"job_id":job_id})
        invoices = []
        for p1 in invoices1:
            invoices.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        # items1 = dbname['new_items_for_xero_invoice']

        arr = []
        for i in range(0, len(invoices)):
            for j in range(0, len(invoices[i]["Line"])):
                if "ItemCode" not in invoices[i]["Line"][j]:
                    if "AccountCode" in invoices[i]["Line"][j]:
                        if invoices[i]["Line"][j]["AccountCode"] not in arr:
                            arr.append(invoices[i]["Line"][j]["AccountCode"])

        for p in range(0, len(arr)):
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for j2 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[j2]:
                    if arr[p] == qbo_coa[j2]["AcctNum"]:
                        QuerySet1["Name"] = (
                            qbo_coa[j2]["FullyQualifiedName"] + "-" + qbo_coa[j2]["AcctNum"]
                        ).replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]

                        if arr[p] == qbo_coa[j2]["AcctNum"]:
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]
                        elif (
                            arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip()
                        ):
                            QuerySet2["value"] = qbo_coa[j2]["Id"]
                            QuerySet2["name"] = qbo_coa[j2]["Name"]

                    elif arr[p].lower().strip() == qbo_coa[j2]["AcctNum"].lower().strip():
                        QuerySet1["Name"] = qbo_coa[j2]["FullyQualifiedName"].replace(":","-")
                        QuerySet1["Sku"] = qbo_coa[j2]["AcctNum"]
                        QuerySet2["value"] = qbo_coa[j2]["Id"]
                        QuerySet2["name"] = qbo_coa[j2]["Name"]

                QuerySet1["IncomeAccountRef"] = QuerySet2
                QuerySet1["ExpenseAccountRef"] = QuerySet2

            payload = json.dumps(QuerySet1)
            print(payload)
            
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
          
    except Exception as ex:
        logging.error(ex, exc_info=True)



def create_item_from_xero_open_vendorcredit_acccode_itemcode(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_using_invoice -> create_item_from_xero_open_invoice_acccode_itemcode")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        qbo_item1 = dbname["QBO_Item"].find({"job_id":job_id})
        qbo_item = []
        for p1 in qbo_item1:
            qbo_item.append(p1)

        qbo_coa1 = dbname["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for p1 in qbo_coa1:
            qbo_coa.append(p1)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        xero_invoice1 = dbname["xero_open_vendorcredit"].find({"job_id":job_id})
        xero_invoice = []
        for p1 in xero_invoice1:
            xero_invoice.append(p1)

        url = f"{base_url}/item?minorversion={minorversion}"

        arr1 = []
        arr2 = []
        arr3 = []

        for i2 in range(0, len(qbo_item)):
            if "Sku" in qbo_item[i2]:
                QuerySet = {}

                QuerySet["ItemCode"] = qbo_item[i2]["Sku"]
                for j2 in range(0, len(qbo_coa)):
                    if "IncomeAccountRef" in qbo_item[i2]:
                        if (
                            qbo_item[i2]["IncomeAccountRef"]["value"]
                            == qbo_coa[j2]["Id"]
                        ):
                            if "AcctNum" in qbo_coa[j2]:
                                QuerySet["AccountCode"] = qbo_coa[j2]["AcctNum"]
                            else:
                                QuerySet["AccountCode"] = "NA"

                arr1.append(QuerySet)

        for i1 in range(0, len(xero_invoice)):
            for j1 in range(0, len(xero_invoice[i1]["Line"])):
                if (
                    "ItemCode" in xero_invoice[i1]["Line"][j1]
                    and "AccountCode" in xero_invoice[i1]["Line"][j1]
                ):
                    QuerySet = {}
                    QuerySet["ItemCode"] = xero_invoice[i1]["Line"][j1]["ItemCode"]

                    QuerySet["AccountCode"] = xero_invoice[i1]["Line"][j1][
                        "AccountCode"
                    ]
                    arr2.append(QuerySet)

        for k in range(0, len(arr2)):
            if arr2[k] in arr1:
                pass
            else:
                if arr2[k] not in arr3:
                    arr3.append(arr2[k])

        QuerySet = arr3
        for i in range(0, len(QuerySet)):
            QuerySet1 = {}
            QuerySet3 = {}
            QuerySet4 = {}

            for i2 in range(0, len(qbo_item)):
                if "Sku" in qbo_item[i2]:
                    if QuerySet[i]["ItemCode"] == qbo_item[i2]["Sku"]:
                        if qbo_item[i2]["Name"] != "":
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Name"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )
                        else:
                            QuerySet1["Name"] = (
                                qbo_item[i2]["Sku"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
                            )

            QuerySet1["Sku"] = (
                QuerySet[i]["ItemCode"] + "-" + QuerySet[i]["AccountCode"]
            ).replace(":","-")
            QuerySet1["Name"] = (
                QuerySet[i]["ItemCode"].replace(":","-") + "-" + QuerySet[i]["AccountCode"]
            ).replace(":","-")

            QuerySet1["Type"] = "NonInventory"
            QuerySet1["TrackQtyOnHand"] = False

            for q1 in range(0, len(qbo_coa)):
                if "AcctNum" in qbo_coa[q1]:
                    if QuerySet[i]["AccountCode"] == qbo_coa[q1]["AcctNum"]:
                        QuerySet3["value"] = qbo_coa[q1]["Id"]
                        QuerySet3["name"] = qbo_coa[q1]["Name"]

            QuerySet1["ExpenseAccountRef"] = QuerySet3
            QuerySet1["IncomeAccountRef"] = QuerySet3

            payload = json.dumps(QuerySet1)
            response = requests.request("POST", url, headers=headers, data=payload)
            
            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
            elif response.status_code == 400:
                res1 = json.loads(response.text)
           
    except Exception as ex:
        logging.error(ex, exc_info=True)

