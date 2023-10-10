from ast import Break

import requests

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database


def get_qbo_archived_customer(job_id, task_id):
    try:
        db1 = get_mongodb_database()
        QBO_ARCHIVED_CUSTOMER1 = db1['QBO_ARCHIVED_CUSTOMER']
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db1['QBO_ARCHIVED_CUSTOMER'].count_documents({'job_id': job_id})

        payload = f"select * from Customer where Active=false startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['QueryResponse']['Customer']

        archivedcustomer = []
        for archived_customer in JsonResponse1:
            archived_customer['job_id'] = job_id
            archived_customer['task_id'] = task_id
            archived_customer['error'] = None
            archived_customer['is_pushed'] = 0
            archived_customer['table_name'] = "QBO_ARCHIVED_COA"

            archivedcustomer.append(archived_customer)

        QBO_ARCHIVED_CUSTOMER1.insert_many(archivedcustomer)

        if JsonResponse['QueryResponse']['maxResults'] < 1000:
            Break
        else:
            get_qbo_archived_customer(job_id)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
