import json
import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_duplicate_chart_account(job_id,task_id):
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"

        classified_coa = db["classified_coa"]
        Collection = db["duplicate_coa"]
        x = classified_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        a = data

        b = []
        for i in range(0, len(a)):
            b.append(a[i]["Name"].lower())

        a1 = {i: b.count(i) for i in b}

        b = []
        for i in a1.keys():
            if a1[i] > 1:
                b.append(i)

        c1 = []

        for j in range(0, len(b)):
            for i in range(0, len(a)):
                e = {}
                if b[j].lower() == a[i]["Name"].lower():
                    e['job_id'] = job_id
                    e['task_id'] = task_id
                    e['error'] = None
                    e['is_pushed'] = 0
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
            try:
                _id=QuerySet1[j]['_id']
                task_id=QuerySet1[j]['task_id']
                    
                QuerySet1[j].pop('job_id')
                QuerySet1[j].pop('_id')
                QuerySet1[j].pop('task_id')
                QuerySet1[j].pop('error')
                QuerySet1[j].pop('is_pushed')
                payload = json.dumps(QuerySet1[j])
                print(payload)
                post_data_in_qbo(url, headers, json.dumps(QuerySet1[j]),Collection,_id, job_id,task_id, QuerySet1[j]["Name"])
            
            except Exception as ex:
                print(ex)

    except Exception as ex:
        traceback.print_exc()
        


def add_xero_duplicate_chart_account(job_id):
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"

        classified_coa = db["classified_coa"]
        Collection = db["duplicate_coa"]
        x = classified_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        a = data

        b = []
        for i in range(0, len(a)):
            b.append(a[i]["Name"])

        a1 = {i: b.count(i) for i in b}

        b = []
        for i in a1.keys():
            if a1[i] > 1:
                b.append(i)

        c1 = []

        for j in range(0, len(b)):
            for i in range(0, len(a)):
                _id=a[i]['_id']
                task_id=a[i]['task_id']
                    
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
            try:
                QuerySet1[j].pop("_id")
                post_data_in_qbo(url, headers, json.dumps(QuerySet1[j]),Collection,_id, job_id,task_id, QuerySet1[j]["Name"])
            except Exception as ex:
                pass
    except Exception as ex:
        traceback.print_exc()
        


def update_qbo_existing_chart_account(job_id,task_id):
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/account?minorversion={minorversion}"

        classified_coa = db["classified_coa"]
        qbo_coa = db["QBO_COA"]
        existing_coa = db["existing_coa_qbo"]

        classified_coa = classified_coa.find({"job_id": job_id})
        classified_coa1 = []
        for p1 in classified_coa:
            classified_coa1.append(p1)

        qbo_coa = qbo_coa.find({"job_id": job_id})
        qbo_coa1 = []
        for p2 in qbo_coa:
            qbo_coa1.append(p2)

        existing = []

        for j in range(0, len(classified_coa1)):
            for j1 in range(0, len(qbo_coa1)):
                a1 = {}
                if (
                        classified_coa1[j]["Name"].lower().strip()
                        == qbo_coa1[j1]["FullyQualifiedName"].lower().strip()
                ):
                    _id=classified_coa1[j]['_id']
                    task_id=classified_coa1[j]['task_id']
                    a1["Name"] = classified_coa1[j]["Name"]
                    a1["AcctNum"] = classified_coa1[j]["AcctNum"]
                    a1["AccountType"] = classified_coa1[j]["AccountType"]
                    a1["AccountSubType"] = classified_coa1[j]["AccountSubType"]
                    a1["Id"] = qbo_coa1[j1]["Id"]
                    a1["SyncToken"] = qbo_coa1[j1]["SyncToken"]
                    existing.append(a1)
                else:
                    pass
        existing_coa.insert_many(existing)
        existing_coa = db["existing_coa_qbo"]
        x = existing_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)
        QuerySet1 = data
        for j3 in range(0, len(QuerySet1)):
            try:
                QuerySet1[j3].pop("_id")
                post_data_in_qbo(url, headers, json.dumps(QuerySet1[j3]),existing_coa,_id, job_id,task_id, QuerySet1[j3]["Name"])
            except Exception as ex:
                pass
    except Exception as ex:
        traceback.print_exc()
        
