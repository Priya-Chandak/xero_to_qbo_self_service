import traceback

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


def get_xero_employee(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        Collection = dbname["xero_employee"]
        payload, base_url, headers = get_settings_xero(job_id)

        main_url = "https://api.xero.com/payroll.xro/1.0/Employees"
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        r1 = response1.json()
        r2 = r1["Employees"]
        no_of_records = len(r2)
        no_of_pages = (no_of_records // 100) + 1

        arr = []
        for pages in range(1, no_of_pages + 1):
            url = f"https://api.xero.com/payroll.xro/1.0/Employees?page={pages}"
            response = requests.request("GET", url, headers=headers, data=payload)
            JsonResponse = response.json()
            JsonResponse1 = JsonResponse["Employees"]

            for i in range(0, len(JsonResponse1)):
                QuerySet = {}
                QuerySet["job_id"] = job_id
                QuerySet["task_id"] = task_id
                QuerySet["error"] = None
                QuerySet["payload"] = None
                QuerySet["table_name"] = "xero_employee"
                QuerySet["is_pushed"] = 0
                QuerySet["EmployeeID"] = JsonResponse1[i]["EmployeeID"]
                QuerySet["FirstName"] = JsonResponse1[i]["FirstName"]
                QuerySet["LastName"] = JsonResponse1[i]["LastName"]
                QuerySet["Status"] = JsonResponse1[i]["Status"]
                QuerySet["Email"] = JsonResponse1[i]["Email"]
                QuerySet["DateOfBirth"] = JsonResponse1[i]["DateOfBirth"]
                QuerySet["Gender"] = JsonResponse1[i]["Gender"]
                QuerySet["Phone"] = JsonResponse1[i]["Phone"]
                QuerySet["Mobile"] = JsonResponse1[i]["Mobile"]
                QuerySet["StartDate"] = JsonResponse1[i]["StartDate"]

                arr.append(QuerySet)

        if dbname["xero_employee"].count_documents({}) == no_of_records:
            pass
        else:
            Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()
        
