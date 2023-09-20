import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


def delete_chart_of_account(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        Collection = dbname["delete_chart_of_account"]
        no_of_records = dbname["delete_chart_of_account"].count_documents({'job_id':job_id})
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/GeneralLedger/Account?$top=1000&$skip={no_of_records}"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            JsonResponse = response.json()
            JsonResponse1 = JsonResponse["Items"]
            if len(JsonResponse["Items"])>0:

                arr = []
                for i in range(0, len(JsonResponse1)):
                    QuerySet = {"job_id": job_id,"task_id": task_id,"is_pushed":0,"table_name":"delete_chart_of_account","UID": JsonResponse1[i]["UID"]}
                        
                    if JsonResponse1[i]["IsActive"] == True:
                        arr.append(QuerySet)

                Collection.insert_many(arr)

                if JsonResponse["NextPageLink"] is not None:
                    url = JsonResponse["NextPageLink"]
                    delete_chart_of_account(job_id, task_id)
                else:
                    Break

        

        
            
    except Exception as ex:
        traceback.print_exc()
        