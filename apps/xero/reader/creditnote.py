import traceback

import requests

from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import  write_task_execution_step,update_task_execution_status
import sys
from datetime import datetime, timedelta
from apps.util.log_file import log_config
import logging
import time


def get_creditnote(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_creditnote = dbname["xero_creditnote"]
        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/CreditNotes?unitdp=4"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/CreditNotes?unitdp=4&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        time.sleep(1)
        
        print(response1)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["CreditNotes"]
            if len(r2)>0:  
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                creditnote = []
                
                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        url = f"{base_url}/CreditNotes?page={pages}&unitdp=4"
                    else:
                        url = f"{base_url}/CreditNotes?page={pages}&unitdp=4&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

                    response = requests.request("GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["CreditNotes"]

                    for i in range(0, len(JsonResponse1)):
                        if (
                            JsonResponse1[i]["Status"] != "DELETED"
                            and JsonResponse1[i]["Status"] != "VOIDED"
                            and JsonResponse1[i]["Status"] != "DRAFT"
                        ):
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["table_name"] = "xero_creditnote" 
                            QuerySet["error"] = None 
                            QuerySet["payload"] = None 

                            QuerySet["Inv_No"] = JsonResponse1[i]["CreditNoteNumber"]
                            QuerySet["Inv_ID"] = JsonResponse1[i]["CreditNoteID"]
                            QuerySet["TxnDate"] = JsonResponse1[i]["DateString"]
                            QuerySet["TotalAmount"] = JsonResponse1[i]["Total"]
                            QuerySet["SubTotal"] = JsonResponse1[i]["SubTotal"]
                            QuerySet["TotalTax"] = JsonResponse1[i]["TotalTax"]
                            QuerySet["Status"] = JsonResponse1[i]["Status"]
                            QuerySet["Type"] = JsonResponse1[i]["Type"]
                            if 'Reference' in JsonResponse1[i]:
                                QuerySet["Reference"] = JsonResponse1[i]["Reference"]
                            QuerySet["LineAmountTypes"] = JsonResponse1[i]["LineAmountTypes"]
                            QuerySet["CurrencyCode"] = JsonResponse1[i]["CurrencyCode"]
                            QuerySet["AmountDue"] = JsonResponse1[i]["RemainingCredit"]
                            QuerySet["ContactName"] = JsonResponse1[i]["Contact"]["Name"]

                            for j in range(0, len(JsonResponse1[i]["LineItems"])):
                                QuerySet1 = {}
                                if "Description" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Description"] = JsonResponse1[i]["LineItems"][j][
                                        "Description"
                                    ]
                                if "UnitAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["UnitAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "UnitAmount"
                                    ]
                                if "TaxAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["TaxAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "TaxAmount"
                                    ]
                                if "LineAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["LineAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "LineAmount"
                                    ]
                                if "AccountCode" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["AccountCode"] = JsonResponse1[i]["LineItems"][j][
                                        "AccountCode"
                                    ]

                                if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                    QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                                    
                                if "Quantity" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Quantity"] = JsonResponse1[i]["LineItems"][j][
                                        "Quantity"
                                    ]
                                
                                if JsonResponse1[i]["LineItems"][j] != None and  JsonResponse1[i]["LineItems"][j] !=[]:
                                    if "Item" in JsonResponse1[i]["LineItems"][j]:
                                        QuerySet1["ItemCode"] = JsonResponse1[i]["LineItems"][j]["Item"]["Code"]
                                        QuerySet1["ItemID"] = JsonResponse1[i]["LineItems"][j]["Item"]["ItemID"]
                                        if "Name" in JsonResponse1[i]["LineItems"][j]["Item"]:
                                            QuerySet1["Name"] = JsonResponse1[i]["LineItems"][j]["Item"]["Name"]
                                    else:
                                        QuerySet1["ItemCode"] = None
                                        QuerySet1["ItemID"] = None
                                        QuerySet1["Name"] = None

                                    if "TaxType" in JsonResponse1[i]["LineItems"][j]:
                                        QuerySet1["TaxType"] = JsonResponse1[i]["LineItems"][j][
                                            "TaxType"
                                        ]
                                    else:
                                        QuerySet1["TaxType"] = None

                                QuerySet["Line"].append(QuerySet1)

                            if JsonResponse1[i]["Type"] == "ACCRECCREDIT":
                                creditnote.append(QuerySet)

                if len(creditnote) > 0:
                    xero_creditnote.insert_many(creditnote)

                step_name = "Reading data from xero creditnote"
                write_task_execution_step(task_id, status=1, step=step_name)
                
    except Exception as ex:
        step_name = "Something went wrong"
        logging.error(ex, exc_info=True)
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
        

