import sys

import requests

from apps.home.data_util import get_job_details
from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


def get_manual_journal(job_id, task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        Collection = dbname["xero_manual_journal"]

        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/ManualJournals?page=1"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/ManualJournals?where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["ManualJournals"]
            if len(r2) > 0:
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                arr = []
                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        url = f"{base_url}/ManualJournals?page={pages}"
                    else:
                        url = f"{base_url}/ManualJournals?page={pages}&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

                    response = requests.request("GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["ManualJournals"]

                    for i in range(0, len(JsonResponse1)):
                        if JsonResponse1[i]["Status"] == "POSTED":
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["table_name"] = "xero_manual_journal"
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["payload"] = None
                            QuerySet["Date"] = JsonResponse1[i]["Date"]
                            QuerySet["Status"] = JsonResponse1[i]["Status"]
                            QuerySet["ManualJournalID"] = JsonResponse1[i]["ManualJournalID"]
                            QuerySet["Narration"] = JsonResponse1[i]["Narration"]
                            QuerySet["LineAmountTypes"] = JsonResponse1[i]["LineAmountTypes"]

                            for j in range(0, len(JsonResponse1[i]["JournalLines"])):
                                QuerySet1 = {}
                                if "Description" in JsonResponse1[i]["JournalLines"][j]:
                                    QuerySet1["Description"] = JsonResponse1[i]["JournalLines"][
                                        j
                                    ]["Description"]
                                QuerySet1["TaxType"] = JsonResponse1[i]["JournalLines"][j][
                                    "TaxType"
                                ]
                                QuerySet1["TaxAmount"] = JsonResponse1[i]["JournalLines"][j][
                                    "TaxAmount"
                                ]
                                QuerySet1["LineAmount"] = JsonResponse1[i]["JournalLines"][j][
                                    "LineAmount"
                                ]
                                QuerySet1["AccountCode"] = JsonResponse1[i]["JournalLines"][j][
                                    "AccountCode"
                                ]
                                QuerySet1["AccountID"] = JsonResponse1[i]["JournalLines"][j][
                                    "AccountID"
                                ]
                                if 'Tracking' in JsonResponse1[i]["JournalLines"][j] and len(JsonResponse1[i]["JournalLines"][j]['Tracking'])>0:
                                    QuerySet1["TrackingID"]=JsonResponse1[i]["JournalLines"][j]['Tracking'][0]['Option']
                                else:
                                    QuerySet1["TrackingID"]=None
                                    
                                QuerySet["Line"].append(QuerySet1)

                            arr.append(QuerySet)

                if len(arr) > 0:
                    Collection.insert_many(arr)

                step_name = "Reading data from xero manual journal"
                write_task_execution_step(task_id, status=1, step=step_name)


    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
