from ast import Break

import requests
from pymongo import MongoClient

from apps.mmc_settings.all_settings import get_settings_qbo


def get_qbo_archived_coa(job_id, task_id):
    try:
        myclient = MongoClient("mongodb://localhost:27017/")
        db1 = myclient["MMC"]
        QBO_ARCHIVED_COA1 = db1['QBO_ARCHIVED_COA']
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db1['QBO_ARCHIVED_COA'].count_documents({'job_id': job_id})

        payload = f"select * from account where Active=false  startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['QueryResponse']['account']

        archivedcoa = []
        for archived_coa in JsonResponse1:
            archived_coa['job_id'] = job_id
            archived_coa['task_id'] = task_id
            archived_coa['error'] = None
            archived_coa['is_pushed'] = 0
            archived_coa['table_name'] = "QBO_ARCHIVED_COA"

            archivedcoa.append(archived_coa)

        QBO_ARCHIVED_COA1.insert_many(archivedcoa)

        if JsonResponse['QueryResponse']['maxResults'] < 1000:
            Break
        else:
            get_qbo_archived_coa(job_id)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