def get_open_creditnote(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_creditnote = dbname["xero_open_creditnote"]
        xero_suppliercredit = dbname["xero_open_suppliercredit"]
        
        xero_customer = dbname['xero_open_customer']
        x = xero_customer.find({"job_id":job_id})
        data1 = []
        for p1 in x:
            p1.pop("_id")
            data1.append(p1)
        
        xero_supplier = dbname['xero_open_supplier']
        y = xero_supplier.find({"job_id":job_id})
        data2 = []
        for p2 in y:
            p2.pop("_id")
            data2.append(p2)
        
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)
        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/CreditNotes?unitdp=4"
        else:
            y1 = int(result_string[0:4])
            m1 = int(result_string[5:7])
            d1 = int(result_string[8:])
            main_url = f"{base_url}/CreditNotes?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        time.sleep(1)
        
        print(response1)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["CreditNotes"]
            if len(r2)>0:  
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                creditnote = []
                suppliercredit = []
                customer=[]
                supplier=[]
                
                
                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        url = f"{base_url}/CreditNotes?page={pages}&unitdp=4"
                    else:
                        url = f"{base_url}/CreditNotes?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})&page={pages}"

                    response = requests.request("GET", url, headers=headers, data=payload)
                    time.sleep(1)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["CreditNotes"]

                    for i in range(0, len(JsonResponse1)):
                        if (JsonResponse1[i]['Status'] not in ['DELETED','PAID']) and (JsonResponse1[i]['RemainingCredit']>=0):
                        
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None 
                            QuerySet["payload"] = None 

                            QuerySet["Inv_No"] = JsonResponse1[i]["CreditNoteNumber"]
                            QuerySet["Inv_ID"] = JsonResponse1[i]["CreditNoteID"]
                            QuerySet["TxnDate"] = JsonResponse1[i]["DateString"]
                            QuerySet["TotalAmount"] = JsonResponse1[i]["Total"]
                            QuerySet["SubTotal"] = JsonResponse1[i]["SubTotal"]
                            QuerySet["TotalTax"] = JsonResponse1[i]["TotalTax"]
                            QuerySet["Status"] = JsonResponse1[i]["Status"]
                            QuerySet["Type"] = JsonResponse1[i]["Type"]
                            if 'Reference' in JsonResponse1[i]:
                                QuerySet["Reference"] = JsonResponse1[i]["Reference"]
                            QuerySet["LineAmountTypes"] = JsonResponse1[i]["LineAmountTypes"]
                            QuerySet["CurrencyCode"] = JsonResponse1[i]["CurrencyCode"]
                            QuerySet["AmountDue"] = JsonResponse1[i]["RemainingCredit"]
                            QuerySet["ContactName"] = JsonResponse1[i]["Contact"]["Name"]

                            for j in range(0, len(JsonResponse1[i]["LineItems"])):
                                QuerySet1 = {}
                                if "Description" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Description"] = JsonResponse1[i]["LineItems"][j][
                                        "Description"
                                    ]
                                if "UnitAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["UnitAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "UnitAmount"
                                    ]
                                if "TaxAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["TaxAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "TaxAmount"
                                    ]
                                if "LineAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["LineAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "LineAmount"
                                    ]
                                if "AccountCode" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["AccountCode"] = JsonResponse1[i]["LineItems"][j][
                                        "AccountCode"
                                    ]

                                if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                    QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                                else:
                                    QuerySet1['TrackingID']=None   
                                if "Quantity" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Quantity"] = JsonResponse1[i]["LineItems"][j][
                                        "Quantity"
                                    ]
                                
                                if JsonResponse1[i]["LineItems"][j] != None and  JsonResponse1[i]["LineItems"][j] !=[]:
                                    if "Item" in JsonResponse1[i]["LineItems"][j]:
                                        QuerySet1["ItemCode"] = JsonResponse1[i]["LineItems"][j]["Item"]["Code"]
                                        QuerySet1["ItemID"] = JsonResponse1[i]["LineItems"][j]["Item"]["ItemID"]
                                        if "Name" in JsonResponse1[i]["LineItems"][j]["Item"]:
                                            QuerySet1["Name"] = JsonResponse1[i]["LineItems"][j]["Item"]["Name"]
                                    else:
                                        QuerySet1["ItemCode"] = None
                                        QuerySet1["ItemID"] = None
                                        QuerySet1["Name"] = None

                                    if "TaxType" in JsonResponse1[i]["LineItems"][j]:
                                        QuerySet1["TaxType"] = JsonResponse1[i]["LineItems"][j][
                                            "TaxType"
                                        ]
                                    else:
                                        QuerySet1["TaxType"] = None

                                QuerySet["Line"].append(QuerySet1)

                            if JsonResponse1[i]["Type"] == "ACCRECCREDIT":
                                QuerySet["table_name"] = "xero_creditnote" 
                                creditnote.append(QuerySet)
                                cust={}
                                cust['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                cust['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                cust['Type'] = "AR"
                                cust['job_id'] = job_id

                                if cust not in data1:
                                    customer.append(cust)
                                else:
                                    print("cust",cust)

                            if JsonResponse1[i]["Type"] == "ACCPAYCREDIT":
                                QuerySet["table_name"] = "xero_suppliercredit" 
                                suppliercredit.append(QuerySet)
                                supp={}
                                supp['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                supp['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                supp['Type'] = "AP"
                                supp['job_id'] = job_id

                                if supp not in data2:
                                    supplier.append(supp)

                if len(creditnote) > 0:
                    xero_creditnote.insert_many(creditnote)
                if len(suppliercredit) > 0:
                    xero_suppliercredit.insert_many(suppliercredit)
                if len(customer)>0:
                    print(len(customer))
                    xero_customer.insert_many(customer)
                if len(supplier)>0:
                    print(len(supplier))
                    xero_supplier.insert_many(supplier)
              

                
                step_name = "Reading data from xero creditnote"
                write_task_execution_step(task_id, status=1, step=step_name)
                
    except Exception as ex:
        step_name = "Something went wrong"
        logging.error(ex, exc_info=True)
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
        

def get_open_creditnote_till_end_date(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_creditnote = dbname["xero_open_creditnote_till_end_date"]
        xero_suppliercredit = dbname["xero_open_suppliercredit_till_end_date"]
        
        xero_customer = dbname['xero_open_customer_till_end_date']
        x = xero_customer.find({"job_id":job_id})
        data1 = []
        for p1 in x:
            p1.pop("_id")
            data1.append(p1)
        
        xero_supplier = dbname['xero_open_supplier_till_end_date']
        y = xero_supplier.find({"job_id":job_id})
        data2 = []
        for p2 in y:
            p2.pop("_id")
            data2.append(p2)
        
        date_object = datetime.strptime(end_date, '%Y-%m-%d')
        result_string = date_object.strftime('%Y-%m-%d')
        print(result_string)
        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/CreditNotes?unitdp=4"
        else:
            y1 = int(result_string[0:4])
            m1 = int(result_string[5:7])
            d1 = int(result_string[8:])
            main_url = f"{base_url}/CreditNotes?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})"

        print(main_url)
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        time.sleep(1)
        
        print(response1.status_code,response1)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["CreditNotes"]
            if len(r2)>0:  
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                creditnote = []
                suppliercredit = []
                customer=[]
                supplier=[]
                
                
                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        url = f"{base_url}/CreditNotes?page={pages}&unitdp=4"
                    else:
                        url = f"{base_url}/CreditNotes?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})&page={pages}"

                    response = requests.request("GET", url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    time.sleep(1)
                    JsonResponse1 = JsonResponse["CreditNotes"]

                    for i in range(0, len(JsonResponse1)):
                        if (JsonResponse1[i]['Status'] not in ['DELETED','PAID']) and (JsonResponse1[i]['RemainingCredit']>=0):
                        
                            QuerySet = {"Line": []}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None 
                            QuerySet["payload"] = None 

                            QuerySet["Inv_No"] = JsonResponse1[i]["CreditNoteNumber"]
                            QuerySet["Inv_ID"] = JsonResponse1[i]["CreditNoteID"]
                            QuerySet["TxnDate"] = JsonResponse1[i]["DateString"]
                            QuerySet["TotalAmount"] = JsonResponse1[i]["Total"]
                            QuerySet["SubTotal"] = JsonResponse1[i]["SubTotal"]
                            QuerySet["TotalTax"] = JsonResponse1[i]["TotalTax"]
                            QuerySet["Status"] = JsonResponse1[i]["Status"]
                            QuerySet["Type"] = JsonResponse1[i]["Type"]
                            if 'Reference' in JsonResponse1[i]:
                                QuerySet["Reference"] = JsonResponse1[i]["Reference"]
                            QuerySet["LineAmountTypes"] = JsonResponse1[i]["LineAmountTypes"]
                            QuerySet["CurrencyCode"] = JsonResponse1[i]["CurrencyCode"]
                            QuerySet["AmountDue"] = JsonResponse1[i]["RemainingCredit"]
                            QuerySet["ContactName"] = JsonResponse1[i]["Contact"]["Name"]

                            for j in range(0, len(JsonResponse1[i]["LineItems"])):
                                QuerySet1 = {}
                                if "Description" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Description"] = JsonResponse1[i]["LineItems"][j][
                                        "Description"
                                    ]
                                if "UnitAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["UnitAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "UnitAmount"
                                    ]
                                if "TaxAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["TaxAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "TaxAmount"
                                    ]
                                if "LineAmount" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["LineAmount"] = JsonResponse1[i]["LineItems"][j][
                                        "LineAmount"
                                    ]
                                if "AccountCode" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["AccountCode"] = JsonResponse1[i]["LineItems"][j][
                                        "AccountCode"
                                    ]

                                if 'Tracking' in JsonResponse1[i]['LineItems'][j] and len(JsonResponse1[i]['LineItems'][j]['Tracking']):
                                    QuerySet1['TrackingID'] = JsonResponse1[i]['LineItems'][j]['Tracking'][0]['Option']
                                else:
                                    QuerySet1['TrackingID']=None  
                                if "Quantity" in JsonResponse1[i]["LineItems"][j]:
                                    QuerySet1["Quantity"] = JsonResponse1[i]["LineItems"][j][
                                        "Quantity"
                                    ]
                                
                                if JsonResponse1[i]["LineItems"][j] != None and  JsonResponse1[i]["LineItems"][j] !=[]:
                                    if "Item" in JsonResponse1[i]["LineItems"][j]:
                                        QuerySet1["ItemCode"] = JsonResponse1[i]["LineItems"][j]["Item"]["Code"]
                                        QuerySet1["ItemID"] = JsonResponse1[i]["LineItems"][j]["Item"]["ItemID"]
                                        if "Name" in JsonResponse1[i]["LineItems"][j]["Item"]:
                                            QuerySet1["Name"] = JsonResponse1[i]["LineItems"][j]["Item"]["Name"]
                                    else:
                                        QuerySet1["ItemCode"] = None
                                        QuerySet1["ItemID"] = None
                                        QuerySet1["Name"] = None

                                    if "TaxType" in JsonResponse1[i]["LineItems"][j]:
                                        QuerySet1["TaxType"] = JsonResponse1[i]["LineItems"][j][
                                            "TaxType"
                                        ]
                                    else:
                                        QuerySet1["TaxType"] = None

                                QuerySet["Line"].append(QuerySet1)

                            if JsonResponse1[i]["Type"] == "ACCRECCREDIT":
                                QuerySet["table_name"] = "xero_creditnote" 
                                creditnote.append(QuerySet)
                                cust={}
                                cust['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                cust['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                cust['Type'] = "AR"
                                cust['job_id'] = job_id

                                if cust not in data1:
                                    customer.append(cust)
                                else:
                                    print("cust",cust)

                            if JsonResponse1[i]["Type"] == "ACCPAYCREDIT":
                                QuerySet["table_name"] = "xero_suppliercredit" 
                                suppliercredit.append(QuerySet)
                                supp={}
                                supp['ContactName'] = JsonResponse1[i]['Contact']['Name']
                                supp['ContactID'] = JsonResponse1[i]['Contact']['ContactID']
                                supp['Type'] = "AP"
                                supp['job_id'] = job_id

                                if supp not in data2:
                                    supplier.append(supp)

                if len(creditnote) > 0:
                    xero_creditnote.insert_many(creditnote)
                if len(suppliercredit) > 0:
                    xero_suppliercredit.insert_many(suppliercredit)
                if len(customer)>0:
                    print(len(customer))
                    xero_customer.insert_many(customer)
                if len(supplier)>0:
                    print(len(supplier))
                    xero_supplier.insert_many(supplier)
              
                step_name = "Reading data from xero creditnote"
                write_task_execution_step(task_id, status=1, step=step_name)
                
    except Exception as ex:
        step_name = "Something went wrong"
        logging.error(ex, exc_info=True)
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
        

