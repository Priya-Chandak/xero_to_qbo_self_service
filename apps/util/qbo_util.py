import json
import logging
from datetime import datetime
from flask import render_template, redirect, request, url_for
import asyncio
from apps.mmc_settings.all_settings import *
import math

import requests
from bson import ObjectId
from apps.home.data_util import get_job_details, add_job_status

from apps.home.data_util import get_job_details, update_task_execution_status
from apps.util.db_mongo import get_mongodb_database


def get_data_from_qbo(job_id, task_id, table_name, json_object_key, qbo_object_name, url, header):
    try:
        db = get_mongodb_database()
        start_date, end_date = get_job_details(job_id)
        mongo_table = db[table_name]
        no_of_records = mongo_table.count_documents({"job_id": job_id})
        remaining_records = 1000
        while remaining_records >= 1000:
            # if start_date != "" and end_date != "":
            #     payload = (
            #         f"select * from {qbo_object_name} WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}' STARTPOSITION {no_of_records} MAXRESULTS 1000"
            #        )
            # else:
            #     payload = (
            #         f"select * from {qbo_object_name} startposition {no_of_records} maxresults 1000" 
            #     )
            if start_date != "" and end_date != "":
                if json_object_key in ['Invoice','Purchase','Deposit','Bill','JournalEntry','Transfer','Payment','BillPayment']:
                    payload = (
                        f"select * from {qbo_object_name} WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}' STARTPOSITION {no_of_records} MAXRESULTS 1000"
                    )
                else:
                    payload = (
                        f"select * from {qbo_object_name} startposition {no_of_records} maxresults 1000" 
                    )

            else:
                payload = (
                    f"select * from {qbo_object_name} startposition {no_of_records} maxresults 1000" 
                )

            print(payload)
            response = requests.request("POST", url, headers=header, data=payload)
            if response and response.status_code == 200:
                api_response = response.json()
                print(api_response)
                items = api_response["QueryResponse"][json_object_key]
                if len(items) > 0:
                    items_output = []
                    for item in items:
                        item["job_id"] = job_id
                        item["task_id"] =task_id
                        item["table_name"] =table_name
                        item["error"] =None
                        item["is_pushed"] = 0
                        item["payload"] = None

                        items_output.append(item)
                    
                    mongo_table.insert_many(items_output)
                    no_of_records = no_of_records + api_response["QueryResponse"]["maxResults"]
                    remaining_records = api_response["QueryResponse"]["maxResults"]
            

    except Exception as ex:
        logging.error("Error in get_data_from_qbo", ex)
        raise ex


def post_data_in_qbo(url, headers, payload, table_name, _id,job_id,task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    response_json = json.loads(response.text)
    if response.status_code == 200:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        return "success"
    
    elif response.status_code == 401:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"
    
    elif response.status_code == 400:
        print(response_json)
        table_name.update_one({'_id':ObjectId(_id)}, {"$set": {"error":f"{response_json}"+" - "+f"{id_or_name_value_for_error}"}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"
        
    else:
        print(response_json)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": f"{response_json}"}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"

blank = []


async def post_data_in_myob(url, headers, payload, table_name, _id, job_id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)

    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error":"None"}}, upsert=True)
        return "success"
    
    elif response.status_code == 401:
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"

    elif response.status_code == 400:
        print(payload)
            
        print(response.text)
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {
            "$set": {"error": f"{response_json['Errors']}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"
    
    else:
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": f"{response_json}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"

    print(blank)


async def post_data_in_reckon(url, headers, payload, table_name, _id, job_id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("POST", url, headers=headers, data=payload)
    print(payload)
    print(response.status_code,"statuscode-------------------------")
    print(response.text)
    print(url)
    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":payload}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error":f"{response.text}"}}, upsert=True)
        return "success"
    
    elif response.status_code == 400:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 0}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":payload}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error":f"{response.text}"+" - "+f"{id_or_name_value_for_error}"}}, upsert=True)
        return "error"
    
    elif response.status_code == 401:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 0}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":payload}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error":"Access Token Expired"}+" - "+f"{id_or_name_value_for_error}"}, upsert=True)
        return "unauthorized"
   

