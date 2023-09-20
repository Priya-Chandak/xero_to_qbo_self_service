import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database


def get_accountright_employee(job_id):
    try:
        db = get_mongodb_database()
        no_of_records = db["accountright_employee"].count_documents({})
        payload, base_url, headers = get_settings_myob(job_id)
        url1 = f"{base_url}/Contact/Employee/?$top=100&$skip={no_of_records}"
        url2 = f"{base_url}/Payroll/Timesheet"
        url3 = f"{base_url}/Contact/EmployeePayrollDetails"

        Collection = db["accountright_employee"]
        response1 = requests.request("GET", url1, headers=headers, data=payload)
        response2 = requests.request("GET", url2, headers=headers, data=payload)
        response3 = requests.request("GET", url3, headers=headers, data=payload)

        JsonResponse1 = response1.json()
        JsonResponse2 = response2.json()
        JsonResponse3 = response3.json()

        arr = []
        for i in range(0, len(JsonResponse1["Items"])):
            QuerySet = {}
            QuerySet['job_id']=job_id
            QuerySet = JsonResponse1["Items"][i]
            QuerySet = JsonResponse2["Items"][i]
            QuerySet = JsonResponse3["Items"][i]
            arr.append(QuerySet)

        Collection.insert_many(arr)

        if JsonResponse1["NextPageLink"] is not None:
            get_accountright_employee(job_id)

        else:
            Break

    except Exception as ex:
        traceback.print_exc()
        
