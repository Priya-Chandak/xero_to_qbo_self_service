import json
from apps.util.log_file import log_config
import logging
import traceback
from datetime import date

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo

from apps.util.log_file import log_config
import logging


def add_xero_item(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_item -> add_xero_item")

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
        #     if data1[i]['Name']=='RUBBISH REMOVAL':
        #         d.append(data1[i])

        # QuerySet=d

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
                                if "AccountCode" in QuerySet[i]["SalesDetails"][0]:
                                    qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "AcctNum": QuerySet[i]["SalesDetails"][0]["AccountCode"]}) 
                                    QuerySet3["value"] = qbo_coa_record.get("Id")
                                    QuerySet3["name"] = qbo_coa_record.get("Name")
                        
                                else:
                                    qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "Name": "Sales"}) 
                                    QuerySet3["value"] = qbo_coa_record.get("Id")
                                    QuerySet3["name"] = qbo_coa_record.get("Name")
                        
                        else:
                            qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "Name": "Sales"}) 
                            QuerySet3["value"] = qbo_coa_record.get("Id")
                            QuerySet3["name"] = qbo_coa_record.get("Name")
                        



                    # for q1 in range(0, len(qbo_coa)):
                        if QuerySet[i]["PurchaseDetails"] is not None:
                            if "UnitPrice" in QuerySet[i]["PurchaseDetails"][0]:
                                QuerySet1["PurchaseCost"] = QuerySet[i]["PurchaseDetails"][
                                    0
                                ]["UnitPrice"]

                            if "COGSAccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                                qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "AcctNum": QuerySet[i]["PurchaseDetails"][0]["COGSAccountCode"]}) 
                                QuerySet4["value"] = qbo_coa_record.get("Id")
                                QuerySet4["name"] = qbo_coa_record.get("Name")
                                

                            elif "AccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                                qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "AcctNum": QuerySet[i]["PurchaseDetails"][0]["AccountCode"]}) 
                                QuerySet4["value"] = qbo_coa_record.get("Id")
                                QuerySet4["name"] = qbo_coa_record.get("Name")
                                
                                
                            else:
                                qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "Name": "Purchases"}) 
                                QuerySet4["value"] = qbo_coa_record.get("Id")
                                QuerySet4["name"] = qbo_coa_record.get("Name")
                                
                        else:
                            qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "Name": "Purchases"}) 
                            QuerySet4["value"] = qbo_coa_record.get("Id")
                            QuerySet4["name"] = qbo_coa_record.get("Name")
                                

                    QuerySet1["IncomeAccountRef"] = QuerySet3
                    QuerySet1["ExpenseAccountRef"] = QuerySet4
                
            else:
                QuerySet1["Type"] = "Service"
                QuerySet3 = {}
                QuerySet4 = {}
                if QuerySet[i]["SalesDetails"] is not None:
                    if "UnitPrice" in QuerySet[i]["SalesDetails"][0]:
                        QuerySet1["UnitPrice"] = QuerySet[i]["SalesDetails"][0][
                            "UnitPrice"
                        ]

                    for q1 in range(0, len(qbo_coa)):
                        
                        if "AccountCode" in QuerySet[i]["SalesDetails"][0]:
                            qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "AcctNum": QuerySet[i]["SalesDetails"][0]["AccountCode"]}) 
                            QuerySet3["value"] = qbo_coa_record.get("Id")
                            QuerySet3["name"] = qbo_coa_record.get("Name")
                            
                        else:
                            qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "Name": "Sales"}) 
                            QuerySet3["value"] = qbo_coa_record.get("Id")
                            QuerySet3["name"] = qbo_coa_record.get("Name")
                            
                         
                        if "COGSAccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                            qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "AcctNum": QuerySet[i]["PurchaseDetails"][0]["COGSAccountCode"]}) 
                            QuerySet4["value"] = qbo_coa_record.get("Id")
                            QuerySet4["name"] = qbo_coa_record.get("Name")
                            break

                           
                        elif "AccountCode" in QuerySet[i]["PurchaseDetails"][0]:
                            qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "AcctNum": QuerySet[i]["PurchaseDetails"][0]["AccountCode"]}) 
                            QuerySet4["value"] = qbo_coa_record.get("Id")
                            QuerySet4["name"] = qbo_coa_record.get("Name")
                            
                        else:
                            qbo_coa_record = dbname["QBO_COA"].find_one({"job_id": job_id, "Name": "Purchases"}) 
                            QuerySet4["value"] = qbo_coa_record.get("Id")
                            QuerySet4["name"] = qbo_coa_record.get("Name")
                            

                    QuerySet1["IncomeAccountRef"] = QuerySet3
                    QuerySet1["ExpenseAccountRef"] = QuerySet4


            payload = json.dumps(QuerySet1)
            print(payload)
            id_or_name_value_for_error = QuerySet[i]["Name"] if "Name" in QuerySet[i] else QuerySet[i]['Code']
            post_data_in_qbo(url, headers, payload,xero_items1,_id, job_id,task_id, id_or_name_value_for_error)

            
    except Exception as ex:
        logging.error(ex, exc_info=True)
        

def add_duplicate_item(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_item -> add_duplicate_item")

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
            if 'Name' in a[i]:
                b.append(a[i]["Name"])
        a1 = {i: b.count(i) for i in b}

        b1 = []
        for i1 in a1.keys():
            if a1[i1] > 1:
                b1.append(i1)

        c1 = []

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
        logging.error(ex, exc_info=True)    