async def update_data_in_myob(url, headers, payload, table_name, _id, job_id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.status_code)

    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "None"}}, upsert=True)
        # table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": None}}, upsert=True)

    elif response.status_code == 401:
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)

    elif response.status_code == 400:
        print(response.text)
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {
            "$set": {"error": f"{response_json['Errors'][0]['Message']}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
    else:
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": f"{response_json}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)

    print(blank)


async def update_data_in_myob(url, headers, payload, table_name, _id, job_id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.status_code)
    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)

    elif response.status_code == 401:
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)
        
    elif response.status_code == 400:
        response_json = json.loads(response.text)
        print(response.text)
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {
            "$set": {"error": f"{response_json['Errors'][0]}" + " - " + f"{id_or_name_value_for_error}"}}, upsert=True)
        
    else:
        response_json = json.loads(response.text)
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": f"{response_json}"}}, upsert=True)


def get_start_end_dates_of_job(job_id):
    start_date, end_date = get_job_details(job_id)
    if start_date != "" and end_date != "":
        return datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(
            end_date, "%Y-%m-%d"
        )


def get_pagination_for_records(task_id,table_name):
    page = request.args.get('page', 1, type=int)
    per_page = 200
    collection = table_name
    total_records = collection.count_documents({"task_id":task_id})
    successful_count = collection.count_documents({"$and":[{"is_pushed": 1},{"task_id":task_id}]})
    error_count = collection.count_documents({"$and": [{"is_pushed": 0}, {"task_id": task_id}]})
    data = table_name.find({"$and": [{"is_pushed": 0}, {"task_id": task_id}]}).skip((page - 1) * per_page).limit(per_page)

    return page,per_page,total_records,successful_count,error_count,data


