import json
from apps.util.log_file import log_config
import logging
import traceback
import time
import datetime
from datetime import *
import requests
from apps.home.data_util import add_job_status,get_job_details

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
import re
from apps.util.log_file import log_config
import logging

def add_qbo_ar_journal(job_id,task_id):
    log_config1=log_config(job_id)
    
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_AR_journal")
        start_date, end_date = get_job_details(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_AR"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QuerySet1 = journal
        
        QuerySet2 = {"Line": []}
        retained_earning_amount=0
        retained_earning={}
        JournalEntryLineDetail1={}
        RE={}
            
        for i in range(0, len(QuerySet1)):
            if 'diff' in QuerySet1[i] and QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0:
                
                date_object = datetime.strptime(start_date, '%Y-%m-%d')
                one_day_before = date_object - timedelta(days=1)
                journal_date1 = one_day_before.strftime('%Y-%m-%d')
                
                AR = {}
                # RE = {}
                
                QuerySet3={}
                JournalEntryLineDetail={}
                entity={}
                EntityRef={}
                TxnTaxDetail = {}
                QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                QuerySet2["DocNumber"] = "AR-Adjustment"
                QuerySet2["TxnDate"] = journal_date1
               
                for j11 in range(0, len(QBO_coa)):
                    if (
                        QBO_coa[j11]["AccountType"]
                        == "Accounts Receivable"
                    ):
                        AR["name"] = QBO_coa[j11][
                            "FullyQualifiedName"
                        ]
                        AR["value"] = QBO_coa[j11]["Id"]

                    if (
                        QBO_coa[j11]["AccountType"] == "Equity" and QBO_coa[j11]["Name"] == "Retained Earnings"
                    ):
                        RE['name'] = QBO_coa[j11]["Name"]
                        RE['value'] = QBO_coa[j11]["Id"]

                
                if QuerySet1[i]['posting_type'] == "Credit":
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AR
                    entity['Type'] = 'Customer'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                elif QuerySet1[i]['posting_type'] == "Debit":
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AR
                    entity['Type'] = 'Customer'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                retained_earning_amount = retained_earning_amount + float(QuerySet1[i]['diff_amount'])
               
                QuerySet2['Line'].append(QuerySet3)
        print(retained_earning_amount)

        if retained_earning_amount<0:
            JournalEntryLineDetail1["PostingType"] = "Debit"
        else:
            JournalEntryLineDetail1["PostingType"] = "Credit"

        retained_earning["DetailType"] = "JournalEntryLineDetail"
        retained_earning['JournalEntryLineDetail'] = JournalEntryLineDetail1
        retained_earning["Amount"] = abs(retained_earning_amount)
        JournalEntryLineDetail1['AccountRef'] = RE

        QuerySet2['Line'].append(retained_earning)

        payload = json.dumps(QuerySet2)
        print(payload,"payload--------------------------------")

        url = f"{base_url}/journalentry?minorversion=14"
        print(url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        print(response.text)
            
    except Exception as ex:
        logging.error(ex, exc_info=True)

def add_qbo_ar_journal_till_end_date(job_id,task_id):
    log_config1=log_config(job_id)
    
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_AR_journal")
        start_date, end_date = get_job_details(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_AR_till_end_date"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QuerySet1 = journal
        
        QuerySet2 = {"Line": []}
        retained_earning_amount=0
        retained_earning={}
        JournalEntryLineDetail1={}
        RE={}
        print("add_qbo_ar_journal_till_end_date",len(QuerySet1))
        for i in range(0, len(QuerySet1)):
            if 'diff' in QuerySet1[i] and QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0:
                print("if")
                date_object = datetime.strptime(end_date, '%Y-%m-%d')
                journal_date1 = date_object.strftime('%Y-%m-%d')
                
                AR = {}
                RE = {}
                
                QuerySet3={}
                JournalEntryLineDetail={}
                entity={}
                EntityRef={}
                TxnTaxDetail = {}
                QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                QuerySet2["DocNumber"] = "AR-Adjustment-Current"
                QuerySet2["TxnDate"] = journal_date1
               
                for j11 in range(0, len(QBO_coa)):
                    if (
                        QBO_coa[j11]["AccountType"]
                        == "Accounts Receivable"
                    ):
                        AR["name"] = QBO_coa[j11][
                            "FullyQualifiedName"
                        ]
                        AR["value"] = QBO_coa[j11]["Id"]

                    if (
                        QBO_coa[j11]["AccountType"] == "Equity" and QBO_coa[j11]["Name"] == "Retained Earnings"
                    ):
                        RE['name'] = QBO_coa[j11]["Name"]
                        RE['value'] = QBO_coa[j11]["Id"]

                
                if QuerySet1[i]['posting_type'] == "Credit":
                    print("Credit")
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AR
                    entity['Type'] = 'Customer'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                elif QuerySet1[i]['posting_type'] == "Debit":
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AR
                    entity['Type'] = 'Customer'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                retained_earning_amount = retained_earning_amount + float(QuerySet1[i]['diff_amount'])
               
                QuerySet2['Line'].append(QuerySet3)
        
        print(retained_earning_amount)

        if retained_earning_amount<0:
            JournalEntryLineDetail1["PostingType"] = "Debit"
        else:
            JournalEntryLineDetail1["PostingType"] = "Credit"

        retained_earning["DetailType"] = "JournalEntryLineDetail"
        retained_earning['JournalEntryLineDetail'] = JournalEntryLineDetail1
        retained_earning["Amount"] = abs(retained_earning_amount)
        JournalEntryLineDetail1['AccountRef'] = RE

        QuerySet2['Line'].append(retained_earning)

        payload = json.dumps(QuerySet2)
        print(payload,"payload--------------------------------")

        url = f"{base_url}/journalentry?minorversion=14"
        print(url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        print(response.text)
            
    except Exception as ex:
        logging.error(ex, exc_info=True)

def add_qbo_ap_journal(job_id,task_id):
    log_config1=log_config(job_id)
    
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_AP_journal")
        start_date, end_date = get_job_details(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_AP"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QuerySet1 = journal
        
        QuerySet2 = {"Line": []}
        retained_earning_amount=0
        retained_earning={}
        JournalEntryLineDetail1={}
        RE = {}
            
        for i in range(0, len(QuerySet1)):
                  
            if 'diff' in QuerySet1[i] and QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0:
                
                date_object = datetime.strptime(start_date, '%Y-%m-%d')
                one_day_before = date_object - timedelta(days=1)
                journal_date1 = one_day_before.strftime('%Y-%m-%d')
                
                AP = {}
                
                
                QuerySet3={}
                JournalEntryLineDetail={}
                entity={}
                EntityRef={}
                TxnTaxDetail = {}
                QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                QuerySet2["DocNumber"] = "AP-Adjustment"
                QuerySet2["TxnDate"] = journal_date1
               
                for j11 in range(0, len(QBO_coa)):
                    if (
                        QBO_coa[j11]["AccountType"]
                        == "Accounts Payable"
                    ):
                        AP["name"] = QBO_coa[j11][
                            "FullyQualifiedName"
                        ]
                        AP["value"] = QBO_coa[j11]["Id"]

                    if (
                        QBO_coa[j11]["AccountType"] == "Equity" and QBO_coa[j11]["Name"] == "Retained Earnings"
                    ):
                        RE['name'] = QBO_coa[j11]["Name"]
                        RE['value'] = QBO_coa[j11]["Id"]

                
                if QuerySet1[i]['posting_type'] == "Credit":
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AP
                    entity['Type'] = 'Vendor'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                elif QuerySet1[i]['posting_type'] == "Debit":
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AP
                    entity['Type'] = 'Vendor'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                retained_earning_amount = retained_earning_amount + float(QuerySet1[i]['diff_amount'])
               
                QuerySet2['Line'].append(QuerySet3)
       
        if retained_earning_amount>0:
            JournalEntryLineDetail1["PostingType"] = "Debit"
        else:
            JournalEntryLineDetail1["PostingType"] = "Credit"

        retained_earning["DetailType"] = "JournalEntryLineDetail"
        retained_earning['JournalEntryLineDetail'] = JournalEntryLineDetail1
        retained_earning["Amount"] = abs(retained_earning_amount)
        JournalEntryLineDetail1['AccountRef'] = RE

        QuerySet2['Line'].append(retained_earning)

        payload = json.dumps(QuerySet2)
        print(payload,"payload--------------------------------")

        url = f"{base_url}/journalentry?minorversion=14"
        print(url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        print(response.text)
            
    except Exception as ex:
        logging.error(ex, exc_info=True)

def add_qbo_ap_journal_till_end_date(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_AP_journal")
        start_date, end_date = get_job_details(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_AP_till_end_date"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QuerySet1 = journal
        
        QuerySet2 = {"Line": []}
        retained_earning_amount=0
        retained_earning={}
        JournalEntryLineDetail1={}
        RE = {}
            
        for i in range(0, len(QuerySet1)):
                  
            if 'diff' in QuerySet1[i] and QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0:
                
                date_object = datetime.strptime(end_date, '%Y-%m-%d')
                journal_date1 = date_object.strftime('%Y-%m-%d')
                
                AP = {}
                
                
                QuerySet3={}
                JournalEntryLineDetail={}
                entity={}
                EntityRef={}
                TxnTaxDetail = {}
                QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                QuerySet2["DocNumber"] = "AP-Adjustment-Current"
                QuerySet2["TxnDate"] = journal_date1
               
                for j11 in range(0, len(QBO_coa)):
                    if (
                        QBO_coa[j11]["AccountType"]
                        == "Accounts Payable"
                    ):
                        AP["name"] = QBO_coa[j11][
                            "FullyQualifiedName"
                        ]
                        AP["value"] = QBO_coa[j11]["Id"]

                    if (
                        QBO_coa[j11]["AccountType"] == "Equity" and QBO_coa[j11]["Name"] == "Retained Earnings"
                    ):
                        RE['name'] = QBO_coa[j11]["Name"]
                        RE['value'] = QBO_coa[j11]["Id"]

                
                if QuerySet1[i]['posting_type'] == "Credit":
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AP
                    entity['Type'] = 'Vendor'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                elif QuerySet1[i]['posting_type'] == "Debit":
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["diff_amount"]))
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = AP
                    entity['Type'] = 'Vendor'
                    entity['EntityRef'] = EntityRef
                    EntityRef['name'] = QuerySet1[i]['ContactName']
                    EntityRef['value'] = QuerySet1[i]['QBO_ContactID']

                retained_earning_amount = retained_earning_amount + float(QuerySet1[i]['diff_amount'])
               
                QuerySet2['Line'].append(QuerySet3)
       
        if retained_earning_amount>0:
            JournalEntryLineDetail1["PostingType"] = "Debit"
        else:
            JournalEntryLineDetail1["PostingType"] = "Credit"

        retained_earning["DetailType"] = "JournalEntryLineDetail"
        retained_earning['JournalEntryLineDetail'] = JournalEntryLineDetail1
        retained_earning["Amount"] = abs(retained_earning_amount)
        JournalEntryLineDetail1['AccountRef'] = RE

        QuerySet2['Line'].append(retained_earning)

        payload = json.dumps(QuerySet2)
        print(payload,"payload--------------------------------")

        url = f"{base_url}/journalentry?minorversion=14"
        print(url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        print(response.text)
            
    except Exception as ex:
        logging.error(ex, exc_info=True)

def add_qbo_reverse_trial_balance(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_qbo_reverse_trial_balance")
        start_date, end_date = get_job_details(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["QBO_Trial_Balance"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p2 in QBO_Customer:
            QBO_customer.append(p2)
        
        QBO_Supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        QBO_supplier = []
        for p2 in QBO_Supplier:
            QBO_supplier.append(p2)

        QuerySet1 = journal
        
        QuerySet2 = {"Line": []}

        for i in range(0, len(QuerySet1)):
            print(i)
            date_object = datetime.strptime(start_date, '%Y-%m-%d')
            one_day_before = date_object - timedelta(days=1)
            journal_date1 = one_day_before.strftime('%Y-%m-%d')
            
            QuerySet3={}
            JournalEntryLineDetail={}
            account={}
            QuerySet2["DocNumber"] = "ReverseTrialBalance"
            QuerySet3["DetailType"] = "JournalEntryLineDetail"
            # QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
            QuerySet2["TxnDate"] = journal_date1
            account['name'] = QuerySet1[i]['bankname']
            account['value'] = QuerySet1[i]['bankid']
            JournalEntryLineDetail['AccountRef'] = account
            if float(QuerySet1[i]['debit'])==0:
                JournalEntryLineDetail["PostingType"] = "Debit"
                QuerySet3["Amount"] = abs(float(QuerySet1[i]["credit"]))
            else:
                JournalEntryLineDetail["PostingType"] = "Credit"
                QuerySet3["Amount"] = abs(float(QuerySet1[i]["debit"]))
                
            QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
            
            for j11 in range(0, len(QBO_coa)):
                print(QuerySet1[i]['bankname'] == QBO_coa[j11]["Name"],QuerySet1[i]['bankname'],QBO_coa[j11]["Name"])
                if (QuerySet1[i]['bankname'] == QBO_coa[j11]["Name"]) and (QBO_coa[j11]["AccountType"] == 'Accounts Payable'):
                    print("AP match")
                    entity={}
                    EntityRef={}
        
                    entity['Type'] = 'Vendor'
                    entity['EntityRef'] = EntityRef
                    for s1 in range(0,len(QBO_supplier)):
                        if QBO_supplier[s1]['DisplayName'] == 'Temp - S':
                            EntityRef['name'] = QBO_supplier[s1]['DisplayName']
                            EntityRef['value'] = QBO_supplier[s1]['Id']
                
                    JournalEntryLineDetail["Entity"] = entity
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail

                elif (QuerySet1[i]['bankname'] == QBO_coa[j11]["Name"]) and (QBO_coa[j11]["AccountType"] == 'Accounts Receivable'):
                    entity={}
                    EntityRef={}
        
                    entity['Type'] = 'Customer'
                    entity['EntityRef'] = EntityRef
                    for c1 in range(0,len(QBO_customer)):
                        if QBO_customer[c1]['DisplayName'] == 'Temp - C':
                            EntityRef['name'] = QBO_customer[c1]['DisplayName']
                            EntityRef['value'] = QBO_customer[c1]['Id']
                
                    JournalEntryLineDetail["Entity"] = entity
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail

            QuerySet2['Line'].append(QuerySet3)
        
        payload = json.dumps(QuerySet2)
        print(payload,"payload--------------------------------")

        url = f"{base_url}/journalentry?minorversion=14"
        print(url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        print(response.text)
                
    except Exception as ex:
        logging.error(ex, exc_info=True)


def add_xero_open_trial_balance(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_qbo_reverse_trial_balance")
        start_date, end_date = get_job_details(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_trial_balance"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        xero_coa1 = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p2 in xero_coa1:
            xero_coa.append(p2)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p2 in QBO_Customer:
            QBO_customer.append(p2)
        
        QBO_Supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        QBO_supplier = []
        for p2 in QBO_Supplier:
            QBO_supplier.append(p2)

        QuerySet1 = journal
        
        QuerySet2 = {"Line": []}

        for i in range(0, len(QuerySet1)):
            date_object = datetime. strptime(start_date, '%Y-%m-%d')
            one_day_before = date_object - timedelta(days=1)
            journal_date1 = one_day_before.strftime('%Y-%m-%d')
            
            QuerySet3={}
            JournalEntryLineDetail={}
            entity={}
            EntityRef={}
            QuerySet2["DocNumber"] = "XeroTrialBalance-Open"
            QuerySet3["DetailType"] = "JournalEntryLineDetail"
            QuerySet2["TxnDate"] = journal_date1
            if float(QuerySet1[i]['debit'])==0:
                JournalEntryLineDetail["PostingType"] = "Debit"
                QuerySet3["Amount"] = abs(float(QuerySet1[i]["credit"]))
            else:
                JournalEntryLineDetail["PostingType"] = "Credit"
                QuerySet3["Amount"] = abs(float(QuerySet1[i]["debit"]))
                

            input_string = QuerySet1[i]['bankname']

            pattern = r"\(([^)]*)\)$"

            match = re.search(pattern, input_string)
            
            if match:
                extracted_text = match.group(1)
                for j12 in range(0,len(xero_coa)):
                    
                    account={}
                    entity={}
                    EntityRef={}
                    for j11 in range(0, len(QBO_coa)):
                
                        if xero_coa[j12]['Code'] == str(extracted_text):
                            if (xero_coa[j12]['SystemAccount']=='DEBTORS') and (QBO_coa[j11]["AccountSubType"] == 'AccountsReceivable'):
                                print("AR---------------------------------------",xero_coa[j12]['Name'],xero_coa[j12]['SystemAccount'],QBO_coa[j11]["FullyQualifiedName"])
                                print(QBO_coa[j11]["FullyQualifiedName"])
                                account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                                account['value'] = QBO_coa[j11]["Id"]
                                JournalEntryLineDetail['AccountRef'] = account
                                QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                                for c12 in range(0,len(QBO_customer)):
                                    if QBO_customer[c12]['FullyQualifiedName'] == 'Temp - C':
                                        entity['Type'] = 'Customer'
                                        EntityRef['value'] = QBO_customer[c12]['Id']
                                        entity['EntityRef'] = EntityRef
                                        
                                JournalEntryLineDetail['Entity'] = entity
                                print(QuerySet3,"AR----------")
                                break
                            
                            elif (xero_coa[j12]['SystemAccount']=='CREDITORS') and (QBO_coa[j11]["AccountSubType"] == 'AccountsPayable'):
                                print(QBO_coa[j11]["FullyQualifiedName"])
                                account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                                account['value'] = QBO_coa[j11]["Id"]
                                JournalEntryLineDetail['AccountRef'] = account
                                QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                                for s12 in range(0,len(QBO_supplier)):
                                    if QBO_supplier[s12]['DisplayName'] == 'Temp - S':
                                        entity['Type'] = 'Vendor'
                                        EntityRef['value'] = QBO_supplier[s12]['Id']
                                        entity['EntityRef'] = EntityRef
                                        
                                JournalEntryLineDetail['Entity'] = entity
                                break

                            elif xero_coa[j12]['Name'] == QBO_coa[j11]["Name"]:
                                account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                                account['value'] = QBO_coa[j11]["Id"]
                                JournalEntryLineDetail['AccountRef'] = account
                                QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                                break






                            
                    
                        
                        




            

                    
            QuerySet2['Line'].append(QuerySet3)
        
        payload = json.dumps(QuerySet2)
        print(payload,"payload--------------------------------")

        url = f"{base_url}/journalentry?minorversion=14"
        print(url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
                
    except Exception as ex:
        logging.error(ex, exc_info=True)


def add_xero_current_trial_balance(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_current_trial_balance")
        start_date, end_date = get_job_details(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"
        print(url)
        journal1 = dbname["unmatched_trial_balance"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p2 in QBO_Customer:
            QBO_customer.append(p2)
        
        QBO_Supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        QBO_supplier = []
        for p2 in QBO_Supplier:
            QBO_supplier.append(p2)

        QuerySet1 = journal
        
        QuerySet2 = {"Line": []}
        retained_earning_amount=0
        retained_earning={}
        JournalEntryLineDetail1={}
        RE={}
        account1={}
        

        for i in range(0, len(QuerySet1)):
            print(i)
            date_object = datetime.strptime(end_date, '%Y-%m-%d')
            result_string = date_object.strftime('%Y-%m-%d')
            journal_date1 = result_string
            
            QuerySet3={}
            JournalEntryLineDetail={}
            entity={}
            EntityRef={}
            QuerySet2["DocNumber"] = "XeroTrialB-today"
            QuerySet3["DetailType"] = "JournalEntryLineDetail"
            QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
            QuerySet2["TxnDate"] = journal_date1

            JournalEntryLineDetail["PostingType"] = "Credit" if (QuerySet1[i]['credit_diff']==True and QuerySet1[i]['debit_diff']==False) or (QuerySet1[i]['credit_diff']==True and QuerySet1[i]['debit_diff']==True) else "Debit"
            if JournalEntryLineDetail["PostingType"] == "Debit":
                QuerySet3["Amount"] =  abs(QuerySet1[i]['credit_diff_amount']) if QuerySet1[i]['credit_diff_amount']!=0 else QuerySet1[i]['debit_diff_amount'] 
            else:
                # QuerySet3["Amount"] =  abs(QuerySet1[i]['debit_diff_amount']) if QuerySet1[i]['debit_diff_amount']!=0 else QuerySet1[i]['credit_diff_amount'] 
                QuerySet3["Amount"] =  abs(float(QuerySet1[i]['debit_diff_amount'])) + abs(float(QuerySet1[i]['credit_diff_amount']))

            if JournalEntryLineDetail!={}: 
                if JournalEntryLineDetail["PostingType"] == "Debit":
                    retained_earning_amount = retained_earning_amount - QuerySet3["Amount"]
                else:
                    retained_earning_amount = retained_earning_amount + QuerySet3["Amount"]

            
            for j12 in range(0, len(QBO_coa)):
                if (
                        QBO_coa[j12]["AccountType"] == "Equity" and QBO_coa[j12]["Name"] == "Retained Earnings"
                    ):
                        RE['name'] = QBO_coa[j12]["Name"]
                        RE['value'] = QBO_coa[j12]["Id"]
                        break

                # if QuerySet1[i]['bankname'].split(" (")[0]=='GST':
                #     if QBO_coa[j12]["FullyQualifiedName"]=='GST Liabilities Payable':
                #         account1['name'] = QBO_coa[j12]["FullyQualifiedName"]
                #         account1['value'] = QBO_coa[j12]["Id"]
                #         JournalEntryLineDetail['AccountRef'] = account1
                #         break

            for j11 in range(0, len(QBO_coa)):
                account={}
            
                if QuerySet1[i]['bankname'].split(" (")[0] == (QBO_coa[j11]["AccountType"]) and (QBO_coa[j11]["AccountType"] == 'Accounts Payable'):
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
        
                    entity['Type'] = 'Vendor'
                    entity['EntityRef'] = EntityRef
                    for s1 in range(0,len(QBO_supplier)):
                        if QBO_supplier[s1]['DisplayName'] == 'Temp - S':
                            EntityRef['name'] = QBO_supplier[s1]['DisplayName']
                            EntityRef['value'] = QBO_supplier[s1]['Id']
                
                    JournalEntryLineDetail["Entity"] = entity
                    JournalEntryLineDetail['AccountRef'] = account
                    break
        
                elif QuerySet1[i]['bankname'].split(" (")[0] == (QBO_coa[j11]["AccountType"]) and (QBO_coa[j11]["AccountType"] == 'Accounts Receivable'):
                
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
        
                    entity['Type'] = 'Customer'
                    entity['EntityRef'] = EntityRef
                    for c1 in range(0,len(QBO_customer)):
                        if QBO_customer[c1]['DisplayName'] == 'Temp - C':
                            EntityRef['name'] = QBO_customer[c1]['DisplayName']
                            EntityRef['value'] = QBO_customer[c1]['Id']
                    JournalEntryLineDetail['AccountRef'] = account
                    JournalEntryLineDetail["Entity"] = entity
                    break

                elif QuerySet1[i]['bankname'].split(" (")[0] == (QBO_coa[j11]["FullyQualifiedName"]) and ('Accounts Payable' not in QuerySet1[i]['bankname'].split(" (")[0]) and ('Accounts Receivable' not in QuerySet1[i]['bankname'].split(" (")[0]):
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
                    JournalEntryLineDetail['AccountRef'] = account
                    break

                # elif QuerySet1[i]['bankname'].split(" (")[0]=='GST':
                #     print("GST",QuerySet1[i]['bankname'].split(" (")[0])
                #     if QBO_coa[j11]["FullyQualifiedName"]=='GST Liabilities Payable':
                #         print("if qbo true------------------------------")
                #         account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                #         account['value'] = QBO_coa[j11]["Id"]
                #         JournalEntryLineDetail['AccountRef'] = account
                #         break

                elif QBO_coa[j11]["FullyQualifiedName"].startswith(QuerySet1[i]['bankname'].split(" (")[0]):
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
                    JournalEntryLineDetail['AccountRef'] = account
                    continue

                

                    
            QuerySet2['Line'].append(QuerySet3)
        
        # print(retained_earning_amount)

        if retained_earning_amount>0:
            JournalEntryLineDetail1["PostingType"] = "Debit"
        else:
            JournalEntryLineDetail1["PostingType"] = "Credit"

        retained_earning["DetailType"] = "JournalEntryLineDetail"
        retained_earning['JournalEntryLineDetail'] = JournalEntryLineDetail1
        retained_earning["Amount"] = abs(retained_earning_amount)
        JournalEntryLineDetail1['AccountRef'] = RE

        if account1!={}:
            JournalEntryLineDetail1['AccountRef'] = account1

            

        QuerySet2['Line'].append(retained_earning)

        payload = json.dumps(QuerySet2)
        print(payload,"payload--------------------------------")

        url = f"{base_url}/journalentry?minorversion=14"
        print(url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        print(response.text)
                
    except Exception as ex:
        logging.error(ex, exc_info=True)
