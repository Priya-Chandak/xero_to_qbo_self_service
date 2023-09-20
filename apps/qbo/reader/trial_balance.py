import traceback

import pandas as pd
import requests

from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database


def get_qbo_trial_balance(job_id):
    try:
        start_date, end_date = get_job_details(job_id)
        db = get_mongodb_database()
        QBO_Trial_Balance = db["QBO_Trial_Balance"]
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/reports/TrialBalance?start_date={start_date}&end_date={end_date}&minorversion{minorversion}"
        payload = {}
        response = requests.request("GET", url, headers=report_headers, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = []
        JsonResponse1.append(JsonResponse)
        QBO_Trial_Balance.insert_many(JsonResponse1)
    except Exception as ex:
        traceback.print_exc()
        


def export_qbo_trial_balance(job_id):
    try:
        path = "/home/ubuntu/mmc-data-transfer/apps/qbo/reader"
        db = get_mongodb_database()
        report = db["QBO_Trial_Balance"].find()

        report1 = []
        for p1 in report:
            report1.append(p1)

        StartPeriod = report1[0]["Header"]["StartPeriod"]
        EndPeriod = report1[0]["Header"]["EndPeriod"]

        col = ["id"]

        for i in range(0, len(report1[0]["Columns"]["Column"])):
            if report1[0]["Columns"]["Column"][i]["ColTitle"] == "":
                column1 = report1[0]["Columns"]["Column"][i]["ColType"]
            else:
                column1 = report1[0]["Columns"]["Column"][i]["ColTitle"]
            col.append(column1)

        acc_name1 = []
        acc_id1 = []
        credit = []
        debit = []
        for j in range(0, len(report1[0]["Rows"]["Row"])):
            if "ColData" in report1[0]["Rows"]["Row"][j]:
                acc_name = report1[0]["Rows"]["Row"][j]["ColData"][0]["value"]
                acc_id = report1[0]["Rows"]["Row"][j]["ColData"][0]["id"]
                acc_name1.append(acc_name)
                acc_id1.append(acc_id)

            if "ColData" in report1[0]["Rows"]["Row"][j]:
                debit1 = report1[0]["Rows"]["Row"][j]["ColData"][1]["value"]
                debit.append(debit1)

            if "ColData" in report1[0]["Rows"]["Row"][j]:
                credit1 = report1[0]["Rows"]["Row"][j]["ColData"][2]["value"]
                credit.append(credit1)

        d = {"id": acc_id1, "account": acc_name1, "Debit": debit, "Credit": credit}
        df = pd.DataFrame(d)
        df.to_excel(f"{path}/{StartPeriod}-{EndPeriod}-Trial_Balance.xlsx", index=False)

    except Exception as ex:
        traceback.print_exc()
        
