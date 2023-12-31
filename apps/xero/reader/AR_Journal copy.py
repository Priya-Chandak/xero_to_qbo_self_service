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
from apps.util.log_file import log_config
import logging

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
            
        for i in range(0, len(QuerySet1)):
            print(i)    
            print(QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0)
                  
            if QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0:
                
                date_object = datetime.strptime(start_date, '%Y-%m-%d')
                one_day_before = date_object - timedelta(days=1)
                journal_date1 = one_day_before.strftime('%Y-%m-%d')
                
                AR = {}
                RE = {}
                
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
            
        for i in range(0, len(QuerySet1)):
            print(i)    
            print(QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0)
                  
            if QuerySet1[i]['diff'] == "True" and float(QuerySet1[i]['diff_amount'])!= 0:
                
                date_object = datetime.strptime(start_date, '%Y-%m-%d')
                one_day_before = date_object - timedelta(days=1)
                journal_date1 = one_day_before.strftime('%Y-%m-%d')
                
                AP = {}
                RE = {}
                
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
        print(retained_earning_amount)

        if retained_earning_amount>0:
            JournalEntryLineDetail1["PostingType"] = "Debit"
        else:
            JournalEntryLineDetail1["PostingType"] = "Credit"

        retained_earning["DetailType"] = "JournalEntryLineDetail"
        retained_earning['JournalEntryLineDetail'] = JournalEntryLineDetail1
        retained_earning["Amount"] = -retained_earning_amount
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
    log_config1=log_config(job_id)
    
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
            entity={}
            account={}
            EntityRef={}
            QuerySet2["DocNumber"] = "ReverseTrialBalance"
            QuerySet3["DetailType"] = "JournalEntryLineDetail"
            QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
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
                

            for j11 in range(0, len(QBO_coa)):
                if 'AcctNum' in QBO_coa[j11]:
                    if (QuerySet1[i]['bankname'] == QBO_coa[j11]["AcctNum"] + " " + QBO_coa[j11]["FullyQualifiedName"]) and (QBO_coa[j11]["AccountType"] == 'Accounts Payable'):
                        entity['Type'] = 'Vendor'
                        entity['EntityRef'] = EntityRef
                        for s1 in range(0,len(QBO_supplier)):
                            if QBO_supplier[s1]['DisplayName'] == 'Temp - S':
                                EntityRef['name'] = QBO_supplier[s1]['DisplayName']
                                EntityRef['value'] = QBO_supplier[s1]['Id']
                    
                        JournalEntryLineDetail["Entity"] = entity

                    elif (QuerySet1[i]['bankname'] == QBO_coa[j11]["AcctNum"] + " " + QBO_coa[j11]["FullyQualifiedName"]) and (QBO_coa[j11]["AccountType"] == 'Accounts Receivable'):
                        entity['Type'] = 'Customer'
                        entity['EntityRef'] = EntityRef
                        for c1 in range(0,len(QBO_customer)):
                            if QBO_customer[c1]['DisplayName'] == 'Temp - C':
                                EntityRef['name'] = QBO_customer[c1]['DisplayName']
                                EntityRef['value'] = QBO_customer[c1]['Id']
                    
                        JournalEntryLineDetail["Entity"] = entity
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
    log_config1=log_config(job_id)
    
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
            entity={}
            EntityRef={}
            QuerySet2["DocNumber"] = "XeroTrialBalance-Open"
            QuerySet3["DetailType"] = "JournalEntryLineDetail"
            QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
            QuerySet2["TxnDate"] = journal_date1
            if float(QuerySet1[i]['debit'])==0:
                JournalEntryLineDetail["PostingType"] = "Debit"
                QuerySet3["Amount"] = abs(float(QuerySet1[i]["credit"]))
            else:
                JournalEntryLineDetail["PostingType"] = "Credit"
                QuerySet3["Amount"] = abs(float(QuerySet1[i]["debit"]))
                

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

                elif QuerySet1[i]['bankname'].split(" (")[0] == (QBO_coa[j11]["FullyQualifiedName"]):
                    print("elif1--",QuerySet1[i]['bankname'])
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
                    JournalEntryLineDetail['AccountRef'] = account
                    break

                elif QBO_coa[j11]["FullyQualifiedName"].startswith(QuerySet1[i]['bankname'].split(" (")[0]):
                    print("elif2-",QuerySet1[i]['bankname'])
                    
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
                    JournalEntryLineDetail['AccountRef'] = account
                    continue

                    
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

def add_xero_current_trial_balance(job_id,task_id):
    log_config1=log_config(job_id)
    
    try:
        logging.info("Started executing xero -> qbowriter -> add_qbo_reverse_trial_balance")
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
        

        for i in range(0, len(QuerySet1)):
            print(i)
            date_object = datetime.strptime(end_date, '%Y-%m-%d')
            journal_date1 = date_object.strftime('%Y-%m-%d')
        
            QuerySet3={}
            JournalEntryLineDetail={}
            entity={}
            EntityRef={}
            QuerySet2["DocNumber"] = "XeroTrialB-today"
            QuerySet3["DetailType"] = "JournalEntryLineDetail"
            QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
            QuerySet2["TxnDate"] = journal_date1

            if QuerySet1[i]['debit_diff']==True and QuerySet1[i]['credit_diff']==True :
                if QuerySet1[i]['debit_diff_amount'] < 0 :
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["debit_diff_amount"]))+abs(float(QuerySet1[i]["credit_diff_amount"]))
                else:
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["debit_diff_amount"]))+abs(float(QuerySet1[i]["credit_diff_amount"]))
                
            
            if QuerySet1[i]['debit_diff']==True and QuerySet1[i]['credit_diff']==False :
                if QuerySet1[i]['debit_diff_amount'] < 0 :
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["debit_diff_amount"]))
                else:
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["debit_diff_amount"]))
                
             
            if QuerySet1[i]['credit_diff']==True and QuerySet1[i]['debit_diff']==False :
                if QuerySet1[i]['credit_diff_amount'] < 0 :
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["credit_diff_amount"]))
                else:
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]["credit_diff_amount"]))
                
            if JournalEntryLineDetail["PostingType"] == "Debit":
                retained_earning_amount = retained_earning_amount - QuerySet3["Amount"]
            else:
                retained_earning_amount = retained_earning_amount + QuerySet3["Amount"]

            
            print(retained_earning_amount,"=retained_earning_amount")
            
            for j11 in range(0, len(QBO_coa)):
                if (
                        QBO_coa[j11]["AccountType"] == "Equity" and QBO_coa[j11]["Name"] == "Retained Earnings"
                    ):
                        RE['name'] = QBO_coa[j11]["Name"]
                        RE['value'] = QBO_coa[j11]["Id"]
                
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

                elif QuerySet1[i]['bankname'].split(" (")[0] == (QBO_coa[j11]["FullyQualifiedName"]):
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
                    JournalEntryLineDetail['AccountRef'] = account
                    break

                elif QBO_coa[j11]["FullyQualifiedName"].startswith(QuerySet1[i]['bankname'].split(" (")[0]):
                    account['name'] = QBO_coa[j11]["FullyQualifiedName"]
                    account['value'] = QBO_coa[j11]["Id"]
                    JournalEntryLineDetail['AccountRef'] = account
                    continue

                

                    
            QuerySet2['Line'].append(QuerySet3)
        
        print(retained_earning_amount)

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