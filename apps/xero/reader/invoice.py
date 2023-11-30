import json
from ast import Break
import json
from os import path
from os.path import exists
from MySQLdb import Connect
from numpy import true_divide
from apps.home.models import Jobs, Tool
from apps import db
from apps.myconstant import *
from sqlalchemy.orm import aliased
import requests
import re
from apps.mmc_settings.all_settings import *

from apps.home.data_util import add_job_status,get_job_details
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import  write_task_execution_step,update_task_execution_status
import sys
import time
from datetime import datetime, timedelta



def get_invoice(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_invoice = dbname['xero_invoice']
        xero_bill = dbname['xero_bill']
        payload, base_url, headers = get_settings_xero(job_id)

        if (start_date == '' and end_date == ''):
            main_url = f"{base_url}/Invoices?unitdp=4"
        else:
            y1=int(start_date[0:4])
            m1=int(start_date[5:7])
            d1=int(start_date[8:])
            y2=int(end_date[0:4])
            m2=int(end_date[5:7])
            d2=int(end_date[8:])
            main_url = f"{base_url}/Invoices?unitdp=4&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"
    
        print(main_url)
        
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
        time.sleep(1)
            
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1['Invoices']
            no_of_records = len(r2)
            if no_of_records>0:
                no_of_pages = (no_of_records // 100) + 1
                invoice = []
                bill = []
                print(no_of_records,no_of_pages)

                for pages in range(1, no_of_pages+1):
                    if (start_date=='' and end_date==''): 
                        url = f"{base_url}/Invoices?page={pages}&unitdp=4"
                    else:
                        url = f"{base_url}/Invoices?page={pages}&unitdp=4&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"
                
                    print(url)

                    response = requests.request(
                        "GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse['Invoices']
                    print(len(JsonResponse1))
                    for i in range(0, len(JsonResponse1)):
                        if (JsonResponse1[i]['Status']!='DELETED') and (JsonResponse1[i]['Status']!='VOIDED') and (JsonResponse1[i]['Status']!='DRAFT'):
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["payload"] = None
                            QuerySet["table_name"] = "xero_invoice" 

                            QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                            QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                            if 'DueDateString' in JsonResponse1[i]:
                                QuerySet['DueDate'] = JsonResponse1[i]['DueDateString']
                            QuerySet['TxnDate'] = JsonResponse1[i]['DateString']
                            QuerySet['TotalAmount'] = JsonResponse1[i]['Total']
                            QuerySet['SubTotal'] = JsonResponse1[i]['SubTotal']
                            QuerySet['Status'] = JsonResponse1[i]['Status']
                            QuerySet['TotalTax'] = JsonResponse1[i]['TotalTax']
                            QuerySet['LineAmountTypes'] = JsonResponse1[i]['LineAmountTypes']
                            # QuerySet['AmountDue'] = JsonResponse1[i]['AmountDue']
                            # QuerySet['AmountPaid'] = JsonResponse1[i]['AmountPaid']
                            # QuerySet['AmountCredited'] = JsonResponse1[i]['AmountCredited']
                            QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                            QuerySet['IsDiscounted'] = JsonResponse1[i]['IsDiscounted']

                            for j in range(0, len(JsonResponse1[i]['LineItems'])):
                                QuerySet1 = {}
                                if 'Description' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['Description'] = JsonResponse1[i]['LineItems'][j]['Description']
                                if 'UnitAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['UnitAmount'] = JsonResponse1[i]['LineItems'][j]['UnitAmount']
                                if 'TaxAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['TaxAmount'] = JsonResponse1[i]['LineItems'][j]['TaxAmount']
                                if 'LineAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['LineAmount'] = JsonResponse1[i]['LineItems'][j]['LineAmount']
                                if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                    QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                            
                                if 'AccountCode' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['AccountCode'] = JsonResponse1[i]['LineItems'][j]['AccountCode']
                                if 'Quantity' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['Quantity'] = JsonResponse1[i]['LineItems'][j]['Quantity']
                                
                                if JsonResponse1[i]['IsDiscounted'] == True:
                                    if 'DiscountRate' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Discount'] = JsonResponse1[i]['LineItems'][j]['DiscountRate']
                                    else:
                                        QuerySet1['Discount'] = 0

                                if 'Item' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['ItemCode'] = JsonResponse1[i]['LineItems'][j]['Item']['Code']
                                    QuerySet1['ItemID'] = JsonResponse1[i]['LineItems'][j]['Item']['ItemID']
                                    if 'Name' in JsonResponse1[i]['LineItems'][j]['Item']:
                                        QuerySet1['Name'] = JsonResponse1[i]['LineItems'][j]['Item']['Name']
                                if 'TaxType' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['TaxType'] = JsonResponse1[i]['LineItems'][j]['TaxType']
                                else:
                                    QuerySet1['TaxType'] = None

                                QuerySet['Line'].append(QuerySet1)

                            if (JsonResponse1[i]['Type'] == "ACCREC"):
                                invoice.append(QuerySet)
                            if (JsonResponse1[i]['Type'] == "ACCPAY"):
                                bill.append(QuerySet)
                            
                            
                if len(invoice)>0:
                    xero_invoice.insert_many(invoice)
                    print("Added")
                if len(bill)>0:
                    xero_bill.insert_many(bill)
                    print("Added")

                step_name = "Reading data from xero invoice"
                write_task_execution_step(task_id, status=1, step=step_name)
                    

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_all_xero_invoice_for_payment(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        xero_invoice = dbname['xero_invoice']
        xero_bill = dbname['xero_bill']

        payload, base_url, headers = get_settings_xero(job_id)

        main_url = f"{base_url}/Invoices"
        
        print(main_url)
        
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1['Invoices']
            no_of_records = len(r2)
            if no_of_records>0:
                no_of_pages = (no_of_records // 100) + 1
                invoice = []
                bill=[]
                print(no_of_records,no_of_pages)

                for pages in range(1, no_of_pages+1):
                    url = f"{base_url}/Invoices?page={pages}"
                    response = requests.request(
                        "GET", url, headers=headers, data=payload)
                    time.sleep(1)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse['Invoices']

                    print(len(JsonResponse1))
                    for i in range(0, len(JsonResponse1)):
                        if (JsonResponse1[i]['Status']!='DELETED') and (JsonResponse1[i]['Status']!='VOIDED') and (JsonResponse1[i]['Status']!='DRAFT'):
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["payload"] = None
                            QuerySet["table_name"] = "xero_invoice" 

                            QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                            QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                            if 'DueDateString' in JsonResponse1[i]:
                                QuerySet['DueDate'] = JsonResponse1[i]['DueDateString']
                            QuerySet['TxnDate'] = JsonResponse1[i]['DateString']
                            QuerySet['TotalAmount'] = JsonResponse1[i]['Total']
                            QuerySet['SubTotal'] = JsonResponse1[i]['SubTotal']
                            QuerySet['Status'] = JsonResponse1[i]['Status']
                            QuerySet['TotalTax'] = JsonResponse1[i]['TotalTax']
                            QuerySet['LineAmountTypes'] = JsonResponse1[i]['LineAmountTypes']
                            # QuerySet['AmountDue'] = JsonResponse1[i]['AmountDue']
                            # QuerySet['AmountPaid'] = JsonResponse1[i]['AmountPaid']
                            # QuerySet['AmountCredited'] = JsonResponse1[i]['AmountCredited']
                            QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                            QuerySet['IsDiscounted'] = JsonResponse1[i]['IsDiscounted']

                            for j in range(0, len(JsonResponse1[i]['LineItems'])):
                                QuerySet1 = {}
                                if 'Description' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['Description'] = JsonResponse1[i]['LineItems'][j]['Description']
                                if 'UnitAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['UnitAmount'] = JsonResponse1[i]['LineItems'][j]['UnitAmount']
                                if 'TaxAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['TaxAmount'] = JsonResponse1[i]['LineItems'][j]['TaxAmount']
                                if 'LineAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['LineAmount'] = JsonResponse1[i]['LineItems'][j]['LineAmount']
                                if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                    QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                            
                                if 'AccountCode' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['AccountCode'] = JsonResponse1[i]['LineItems'][j]['AccountCode']
                                if 'Quantity' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['Quantity'] = JsonResponse1[i]['LineItems'][j]['Quantity']
                                
                                if JsonResponse1[i]['IsDiscounted'] == True:
                                    if 'DiscountRate' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Discount'] = JsonResponse1[i]['LineItems'][j]['DiscountRate']
                                    else:
                                        QuerySet1['Discount'] = 0

                                if 'Item' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['ItemCode'] = JsonResponse1[i]['LineItems'][j]['Item']['Code']
                                    QuerySet1['ItemID'] = JsonResponse1[i]['LineItems'][j]['Item']['ItemID']
                                    if 'Name' in JsonResponse1[i]['LineItems'][j]['Item']:
                                        QuerySet1['Name'] = JsonResponse1[i]['LineItems'][j]['Item']['Name']
                                if 'TaxType' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['TaxType'] = JsonResponse1[i]['LineItems'][j]['TaxType']
                                else:
                                    QuerySet1['TaxType'] = None

                                QuerySet['Line'].append(QuerySet1)

                            if (JsonResponse1[i]['Type'] == "ACCREC"):
                                invoice.append(QuerySet)
                            if (JsonResponse1[i]['Type'] == "ACCPAY"):
                                bill.append(QuerySet)
                                
                            
                            
                if len(invoice)>0:
                    xero_invoice.insert_many(invoice)
                    print("Added")
                # if len(bill)>0:
                #     xero_bill.insert_many(bill)
                #     print("Added")
                step_name = "Reading data from xero all invoice "
                write_task_execution_step(task_id, status=1, step=step_name)
            
                

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_all_xero_bill_for_payment(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        xero_invoice = dbname['xero_invoice']
        xero_bill = dbname['xero_bill']

        payload, base_url, headers = get_settings_xero(job_id)

        main_url = f"{base_url}/Invoices"
        
        print(main_url)
        
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1['Invoices']
            no_of_records = len(r2)
            if no_of_records>0:
                no_of_pages = (no_of_records // 100) + 1
                invoice = []
                bill=[]
                print(no_of_records,no_of_pages)

                for pages in range(1, no_of_pages+1):
                    url = f"{base_url}/Invoices?page={pages}"
                    response = requests.request(
                        "GET", url, headers=headers, data=payload)
                    print(response)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse['Invoices']

                    print(len(JsonResponse1))
                    for i in range(0, len(JsonResponse1)):
                        if (JsonResponse1[i]['Status']!='DELETED') and (JsonResponse1[i]['Status']!='VOIDED') and (JsonResponse1[i]['Status']!='DRAFT'):
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["table_name"] = "xero_invoice" 

                            QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                            QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                            if 'DueDateString' in JsonResponse1[i]:
                                QuerySet['DueDate'] = JsonResponse1[i]['DueDateString']
                            QuerySet['TxnDate'] = JsonResponse1[i]['DateString']
                            QuerySet['TotalAmount'] = JsonResponse1[i]['Total']
                            QuerySet['SubTotal'] = JsonResponse1[i]['SubTotal']
                            QuerySet['Status'] = JsonResponse1[i]['Status']
                            QuerySet['TotalTax'] = JsonResponse1[i]['TotalTax']
                            QuerySet['LineAmountTypes'] = JsonResponse1[i]['LineAmountTypes']
                            # QuerySet['AmountDue'] = JsonResponse1[i]['AmountDue']
                            # QuerySet['AmountPaid'] = JsonResponse1[i]['AmountPaid']
                            # QuerySet['AmountCredited'] = JsonResponse1[i]['AmountCredited']
                            QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                            QuerySet['IsDiscounted'] = JsonResponse1[i]['IsDiscounted']

                            for j in range(0, len(JsonResponse1[i]['LineItems'])):
                                QuerySet1 = {}
                                if 'Description' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['Description'] = JsonResponse1[i]['LineItems'][j]['Description']
                                if 'UnitAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['UnitAmount'] = JsonResponse1[i]['LineItems'][j]['UnitAmount']
                                if 'TaxAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['TaxAmount'] = JsonResponse1[i]['LineItems'][j]['TaxAmount']
                                if 'LineAmount' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['LineAmount'] = JsonResponse1[i]['LineItems'][j]['LineAmount']
                                if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                    QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                            
                                if 'AccountCode' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['AccountCode'] = JsonResponse1[i]['LineItems'][j]['AccountCode']
                                if 'Quantity' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['Quantity'] = JsonResponse1[i]['LineItems'][j]['Quantity']
                                
                                if JsonResponse1[i]['IsDiscounted'] == True:
                                    if 'DiscountRate' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Discount'] = JsonResponse1[i]['LineItems'][j]['DiscountRate']
                                    else:
                                        QuerySet1['Discount'] = 0

                                if 'Item' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['ItemCode'] = JsonResponse1[i]['LineItems'][j]['Item']['Code']
                                    QuerySet1['ItemID'] = JsonResponse1[i]['LineItems'][j]['Item']['ItemID']
                                    if 'Name' in JsonResponse1[i]['LineItems'][j]['Item']:
                                        QuerySet1['Name'] = JsonResponse1[i]['LineItems'][j]['Item']['Name']
                                if 'TaxType' in JsonResponse1[i]['LineItems'][j]:
                                    QuerySet1['TaxType'] = JsonResponse1[i]['LineItems'][j]['TaxType']
                                else:
                                    QuerySet1['TaxType'] = None

                                QuerySet['Line'].append(QuerySet1)

                            if (JsonResponse1[i]['Type'] == "ACCREC"):
                                invoice.append(QuerySet)
                            if (JsonResponse1[i]['Type'] == "ACCPAY"):
                                bill.append(QuerySet)
                                
                            
                            
                # if len(invoice)>0:
                #     xero_invoice.insert_many(invoice)
                #     print("Added")
                if len(bill)>0:
                    xero_bill.insert_many(bill)
                  

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


def get_invoice_customers(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_invoice = dbname['xero_invoice_customers']
        payload, base_url, headers = get_settings_xero(job_id)

        if (start_date == '' and end_date == ''):
            main_url = f"{base_url}/Invoices"
        else:
            y1=int(start_date[0:4])
            m1=int(start_date[5:7])
            d1=int(start_date[8:])
            y2=int(end_date[0:4])
            m2=int(end_date[5:7])
            d2=int(end_date[8:])
            main_url = f"{base_url}/Invoices?unitdp=4&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"
    
        print(main_url)
        
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
        time.sleep(1)
        
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1['Invoices']
            no_of_records = len(r2)
            if no_of_records>0:
                no_of_pages = (no_of_records // 100) + 1
                invoice = []
                bill = []
                print(no_of_records,no_of_pages)

                for pages in range(1, no_of_pages+1):
                    if (start_date=='' and end_date==''): 
                        url = f"{base_url}/Invoices?page={pages}&unitdp=4"
                    else:
                        url = f"{base_url}/Invoices?page={pages}&unitdp=4&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"
                
                    print(url)

                    response = requests.request(
                        "GET", url, headers=headers, data=payload)
                    time.sleep(1)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse['Invoices']
                    print(len(JsonResponse1))
                    for i in range(0, len(JsonResponse1)):
                        if (JsonResponse1[i]['Status']!='DELETED') and (JsonResponse1[i]['Status']!='VOIDED') and (JsonResponse1[i]['Status']!='DRAFT'):
                            QuerySet = {}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["payload"] = None
                            QuerySet["table_name"] = "xero_invoice" 

                            QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                            QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                            QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                            
                            if (JsonResponse1[i]['Type'] == "ACCREC"):
                                invoice.append(QuerySet)
                            
                if len(invoice)>0:
                    xero_invoice.insert_many(invoice)
                    print("Added")
                    

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


def get_open_invoice(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_invoice = dbname['xero_open_invoice']
        xero_bill = dbname['xero_open_bill']
        xero_customer = dbname['xero_open_customer']
        xero_supplier = dbname['xero_open_supplier']
        payload, base_url, headers = get_settings_xero(job_id)

        print(start_date,type(start_date))
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)

        if (start_date == '' and end_date == ''):
            # main_url = f"{base_url}/Invoices?unitdp=4"
            main_url = f"{base_url}/Invoices?where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})"
            

        else:
            y1=int(result_string[0:4])
            m1=int(result_string[5:7])
            d1=int(result_string[8:])
            # y2=int(start_date[0:4])
            # m2=int(start_date[5:7])
            # d2=int(start_date[8:])
            # main_url = f"{base_url}/Invoices?unitdp=4&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"
            main_url = f"{base_url}/Invoices?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})"

        # print(main_url)
        
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
        time.sleep(1)
            
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1['Invoices']
            no_of_records = len(r2)
            if no_of_records>0:
                no_of_pages = (no_of_records // 100) + 1
                print(no_of_pages)
                invoice = []
                bill = []
                customer=[]
                supplier=[]
                print(no_of_records,no_of_pages,"======================")

                for pages in range(1, no_of_pages+1):
                    print(pages)
                    if (start_date=='' and end_date==''): 
                        url = f"{base_url}/Invoices?page={pages}&unitdp=4"
                    else:
                        url = f"{base_url}/Invoices?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})&page={pages}"

                    print(url)
                    response = requests.request(
                        "GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse['Invoices']
                    for i in range(0, len(JsonResponse1)):
                        if len(JsonResponse1[i]["Payments"])>0:
                            date_string = JsonResponse1[i]["Payments"][0]['Date']
                            match = re.search(r'\d+', date_string)
                            timestamp = int(match.group()) / 1000  # Convert milliseconds to seconds
                            date = datetime.utcfromtimestamp(timestamp)

                            # Desired date "30-06-2023"
                            desired_date = one_day_before

                            # Compare the dates
                            # if date < desired_date:
                            #     print("The result date less than 30-06-2023.")
                          
                            if (JsonResponse1[i]['Status'] =='AUTHORISED') or (JsonResponse1[i]['Status'] == 'PAID' and date > desired_date) :
                                QuerySet = {"Line": []}
                                QuerySet["job_id"] = job_id
                                QuerySet["task_id"] = task_id
                                QuerySet["is_pushed"] = 0
                                QuerySet["error"] = None
                                QuerySet["payload"] = None
                                
                                QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                                QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                                if 'DueDateString' in JsonResponse1[i]:
                                    QuerySet['DueDate'] = JsonResponse1[i]['DueDateString']
                                QuerySet['TxnDate'] = JsonResponse1[i]['DateString']
                                QuerySet['TotalAmount'] = JsonResponse1[i]['Total']
                                QuerySet['SubTotal'] = JsonResponse1[i]['SubTotal']
                                QuerySet['Status'] = JsonResponse1[i]['Status']
                                QuerySet['TotalTax'] = JsonResponse1[i]['TotalTax']
                                QuerySet['LineAmountTypes'] = JsonResponse1[i]['LineAmountTypes']
                                # QuerySet['AmountDue'] = JsonResponse1[i]['AmountDue']
                                # QuerySet['AmountPaid'] = JsonResponse1[i]['AmountPaid']
                                # QuerySet['AmountCredited'] = JsonResponse1[i]['AmountCredited']
                                QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                QuerySet['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                QuerySet['IsDiscounted'] = JsonResponse1[i]['IsDiscounted']

                                for j in range(0, len(JsonResponse1[i]['LineItems'])):
                                    QuerySet1 = {}
                                    if 'Description' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Description'] = JsonResponse1[i]['LineItems'][j]['Description']
                                    if 'UnitAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['UnitAmount'] = JsonResponse1[i]['LineItems'][j]['UnitAmount']
                                    if 'TaxAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxAmount'] = JsonResponse1[i]['LineItems'][j]['TaxAmount']
                                    if 'LineAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['LineAmount'] = JsonResponse1[i]['LineItems'][j]['LineAmount']
                                    if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                        QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                                
                                    if 'AccountCode' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['AccountCode'] = JsonResponse1[i]['LineItems'][j]['AccountCode']
                                    if 'Quantity' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Quantity'] = JsonResponse1[i]['LineItems'][j]['Quantity']
                                    
                                    if JsonResponse1[i]['IsDiscounted'] == True:
                                        if 'DiscountRate' in JsonResponse1[i]['LineItems'][j]:
                                            QuerySet1['Discount'] = JsonResponse1[i]['LineItems'][j]['DiscountRate']
                                        else:
                                            QuerySet1['Discount'] = 0

                                    if 'Item' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['ItemCode'] = JsonResponse1[i]['LineItems'][j]['Item']['Code']
                                        QuerySet1['ItemID'] = JsonResponse1[i]['LineItems'][j]['Item']['ItemID']
                                        if 'Name' in JsonResponse1[i]['LineItems'][j]['Item']:
                                            QuerySet1['Name'] = JsonResponse1[i]['LineItems'][j]['Item']['Name']
                                    if 'TaxType' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxType'] = JsonResponse1[i]['LineItems'][j]['TaxType']
                                    else:
                                        QuerySet1['TaxType'] = None

                                    QuerySet['Line'].append(QuerySet1)

                                if (JsonResponse1[i]['Type'] == "ACCREC"): #and (JsonResponse1[i]['AmountDue']>0):
                                    cust={}
                                    QuerySet["table_name"] = "xero_open_invoice" 
                                    cust['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    cust['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    cust['Type'] = "AR"
                                    cust['job_id'] = job_id

                                    invoice.append(QuerySet)
                                    if cust not in customer: 
                                        customer.append(cust)

                                if (JsonResponse1[i]['Type'] == "ACCPAY"):
                                    QuerySet["table_name"] = "xero_open_bill" 
                                    supp={}
                                    supp['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    supp['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    supp['Type'] = "AP"
                                    supp['job_id'] = job_id

                                    bill.append(QuerySet)
                                    if supp not in supplier: 
                                        supplier.append(supp)
                                
                        elif len(JsonResponse1[i]["Payments"])==0:
                            if (JsonResponse1[i]['Status'] =='AUTHORISED'):
                                QuerySet = {"Line": []}
                                QuerySet["job_id"] = job_id
                                QuerySet["task_id"] = task_id
                                QuerySet["is_pushed"] = 0
                                QuerySet["error"] = None
                                QuerySet["payload"] = None
                                
                                QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                                QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                                if 'DueDateString' in JsonResponse1[i]:
                                    QuerySet['DueDate'] = JsonResponse1[i]['DueDateString']
                                QuerySet['TxnDate'] = JsonResponse1[i]['DateString']
                                QuerySet['TotalAmount'] = JsonResponse1[i]['Total']
                                QuerySet['SubTotal'] = JsonResponse1[i]['SubTotal']
                                QuerySet['Status'] = JsonResponse1[i]['Status']
                                QuerySet['TotalTax'] = JsonResponse1[i]['TotalTax']
                                QuerySet['LineAmountTypes'] = JsonResponse1[i]['LineAmountTypes']
                                # QuerySet['AmountDue'] = JsonResponse1[i]['AmountDue']
                                # QuerySet['AmountPaid'] = JsonResponse1[i]['AmountPaid']
                                # QuerySet['AmountCredited'] = JsonResponse1[i]['AmountCredited']
                                QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                QuerySet['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                QuerySet['IsDiscounted'] = JsonResponse1[i]['IsDiscounted']

                                for j in range(0, len(JsonResponse1[i]['LineItems'])):
                                    QuerySet1 = {}
                                    if 'Description' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Description'] = JsonResponse1[i]['LineItems'][j]['Description']
                                    if 'UnitAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['UnitAmount'] = JsonResponse1[i]['LineItems'][j]['UnitAmount']
                                    if 'TaxAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxAmount'] = JsonResponse1[i]['LineItems'][j]['TaxAmount']
                                    if 'LineAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['LineAmount'] = JsonResponse1[i]['LineItems'][j]['LineAmount']
                                    if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                        QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                                
                                    if 'AccountCode' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['AccountCode'] = JsonResponse1[i]['LineItems'][j]['AccountCode']
                                    if 'Quantity' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Quantity'] = JsonResponse1[i]['LineItems'][j]['Quantity']
                                    
                                    if JsonResponse1[i]['IsDiscounted'] == True:
                                        if 'DiscountRate' in JsonResponse1[i]['LineItems'][j]:
                                            QuerySet1['Discount'] = JsonResponse1[i]['LineItems'][j]['DiscountRate']
                                        else:
                                            QuerySet1['Discount'] = 0

                                    if 'Item' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['ItemCode'] = JsonResponse1[i]['LineItems'][j]['Item']['Code']
                                        QuerySet1['ItemID'] = JsonResponse1[i]['LineItems'][j]['Item']['ItemID']
                                        if 'Name' in JsonResponse1[i]['LineItems'][j]['Item']:
                                            QuerySet1['Name'] = JsonResponse1[i]['LineItems'][j]['Item']['Name']
                                    if 'TaxType' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxType'] = JsonResponse1[i]['LineItems'][j]['TaxType']
                                    else:
                                        QuerySet1['TaxType'] = None

                                    QuerySet['Line'].append(QuerySet1)

                                if (JsonResponse1[i]['Type'] == "ACCREC"): #and (JsonResponse1[i]['AmountDue']>0):
                                    cust={}
                                    QuerySet["table_name"] = "xero_open_invoice" 
                                    cust['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    cust['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    cust['Type'] = "AR"
                                    cust['job_id'] = job_id

                                    invoice.append(QuerySet)
                                    if cust not in customer: 
                                        customer.append(cust)

                                if (JsonResponse1[i]['Type'] == "ACCPAY"):
                                    QuerySet["table_name"] = "xero_open_bill" 
                                    supp={}
                                    supp['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    supp['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    supp['Type'] = "AP"
                                    supp['job_id'] = job_id

                                    bill.append(QuerySet)
                                    if supp not in supplier: 
                                        supplier.append(supp)
                            
                        
                            
                if len(invoice)>0:
                    print(len(invoice))
                    xero_invoice.insert_many(invoice)
                if len(bill)>0:
                    print(len(bill),"bill count------------------------------")
                    xero_bill.insert_many(bill)
                if len(customer)>0:
                    print(len(customer))
                    xero_customer.insert_many(customer)
                if len(supplier)>0:
                    print(len(supplier))
                    xero_supplier.insert_many(supplier)
              
              
                step_name = "Reading data from xero invoice"
                write_task_execution_step(task_id, status=1, step=step_name)
                    

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_open_invoice_till_end_date(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_invoice = dbname['xero_open_invoice_end_date']
        xero_bill = dbname['xero_open_bill_end_date']
        xero_customer = dbname['xero_open_customer_end_date']
        xero_supplier = dbname['xero_open_supplier_end_date']
        payload, base_url, headers = get_settings_xero(job_id)

        print(end_date,type(end_date))
        date_object = datetime.strptime(end_date, '%Y-%m-%d')
        result_string = date_object.strftime('%Y-%m-%d')
        print(result_string)

        if (start_date == '' and end_date == ''):
            main_url = f"{base_url}/Invoices?where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})"
            
        else:
            y1=int(result_string[0:4])
            m1=int(result_string[5:7])
            d1=int(result_string[8:])
            main_url = f"{base_url}/Invoices?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})"

        print(main_url)
        
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
        time.sleep(1)
            
        if response1.status_code == 200:
            print("if")
            r1 = response1.json()
            r2 = r1['Invoices']
            no_of_records = len(r2)
            if no_of_records>0:
                no_of_pages = (no_of_records // 100) + 1
                print(no_of_pages)
                invoice = []
                bill = []
                customer=[]
                supplier=[]
                print(no_of_records,no_of_pages,"======================")

                for pages in range(1, no_of_pages+1):
                    print(pages)
                    if (start_date=='' and end_date==''): 
                        url = f"{base_url}/Invoices?page={pages}&unitdp=4"
                    else:
                        url = f"{base_url}/Invoices?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})&page={pages}"

                    print(url)
                    response = requests.request(
                        "GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse['Invoices']
                    for i in range(0, len(JsonResponse1)):
                        if len(JsonResponse1[i]["Payments"])>0:
                            date_string = JsonResponse1[i]["Payments"][0]['Date']
                            match = re.search(r'\d+', date_string)
                            timestamp = int(match.group()) / 1000  # Convert milliseconds to seconds
                            date = datetime.utcfromtimestamp(timestamp)

                            # Desired date "30-06-2023"
                            desired_date = date_object

                            # Compare the dates
                            # if date < desired_date:
                            #     print("The result date less than 30-06-2023.")
                          
                            if (JsonResponse1[i]['Status'] =='AUTHORISED') or (JsonResponse1[i]['Status'] == 'PAID' and date > desired_date) :
                                QuerySet = {"Line": []}
                                QuerySet["job_id"] = job_id
                                QuerySet["task_id"] = task_id
                                QuerySet["is_pushed"] = 0
                                QuerySet["error"] = None
                                QuerySet["payload"] = None
                                
                                QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                                QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                                if 'DueDateString' in JsonResponse1[i]:
                                    QuerySet['DueDate'] = JsonResponse1[i]['DueDateString']
                                QuerySet['TxnDate'] = JsonResponse1[i]['DateString']
                                QuerySet['TotalAmount'] = JsonResponse1[i]['Total']
                                QuerySet['SubTotal'] = JsonResponse1[i]['SubTotal']
                                QuerySet['Status'] = JsonResponse1[i]['Status']
                                QuerySet['TotalTax'] = JsonResponse1[i]['TotalTax']
                                QuerySet['LineAmountTypes'] = JsonResponse1[i]['LineAmountTypes']
                                # QuerySet['AmountDue'] = JsonResponse1[i]['AmountDue']
                                # QuerySet['AmountPaid'] = JsonResponse1[i]['AmountPaid']
                                # QuerySet['AmountCredited'] = JsonResponse1[i]['AmountCredited']
                                QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                QuerySet['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                QuerySet['IsDiscounted'] = JsonResponse1[i]['IsDiscounted']

                                for j in range(0, len(JsonResponse1[i]['LineItems'])):
                                    QuerySet1 = {}
                                    if 'Description' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Description'] = JsonResponse1[i]['LineItems'][j]['Description']
                                    if 'UnitAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['UnitAmount'] = JsonResponse1[i]['LineItems'][j]['UnitAmount']
                                    if 'TaxAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxAmount'] = JsonResponse1[i]['LineItems'][j]['TaxAmount']
                                    if 'LineAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['LineAmount'] = JsonResponse1[i]['LineItems'][j]['LineAmount']
                                    if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                        QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                                
                                    if 'AccountCode' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['AccountCode'] = JsonResponse1[i]['LineItems'][j]['AccountCode']
                                    if 'Quantity' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Quantity'] = JsonResponse1[i]['LineItems'][j]['Quantity']
                                    
                                    if JsonResponse1[i]['IsDiscounted'] == True:
                                        if 'DiscountRate' in JsonResponse1[i]['LineItems'][j]:
                                            QuerySet1['Discount'] = JsonResponse1[i]['LineItems'][j]['DiscountRate']
                                        else:
                                            QuerySet1['Discount'] = 0

                                    if 'Item' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['ItemCode'] = JsonResponse1[i]['LineItems'][j]['Item']['Code']
                                        QuerySet1['ItemID'] = JsonResponse1[i]['LineItems'][j]['Item']['ItemID']
                                        if 'Name' in JsonResponse1[i]['LineItems'][j]['Item']:
                                            QuerySet1['Name'] = JsonResponse1[i]['LineItems'][j]['Item']['Name']
                                    if 'TaxType' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxType'] = JsonResponse1[i]['LineItems'][j]['TaxType']
                                    else:
                                        QuerySet1['TaxType'] = None

                                    QuerySet['Line'].append(QuerySet1)

                                if (JsonResponse1[i]['Type'] == "ACCREC"): #and (JsonResponse1[i]['AmountDue']>0):
                                    cust={}
                                    QuerySet["table_name"] = "xero_open_invoice_end_date" 
                                    cust['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    cust['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    cust['Type'] = "AR"
                                    cust['job_id'] = job_id

                                    invoice.append(QuerySet)
                                    if cust not in customer: 
                                        customer.append(cust)

                                if (JsonResponse1[i]['Type'] == "ACCPAY"):
                                    QuerySet["table_name"] = "xero_open_bill_end_date" 
                                    supp={}
                                    supp['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    supp['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    supp['Type'] = "AP"
                                    supp['job_id'] = job_id

                                    bill.append(QuerySet)
                                    if supp not in supplier: 
                                        supplier.append(supp)
                                
                        elif len(JsonResponse1[i]["Payments"])==0:
                            if (JsonResponse1[i]['Status'] =='AUTHORISED'):
                                QuerySet = {"Line": []}
                                QuerySet["job_id"] = job_id
                                QuerySet["task_id"] = task_id
                                QuerySet["is_pushed"] = 0
                                QuerySet["error"] = None
                                QuerySet["payload"] = None
                                
                                QuerySet['Inv_No'] = JsonResponse1[i]['InvoiceNumber']
                                QuerySet['Inv_ID'] = JsonResponse1[i]['InvoiceID']
                                if 'DueDateString' in JsonResponse1[i]:
                                    QuerySet['DueDate'] = JsonResponse1[i]['DueDateString']
                                QuerySet['TxnDate'] = JsonResponse1[i]['DateString']
                                QuerySet['TotalAmount'] = JsonResponse1[i]['Total']
                                QuerySet['SubTotal'] = JsonResponse1[i]['SubTotal']
                                QuerySet['Status'] = JsonResponse1[i]['Status']
                                QuerySet['TotalTax'] = JsonResponse1[i]['TotalTax']
                                QuerySet['LineAmountTypes'] = JsonResponse1[i]['LineAmountTypes']
                                # QuerySet['AmountDue'] = JsonResponse1[i]['AmountDue']
                                # QuerySet['AmountPaid'] = JsonResponse1[i]['AmountPaid']
                                # QuerySet['AmountCredited'] = JsonResponse1[i]['AmountCredited']
                                QuerySet['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                QuerySet['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                QuerySet['IsDiscounted'] = JsonResponse1[i]['IsDiscounted']

                                for j in range(0, len(JsonResponse1[i]['LineItems'])):
                                    QuerySet1 = {}
                                    if 'Description' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Description'] = JsonResponse1[i]['LineItems'][j]['Description']
                                    if 'UnitAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['UnitAmount'] = JsonResponse1[i]['LineItems'][j]['UnitAmount']
                                    if 'TaxAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxAmount'] = JsonResponse1[i]['LineItems'][j]['TaxAmount']
                                    if 'LineAmount' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['LineAmount'] = JsonResponse1[i]['LineItems'][j]['LineAmount']
                                    if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                        QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                                
                                    if 'AccountCode' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['AccountCode'] = JsonResponse1[i]['LineItems'][j]['AccountCode']
                                    if 'Quantity' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['Quantity'] = JsonResponse1[i]['LineItems'][j]['Quantity']
                                    
                                    if JsonResponse1[i]['IsDiscounted'] == True:
                                        if 'DiscountRate' in JsonResponse1[i]['LineItems'][j]:
                                            QuerySet1['Discount'] = JsonResponse1[i]['LineItems'][j]['DiscountRate']
                                        else:
                                            QuerySet1['Discount'] = 0

                                    if 'Item' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['ItemCode'] = JsonResponse1[i]['LineItems'][j]['Item']['Code']
                                        QuerySet1['ItemID'] = JsonResponse1[i]['LineItems'][j]['Item']['ItemID']
                                        if 'Name' in JsonResponse1[i]['LineItems'][j]['Item']:
                                            QuerySet1['Name'] = JsonResponse1[i]['LineItems'][j]['Item']['Name']
                                    if 'TaxType' in JsonResponse1[i]['LineItems'][j]:
                                        QuerySet1['TaxType'] = JsonResponse1[i]['LineItems'][j]['TaxType']
                                    else:
                                        QuerySet1['TaxType'] = None

                                    QuerySet['Line'].append(QuerySet1)

                                if (JsonResponse1[i]['Type'] == "ACCREC"): #and (JsonResponse1[i]['AmountDue']>0):
                                    cust={}
                                    QuerySet["table_name"] = "xero_open_invoice_end_date" 
                                    cust['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    cust['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    cust['Type'] = "AR"
                                    cust['job_id'] = job_id

                                    invoice.append(QuerySet)
                                    if cust not in customer: 
                                        customer.append(cust)

                                if (JsonResponse1[i]['Type'] == "ACCPAY"):
                                    QuerySet["table_name"] = "xero_open_bill_end_date" 
                                    supp={}
                                    supp['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                    supp['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                    supp['Type'] = "AP"
                                    supp['job_id'] = job_id

                                    bill.append(QuerySet)
                                    if supp not in supplier: 
                                        supplier.append(supp)
                            
                        
                            
                if len(invoice)>0:
                    print(len(invoice))
                    xero_invoice.insert_many(invoice)
                if len(bill)>0:
                    print(len(bill),"bill count------------------------------")
                    xero_bill.insert_many(bill)
                if len(customer)>0:
                    print(len(customer))
                    xero_customer.insert_many(customer)
                if len(supplier)>0:
                    print(len(supplier))
                    xero_supplier.insert_many(supplier)
              
              
                step_name = "Reading data from xero invoice"
                write_task_execution_step(task_id, status=1, step=step_name)
                    

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
