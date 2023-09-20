import json
import traceback

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo



def add_xero_duplicate_chart_account(job_id,task_id):
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"

        xero_classified_coa = db["xero_classified_coa"]
        Collection = db["duplicate_coa"]
        x = xero_classified_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        a = data

        b = []
        for i in range(0, len(a)):
            b.append(a[i]["Name"])

        a1 = {i: b.count(i) for i in b}

        b = []
        for i1 in a1.keys():
            if a1[i1] > 1:
                b.append(i)

        c1 = []

        for j in range(0, len(b)):
            for i in range(0, len(a)):
                if (a[i]["AcctNum"] is not None) and (a[i]["AcctNum"] != ""):
                    if "AccountType" in a[i]:
                        e = {}
                        if b[j] == a[i]["Name"]:
                            e["Name"] = a[i]["Name"] + "-" + a[i]["AcctNum"]
                            e["AcctNum"] = a[i]["AcctNum"]
                            e["AccountType"] = a[i]["AccountType"]
                            e["AccountSubType"] = a[i]["AccountSubType"]
                            c1.append(e)

        Collection.insert_many(c1)

        duplicate_coa = db["duplicate_coa"]
        x = duplicate_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        QuerySet1 = data
        for j in range(0, len(QuerySet1)):
            _id = QuerySet1[j]['_id']
            task_id = QuerySet1[j]['task_id']
            
            try:
                payload = json.dumps(QuerySet1[j])
                post_data_in_qbo(url, headers, payload,db["duplicate_coa"],_id, job_id,task_id, QuerySet1[j]["Name"])
                    
            except Exception as ex:
                pass

    except Exception as ex:
        traceback.print_exc()
        


def update_xero_existing_chart_account(job_id,task_id):
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"

        xero_classified_coa = db["xero_classified_coa"]
        qbo_coa = db["QBO_COA"]
        existing_coa = db["existing_coa"]

        xero_classified_coa = xero_classified_coa.find({"job_id": job_id})
        xero_classified_coa1 = []
        for p1 in xero_classified_coa:
            xero_classified_coa1.append(p1)

        qbo_coa = qbo_coa.find({"job_id": job_id})
        qbo_coa1 = []
        for p2 in qbo_coa:
            qbo_coa1.append(p2)

        existing = []
        for j in range(0, len(xero_classified_coa1)):
            for j1 in range(0, len(qbo_coa1)):
                if (
                    xero_classified_coa1[j]["Name"].lower().strip()
                    == qbo_coa1[j1]["FullyQualifiedName"].lower().strip()
                ):
                    existing.append(xero_classified_coa1[j])
                else:
                    pass

        existing_coa.insert_many(existing)

        existing_coa1 = db["existing_coa"]
        x = existing_coa1.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        QuerySet1 = data
        for j3 in range(0, len(QuerySet1)):
            _id = QuerySet1[j3]['_id']
            task_id = QuerySet1[j3]['task_id']
            try:
                if (QuerySet1[j3]["AcctNum"] is not None) and (
                    QuerySet1[j3]["AcctNum"] != ""
                ):
                    e = {}
                    e["Name"] = QuerySet1[j3]["Name"]
                    e["AcctNum"] = QuerySet1[j3]["AcctNum"]
                    for j4 in range(0, len(qbo_coa1)):
                        if (
                            QuerySet1[j3]["Name"].lower().strip()
                            == qbo_coa1[j4]["FullyQualifiedName"].lower().strip()
                        ):
                            e["AccountType"] = qbo_coa1[j4]["AccountType"]
                            e["AccountSubType"] = qbo_coa1[j4]["AccountSubType"]
                            e["SyncToken"] = qbo_coa1[j4]["SyncToken"]
                            e["Id"] = qbo_coa1[j4]["Id"]

                    payload = json.dumps(e)
                    post_data_in_qbo(url, headers, payload,db["existing_coa"],_id, job_id,task_id, QuerySet1[j3]["Name"])
                else:
                    print("Acct Num Missing")  

            except Exception as ex:
                pass

    except Exception as ex:
        traceback.print_exc()
        
