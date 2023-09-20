from apps.home.data_util import update_task_execution_status, write_task_execution_step
from apps.myob.delete_apis import *

from apps.functiondata_delete.myob_read_delete.chart_of_account_delete import delete_chart_of_account
from apps.functiondata_delete.myob_read_delete.customer_delete import delete_customer
from apps.functiondata_delete.myob_read_delete.supplier_delete import delete_supplier
from apps.functiondata_delete.myob_read_delete.job_delete import delete_job
from apps.functiondata_delete.myob_read_delete.item_delete import delete_item
from apps.functiondata_delete.myob_read_delete.journal_delete import delete_journal
from apps.functiondata_delete.myob_read_delete.invoice_delete import delete_invoice
from apps.functiondata_delete.myob_read_delete.bill_delete import delete_bill
from apps.functiondata_delete.myob_read_delete.bank_transfer_delete import delete_bank_transfer
from apps.functiondata_delete.myob_read_delete.spend_money_delete import delete_spend_money
from apps.functiondata_delete.myob_read_delete.received_money_delete import delete_received_money
from apps.functiondata_delete.myob_read_delete.bill_payment_delete import delete_bill_payment
from apps.functiondata_delete.myob_read_delete.invoice_payment_delete import delete_invoice_payment
from apps.util.db_mongo import get_mongodb_database
from apps.mmc_settings.all_settings import *
import requests
from apps.home.data_util import get_job_details, add_job_status
import json
import asyncio
from apps.util.qbo_util import delete_data_in_myob

def delete_myob_data(job_id,task_function_name):
    dbname = get_mongodb_database()
    start_date, end_date = get_job_details(job_id)
    payload, base_url, headers = get_settings_myob(job_id)
    
    static_function = {"Chart of account" : [f"{base_url}/GeneralLedger/Account",dbname['chart_of_account']],
          "Customer" : [f"{base_url}/Contact/Customer",dbname['customer']],
          "Supplier" : [f"{base_url}/Contact/Supplier",dbname['supplier']],
          "Item" : [f"{base_url}/Inventory/Item",dbname['xero_items']],
          "Spend Money" : [f"{base_url}/Banking/SpendMoneyTxn",dbname['myob_spend_money']],
          "Receive Money" : [f"{base_url}/Banking/ReceiveMoneyTxn",dbname['received_money']],
          "Bank Transfer" : [f"{base_url}/Banking/TransferMoneyTxn",dbname['bank_transfer']],
          "Invoice" : [f"{base_url}/Sale/Invoice/Item",dbname['invoice']],
          "Bill": [f"{base_url}/Purchase/Bill/Item",dbname['bill']],
          "Invoice Payment" : [f"{base_url}/Sale/CustomerPayment",dbname['invoice_payment']],
          "Bill Payment" :[f"{base_url}/Sale/SupplierPayment",dbname['bill_payment']],
          "Journal":[f"{base_url}/GeneralLedger/GeneralJournal",dbname['manual_journal']],
          "Job":[f"{base_url}/GeneralLedger/Category",dbname['job']],
          }

    function_url = static_function[task_function_name][0]
    table_name = str(task_function_name).replace(" ","")
    mongo_table = dbname[f'deleted_myob_{table_name}']
    no_of_records = dbname[f'deleted_myob_{task_function_name}'].count_documents({'job_id':job_id})
    
    if start_date == "" and end_date == "":
        url = f"{function_url}?$top=1000&$skip={no_of_records}"
    else:
        url = f"{function_url}?$top=1000&$skip={no_of_records}&$filter=Date ge datetime'{start_date[0:10]}' and Date le datetime'{end_date[0:10]}'"

    payload = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)

    a=response.json()
    a1=a['Items']

    b=[]
    
    c=[]
    for i in range(0,len(a1)):
        e={}
        e['job_id'] = job_id
        e['payload'] = a1[i]
        c.append(e)
        b.append(a1[i]['UID'])

    print(len(b))
    mongo_table.insert_many(c)
    print("data added")

    for j in range(0,len(b)):
        url = f"{function_url}/{b[j]}"
        uid = b[j]
        print(url)
        payload = ""
        
        response = requests.request("DELETE", url, headers=headers, data=payload)
        print(response)    


       

    