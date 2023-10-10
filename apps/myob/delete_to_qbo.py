import json

import requests

from apps.home.data_util import get_job_details
from apps.home.data_util import update_task_execution_status, write_task_execution_step
from apps.util.qbo_util import post_data_in_qbo
from apps.xero.myob_ledger_writer.edit_chart_of_account import *


def delete_qbo_data(job_id, task_function_name, task_id):
    print("inside delete_qbo_data")
    dbname = get_mongodb_database()

    base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

    static_function = {"Chart of account": ['account', 'account', dbname['QBO_COA']],
                       "Customer": ['Customer', 'customer', dbname['QBO_Customer']],
                       "Supplier": ['Vendor', 'vendor', dbname['QBO_Supplier']],
                       "Item": ['Item', 'item', dbname['QBO_Item']],
                       "Spend Money": ['Purchase', 'purchase', dbname['QBO_Spend_Money']],
                       "Receive Money": ['Deposit', 'deposit', dbname['QBO_Received_Money']],
                       "Bank Transfer": ['Transfer', 'transfer', dbname['QBO_Bank_Transfer']],
                       "Invoice": ['Invoice', 'invoice', dbname['QBO_Invoice']],
                       "Invoice CreditNote": ['CreditMemo', 'creditmemo', dbname['QBO_CreditMemo']],
                       "Bill": ['Bill', 'bill', dbname['QBO_Bill']],
                       "Bill VendorCredit": ['VendorCredit', 'vendorcredit', dbname['QBO_VendorCredit']],
                       "Invoice Payment": ['Payment', 'payment', dbname['QBO_Payment']],
                       "Bill Payment": ['BillPayment', 'billpayment', dbname['QBO_Bill_Payment']],
                       "Journal": ['JournalEntry', 'journalentry', dbname['QBO_Journal']]
                       }

    json_object_key = static_function[task_function_name][0]
    print(json_object_key)
    url_object_key = static_function[task_function_name][1]
    table_name = str(task_function_name).replace(" ", "")
    mongo_table = dbname[f'deleted_qbo_{table_name}']
    mongo_table1 = dbname[f'deleted_qbo_{table_name}'].find({'job_id': job_id})
    no_of_records = dbname[f'deleted_qbo_{table_name}'].count_documents({'job_id': job_id})

    url1 = f"{base_url}/query?minorversion=14"
    print(url1)
    start_date, end_date = get_job_details(job_id)

    if start_date != "" and end_date != "":
        payload = (
            f"select * from {json_object_key} WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}' STARTPOSITION {no_of_records} MAXRESULTS 1000"
        )
    else:
        payload = (
            f"select * from {json_object_key} startposition {no_of_records} maxresults 1000"
        )

    response = requests.request("POST", url1, headers=get_data_header, data=payload)
    a = response.json()
    print(response.status_code)

    a1 = a['QueryResponse'][f'{json_object_key}']
    b1 = []

    if json_object_key in ['Customer', 'Supplier', 'Item']:
        for g1 in range(0, len(a1)):
            e = {}
            e['is_pushed'] = 0
            e['Id'] = a1[g1]['Id']
            e['job_id'] = job_id
            e['SyncToken'] = a1[g1]['SyncToken']
            e['sparse'] = True
            e['Active'] = False

            b1.append(e)
        mongo_table.insert_many(b1)
        records_to_delete = []

        for p1 in mongo_table1:
            records_to_delete.append(p1)

        url = f"{base_url}/{url_object_key}/?operation=delete"
        for j in range(0, len(records_to_delete)):
            _id = records_to_delete[j]['_id']
            records_to_delete[j].pop("_id")
            records_to_delete[j].pop("job_id")
            records_to_delete[j].pop("is_pushed")
            payload = json.dumps(records_to_delete[j])
            post_data_in_qbo(url, headers, payload, mongo_table, _id, job_id, task_id, "NA")
            # response = requests.request("POST", url, headers=headers, data=payload)
            # print(response)

    elif json_object_key in ['Bill', 'Invoice', 'CreditMemo', 'VendorCredit', 'Purchase', 'Deposit', 'BillPayment',
                             'Payment', 'JournalEntry', 'Transfer']:
        for g1 in range(0, len(a1)):
            e = {}
            e['is_pushed'] = 0
            e['Id'] = a1[g1]['Id']
            e['job_id'] = job_id
            e['SyncToken'] = a1[g1]['SyncToken']
            b1.append(e)
        mongo_table.insert_many(b1)
        url = f"{base_url}/{url_object_key}/?operation=delete"

        records_to_delete = []

        for p1 in mongo_table1:
            records_to_delete.append(p1)

        for j in range(0, len(records_to_delete)):
            _id = records_to_delete[j]['_id']
            records_to_delete[j].pop("_id")
            records_to_delete[j].pop("job_id")
            records_to_delete[j].pop("is_pushed")
            payload = json.dumps(records_to_delete[j])
            post_data_in_qbo(url, headers, payload, mongo_table, _id, job_id, task_id, "NA")
            # response = requests.request("POST", url, headers=headers, data=payload)
            # print(response)


class DeleteToQbo(object):
    @staticmethod
    def read_data(job_id, task):
        step_name = None
        print(task.function_name)
        try:
            update_task_execution_status(task.id, status=2, task_type="read")
            step_name = f"Reading {task.function_name} data in QBO"
            write_task_execution_step(task.id, status=2, step=step_name)
            write_task_execution_step(task.id, status=1, step=step_name)
            update_task_execution_status(task.id, status=1, task_type="read")


        except Exception as ex:
            write_task_execution_step(task.id, status=0, step=step_name)
            update_task_execution_status(task.id, status=0, task_type="read")
            raise ex

    @staticmethod
    def write_data(job_id, task):
        # step_name = None
        try:
            update_task_execution_status(task.id, status=2, task_type="write")

            step_name = f"Deleting {task.function_name} data in QBO"
            write_task_execution_step(task.id, status=2, step=step_name)
            delete_qbo_data(job_id, task.function_name, task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            update_task_execution_status(task.id, status=1, task_type="write")

        except Exception as ex:
            write_task_execution_step(task.id, status=0, step=step_name)
            update_task_execution_status(task.id, status=0, task_type="read")
            raise ex
