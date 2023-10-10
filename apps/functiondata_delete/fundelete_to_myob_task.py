import requests

from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


def delete_myob_data(job_id, task_function_name):
    dbname = get_mongodb_database()
    start_date, end_date = get_job_details(job_id)
    payload, base_url, headers = get_settings_myob(job_id)

    static_function = {"Chart of account": [f"{base_url}/GeneralLedger/Account", dbname['chart_of_account']],
                       "Customer": [f"{base_url}/Contact/Customer", dbname['customer']],
                       "Supplier": [f"{base_url}/Contact/Supplier", dbname['supplier']],
                       "Item": [f"{base_url}/Inventory/Item", dbname['xero_items']],
                       "Spend Money": [f"{base_url}/Banking/SpendMoneyTxn", dbname['myob_spend_money']],
                       "Receive Money": [f"{base_url}/Banking/ReceiveMoneyTxn", dbname['received_money']],
                       "Bank Transfer": [f"{base_url}/Banking/TransferMoneyTxn", dbname['bank_transfer']],
                       "Invoice": [f"{base_url}/Sale/Invoice/Item", dbname['invoice']],
                       "Bill": [f"{base_url}/Purchase/Bill/Item", dbname['bill']],
                       "Invoice Payment": [f"{base_url}/Sale/CustomerPayment", dbname['invoice_payment']],
                       "Bill Payment": [f"{base_url}/Sale/SupplierPayment", dbname['bill_payment']],
                       "Journal": [f"{base_url}/GeneralLedger/GeneralJournal", dbname['manual_journal']],
                       "Job": [f"{base_url}/GeneralLedger/Category", dbname['job']],
                       }

    function_url = static_function[task_function_name][0]
    table_name = str(task_function_name).replace(" ", "")
    mongo_table = dbname[f'deleted_myob_{table_name}']
    no_of_records = dbname[f'deleted_myob_{task_function_name}'].count_documents({'job_id': job_id})

    if start_date == "" and end_date == "":
        url = f"{function_url}?$top=1000&$skip={no_of_records}"
    else:
        url = f"{function_url}?$top=1000&$skip={no_of_records}&$filter=Date ge datetime'{start_date[0:10]}' and Date le datetime'{end_date[0:10]}'"

    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    a = response.json()
    a1 = a['Items']

    b = []

    c = []
    for i in range(0, len(a1)):
        e = {}
        e['job_id'] = job_id
        e['payload'] = a1[i]
        c.append(e)
        b.append(a1[i]['UID'])

    print(len(b))
    mongo_table.insert_many(c)
    print("data added")

    for j in range(0, len(b)):
        url = f"{function_url}/{b[j]}"
        uid = b[j]
        print(url)
        payload = ""

        response = requests.request("DELETE", url, headers=headers, data=payload)
        print(response)
