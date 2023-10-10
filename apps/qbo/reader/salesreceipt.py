from ast import Break

import requests
from pymongo import MongoClient

from apps.mmc_settings.all_settings import get_settings_qbo


def get_qbo_sales_receipt(job_id, task_id):
    try:
        myclient = MongoClient("mongodb://localhost:27017/")
        db1 = myclient["MMC"]
        QBO_SALES_RECEIPT1 = db1['QBO_SALES_RECEIPT']
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db1['QBO_SALES_RECEIPT'].count_documents({'job_id': job_id})

        payload = f"select * from salesreceipt startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['QueryResponse']['SalesReceipt']

        salesreceipt = []
        for sales_receipt in JsonResponse1:
            sales_receipt['job_id'] = job_id
            sales_receipt['task_id'] = task_id
            sales_receipt['error'] = None
            sales_receipt['is_pushed'] = 0
            sales_receipt['table_name'] = "QBO_SALES_RECEIPT"

            salesreceipt.append(sales_receipt)

        QBO_SALES_RECEIPT1.insert_many(salesreceipt)

        if JsonResponse['QueryResponse']['maxResults'] < 1000:
            Break
        else:
            get_qbo_sales_receipt(job_id)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
