from ast import Break

import requests

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database


def get_qbo_refund_receipt(job_id, task_id):
    print("inside refund")
    try:
        db1 = get_mongodb_database()
        QBO_REFUND_RECEIPT1 = db1['QBO_REFUND_RECEIPT']
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db1['QBO_REFUND_RECEIPT'].count_documents({'job_id': job_id})

        payload = f"select * from refundreceipt startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['QueryResponse']['RefundReceipt']

        refundreceipt = []
        for refund_receipt in JsonResponse1:
            refund_receipt['job_id'] = job_id
            refund_receipt['task_id'] = task_id
            refund_receipt['error'] = None
            refund_receipt['is_pushed'] = 0
            refund_receipt['table_name'] = "QBO_REFUND_RECEIPT"

            refundreceipt.append(refund_receipt)

        QBO_REFUND_RECEIPT1.insert_many(refundreceipt)

        if JsonResponse['QueryResponse']['maxResults'] < 1000:
            Break
        else:
            get_qbo_refund_receipt(job_id)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
