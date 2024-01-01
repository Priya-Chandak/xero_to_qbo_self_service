import json
from apps.util.log_file import log_config
import logging
import traceback
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


from apps.util.log_file import log_config
import logging

def add_open_xero_invoice_payment(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_invoice_payment")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/payment?minorversion={minorversion}"

        Collection = dbname["xero_open_invoice_payment"]
        QBO_Customer = dbname["QBO_Customer"]
        QBO_Invoice = dbname["QBO_Invoice"]
        QBO_Bill = dbname["QBO_Bill"]
        QBO_COA = dbname["QBO_COA"]
        xero_coa = dbname["xero_coa"]
        xero_arc_coa = dbname["xero_archived_coa"]

        x = Collection.find({"job_id":job_id})
        data1 = []
        for k in x:
            data1.append(k)

        cust = QBO_Customer.find({"job_id":job_id})
        cust1 = []
        for k in cust:
            cust1.append(k)

        QBO_Invoice = QBO_Invoice.find({"job_id":job_id})
        QBO_Invoice1 = []
        for k in QBO_Invoice:
            QBO_Invoice1.append(k)

        QBO_Bill = QBO_Bill.find({"job_id":job_id})
        QBO_Bill1 = []
        for k in QBO_Bill:
            QBO_Bill1.append(k)

        QBO_COA = QBO_COA.find({"job_id":job_id})
        QBO_COA1 = []
        for k in QBO_COA:
            QBO_COA1.append(k)

        xero_coa = xero_coa.find({"job_id":job_id})
        xero_coa1 = []
        for k in xero_coa:
            xero_coa1.append(k)

        xero_arc_coa1 = xero_arc_coa.find({"job_id":job_id})
        for k1 in xero_arc_coa1:
            xero_coa1.append(k1)

        QuerySet1 = data1

        for i in range(0, len(QuerySet1)):
            if QuerySet1[i]["InvoiceType"] == "ACCREC":
                for j1 in range(0, len(QBO_COA1)):
                    for j2 in range(0, len(xero_coa1)):
                        if QuerySet1[i]["AccountCode"] == xero_coa1[j2]["AccountID"]:
                            
                            if (xero_coa1[j2]["Name"].strip().lower()== QBO_COA1[j1]["FullyQualifiedName"].strip().lower()) or (xero_coa1[j2]["Name"].replace(":","-")== QBO_COA1[j1]["FullyQualifiedName"]):
                                if QBO_COA1[j1]["AccountType"] == "Bank":
                                    print(i)
            
                                    _id = QuerySet1[i]['_id']
                                    task_id = QuerySet1[i]['task_id']
                                    QuerySet2 = {"Line": []}
                                    CustomerRef = {}
                                    QuerySet4 = {"LinkedTxn": []}
                                    QuerySet5 = {}
                                    QuerySet6 = {}
                                    QuerySet6["name"] = QBO_COA1[j1][
                                        "FullyQualifiedName"
                                    ]
                                    QuerySet6["value"] = QBO_COA1[j1]["Id"]


                                    payment_date = QuerySet1[i]["Date"]
                                    payment_date11 = int(payment_date[6:16])
                                    payment_date12 = datetime.utcfromtimestamp(payment_date11).strftime(
                                        "%Y-%m-%d"
                                    )

                                    QuerySet2["TxnDate"] = payment_date12
                                    if 'Reference' in QuerySet1[i]:
                                        QuerySet2['PaymentRefNum'] = QuerySet1[i]['Reference'][0:21]
                                    
                                    for c1 in range(0, len(cust1)):
                                        if (
                                            QuerySet1[i]["Contact"].lower()
                                            == cust1[c1]["DisplayName"].lower()
                                        ):
                                            CustomerRef["name"] = cust1[c1]["DisplayName"]
                                            CustomerRef["value"] = cust1[c1]["Id"]
                                            break
                                        elif cust1[c1]["DisplayName"].startswith(
                                            QuerySet1[i]["Contact"]
                                        ) and cust1[c1]["DisplayName"].endswith("- C"):
                                            CustomerRef["name"] = cust1[c1]["DisplayName"]
                                            CustomerRef["value"] = cust1[c1]["Id"]
                                            break
                                        
                                
                                    # a11=dbname["QBO_Customer"].find({"DisplayName": QuerySet1[i]["Contact"],'job_id':job_id})
                                    # a12=dbname["QBO_Customer"].find({"DisplayName": QuerySet1[i]["Contact"]+" - C",'job_id':job_id})
                                    # a13=dbname["QBO_Customer"].find({"DisplayName": QuerySet1[i]["Contact"].upper(),'job_id':job_id})
                                    
                                    # for x3 in a11:
                                    #     CustomerRef["name"] = x3.get("DisplayName")
                                    #     CustomerRef["value"] = x3.get("Id")
                                    #     break
                                    # for x32 in a13:
                                    #     CustomerRef["name"] = x32.get("DisplayName")
                                    #     CustomerRef["value"] = x32.get("Id")
                                    #     break
                                    # for x31 in a12:
                                    #     CustomerRef["name"] = x31.get("DisplayName")
                                    #     CustomerRef["value"] = x31.get("Id")
                                    #     break

                                        
                                    QuerySet2["TotalAmt"] = QuerySet1[i]["BankAmount"]
                                    QuerySet4["Amount"] = QuerySet1[i]["BankAmount"]
                                    
                                    a11=dbname["QBO_Invoice"].find({"DocNumber": QuerySet1[i]["InvoiceNumber"],'job_id':job_id})
                                    for x3 in a11:
                                        QuerySet5["TxnId"] = x3.get("Id")
                                        QuerySet5["TxnType"] = "Invoice"
                                        break
                                    
                                    for k12 in range(0, len(QBO_Invoice1)):
                                        if "DocNumber" in QBO_Invoice1[k12]:
                                            if (
                                                QuerySet1[i]["InvoiceNumber"]
                                                == QBO_Invoice1[k12]["DocNumber"]
                                            ):
                                                QuerySet5["TxnId"] = QBO_Invoice1[k12]["Id"]
                                                QuerySet5["TxnType"] = "Invoice"
                                                
                                            elif QBO_Invoice1[k12]["DocNumber"].startswith(QuerySet1[i]["InvoiceNumber"][0:14]) and QBO_Invoice1[k12]["DocNumber"].endswith(QuerySet1[i]["InvoiceID"][-6:]):
                                                QuerySet5["TxnId"] = QBO_Invoice1[k12]["Id"]
                                                QuerySet5["TxnType"] = "Invoice"

                                    
                                    QuerySet2["DepositToAccountRef"] = QuerySet6

                                    QuerySet2["CustomerRef"] = CustomerRef
                                    QuerySet2["Line"].append(QuerySet4)
                                    QuerySet4["LinkedTxn"].append(QuerySet5)

                                    payload = json.dumps(QuerySet2)
                                    post_data_in_qbo(url, headers, payload,dbname['xero_open_invoice_payment'],_id, job_id,task_id, QuerySet1[i]['InvoiceNumber'])
                    
    except Exception as ex:
        logging.error(ex, exc_info=True)
        


def add_open_xero_bill_payment(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_payment -> add_xero_bill_payment")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/billpayment?minorversion={minorversion}"

        Collection = dbname["xero_open_bill_payment"]
        QBO_Supplier = dbname["QBO_Supplier"]
        QBO_Bill = dbname["QBO_Bill"]
        QBO_COA = dbname["QBO_COA"]
        xero_coa = dbname["xero_coa"]
        xero_arc_coa = dbname["xero_archived_coa"]

        x = Collection.find({"job_id":job_id})
        data1 = []
        for k in x:
            data1.append(k)

        supplier = QBO_Supplier.find({"job_id":job_id})
        supplier1 = []
        for k in supplier:
            supplier1.append(k)

        QBO_Bill = QBO_Bill.find({"job_id":job_id})
        QBO_Bill1 = []
        for k in QBO_Bill:
            QBO_Bill1.append(k)

        QBO_COA = QBO_COA.find({"job_id":job_id})
        QBO_COA1 = []
        for k in QBO_COA:
            QBO_COA1.append(k)

        xero_coa = xero_coa.find({"job_id":job_id})
        xero_coa1 = []
        for k in xero_coa:
            xero_coa1.append(k)

        xero_arc_coa = xero_arc_coa.find({"job_id":job_id})
        # xero_arc_coa1 = []
        for k in xero_arc_coa:
            xero_coa1.append(k)

        QuerySet1 = data1

        for i in range(0, len(QuerySet1)):
            if QuerySet1[i]["InvoiceType"] == "ACCPAY":
                _id = QuerySet1[i]['_id']
                task_id = QuerySet1[i]['task_id']
                
                for j1 in range(0, len(QBO_COA1)):
                    for j2 in range(0, len(xero_coa1)):
                        if QuerySet1[i]["AccountCode"] == xero_coa1[j2]["AccountID"]:
                            if (xero_coa1[j2]["Name"].strip().lower()== QBO_COA1[j1]["FullyQualifiedName"].strip().lower()) or (xero_coa1[j2]["Name"].replace(":","-")== QBO_COA1[j1]["FullyQualifiedName"]):
                            
                                if QBO_COA1[j1]["AccountType"] == "Bank":

                                    print("bank",i)
                                    QuerySet2 = {"Line": []}
                                    VendorRef = {}
                                    QuerySet4 = {"LinkedTxn": []}
                                    QuerySet5 = {}
                                    BankAccountRef = {}
                                    CheckPayment = {}

                                    BankAccountRef["name"] = QBO_COA1[j1][
                                        "FullyQualifiedName"
                                    ]
                                    BankAccountRef["value"] = QBO_COA1[j1]["Id"]

                                    # for s1 in range(0, len(supplier1)):
                                    #     if (
                                    #         QuerySet1[i]["Contact"]
                                    #         == supplier1[s1]["DisplayName"]
                                    #     ):
                                    #         VendorRef["name"] = supplier1[s1][
                                    #             "DisplayName"
                                    #         ]
                                    #         VendorRef["value"] = supplier1[s1]["Id"]
                                    #         break
                                    #     elif supplier1[s1]["DisplayName"].startswith(
                                    #         QuerySet1[i]["Contact"]
                                    #     ) and supplier1[s1]["DisplayName"].endswith(
                                    #         "- S"
                                    #     ):
                                    #         VendorRef["name"] = supplier1[s1][
                                    #             "DisplayName"
                                    #         ]
                                    #         VendorRef["value"] = supplier1[s1]["Id"]
                                    #         continue
                                        
                                    QuerySet2["TotalAmt"] = QuerySet1[i]["BankAmount"]
                                    QuerySet4["Amount"] = QuerySet1[i]["BankAmount"]
                                    payment_date = QuerySet1[i]["Date"]
                                    payment_date11 = int(payment_date[6:16])
                                    payment_date12 = datetime.utcfromtimestamp(
                                        payment_date11
                                    ).strftime("%Y-%m-%d")

                                    QuerySet2["TxnDate"] = payment_date12
                                    print(QuerySet1[i]['InvoiceNumber'])
                                    for k12 in range(0, len(QBO_Bill1)):
                                        QuerySet5["TxnType"] = "Bill"
                                            
                                        if "DocNumber" in QBO_Bill1[k12]:
                                            if QuerySet1[i]['InvoiceNumber'][0:14]+"-"+QuerySet1[i]['InvoiceID'][-6:]== QBO_Bill1[k12]["DocNumber"]:
                                                QuerySet5["TxnId"] = QBO_Bill1[k12][
                                                    "Id"
                                                ]
                                                VendorRef = QBO_Bill1[k12]['VendorRef']
                                                break
                                            elif (
                                                QuerySet1[i]["InvoiceNumber"]
                                                == QBO_Bill1[k12]["DocNumber"]
                                            ):
                                                QuerySet5["TxnId"] = QBO_Bill1[k12][
                                                    "Id"
                                                ]
                                                VendorRef = QBO_Bill1[k12]['VendorRef']
                                                break

                                            elif QuerySet1[i]["InvoiceNumber"][0:21]==QBO_Bill1[k12]["DocNumber"][0:21]:
                                                QuerySet5["TxnId"] = QBO_Bill1[k12][
                                                    "Id"
                                                ]
                                                print(QuerySet5["TxnId"])
                                                VendorRef = QBO_Bill1[k12]['VendorRef']
                                                continue
                                                

                                    QuerySet2["VendorRef"] = VendorRef
                                    QuerySet2["PayType"] = "Check"

                                    CheckPayment["BankAccountRef"] = BankAccountRef
                                    QuerySet2["CheckPayment"] = CheckPayment

                                    QuerySet4["LinkedTxn"].append(QuerySet5)
                                    QuerySet2["Line"].append(QuerySet4)

                                    payload = json.dumps(QuerySet2)
                                   
                                    post_data_in_qbo(url, headers, payload,dbname['xero_open_bill_payment'],_id, job_id,task_id, QuerySet1[i]['InvoiceNumber'])
                            
    except Exception as ex:
        logging.error(ex, exc_info=True)
        

def add_xero_open_receive_overpayment_cash_refund_as_journal(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_open_receive_overpayment_cash_refund"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        supplier1 = []
        for k in supplier:
            supplier1.append(k)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p3 in QBO_Customer:
            QBO_customer.append(p3)

        QBO_Tax = dbname["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)

        Xero_COA = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        xero_archived_coa1 = dbname["xero_archived_coa"].find({"job_id":job_id})
        for p7 in xero_archived_coa1:
            xero_coa.append(p7)

        QuerySet1 = journal

        for i in range(0, len(QuerySet1)):
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']
            for j1 in range(0, len(QBO_coa)):
                for j2 in range(0, len(xero_coa)):
                    if QuerySet1[i]["AccountCode"] == xero_coa[j2]["AccountID"]:
                        if (xero_coa[j2]["Name"].strip().lower()== QBO_coa[j1]["FullyQualifiedName"].strip().lower()) or (xero_coa[j2]["Name"].replace(":","-")== QBO_coa[j1]["FullyQualifiedName"]):
                        
                            payment_date = QuerySet1[i]["Date"]
                            payment_date11 = int(payment_date[6:16])
                            journal_date1 = datetime.utcfromtimestamp(
                                payment_date11
                            ).strftime("%Y-%m-%d")

                            QuerySet2 = {"Line": []}
                            TxnTaxDetail = {}
                            QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                            QuerySet2["DocNumber"] = (
                                "OpenRMOPCR-" + QuerySet1[i]["AccountCode"][-5:]
                            )
                            # QuerySet2['PrivateNote'] = "InvoiceID:- "+QuerySet1[i]['InvoiceID']+" & "+"ReceiveMoneyOverPaymentNo:- "+QuerySet1[i]['InvoiceNumber']
                            QuerySet2["TxnDate"] = str(journal_date1)[0:10]

                            QuerySet3 = {}
                            QuerySet31 = {}
                            QuerySet32 = {}

                            QuerySet4 = {}
                            QuerySet41 = {}
                            QuerySet42 = {}
                            entity = {}
                            EntityRef = {}

                            QuerySet3["Amount"] = QuerySet1[i]["Amount"]
                            QuerySet3["DetailType"] = "JournalEntryLineDetail"
                            QuerySet3["JournalEntryLineDetail"] = QuerySet31
                            QuerySet31["PostingType"] = "Credit"
                            QuerySet31["AccountRef"] = QuerySet32

                            QuerySet32["name"] = QBO_coa[j1]["FullyQualifiedName"]
                            QuerySet32["value"] = QBO_coa[j1]["Id"]

                            QuerySet4["Amount"] = QuerySet1[i]["Amount"]
                            QuerySet4["DetailType"] = "JournalEntryLineDetail"
                            QuerySet4["JournalEntryLineDetail"] = QuerySet41
                            QuerySet41["PostingType"] = "Debit"
                            QuerySet41["Entity"] = entity
                            entity["EntityRef"] = EntityRef

                            for c1 in range(0, len(QBO_customer)):
                                entity["Type"] = "Customer"
                                if (
                                    QuerySet1[i]["Contact"].lower()
                                    == QBO_customer[c1]["DisplayName"].lower()
                                ):
                                    EntityRef["name"] = QBO_customer[c1]["DisplayName"]
                                    EntityRef["value"] = QBO_customer[c1]["Id"]
                                    break
                                elif QBO_customer[c1]["DisplayName"].startswith(
                                    QuerySet1[i]["Contact"]
                                ) and QBO_customer[c1]["DisplayName"].endswith("- C"):
                                    EntityRef["name"] = QBO_customer[c1]["DisplayName"]
                                    EntityRef["value"] = QBO_customer[c1]["Id"]
                                    continue
                            
                            QuerySet41["AccountRef"] = QuerySet42

                            for j1 in range(0, len(QBO_coa)):
                                if (
                                    QBO_coa[j1]["AccountType"]
                                    == "Accounts Receivable"
                                ):
                                    QuerySet42["value"] = QBO_coa[j1]["Id"]

                            QuerySet2["Line"].append(QuerySet3)
                            QuerySet2["Line"].append(QuerySet4)

                            payload = json.dumps(QuerySet2)
                            print(payload)
                            print("-")

                            post_data_in_qbo(url, headers, payload,dbname['xero_open_receive_overpayment_cash_refund'],_id, job_id,task_id, QuerySet1[i]['AccountCode'])
            
    except Exception as ex:
        logging.error(ex, exc_info=True)
        


def add_xero_open_spend_overpayment_cash_refund_as_journal(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_open_spend_overpayment_cash_refund"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        supplier1 = []
        for k in supplier:
            supplier1.append(k)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        customer1 = []
        for p3 in QBO_Customer:
            customer1.append(p3)

        QBO_Tax = dbname["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)

        Xero_COA = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        xero_archived_coa1 = dbname["xero_archived_coa"].find({"job_id":job_id})
        for p7 in xero_archived_coa1:
            xero_coa.append(p7)

        QuerySet1 = journal

        for i in range(0, len(QuerySet1)):
            print(i)
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']
            for j1 in range(0, len(QBO_coa)):
                for j2 in range(0, len(xero_coa)):
                    if QuerySet1[i]["AccountCode"] == xero_coa[j2]["AccountID"]:
                        if (xero_coa[j2]["Name"].strip().lower()== QBO_coa[j1]["FullyQualifiedName"].strip().lower()) or (xero_coa[j2]["Name"].replace(":","-")== QBO_coa[j1]["FullyQualifiedName"]):
                            print(QBO_coa[j1]["FullyQualifiedName"])
                            payment_date = QuerySet1[i]["Date"]
                            payment_date11 = int(payment_date[6:16])
                            journal_date1 = datetime.utcfromtimestamp(
                                payment_date11
                            ).strftime("%Y-%m-%d")

                            QuerySet2 = {"Line": []}
                            TxnTaxDetail = {}
                            QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                            QuerySet2["DocNumber"] = (
                                "OpenSMOPCR-" + QuerySet1[i]["AccountCode"][-5:]
                            )
                            # QuerySet2['PrivateNote'] = "InvoiceID:- "+QuerySet1[i]['InvoiceID']+" & "+"SpendMoneyOverPaymentNo:- "+QuerySet1[i]['InvoiceNumber']
                            QuerySet2["TxnDate"] = str(journal_date1)[0:10]

                            QuerySet3 = {}
                            QuerySet31 = {}
                            QuerySet32 = {}

                            QuerySet4 = {}
                            QuerySet41 = {}
                            QuerySet42 = {}
                            entity = {}
                            EntityRef = {}

                            QuerySet3["Amount"] = QuerySet1[i]["Amount"]
                            QuerySet3["DetailType"] = "JournalEntryLineDetail"
                            QuerySet3["JournalEntryLineDetail"] = QuerySet31
                            QuerySet31["PostingType"] = "Debit"
                            QuerySet31["AccountRef"] = QuerySet32

                            QuerySet32["name"] = QBO_coa[j1]["FullyQualifiedName"]
                            QuerySet32["value"] = QBO_coa[j1]["Id"]

                            QuerySet4["Amount"] = QuerySet1[i]["Amount"]
                            QuerySet4["DetailType"] = "JournalEntryLineDetail"
                            QuerySet4["JournalEntryLineDetail"] = QuerySet41
                            QuerySet41["PostingType"] = "Credit"
                            QuerySet41["Entity"] = entity
                            entity["EntityRef"] = EntityRef

                            for j in range(0, len(supplier1)):
                                entity["Type"] = "Vendor"
                                if (
                                    QuerySet1[i]["Contact"].lower()
                                    == supplier1[j]["DisplayName"].lower()
                                ):
                                    EntityRef["name"] = supplier1[j]["DisplayName"]
                                    EntityRef["value"] = supplier1[j]["Id"]
                                    break
                                elif supplier1[j]["DisplayName"].startswith(
                                    QuerySet1[i]["Contact"]
                                ) and supplier1[j]["DisplayName"].endswith("- S"):
                                    EntityRef["name"] = supplier1[j]["DisplayName"]
                                    EntityRef["value"] = supplier1[j]["Id"]
                                    continue
                            
                            QuerySet41["AccountRef"] = QuerySet42

                            for j3 in range(0, len(QBO_coa)):
                                if (
                                    QBO_coa[j3]["AccountType"]
                                    == "Accounts Payable"
                                ):
                                    QuerySet42["value"] = QBO_coa[j3]["Id"]

                            QuerySet2["Line"].append(QuerySet3)
                            QuerySet2["Line"].append(QuerySet4)

                            payload = json.dumps(QuerySet2)
                            print(payload)
                            print("-")

                            post_data_in_qbo(url, headers, payload,dbname['xero_open_spend_overpayment_cash_refund'],_id, job_id,task_id, QuerySet1[i]['AccountCode'])
                            
    except Exception as ex:
        logging.error(ex, exc_info=True)
    

def add_xero_creditnote_payment_refund_as_journal(job_id,task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_creditnote_payment_refund_as_journal")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_credit_memo_cash_refund"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        supplier1 = []
        for k in supplier:
            supplier1.append(k)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p3 in QBO_Customer:
            QBO_customer.append(p3)

        QBO_Tax = dbname["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)

        Xero_COA = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        xero_arc_coa = dbname["xero_archived_coa"].find({"job_id":job_id})
        for p7 in xero_arc_coa:
            xero_coa.append(p7)

        QuerySet1 = journal

        for i in range(0, len(QuerySet1)):
            print(i)
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']
            for j1 in range(0, len(QBO_coa)):
                for j2 in range(0, len(xero_coa)):
                    if QuerySet1[i]["AccountCode"] == xero_coa[j2]["AccountID"]:
                        if (xero_coa[j2]["Name"].strip().lower()== QBO_coa[j1]["FullyQualifiedName"].strip().lower()) or (xero_coa[j2]["Name"].replace(":","-")== QBO_coa[j1]["FullyQualifiedName"]):
                            if QBO_coa[j1]["AccountType"] == "Bank":
                                payment_date = QuerySet1[i]["Date"]
                                payment_date11 = int(payment_date[6:16])
                                journal_date1 = datetime.utcfromtimestamp(
                                    payment_date11
                                ).strftime("%Y-%m-%d")

                                QuerySet2 = {"Line": []}
                                TxnTaxDetail = {}
                                QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                                QuerySet2["DocNumber"] = (
                                    "CNP-" + QuerySet1[i]["InvoiceID"][-10:]
                                )
                                
                                QuerySet2["TxnDate"] = str(journal_date1)[0:10]
                                QuerySet2['PrivateNote'] = "InvoiceID:- "+QuerySet1[i]['InvoiceID']+" & "+"InvoiceNo:- "+QuerySet1[i]['InvoiceNumber']

                                QuerySet3 = {}
                                QuerySet31 = {}
                                QuerySet32 = {}

                                QuerySet4 = {}
                                QuerySet41 = {}
                                QuerySet42 = {}
                                entity = {}
                                EntityRef = {}

                                QuerySet3["Amount"] = QuerySet1[i]["Amount"]
                                QuerySet3["DetailType"] = "JournalEntryLineDetail"
                                QuerySet3["JournalEntryLineDetail"] = QuerySet31
                                QuerySet31["PostingType"] = "Credit"
                                QuerySet31["AccountRef"] = QuerySet32

                                QuerySet32["name"] = QBO_coa[j1]["FullyQualifiedName"]
                                QuerySet32["value"] = QBO_coa[j1]["Id"]

                                QuerySet4["Amount"] = QuerySet1[i]["Amount"]
                                QuerySet4["DetailType"] = "JournalEntryLineDetail"
                                QuerySet4["JournalEntryLineDetail"] = QuerySet41
                                QuerySet41["PostingType"] = "Debit"
                                QuerySet41["Entity"] = entity
                                entity["EntityRef"] = EntityRef

                                for c1 in range(0, len(QBO_customer)):
                                    entity["Type"] = "Customer"
                                    if (
                                        QuerySet1[i]["Contact"].lower()
                                        == QBO_customer[c1]["DisplayName"].lower()
                                    ):
                                        EntityRef["name"] = QBO_customer[c1]["DisplayName"]
                                        EntityRef["value"] = QBO_customer[c1]["Id"]
                                    elif QBO_customer[c1]["DisplayName"].startswith(
                                        QuerySet1[i]["Contact"]
                                    ) and QBO_customer[c1]["DisplayName"].endswith("- C"):
                                        EntityRef["name"] = QBO_customer[c1]["DisplayName"]
                                        EntityRef["value"] = QBO_customer[c1]["Id"]
                                    
                                QuerySet41["AccountRef"] = QuerySet42

                                for j11 in range(0, len(QBO_coa)):
                                    if (
                                        QBO_coa[j11]["AccountType"]
                                        == "Accounts Receivable"
                                    ):
                                        QuerySet42["name"] = QBO_coa[j11][
                                            "FullyQualifiedName"
                                        ]
                                        QuerySet42["value"] = QBO_coa[j11]["Id"]

                                QuerySet2["Line"].append(QuerySet3)
                                QuerySet2["Line"].append(QuerySet4)

                                payload = json.dumps(QuerySet2)
                                

                                post_data_in_qbo(url, headers, payload,dbname['xero_credit_memo_cash_refund'],_id, job_id,task_id, QuerySet1[i]['InvoiceNumber'])
                
    except Exception as ex:
        logging.error(ex, exc_info=True)
       
