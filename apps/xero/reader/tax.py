import traceback

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import  write_task_execution_step,update_task_execution_status
import sys



def get_xero_tax(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        Collection = dbname["xero_taxrate"]
        payload, base_url, headers = get_settings_xero(job_id)

        main_url = f"{base_url}/TaxRates"
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        r1 = response1.json()
        r2 = r1["TaxRates"]
        no_of_records = dbname["xero_taxrate"].count_documents({'job_id':job_id})
        no_of_pages = (no_of_records // 100) + 1

        arr = []
        for pages in range(1, no_of_pages + 1):
            url = f"{base_url}/TaxRates?pages={pages}"
            response = requests.request("GET", url, headers=headers, data=payload)
            JsonResponse = response.json()
            JsonResponse1 = JsonResponse["TaxRates"]

            for i in range(0, len(JsonResponse1)):
                QuerySet = {"job_id": job_id, "task_id": task_id, "is_pushed": 0,"error":None, "table_name": "xero_taxrate",
                            "Name": JsonResponse1[i]["Name"], "TaxType": JsonResponse1[i]["TaxType"],
                            "TaxName": JsonResponse1[i]["TaxComponents"][0]["Name"],
                            "TaxRate": JsonResponse1[i]["TaxComponents"][0]["Rate"]}

                arr.append(QuerySet)

        Collection.insert_many(arr)
        
        step_name = "Reading data from xero tax"
        write_task_execution_step(task_id, status=1, step=step_name)

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
        