async def delete_data_in_myob(url, headers, payload, table_name, _id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("DELETE", url, headers=headers, data=payload)
    print(response.status_code)
    
    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error":"None"}}, upsert=True)
        return "success"
    
    elif response.status_code == 401:
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"

    elif response.status_code == 400:
        print(response.text)
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {
            "$set": {"error": f"{response_json['Errors']}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"
    
    else:
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": f"{response_json}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload":f"{payload}"}}, upsert=True)
        return "error"



blank = []

def retry_payload_for_xero_to_myob(job_id,payload,_id,task_id,task_function_name):
    dbname = get_mongodb_database()
    
    payload1, base_url, headers = get_settings_myob(job_id)

    static_function = {"Chart of account" : [f"{base_url}/GeneralLedger/Account",dbname['xero_coa']],
          "Customer" : [f"{base_url}/Contact/Customer",dbname['xero_customer']],
          "Supplier" : [f"{base_url}/Contact/Supplier",dbname['xero_supplier']],
          "Item" : [f"{base_url}/Inventory/Item",dbname['xero_items']],
          "Spend Money" : [f"{base_url}/Banking/SpendMoneyTxn",dbname['xero_spend_money']],
          "Receive Money" : [f"{base_url}/Banking/ReceiveMoneyTxn",dbname['xero_receive_money']],
          "Bank Transfer" : [f"{base_url}/Banking/TransferMoneyTxn",dbname['xero_bank_transfer']],
          "Invoice" : [f"{base_url}/Sale/Invoice/Item",dbname['xero_invoice']],
          "Bill": [f"{base_url}/Purchase/Bill/Item",dbname['xero_bill']],
          "Invoice Payment" : [f"{base_url}/Sale/CustomerPayment",dbname['xero_invoice_payment']],
          "Bill Payment" :[f"{base_url}/Purchase/SupplierPayment",dbname['xero_bill_payment']],
          "Journal":[f"{base_url}/GeneralLedger/GeneralJournal",dbname['xero_manual_journal']],
        #   "Existing Chart of account":[f"{base_url}/GeneralLedger/Account",dbname['xero_coa']],
          "Job":[f"{base_url}/GeneralLedger/Category",dbname['xero_job']],
          "Archieved Customer" : [f"{base_url}/Contact/Customer",dbname['xero_archived_customer']],
          "Archieved Supplier" : [f"{base_url}/Contact/Supplier",dbname['xero_archived_supplier']]
          }

    function_name = list(static_function.keys())
    print(function_name)
    
    if task_function_name in function_name:
        print(static_function[task_function_name])
        url = static_function[task_function_name][0]
        tablename = static_function[task_function_name][1]
        id_or_name_value_for_error="NA"
                    
        status=asyncio.run(post_data_in_myob(url, headers, payload, tablename, _id, job_id, task_id,
                                                    id_or_name_value_for_error))
        if status == 'success':
            return 'success'
        else:
            return 'error'    


def retry_payload_for_qbo_to_myob(job_id,payload,_id,task_id,task_function_name):
    dbname = get_mongodb_database()
    
    payload1, base_url, headers = get_settings_myob(job_id)

    static_function = {"Chart of account" : [f"{base_url}/GeneralLedger/Account",dbname['QBO_COA']],
          "Customer" : [f"{base_url}/Contact/Customer",dbname['QBO_Customer']],
          "Supplier" : [f"{base_url}/Contact/Supplier",dbname['QBO_Supplier']],
          "Item" : [f"{base_url}/Inventory/Item",dbname['QBO_Item']],
          "Spend Money" : [f"{base_url}/Banking/SpendMoneyTxn",dbname['QBO_Spend_Money']],
          "Receive Money" : [f"{base_url}/Banking/ReceiveMoneyTxn",dbname['QBO_Received_Money']],
          "Bank Transfer" : [f"{base_url}/Banking/TransferMoneyTxn",dbname['QBO_Bank_Transfer']],
          "Invoice" : [f"{base_url}/Sale/Invoice/Item",dbname['QBO_Invoice']],
          "Invoice CreditNote" : [f"{base_url}/Sale/Invoice/Item",dbname['QBO_Invoice']],
          "Bill": [f"{base_url}/Purchase/Bill/Item",dbname['QBO_Bill']],
          "Bill VendorCredit": [f"{base_url}/Purchase/Bill/Item",dbname['QBO_Bill']],
          "Invoice Payment" : [f"{base_url}/Sale/CustomerPayment",dbname['QBO_Payment']],
          "Bill Payment" :[f"{base_url}/Sale/SupplierPayment",dbname['QBO_Bill_Payment']],
          "Journal":[f"{base_url}/GeneralLedger/GeneralJournal",dbname['QBO_Journal']],
        #   "Existing Chart of account":[f"{base_url}/GeneralLedger/Account",dbname['xero_coa']],
          "Job":[f"{base_url}/GeneralLedger/Category",dbname['QBO_Class']],
          }

    function_name = list(static_function.keys())
    if task_function_name in function_name:
        print(static_function[task_function_name])
        url = static_function[task_function_name][0]
        tablename = static_function[task_function_name][1]
        id_or_name_value_for_error="NA"
                    
        status=asyncio.run(post_data_in_myob(url, headers, payload, tablename, _id, job_id, task_id,
                                                    id_or_name_value_for_error))
        if status == 'success':
            return 'success'
        else:
            return 'error'


def retry_payload_for_excel_to_myob(job_id,payload,_id,task_id,task_function_name):
    dbname = get_mongodb_database()
    
    payload1, base_url, headers = get_settings_myob(job_id)

    static_function = {"COA" : [f"{base_url}/GeneralLedger/Account",dbname['excel_chart_of_account']],
          "Contact" : [f"{base_url}/Contact/Customer",dbname['excel_customer']],
          "Contact" : [f"{base_url}/Contact/Supplier",dbname['excel_supplier']],
          "Item" : [f"{base_url}/Inventory/Item",dbname['excel_item']],
          "Spend Money" : [f"{base_url}/Banking/SpendMoneyTxn",dbname['excel_spend_money']],
          "Receive Money" : [f"{base_url}/Banking/ReceiveMoneyTxn",dbname['excel_receive_money']],
          "Bank Transfer" : [f"{base_url}/Banking/TransferMoneyTxn",dbname['excel_bank_transfer']],
          "Invoice" : [f"{base_url}/Sale/Invoice/Item",dbname['excel_invoice']],
          "Customer return": [f"{base_url}/Sale/Invoice/Item",dbname['excel_bill']],
          "Invoice" : [f"{base_url}/Sale/Invoice/Item",dbname['excel_invoice']],
          "Bill VendorCredit": [f"{base_url}/Purchase/Bill/Item",dbname['excel_bill']],
          "Customer payment" : [f"{base_url}/Sale/CustomerPayment",dbname['excel_invoice_payment']],
          "Supplier return" :[f"{base_url}/Sale/SupplierPayment",dbname['excel_bill_payment']],
          "Journals":[f"{base_url}/GeneralLedger/GeneralJournal",dbname['excel_journal']],
        #   "Existing Chart of account":[f"{base_url}/GeneralLedger/Account",dbname['xero_coa']],
          "Job":[f"{base_url}/GeneralLedger/Job",dbname['excel_job']],
          }

    function_name = list(static_function.keys())
    print(function_name)
    
    if task_function_name in function_name:
        print(static_function[task_function_name])
        url = static_function[task_function_name][0]
        tablename = static_function[task_function_name][1]
        id_or_name_value_for_error="NA"
                    
        status=asyncio.run(post_data_in_myob(url, headers, payload, tablename, _id, job_id, task_id,
                                                    id_or_name_value_for_error))
        if status == 'success':
            return 'success'
        else:
            return 'error'    

def retry_payload_for_excel_to_reckon(job_id,payload,_id,task_id,task_function_name):
    dbname = get_mongodb_database()
    
    payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

    static_function = {"COA" : [f"{base_url}/accounts",dbname['excel_reckon_chart_of_account']],
          "Contact" : [f"{base_url}/contacts",dbname['excel_reckon_contact']],
        #   "Contact" : [f"{base_url}/contacts",dbname['excel_reckon_customer']],
        #   "Contact" : [f"{base_url}/contacts",dbname['excel_reckon_supplier']],
          "Employee" : [f"{base_url}/contacts",dbname['excel_reckon_employee']],
          "Spend Money" : [f"{base_url}/estimates",dbname['excel_reckon_spend_money']],
          "Receive Money" : [f"{base_url}/receipts",dbname['excel_reckon_receive_money']],
          "Bank Transfer" : [f"{base_url}/banktransfers",dbname['excel_reckon_bank_transfer']],
          "Invoice" : [f"{base_url}/invoices",dbname['excel_reckon_invoice']],
          "Item" : [f"{base_url}/items",dbname['excel_reckon_item']],
          "Bills": [f"{base_url}/bills",dbname['excel_reckon_bill']],
          "Customer payment" : [f"{base_url}/receipts",dbname['excel_reckon_invoice_payment']],
          "Supplier return" :[f"{base_url}/payments",dbname['excel_reckon_bill_payment']],
          "Journals":[f"{base_url}/journals",dbname['excel_reckon_journal']]
          }

    function_name = list(static_function.keys())
    print(function_name)
    
    if task_function_name in function_name:
        print(static_function[task_function_name])
        url = static_function[task_function_name][0]
        tablename = static_function[task_function_name][1]
        id_or_name_value_for_error="NA"
                    
        status=asyncio.run(post_data_in_reckon(url, post_headers, payload,tablename,_id, job_id,task_id,id_or_name_value_for_error))
        if status == 'success':
            return 'success'
        else:
            return 'error'    

def retry_payload_for_xero_to_qbo(job_id,payload,_id,task_id,task_function_name):
    dbname = get_mongodb_database()
    
    base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)
    static_function = {"Chart of account" : [f"{base_url}/account?minorversion={minorversion}",dbname['xero_classified_coa']],
          "Archieved Chart of account" : [f"{base_url}/account?minorversion={minorversion}",dbname['xero_classified_archived_coa']],
          "Customer" : [f"{base_url}/customer?minorversion={minorversion}",dbname['xero_customer']],
          "Archieved Customer" : [f"{base_url}/customer?minorversion={minorversion}",dbname['xero_archived_customer_in_invoice']],
          "Supplier" : [f"{base_url}/vendor?minorversion=40",dbname['xero_supplier']],
          "Archieved Supplier" : [f"{base_url}/vendor?minorversion=40",dbname['xero_archived_supplier_in_bill']],
          "Item" : [f"{base_url}/item?minorversion={minorversion}",dbname['xero_items']],
          "Spend Money" : [f"{base_url}/purchase?minorversion={minorversion}",dbname['xero_spend_money']],
          "Receive Money" : [f"{base_url}/deposit?minorversion={minorversion}",dbname['xero_receive_money']],
          "Bank Transfer" : [f"{base_url}/transfer?minorversion={minorversion}",dbname['xero_bank_transfer']],
          "Invoice" : [f"{base_url}/invoice?minorversion={minorversion}",dbname['xero_invoice']],
          "Bill": [f"{base_url}/bill?minorversion={minorversion}",dbname['xero_bill']],
          "Invoice CreditNote" : [f"{base_url}/invoice?minorversion={minorversion}",dbname['xero_invoice']],
          "Bill VendorCredit": [f"{base_url}/bill?minorversion={minorversion}",dbname['xero_bill']],
          "Invoice Payment" : [f"{base_url}/payment?minorversion={minorversion}",dbname['xero_invoice_payment']],
          "Bill Payment" :[f"{base_url}/billpayment?minorversion={minorversion}",dbname['xero_bill_payment']],
          "Journal":[f"{base_url}/journalentry?minorversion={minorversion}",dbname['xero_manual_journal']],
        #   "Existing Chart of account":[f"{base_url}/GeneralLedger/Account",dbname['xero_coa']],
          "Job":[f"{base_url}/class?minorversion={minorversion}",dbname['xero_job']],
          }

    function_name = list(static_function.keys())
    
    print(task_function_name,"key-----------------")
    if task_function_name in function_name:
        url1 = static_function[task_function_name][0]
        tablename = static_function[task_function_name][1]
        id_or_name_value_for_error="NA"
        status=post_data_in_qbo(url1, headers, payload,tablename,_id, job_id,task_id, id_or_name_value_for_error)
        
        if status == 'success':
            return 'success'
        else:
            return 'error'    

        
def retry_payload_for_myob_to_qbo(job_id,payload,_id,task_id,task_function_name):
    dbname = get_mongodb_database()
    
    base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)
    static_function = {"Chart of account" : [f"{base_url}/account?minorversion={minorversion}",dbname['classified_coa']],
          "Customer" : [f"{base_url}/customer?minorversion={minorversion}",dbname['customer']],
          "Archieved Customer" : [f"{base_url}/customer?minorversion={minorversion}",dbname['archived_customer_in_invoice']],
          "Supplier" : [f"{base_url}/vendor?minorversion=40",dbname['supplier']],
          "Archieved Supplier" : [f"{base_url}/vendor?minorversion=40",dbname['archived_supplier_in_bill']],
          "Item" : [f"{base_url}/item?minorversion={minorversion}",dbname['item']],
          "Spend Money" : [f"{base_url}/purchase?minorversion={minorversion}",dbname['myob_spend_money']],
          "Receive Money" : [f"{base_url}/deposit?minorversion={minorversion}",dbname['received_money']],
          "Bank Transfer" : [f"{base_url}/transfer?minorversion={minorversion}",dbname['bank_transfer']],
          "Invoice" : [f"{base_url}/invoice?minorversion={minorversion}",dbname['item_invoice']],
          "Invoice CreditNote" : [f"{base_url}/invoice?minorversion={minorversion}",dbname['item_invoice']],
          "Bill": [f"{base_url}/bill?minorversion={minorversion}",dbname['final_bill']],
          "Bill VendorCredit": [f"{base_url}/bill?minorversion={minorversion}",dbname['final_bill']],
          "Invoice Payment" : [f"{base_url}/payment?minorversion={minorversion}",dbname['invoice_payment']],
          "Bill Payment" :[f"{base_url}/billpayment?minorversion={minorversion}",dbname['bill_payment']],
          "Journal":[f"{base_url}/journalentry?minorversion={minorversion}",dbname['journal']],
        #   "Existing Chart of account":[f"{base_url}/GeneralLedger/Account",dbname['xero_coa']],
          "Job":[f"{base_url}/class?minorversion={minorversion}",dbname['job']],
          }

    function_name = list(static_function.keys())
    print(function_name)

    print(task_function_name,"key-----------------")
    if task_function_name in function_name:
        print(static_function[task_function_name])
        url = static_function[task_function_name][0]
        tablename = static_function[task_function_name][1]
        id_or_name_value_for_error="NA"
                    
        status=post_data_in_qbo(base_url, headers, payload,dbname["xero_classified_coa"],_id, job_id,task_id, id_or_name_value_for_error)
        
        if status == 'success':
            return 'success'
        else:
            return 'error'    


def instance_check(instance_name,row_value):
    
    if isinstance(row_value, float):
        if math.isnan(row_value):
            instance_name = None
        else:
            instance_name = row_value
        
    elif isinstance(row_value, str):
        if len(row_value) == 0:
            instance_name = None
        else:
            instance_name = row_value
    
    elif isinstance(row_value, int):
        if math.isnan(row_value):
            instance_name = None
        else:
            instance_name = row_value
        
    return instance_name
