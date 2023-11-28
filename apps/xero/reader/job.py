import sys

import requests

from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import *
from apps.myconstant import JOB_STATUS_FAILED
from apps.util.db_mongo import get_mongodb_database


def get_xero_job(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        xero_job = dbname["xero_job"]
        payload, base_url, headers = get_settings_xero(job_id)

        main_url = "https://api.xero.com/api.xro/2.0/TrackingCategories"
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        r1 = response1.json()
        r2 = r1["TrackingCategories"]
        no_of_records = len(r2)
        no_of_pages = (no_of_records // 100) + 1

        arr = []
        for pages in range(1, no_of_pages + 1):
            url = f"https://api.xero.com/api.xro/2.0/TrackingCategories?page={pages}"
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                JsonResponse = response.json()
                if len(JsonResponse['TrackingCategories']) > 0:
                    JsonResponse1 = JsonResponse["TrackingCategories"][0]["Options"]
                    arr = []
                    for i in range(0, len(JsonResponse1)):
                        QuerySet = {"job_id": job_id, "task_id": task_id, "is_pushed": 0, "table_name": "xero_job",
                                    'error': None, 'payload': None,
                                    "UID": JsonResponse1[i]["TrackingOptionID"], "Name": JsonResponse1[i]["Name"]}
                        arr.append(QuerySet)
                    if len(arr)>0:
                        xero_job.insert_many(arr)
                else:
                    print("No data available")
            else:
                return JOB_STATUS_FAILED
        step_name = "Reading data from job"
        write_task_execution_step(task_id, status=1, step=step_name)

    except Exception as ex:
        print("------------------------------")
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
