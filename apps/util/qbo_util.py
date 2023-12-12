import asyncio
import json
import logging
import math
from datetime import datetime

import requests
from bson import ObjectId
from flask import request

from apps.home.data_util import get_job_details, update_task_execution_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


def get_data_from_qbo(job_id, task_id, table_name, json_object_key, qbo_object_name, url, header):
    print("inside get_data_from_qbo")
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
                if json_object_key in ['Invoice', 'Purchase', 'Deposit', 'Bill', 'JournalEntry', 'Transfer', 'Payment',
                                       'BillPayment']:
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

            response = requests.request("POST", url, headers=header, data=payload)
            if response and response.status_code == 200:
                api_response = response.json()
                items = api_response["QueryResponse"][json_object_key]
                if len(items) > 0:
                    items_output = []
                    for item in items:
                        item["job_id"] = job_id
                        item["task_id"] = task_id
                        item["table_name"] = table_name
                        item["error"] = None
                        item["is_pushed"] = 0
                        item["payload"] = None

                        items_output.append(item)

                    mongo_table.insert_many(items_output)
                    no_of_records = no_of_records + api_response["QueryResponse"]["maxResults"]
                    remaining_records = api_response["QueryResponse"]["maxResults"]


    except Exception as ex:
        logging.error("Error in get_data_from_qbo", ex)
        raise ex


def post_data_in_qbo(url, headers, payload, table_name, _id, job_id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    response_json = json.loads(response.text)
    if response.status_code == 200:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        return "success"

    elif response.status_code == 401:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"

    elif response.status_code == 400:
        print(response_json)
        table_name.update_one({'_id': ObjectId(_id)},
                              {"$set": {"error": f"{response_json}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"

    else:
        print(response_json)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": f"{response_json}"}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"


blank = []


async def post_data_in_myob(url, headers, payload, table_name, _id, job_id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)

    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "None"}}, upsert=True)
        return "success"

    elif response.status_code == 401:
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"

    elif response.status_code == 400:
        print(payload)

        print(response.text)
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {
            "$set": {"error": f"{response_json['Errors']}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"

    else:
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)},
                              {"$set": {"error": f"{response_json}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"

    print(blank)


async def post_data_in_reckon(url, headers, payload, table_name, _id, job_id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("POST", url, headers=headers, data=payload)
    print(payload)
    print(response.status_code, "statuscode-------------------------")
    print(response.text)
    print(url)
    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": payload}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": f"{response.text}"}}, upsert=True)
        return "success"

    elif response.status_code == 400:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 0}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": payload}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)},
                              {"$set": {"error": f"{response.text}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        return "error"

    elif response.status_code == 401:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 0}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": payload}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)},
                              {"$set": {"error": "Access Token Expired"} + " - " + f"{id_or_name_value_for_error}"},
                              upsert=True)
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
        table_name.update_one({'_id': ObjectId(_id)},
                              {"$set": {"error": f"{response_json}" + " - " + f"{id_or_name_value_for_error}"}},
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


def get_pagination_for_records(task_id, table_name):
    print("inside get_pagination_for_records")
    page = request.args.get('page', 1, type=int)
    per_page = 200
    collection = table_name
    total_records = collection.count_documents({"task_id": task_id})
    successful_count = collection.count_documents({"$and": [{"is_pushed": 1}, {"task_id": task_id}]})
    error_count = collection.count_documents({"$and": [{"is_pushed": 0}, {"task_id": task_id}]})
    data = table_name.find({"$and": [{"is_pushed": 0}, {"task_id": task_id}]}).skip((page - 1) * per_page).limit(
        per_page)

    return page, per_page, total_records, successful_count, error_count, data


async def delete_data_in_myob(url, headers, payload, table_name, _id, task_id, id_or_name_value_for_error):
    db = get_mongodb_database()
    response = requests.request("DELETE", url, headers=headers, data=payload)
    print(response.status_code)

    if response.status_code == 200 or response.status_code == 201:
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"is_pushed": 1}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "None"}}, upsert=True)
        return "success"

    elif response.status_code == 401:
        update_task_execution_status(
            task_id, status=0, task_type="write")
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"error": "Access Token Expired "}}, upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"

    elif response.status_code == 400:
        print(response.text)
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)}, {
            "$set": {"error": f"{response_json['Errors']}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"

    else:
        blank.append(id_or_name_value_for_error)
        response_json = json.loads(response.text)
        table_name.update_one({'_id': ObjectId(_id)},
                              {"$set": {"error": f"{response_json}" + " - " + f"{id_or_name_value_for_error}"}},
                              upsert=True)
        table_name.update_one({'_id': ObjectId(_id)}, {"$set": {"payload": f"{payload}"}}, upsert=True)
        return "error"


blank = []



def retry_payload_for_xero_to_qbo(job_id, payload, _id, task_id, task_function_name):
    dbname = get_mongodb_database()

    base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo_for_report(job_id)
    static_function = {
        "Chart of account": [f"{base_url}/account?minorversion={minorversion}", dbname['xero_classified_coa']],
        "Archieved Chart of account": [f"{base_url}/account?minorversion={minorversion}",
                                       dbname['xero_classified_archived_coa']],
        "Customer": [f"{base_url}/customer?minorversion={minorversion}", dbname['xero_customer']],
        "Archieved Customer": [f"{base_url}/customer?minorversion={minorversion}",
                               dbname['xero_archived_customer_in_invoice']],
        "Supplier": [f"{base_url}/vendor?minorversion=40", dbname['xero_supplier']],
        "Archieved Supplier": [f"{base_url}/vendor?minorversion=40", dbname['xero_archived_supplier_in_bill']],
        "Item": [f"{base_url}/item?minorversion={minorversion}", dbname['xero_items']],
        "Spend Money": [f"{base_url}/purchase?minorversion={minorversion}", dbname['xero_spend_money']],
        "Receive Money": [f"{base_url}/deposit?minorversion={minorversion}", dbname['xero_receive_money']],
        "Bank Transfer": [f"{base_url}/transfer?minorversion={minorversion}", dbname['xero_bank_transfer']],
        "Invoice": [f"{base_url}/invoice?minorversion={minorversion}", dbname['xero_invoice']],
        "Bill": [f"{base_url}/bill?minorversion={minorversion}", dbname['xero_bill']],
        "Invoice CreditNote": [f"{base_url}/invoice?minorversion={minorversion}", dbname['xero_invoice']],
        "Bill VendorCredit": [f"{base_url}/bill?minorversion={minorversion}", dbname['xero_bill']],
        "Invoice Payment": [f"{base_url}/payment?minorversion={minorversion}", dbname['xero_invoice_payment']],
        "Bill Payment": [f"{base_url}/billpayment?minorversion={minorversion}", dbname['xero_bill_payment']],
        "Journal": [f"{base_url}/journalentry?minorversion={minorversion}", dbname['xero_manual_journal']],
        #   "Existing Chart of account":[f"{base_url}/GeneralLedger/account",dbname['xero_coa']],
        "Job": [f"{base_url}/class?minorversion={minorversion}", dbname['xero_job']],
    }

    function_name = list(static_function.keys())

    print(task_function_name, "key-----------------")
    if task_function_name in function_name:
        url1 = static_function[task_function_name][0]
        tablename = static_function[task_function_name][1]
        id_or_name_value_for_error = "NA"
        status = post_data_in_qbo(url1, headers, payload, tablename, _id, job_id, task_id, id_or_name_value_for_error)

        if status == 'success':
            return 'success'
        else:
            return 'error'


def instance_check(instance_name, row_value):
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
