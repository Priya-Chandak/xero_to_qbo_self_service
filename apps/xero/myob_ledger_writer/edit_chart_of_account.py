import asyncio
import json
import sys

from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import update_data_in_myob


def get_duplicate_chart_of_account_myob(job_id, task_id):
    try:
        db = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        chart_of_account1 = db['chart_of_account']
        xero_coa = db['xero_coa']
        existing_coa1 = db['existing_coa_myob']

        x = xero_coa.find({"job_id": job_id})
        xero_coa1 = []
        for k in x:
            xero_coa1.append(k)

        chart_of_account1 = chart_of_account1.find({"job_id": job_id})
        chart_of_account = []
        for p1 in chart_of_account1:
            chart_of_account.append(p1)

        existing1 = []

        for j in range(0, len(chart_of_account)):
            for j1 in range(0, len(xero_coa1)):
                if chart_of_account[j]["IsHeader"] != True:
                    a1 = {}
                    if chart_of_account[j]['Name'].lower().strip() == xero_coa1[j1]['Name'].lower().strip():
                        a1 = {"job_id": job_id, "task_id": task_id, "is_pushed": 0, "table_name": "chart_of_account",
                              "error": None}
                        a1['UID'] = chart_of_account[j]['UID']
                        a1['Name'] = chart_of_account[j]['Name']
                        a1['IsHeader'] = chart_of_account[j]['IsHeader']
                        a1['TaxCode'] = chart_of_account[j]['TaxCode']
                        a1['ParentAccount'] = chart_of_account[j]['ParentAccount']
                        a1['RowVersion'] = chart_of_account[j]['RowVersion']

                        a1['FullyQualifiedName'] = xero_coa1[j1]['Name']
                        # a1['Classification'] = xero_coa1[j1]['Classification']
                        a1['Type'] = chart_of_account[j]['Account_Type']

                        if a1['Type'] in ["Bank", "account receivable", "Other current asset", "Fixed asset",
                                          "OtherAsset"]:
                            main_acc = "1-"
                        elif a1['Type'] in ["Credit card", "account payable", "Other current liability",
                                            "Long term liability", "Other liability"]:
                            main_acc = "2-"
                        elif a1['Type'] in ["Equity"]:
                            main_acc = "3-"
                        elif a1['Type'] in ["Income"]:
                            main_acc = "4-"
                        elif a1['Type'] in ["Cost of sales"]:
                            main_acc = "5-"
                        elif a1['Type'] in ["Expense"]:
                            main_acc = "6-"
                        elif a1['Type'] in ["OtherIncome"]:
                            main_acc = "7-"
                        elif a1['Type'] in ["Other expense"]:
                            main_acc = "8-"

                        if "Code" in xero_coa1[j1]:
                            if len(str(xero_coa1[j1]['Code'])) == 3:
                                d1 = "0" + str(xero_coa1[j1]['Code'])
                                a1['DisplayID'] = chart_of_account[j]['DisplayId'].replace(
                                    chart_of_account[j]['DisplayId'][-4:], f"{d1}")

                            else:
                                a1["DisplayID"] = chart_of_account[j]['DisplayId'].replace(
                                    chart_of_account[j]['DisplayId'][-4:], f"{xero_coa1[j1]['Code']}")
                                a1['Number'] = xero_coa1[j1]['Code']


                        else:
                            a1['DisplayID'] = f"{main_acc}" + 9000 + j
                            a1['Number'] = 9000 + j

                        existing1.append(a1)
        existing_coa1.insert_many(existing1)
        step_name = "Reading data from xero edit chart of account"
        write_task_execution_step(task_id, status=1, step=step_name)


    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def update_existing_chart_account_xero_myob(job_id, task_id):
    try:

        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        existing_coa = dbname['existing_coa_myob']

        existing_coa_myob = existing_coa.find({"job_id": job_id})
        existing_coa_myob1 = []
        for k in existing_coa_myob:
            existing_coa_myob1.append(k)

        for i in range(0, len(existing_coa_myob1)):
            _id = existing_coa_myob1[i]["_id"]
            task_id = existing_coa_myob1[i]["task_id"]
            existing_coa_myob1[i].pop("_id")
            existing_coa_myob1[i].pop("job_id")
            existing_coa_myob1[i].pop("is_pushed")
            existing_coa_myob1[i].pop("error")
            existing_coa_myob1[i].pop("task_id")
            existing_coa_myob1[i].pop("table_name")
            QuerySet1 = existing_coa_myob1[i]

            payload = json.dumps(QuerySet1)

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/GeneralLedger/account/{existing_coa_myob1[i]['UID']}"
            asyncio.run(update_data_in_myob(url, headers, payload, dbname['existing_coa_myob'], _id, job_id, task_id,
                                            existing_coa_myob1[i]['Name']))





    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
