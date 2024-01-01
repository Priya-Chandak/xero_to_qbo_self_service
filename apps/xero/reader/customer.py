import sys

import requests

from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import *
# from apps.db_mongo_connection.db_mongo import get_mongodb_database
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
import logging

# job_url = f"{base_url}/GeneralLedger/account?$top=100&$skip=0"

def get_xero_customer(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        dbname = get_mongodb_database()

        xero_customer = dbname['xero_customer']
        xero_supplier = dbname['xero_supplier']
        payload, base_url, headers = get_settings_xero(job_id)

        main_url = f"{base_url}/Contacts"
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
        r1 = response1.json()
        r2 = r1['Contacts']
        no_of_records = len(r2)
        no_of_pages = (no_of_records // 100) + 1

        customer = []
        supplier = []

        for pages in range(1, no_of_pages + 1):
            url = f"{base_url}/Contacts/?page={pages}"
            print(url)
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            JsonResponse = response.json()

            for i in range(0, len(JsonResponse['Contacts'])):
                if (JsonResponse['Contacts'][i]['IsSupplier'] == True and JsonResponse['Contacts'][i][
                    'IsCustomer'] == False):
                    QuerySet = {"Address": [], "Phone": []}
                    QuerySet['job_id'] = job_id
                    QuerySet['task_id'] = task_id
                    QuerySet['table_name'] = "xero_supplier"
                    QuerySet["is_pushed"] = 0
                    QuerySet["error"] = None
                    QuerySet["payload"] = None
                    if 'FirstName' in JsonResponse['Contacts'][i]:
                        QuerySet['FirstName'] = JsonResponse['Contacts'][i]['FirstName']
                    if 'LastName' in JsonResponse['Contacts'][i]:
                        QuerySet['LastName'] = JsonResponse['Contacts'][i]['LastName']
                    if 'Discount' in JsonResponse['Contacts'][i]:
                        QuerySet['Discount'] = JsonResponse['Contacts'][i]['Discount']
                    if 'Website' in JsonResponse['Contacts'][i]:
                        QuerySet['Website'] = JsonResponse['Contacts'][i]['Website']
                    if 'Name' in JsonResponse['Contacts'][i]:
                        QuerySet['Name'] = JsonResponse['Contacts'][i]['Name']
                    if 'EmailAddress' in JsonResponse['Contacts'][i]:
                        QuerySet['email'] = JsonResponse['Contacts'][i]['EmailAddress']
                    if 'TaxNumber' in JsonResponse['Contacts'][i]:
                        QuerySet['TaxNumber'] = JsonResponse['Contacts'][i]['TaxNumber'].strip()
                    if 'BatchPayments' in JsonResponse['Contacts'][i]:
                        QuerySet['BankAccNumber'] = JsonResponse['Contacts'][i]['BatchPayments']['BankAccountNumber']
                        if 'BankAccountName' in JsonResponse['Contacts'][i]['BatchPayments']:
                            QuerySet['BankAccName'] = JsonResponse['Contacts'][i]['BatchPayments']['BankAccountName']
                        if 'Details' in JsonResponse['Contacts'][i]['BatchPayments']:
                            QuerySet['Details'] = JsonResponse['Contacts'][i]['BatchPayments']['Details']
                    if 'BankAccountDetails' in JsonResponse['Contacts'][i]:
                        QuerySet['BankAccountDetails'] = JsonResponse['Contacts'][i]['BankAccountDetails']

                    QuerySet['ContactID'] = JsonResponse['Contacts'][i]['ContactID']

                    for j in range(0, len(JsonResponse['Contacts'][i]['Addresses'])):
                        QuerySet1 = {}

                        if 'AddressType' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['AddressType'] = JsonResponse['Contacts'][i]['Addresses'][j]['AddressType']
                        if 'AddressLine1' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['AddressLine1'] = JsonResponse['Contacts'][i]['Addresses'][j]['AddressLine1']
                        if 'AddressLine2' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['AddressLine2'] = JsonResponse['Contacts'][i]['Addresses'][j]['AddressLine2']
                        if 'City' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['City'] = JsonResponse['Contacts'][i]['Addresses'][j]['City']
                        if 'Region' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['Region'] = JsonResponse['Contacts'][i]['Addresses'][j]['Region']
                        if 'PostalCode' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['PostalCode'] = JsonResponse['Contacts'][i]['Addresses'][j]['PostalCode']
                        if 'Country' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['Country'] = JsonResponse['Contacts'][i]['Addresses'][j]['Country']

                        QuerySet["Address"].append(QuerySet1)

                    for k in range(0, len(JsonResponse['Contacts'][i]['Phones'])):
                        QuerySet2 = {}
                        if 'PhoneType' in JsonResponse['Contacts'][i]['Phones'][k]:
                            QuerySet2['PhoneType'] = JsonResponse['Contacts'][i]['Phones'][k]['PhoneType']
                        if 'PhoneNumber' in JsonResponse['Contacts'][i]['Phones'][k]:
                            QuerySet2['PhoneNumber'] = JsonResponse['Contacts'][i]['Phones'][k]['PhoneNumber']

                        QuerySet["Phone"].append(QuerySet2)

                    supplier.append(QuerySet)

                elif (JsonResponse['Contacts'][i]['IsSupplier'] == False and JsonResponse['Contacts'][i][
                    'IsCustomer'] == True):
                    QuerySet = {"Address": [], "Phone": []}
                    QuerySet['job_id'] = job_id
                    QuerySet['task_id'] = task_id
                    QuerySet['table_name'] = "xero_customer"
                    QuerySet["is_pushed"] = 0
                    QuerySet["error"] = None
                    if 'FirstName' in JsonResponse['Contacts'][i]:
                        QuerySet['FirstName'] = JsonResponse['Contacts'][i]['FirstName']
                    if 'LastName' in JsonResponse['Contacts'][i]:
                        QuerySet['LastName'] = JsonResponse['Contacts'][i]['LastName']
                    if 'Name' in JsonResponse['Contacts'][i]:
                        QuerySet['Name'] = JsonResponse['Contacts'][i]['Name']
                    if 'EmailAddress' in JsonResponse['Contacts'][i]:
                        QuerySet['email'] = JsonResponse['Contacts'][i]['EmailAddress']
                    if 'TaxNumber' in JsonResponse['Contacts'][i]:
                        QuerySet['TaxNumber'] = JsonResponse['Contacts'][i]['TaxNumber'].strip()
                    if 'BatchPayments' in JsonResponse['Contacts'][i]:
                        QuerySet['BatchPayments'] = JsonResponse['Contacts'][i]['BatchPayments']
                    if 'BankAccountDetails' in JsonResponse['Contacts'][i]:
                        QuerySet['BankAccountDetails'] = JsonResponse['Contacts'][i]['BankAccountDetails']

                    QuerySet['ContactID'] = JsonResponse['Contacts'][i]['ContactID']

                    for j in range(0, len(JsonResponse['Contacts'][i]['Addresses'])):
                        QuerySet1 = {}

                        if 'AddressType' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['AddressType'] = JsonResponse['Contacts'][i]['Addresses'][j]['AddressType']
                        if 'AddressLine1' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['AddressLine1'] = JsonResponse['Contacts'][i]['Addresses'][j]['AddressLine1']
                        if 'AddressLine2' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['AddressLine2'] = JsonResponse['Contacts'][i]['Addresses'][j]['AddressLine2']
                        if 'City' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['City'] = JsonResponse['Contacts'][i]['Addresses'][j]['City']
                        if 'Region' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['Region'] = JsonResponse['Contacts'][i]['Addresses'][j]['Region']
                        if 'PostalCode' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['PostalCode'] = JsonResponse['Contacts'][i]['Addresses'][j]['PostalCode']
                        if 'Country' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            QuerySet1['Country'] = JsonResponse['Contacts'][i]['Addresses'][j]['Country']

                        QuerySet["Address"].append(QuerySet1)

                    for k in range(0, len(JsonResponse['Contacts'][i]['Phones'])):
                        QuerySet2 = {}
                        if 'PhoneType' in JsonResponse['Contacts'][i]['Phones'][k]:
                            QuerySet2['PhoneType'] = JsonResponse['Contacts'][i]['Phones'][k]['PhoneType']
                        if 'PhoneNumber' in JsonResponse['Contacts'][i]['Phones'][k]:
                            QuerySet2['PhoneNumber'] = JsonResponse['Contacts'][i]['Phones'][k]['PhoneNumber']

                        QuerySet["Phone"].append(QuerySet2)

                    customer.append(QuerySet)

                elif (JsonResponse['Contacts'][i]['IsSupplier'] == True and JsonResponse['Contacts'][i][
                    'IsCustomer'] == True) or (
                        JsonResponse['Contacts'][i]['IsSupplier'] == False and JsonResponse['Contacts'][i][
                    'IsCustomer'] == False):
                    supplier_object = {"Address": [], "Phone": []}
                    supplier_object['job_id'] = job_id
                    supplier_object['task_id'] = task_id
                    supplier_object['table_name'] = "xero_supplier"
                    supplier_object["is_pushed"] = 0
                    supplier_object["error"] = None
                    supplier_object["payload"] = None

                    if 'FirstName' in JsonResponse['Contacts'][i]:
                        supplier_object['FirstName'] = JsonResponse['Contacts'][i]['FirstName'] + " - S"
                    if 'LastName' in JsonResponse['Contacts'][i]:
                        supplier_object['LastName'] = JsonResponse['Contacts'][i]['LastName'] + " - S"
                    if 'Discount' in JsonResponse['Contacts'][i]:
                        supplier_object['Discount'] = JsonResponse['Contacts'][i]['Discount']
                    if 'Website' in JsonResponse['Contacts'][i]:
                        supplier_object['Website'] = JsonResponse['Contacts'][i]['Website']
                    if 'Name' in JsonResponse['Contacts'][i]:
                        supplier_object['Name'] = JsonResponse['Contacts'][i]['Name'] + " - S"
                    if 'EmailAddress' in JsonResponse['Contacts'][i]:
                        supplier_object['email'] = JsonResponse['Contacts'][i]['EmailAddress']
                    if 'TaxNumber' in JsonResponse['Contacts'][i]:
                        supplier_object['TaxNumber'] = JsonResponse['Contacts'][i]['TaxNumber'].strip()
                    if 'BatchPayments' in JsonResponse['Contacts'][i]:
                        supplier_object['BankAccNumber'] = JsonResponse['Contacts'][i]['BatchPayments'][
                            'BankAccountNumber']
                        if 'BankAccountName' in JsonResponse['Contacts'][i]['BatchPayments']:
                            supplier_object['BankAccName'] = JsonResponse['Contacts'][i]['BatchPayments'][
                                'BankAccountName']
                        if 'Details' in JsonResponse['Contacts'][i]['BatchPayments']:
                            supplier_object['Details'] = JsonResponse['Contacts'][i]['BatchPayments']['Details']

                    if 'BankAccountDetails' in JsonResponse['Contacts'][i]:
                        supplier_object['BankAccountDetails'] = JsonResponse['Contacts'][i]['BankAccountDetails']

                    supplier_object['ContactID'] = JsonResponse['Contacts'][i]['ContactID']

                    for j1 in range(0, len(JsonResponse['Contacts'][i]['Addresses'])):
                        supplier_object1 = {}

                        if 'AddressType' in JsonResponse['Contacts'][i]['Addresses'][j1]:
                            supplier_object1['AddressType'] = JsonResponse['Contacts'][i]['Addresses'][j1][
                                'AddressType']
                        if 'AddressLine1' in JsonResponse['Contacts'][i]['Addresses'][j1]:
                            supplier_object1['AddressLine1'] = JsonResponse['Contacts'][i]['Addresses'][j1][
                                'AddressLine1']
                        if 'AddressLine2' in JsonResponse['Contacts'][i]['Addresses'][j1]:
                            supplier_object1['AddressLine2'] = JsonResponse['Contacts'][i]['Addresses'][j1][
                                'AddressLine2']
                        if 'City' in JsonResponse['Contacts'][i]['Addresses'][j1]:
                            supplier_object1['City'] = JsonResponse['Contacts'][i]['Addresses'][j1]['City']
                        if 'Region' in JsonResponse['Contacts'][i]['Addresses'][j1]:
                            supplier_object1['Region'] = JsonResponse['Contacts'][i]['Addresses'][j1]['Region']
                        if 'PostalCode' in JsonResponse['Contacts'][i]['Addresses'][j1]:
                            supplier_object1['PostalCode'] = JsonResponse['Contacts'][i]['Addresses'][j1]['PostalCode']
                        if 'Country' in JsonResponse['Contacts'][i]['Addresses'][j1]:
                            supplier_object1['Country'] = JsonResponse['Contacts'][i]['Addresses'][j1]['Country']

                        supplier_object["Address"].append(supplier_object1)

                    for k1 in range(0, len(JsonResponse['Contacts'][i]['Phones'])):
                        supplier_object2 = {}
                        if 'PhoneType' in JsonResponse['Contacts'][i]['Phones'][k1]:
                            supplier_object2['PhoneType'] = JsonResponse['Contacts'][i]['Phones'][k1]['PhoneType']
                        if 'PhoneNumber' in JsonResponse['Contacts'][i]['Phones'][k1]:
                            supplier_object2['PhoneNumber'] = JsonResponse['Contacts'][i]['Phones'][k1]['PhoneNumber']

                        supplier_object["Phone"].append(supplier_object2)

                    supplier.append(supplier_object)

                    customer_object = {"Address": [], "Phone": []}
                    customer_object['job_id'] = job_id
                    customer_object['task_id'] = task_id
                    customer_object['table_name'] = "xero_customer"
                    customer_object['is_pushed'] = 0
                    customer_object['error'] = None
                    customer_object['payload'] = None

                    if 'FirstName' in JsonResponse['Contacts'][i]:
                        customer_object['FirstName'] = JsonResponse['Contacts'][i]['FirstName'] + " - C"
                    if 'LastName' in JsonResponse['Contacts'][i]:
                        customer_object['LastName'] = JsonResponse['Contacts'][i]['LastName'] + " - C"
                    if 'Website' in JsonResponse['Contacts'][i]:
                        customer_object['Website'] = JsonResponse['Contacts'][i]['Website']
                    if 'Name' in JsonResponse['Contacts'][i]:
                        customer_object['Name'] = JsonResponse['Contacts'][i]['Name'] + " - C"
                    if 'EmailAddress' in JsonResponse['Contacts'][i]:
                        customer_object['email'] = JsonResponse['Contacts'][i]['EmailAddress']
                    if 'TaxNumber' in JsonResponse['Contacts'][i]:
                        customer_object['TaxNumber'] = JsonResponse['Contacts'][i]['TaxNumber'].strip()
                    if 'BatchPayments' in JsonResponse['Contacts'][i]:
                        customer_object['BatchPayments'] = JsonResponse['Contacts'][i]['BatchPayments']
                    if 'BankAccountDetails' in JsonResponse['Contacts'][i]:
                        customer_object['BankAccountDetails'] = JsonResponse['Contacts'][i]['BankAccountDetails']

                    customer_object['ContactID'] = JsonResponse['Contacts'][i]['ContactID']

                    for j in range(0, len(JsonResponse['Contacts'][i]['Addresses'])):
                        customer_object1 = {}

                        if 'AddressType' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            customer_object1['AddressType'] = JsonResponse['Contacts'][i]['Addresses'][j]['AddressType']
                        if 'AddressLine1' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            customer_object1['AddressLine1'] = JsonResponse['Contacts'][i]['Addresses'][j][
                                'AddressLine1']
                        if 'AddressLine2' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            customer_object1['AddressLine2'] = JsonResponse['Contacts'][i]['Addresses'][j][
                                'AddressLine2']
                        if 'City' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            customer_object1['City'] = JsonResponse['Contacts'][i]['Addresses'][j]['City']
                        if 'Region' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            customer_object1['Region'] = JsonResponse['Contacts'][i]['Addresses'][j]['Region']
                        if 'PostalCode' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            customer_object1['PostalCode'] = JsonResponse['Contacts'][i]['Addresses'][j]['PostalCode']
                        if 'Country' in JsonResponse['Contacts'][i]['Addresses'][j]:
                            customer_object1['Country'] = JsonResponse['Contacts'][i]['Addresses'][j]['Country']

                        customer_object["Address"].append(customer_object1)

                    for k in range(0, len(JsonResponse['Contacts'][i]['Phones'])):
                        customer_object2 = {}
                        if 'PhoneType' in JsonResponse['Contacts'][i]['Phones'][k]:
                            customer_object2['PhoneType'] = JsonResponse['Contacts'][i]['Phones'][k]['PhoneType']
                        if 'PhoneNumber' in JsonResponse['Contacts'][i]['Phones'][k]:
                            customer_object2['PhoneNumber'] = JsonResponse['Contacts'][i]['Phones'][k]['PhoneNumber']

                        customer_object["Phone"].append(customer_object2)

                    customer.append(customer_object)

        # if dbname['xero_supplier'].count_documents({}) != 0:
        #     pass
        # else:
        #     xero_supplier.insert_many(supplier)

        if dbname['xero_customer'].count_documents({'job_id': job_id}) != 0:
            pass
        else:
            xero_customer.insert_many(customer)

            step_name = "Reading data from contact"
            write_task_execution_step(task_id, status=1, step=step_name)

    except Exception as ex:
        print("------------------------------")
        step_name = "Something went wrong"
        logging.error(ex, exc_info=True)
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")

        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
