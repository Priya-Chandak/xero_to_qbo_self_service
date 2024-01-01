import traceback

import requests

from apps.home.data_util import add_job_status
from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import  write_task_execution_step,update_task_execution_status
import sys
from datetime import datetime, timedelta
import time

def get_xero_payment(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_bill_payment = dbname["xero_bill_payment"]
        xero_invoice_payment = dbname["xero_invoice_payment"]
        xero_supplier_credit_cash_refund = dbname["xero_supplier_credit_cash_refund"]
        xero_receive_overpayment_cash_refund =dbname['xero_receive_overpayment_cash_refund']
        xero_spend_overpayment_cash_refund = dbname['xero_spend_overpayment_cash_refund']
        xero_credit_memo_cash_refund =dbname['xero_credit_memo_cash_refund']

        payload, base_url, headers = get_settings_xero(job_id)

        if start_date == "" and end_date == "":
            main_url = f"{base_url}/Payments"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/Payments?where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        time.sleep(1)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["Payments"]
            if len(r2)>0:
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                bill_payment = []
                invoice_payment = []
                supplier_credit_cash_refund=[]
                receive_overpayment_cash_refund=[]
                spend_overpayment_cash_refund=[]
                credit_memo_refund_payment=[]

                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        main_url = f"{base_url}/Payments?page={pages}"
                    else:
                        y1 = int(start_date[0:4])
                        m1 = int(start_date[5:7])
                        d1 = int(start_date[8:])
                        y2 = int(end_date[0:4])
                        m2 = int(end_date[5:7])
                        d2 = int(end_date[8:])
                        main_url = f"{base_url}/Payments?page={pages}&where=Date%3E%3DDateTime({y1}%2C{m1}%2C{d1})%20AND%20Date%3C%3DDateTime({y2}%2C{m2}%2C{d2})"

                    print(main_url)
                    response = requests.request("GET", main_url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    time.sleep(1)
                    JsonResponse1 = JsonResponse["Payments"]

                    for i in range(0, len(JsonResponse1)):
                        if (
                            JsonResponse1[i]["Status"] != "DELETED"
                            and JsonResponse1[i]["Status"] != "VOIDED"
                        ):
                            QuerySet = {}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["payload"] = None
                            QuerySet["Date"] = JsonResponse1[i]["Date"]
                            QuerySet["BankAmount"] = JsonResponse1[i]["BankAmount"]
                            QuerySet["Amount"] = JsonResponse1[i]["Amount"]

                            if "BatchPayment" in JsonResponse1[i]:
                                QuerySet["BatchPaymentID"] = JsonResponse1[i]["BatchPayment"][
                                    "BatchPaymentID"
                                ]
                                QuerySet["Type"] = JsonResponse1[i]["BatchPayment"]["Type"]
                                QuerySet["TotalAmount"] = JsonResponse1[i]["BatchPayment"][
                                    "TotalAmount"
                                ]
                            else:
                                QuerySet["Type"] = "SinglePayment"

                            if "Reference" in JsonResponse1[i]:
                                QuerySet["Reference"] = JsonResponse1[i]["Reference"]
                            QuerySet["PaymentType"] = JsonResponse1[i]["PaymentType"]
                            QuerySet["Status"] = JsonResponse1[i]["Status"]
                            QuerySet["HasAccount"] = JsonResponse1[i]["HasAccount"]

                            if QuerySet["HasAccount"] == True:
                                QuerySet["AccountCode"] = JsonResponse1[i]["Account"]["AccountID"]

                            if "InvoiceNumber" in JsonResponse1[i]["Invoice"]:
                                QuerySet["InvoiceNumber"] = JsonResponse1[i]["Invoice"][
                                    "InvoiceNumber"
                                ]
                                QuerySet["InvoiceID"] = JsonResponse1[i]["Invoice"]["InvoiceID"]

                            QuerySet["InvoiceType"] = JsonResponse1[i]["Invoice"]["Type"]
                            QuerySet["Contact"] = JsonResponse1[i]["Invoice"]["Contact"]["Name"]
                            QuerySet["ContactID"] = JsonResponse1[i]["Invoice"]["Contact"]["ContactID"]

                            if JsonResponse1[i]["PaymentType"] == "ACCRECPAYMENT":
                                QuerySet["table_name"] = "xero_invoice_payment" 
                                invoice_payment.append(QuerySet)
                            elif JsonResponse1[i]["PaymentType"] == "ACCPAYPAYMENT":
                                QuerySet["table_name"] = "xero_bill_payment" 
                                bill_payment.append(QuerySet)
                            elif JsonResponse1[i]["PaymentType"] == "APCREDITPAYMENT":
                                QuerySet["table_name"] = "xero_supplier_credit_cash_refund" 
                                supplier_credit_cash_refund.append(QuerySet)
                            elif JsonResponse1[i]["PaymentType"] == "ARCREDITPAYMENT":
                                QuerySet["table_name"] = "xero_credit_memo_cash_refund" 
                                credit_memo_refund_payment.append(QuerySet)
                            elif JsonResponse1[i]["PaymentType"] == "AROVERPAYMENTPAYMENT":
                                QuerySet["table_name"] = "xero_receive_overpayment_cash_refund" 
                                receive_overpayment_cash_refund.append(QuerySet)
                            elif JsonResponse1[i]["PaymentType"] == "APOVERPAYMENTPAYMENT":
                                QuerySet["table_name"] = "xero_spend_overpayment_cash_refund" 
                                spend_overpayment_cash_refund.append(QuerySet)

                if len(bill_payment) > 0:
                    xero_bill_payment.insert_many(bill_payment)
                if len(invoice_payment) > 0:
                    xero_invoice_payment.insert_many(invoice_payment)
                if len(supplier_credit_cash_refund) > 0:
                    xero_supplier_credit_cash_refund.insert_many(supplier_credit_cash_refund)
                if len(receive_overpayment_cash_refund) > 0:
                    xero_receive_overpayment_cash_refund.insert_many(receive_overpayment_cash_refund)
                if len(spend_overpayment_cash_refund)>0:
                    xero_spend_overpayment_cash_refund.insert_many(spend_overpayment_cash_refund)
                if len(credit_memo_refund_payment)>0:
                    xero_credit_memo_cash_refund.insert_many(credit_memo_refund_payment)
                    
                step_name = "Reading data from xero payment"
                write_task_execution_step(task_id, status=1, step=step_name)
             

    except Exception as ex:
        step_name = "Something went wrong"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
        


def get_open_xero_payment(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_bill_payment = dbname["xero_open_bill_payment"]
        xero_invoice_payment = dbname["xero_open_invoice_payment"]
        xero_supplier_credit_cash_refund = dbname["xero_open_supplier_credit_cash_refund"]
        xero_receive_overpayment_cash_refund =dbname['xero_open_receive_overpayment_cash_refund']
        xero_spend_overpayment_cash_refund = dbname['xero_open_spend_overpayment_cash_refund']
        xero_credit_memo_cash_refund =dbname['xero_open_credit_memo_cash_refund']
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
            main_url = f"{base_url}/Payments"
        else:
            y1 = int(start_date[0:4])
            m1 = int(start_date[5:7])
            d1 = int(start_date[8:])
            y2 = int(end_date[0:4])
            m2 = int(end_date[5:7])
            d2 = int(end_date[8:])
            main_url = f"{base_url}/Payments?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})"

        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        time.sleep(1)
        if response1.status_code == 200:
            r1 = response1.json()
            r2 = r1["Payments"]
            if len(r2)>0:
                no_of_records = len(r2)
                no_of_pages = (no_of_records // 100) + 1

                bill_payment = []
                invoice_payment = []
                supplier_credit_cash_refund=[]
                receive_overpayment_cash_refund=[]
                spend_overpayment_cash_refund=[]
                credit_memo_refund_payment=[]
                customer=[]
                supplier=[]
                
                for pages in range(1, no_of_pages + 1):
                    if start_date == "" and end_date == "":
                        main_url = f"{base_url}/Payments?page={pages}"
                    else:
                        y1 = int(result_string[0:4])
                        m1 = int(result_string[5:7])
                        d1 = int(result_string[8:])
                        main_url = f"{base_url}/Payments?where=Date%3C%3DDateTime({y1}%2C{m1}%2C{d1})&page={pages}"

                    print(main_url)
                    response = requests.request("GET", main_url, headers=headers, data=payload)
                    JsonResponse = response.json()
                    JsonResponse1 = JsonResponse["Payments"]

                    for i in range(0, len(JsonResponse1)):
                        if (
                            JsonResponse1[i]["Status"] != "DELETED"
                        ):
                            print(JsonResponse1[i])
                            QuerySet = {}
                            QuerySet["job_id"] = job_id
                            QuerySet["task_id"] = task_id
                            QuerySet["is_pushed"] = 0
                            QuerySet["error"] = None
                            QuerySet["payload"] = None
                            QuerySet["Date"] = JsonResponse1[i]["Date"]
                            QuerySet["BankAmount"] = JsonResponse1[i]["BankAmount"]
                            QuerySet["Amount"] = JsonResponse1[i]["Amount"]

                            if "BatchPayment" in JsonResponse1[i]:
                                QuerySet["BatchPaymentID"] = JsonResponse1[i]["BatchPayment"][
                                    "BatchPaymentID"
                                ]
                                QuerySet["Type"] = JsonResponse1[i]["BatchPayment"]["Type"]
                                QuerySet["TotalAmount"] = JsonResponse1[i]["BatchPayment"][
                                    "TotalAmount"
                                ]
                            else:
                                QuerySet["Type"] = "SinglePayment"

                            if "Reference" in JsonResponse1[i]:
                                QuerySet["Reference"] = JsonResponse1[i]["Reference"]
                            QuerySet["PaymentType"] = JsonResponse1[i]["PaymentType"]
                            QuerySet["Status"] = JsonResponse1[i]["Status"]
                            QuerySet["HasAccount"] = JsonResponse1[i]["HasAccount"]

                            if QuerySet["HasAccount"] == True:
                                QuerySet["AccountCode"] = JsonResponse1[i]["Account"]["AccountID"]

                            if "InvoiceNumber" in JsonResponse1[i]["Invoice"]:
                                QuerySet["InvoiceNumber"] = JsonResponse1[i]["Invoice"][
                                    "InvoiceNumber"
                                ]
                                QuerySet["InvoiceID"] = JsonResponse1[i]["Invoice"]["InvoiceID"]

                            QuerySet["InvoiceType"] = JsonResponse1[i]["Invoice"]["Type"]
                            QuerySet["Contact"] = JsonResponse1[i]["Invoice"]["Contact"]["Name"]
                            QuerySet["ContactID"] = JsonResponse1[i]["Invoice"]["Contact"]["ContactID"]

                            if JsonResponse1[i]["PaymentType"] == "ACCRECPAYMENT":
                                QuerySet["table_name"] = "xero_invoice_payment" 
                                invoice_payment.append(QuerySet)
                                cust={}
                                cust['ContactName'] = JsonResponse1[i]["Invoice"]["Contact"]['Name']
                                cust['ContactID'] = JsonResponse1[i]["Invoice"]["Contact"]['ContactID']
                                cust['Type'] = "AR"
                                cust['job_id'] = job_id

                                if cust not in data1:
                                    customer.append(cust)
                                else:
                                    print("cust1",cust)
                                
                            elif JsonResponse1[i]["PaymentType"] == "ACCPAYPAYMENT":
                                QuerySet["table_name"] = "xero_bill_payment" 
                                bill_payment.append(QuerySet)
                                supp={}
                                supp['ContactName'] = JsonResponse1[i]["Invoice"]["Contact"]['Name']
                                supp['ContactID'] = JsonResponse1[i]["Invoice"]["Contact"]['ContactID']
                                supp['Type'] = "AP"
                                supp['job_id'] = job_id

                                if supp not in data2:
                                    supplier.append(supp)

                            elif JsonResponse1[i]["PaymentType"] == "APCREDITPAYMENT":
                                QuerySet["table_name"] = "xero_supplier_credit_cash_refund" 
                                supplier_credit_cash_refund.append(QuerySet)
                                supp={}
                                supp['ContactName'] = JsonResponse1[i]["Invoice"]["Contact"]['Name']
                                supp['ContactID'] = JsonResponse1[i]["Invoice"]["Contact"]['ContactID']
                                supp['Type'] = "AP"
                                supp['job_id'] = job_id

                                if supp not in data2:
                                    supplier.append(supp)

                            elif JsonResponse1[i]["PaymentType"] == "ARCREDITPAYMENT":
                                QuerySet["table_name"] = "xero_credit_memo_cash_refund" 
                                credit_memo_refund_payment.append(QuerySet)
                                cust={}
                                cust['ContactName'] = JsonResponse1[i]["Invoice"]["Contact"]['Name']
                                cust['ContactID'] = JsonResponse1[i]["Invoice"]["Contact"]['ContactID']
                                cust['Type'] = "AR"
                                cust['job_id'] = job_id

                                if cust not in data1:
                                    customer.append(cust)
                                else:
                                    print("cust2",cust)

                            elif JsonResponse1[i]["PaymentType"] == "AROVERPAYMENTPAYMENT":
                                QuerySet["table_name"] = "xero_receive_overpayment_cash_refund" 
                                receive_overpayment_cash_refund.append(QuerySet)
                                cust={}
                                cust['ContactName'] = JsonResponse1[i]["Invoice"]["Contact"]['Name']
                                cust['ContactID'] = JsonResponse1[i]["Invoice"]["Contact"]['ContactID']
                                cust['Type'] = "AR"
                                cust['job_id'] = job_id

                                if cust not in data1:
                                    customer.append(cust)
                                else:
                                    print("cust3",cust)
                                    
                            elif JsonResponse1[i]["PaymentType"] == "APOVERPAYMENTPAYMENT":
                                QuerySet["table_name"] = "xero_spend_overpayment_cash_refund" 
                                spend_overpayment_cash_refund.append(QuerySet)
                                supp={}
                                supp['ContactName'] = JsonResponse1[i]["Invoice"]["Contact"]['Name']
                                supp['ContactID'] = JsonResponse1[i]["Invoice"]["Contact"]['ContactID']
                                supp['Type'] = "AP"
                                supp['job_id'] = job_id

                                if supp not in data2:
                                    supplier.append(supp)

                if len(bill_payment) > 0:
                    xero_bill_payment.insert_many(bill_payment)
                if len(invoice_payment) > 0:
                    xero_invoice_payment.insert_many(invoice_payment)
                if len(supplier_credit_cash_refund) > 0:
                    xero_supplier_credit_cash_refund.insert_many(supplier_credit_cash_refund)
                if len(receive_overpayment_cash_refund) > 0:
                    xero_receive_overpayment_cash_refund.insert_many(receive_overpayment_cash_refund)
                if len(spend_overpayment_cash_refund)>0:
                    xero_spend_overpayment_cash_refund.insert_many(spend_overpayment_cash_refund)
                if len(credit_memo_refund_payment)>0:
                    xero_credit_memo_cash_refund.insert_many(credit_memo_refund_payment)
                if len(customer)>0:
                    print(len(customer))
                    xero_customer.insert_many(customer)
                if len(supplier)>0:
                    print(len(supplier))
                    xero_supplier.insert_many(supplier)
                
                step_name = "Reading data from xero payment"
                write_task_execution_step(task_id, status=1, step=step_name)
             

    except Exception as ex:
        step_name = "Something went wrong"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
