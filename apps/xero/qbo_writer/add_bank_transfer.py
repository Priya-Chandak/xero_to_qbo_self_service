from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.home.models import Jobs, JobExecutionStatus
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo
from apps.util.log_file import log_config
import logging


def add_xero_bank_transfer(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()

        if start_date != '' and end_date != '':
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(
            job_id)
        url = f"{base_url}/transfer?minorversion={minorversion}"

        xero_bank_transfer = dbname['xero_bank_transfer'].find({'job_id':job_id})

        xero_bank_transfer1 = [p1 for p1 in xero_bank_transfer]
        QuerySet1 = xero_bank_transfer1

        QBO_COA = dbname['QBO_COA'].find({'job_id':job_id})
        QBO_coa = [p2 for p2 in QBO_COA]

        for item in QuerySet1:
            _id = item['_id']
            task_id = item['task_id']
            FromAccountRef = {}
            ToAccountRef = {}
            QuerySet2 = {}

            QuerySet2['Amount'] = item['Amount']
            if 'Memo' in item:
                if item['Memo'] != None:
                    QuerySet2['PrivateNote'] = item['Memo'] + \
                        "-" + item['TransferNumber']
            else:
                QuerySet2['PrivateNote'] = item['TransferNumber']
            QuerySet2['TxnDate'] = item['Date']

            for account in QBO_coa:
                if item['FromAccountName'].lower().strip() == account['Name'].lower().strip():
                    FromAccountRef['name'] = account['Name']
                    FromAccountRef['value'] = account['Id']

                if item['ToAccountName'].lower().strip() == account['Name'].lower().strip():
                    ToAccountRef['name'] = account['Name']
                    ToAccountRef['value'] = account['Id']

            QuerySet2['FromAccountRef'] = FromAccountRef
            QuerySet2['ToAccountRef'] = ToAccountRef

            payload = json.dumps(QuerySet2)
            xero_bank_transfer_date = item["Date"][0:10]
            xero_bank_transfer_date1 = datetime.strptime(xero_bank_transfer_date, '%Y-%m-%d')
            if start_date != '' and end_date != '':
                if (xero_bank_transfer_date1 >= start_date1) and (xero_bank_transfer_date1 <= end_date1):
                    post_data_in_qbo(url, headers, payload, dbname['xero_bank_transfer'], _id, job_id, task_id,
                                     item['TransferNumber'])
                else:
                    print("No Bank Transfer Available")
            else:
                post_data_in_qbo(url, headers, payload, dbname['xero_bank_transfer'], _id, job_id, task_id,
                                 item['TransferNumber'])

    except Exception as ex:
        logging.error(ex, exc_info=True)
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
