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
from apps.util.qbo_util import get_start_end_dates_of_job

import re
from apps.mmc_settings.all_settings import *
import logging
import logging

from apps.home.data_util import add_job_status,get_job_details
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import  write_task_execution_step,update_task_execution_status
import sys
import time
from datetime import datetime, timedelta


def get_xero_asset_types(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_asset_types = dbname['xero_asset_types']
        payload, base_url, headers = get_settings_xero(job_id)

        url = "https://api.xero.com/assets.xro/1.0/AssetTypes"

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            JsonResponse = response.json()
            print(JsonResponse)
            payrun_list=[]
            payrun_list.append(JsonResponse)

            print(payrun_list)   
            if JsonResponse != []:
                e={}
                e['job_id']=job_id
                e['type']=JsonResponse[0]
                xero_asset_types.insert_one(e)
                        
            step_name = "Reading data from xero asset types"
            write_task_execution_step(task_id, status=1, step=step_name)
                        

    except Exception as ex:
        step_name = "Something went wrong"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)

offset=0
def get_xero_journal(job_id,task_id):
    try:
        global offset
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        xero_journal = dbname["xero_journal"]

        payload, base_url, headers = get_settings_xero(job_id)
        
        main_url = f"https://api.xero.com/api.xro/2.0/Journals?offset={offset}"
        print(main_url)
        response1 = requests.request("GET", main_url, headers=headers, data=payload)
        time.sleep(1)
        if response1.status_code == 200:
            r1 = response1.json()
            jsonresponse = r1["Journals"]
            arr=[]
            
            if len(jsonresponse) != 0:
                
                for i in range(0,len(jsonresponse)):
                    if 'SourceType' not in jsonresponse[i]:
                        date_string = jsonresponse[i]['JournalDate']
                        match = re.search(r'\d+', date_string)
                        if match:
                            timestamp = int(match.group())
                            timestamp /= 1000
                            datetime_obj = datetime.utcfromtimestamp(timestamp)
                            xero_journal_date1 = datetime_obj.strftime("%Y-%m-%d")
                        
                        e={'Lines':[]}
                        e1={}
                        e['job_id']=job_id
                        e['JournalID'] = jsonresponse[i]['JournalID']
                        e['JournalDate'] = xero_journal_date1
                        e['JournalNumber'] = jsonresponse[i]['JournalNumber']
                        # e['Reference'] = jsonresponse[i]['Reference']
                        for j in range(0,len(jsonresponse[i]['JournalLines'])):
                            e1={}
                            e1['AccountID'] = jsonresponse[i]['JournalLines'][j]['AccountID']
                            if 'AccountCode' in jsonresponse[i]['JournalLines'][j]:
                                e1['AccountCode'] = jsonresponse[i]['JournalLines'][j]['AccountCode']
                            e1['AccountType'] = jsonresponse[i]['JournalLines'][j]['AccountType']
                            e1['AccountName'] = jsonresponse[i]['JournalLines'][j]['AccountName']
                            e1['Description'] = jsonresponse[i]['JournalLines'][j]['Description']
                            e1['NetAmount'] = jsonresponse[i]['JournalLines'][j]['NetAmount']
                            e1['GrossAmount'] = jsonresponse[i]['JournalLines'][j]['GrossAmount']
                            e['Lines'].append(e1)
                        
                        arr.append(e)

            if len(arr)>0 :
                xero_journal.insert_many(arr)

            if len(jsonresponse)==100:
                offset = offset+100
                get_xero_journal(job_id,task_id)
            
            
    except Exception as ex:
        step_name = "Something went wrong"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
        

def get_xero_depreciation_journal(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> get_xero_depreciation_journal")
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        
        xero_depreciation_journal = dbname["xero_depreciation_journal"]

        xero_journal1 = dbname["xero_journal"].find({"job_id":job_id})
        xero_journal = []
        for p1 in xero_journal1:
            xero_journal.append(p1)

        xero_asset_types1 = dbname["xero_asset_types"].find({"job_id":job_id})
        xero_asset_types = []
        for p1 in xero_asset_types1:
            xero_asset_types.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        acc_list=[]
        if len(xero_asset_types)> 0:
            acc_list.append(xero_asset_types[0]['type']['depreciationExpenseAccountId'])
            acc_list.append(xero_asset_types[0]['type']['accumulatedDepreciationAccountId'])
        
        depreciation_journal=[]
        for i in range(0,len(xero_journal)):
            line_Acc=[]
                
            for j in range(0,len(xero_journal[i]['Lines'])):
                line_Acc.append(xero_journal[i]['Lines'][j]['AccountID'])
                if set(line_Acc) == set(acc_list):
                    e={}
                    e['job_id']=job_id
                    e['journal']=xero_journal[i]
                    depreciation_journal.append(e)

        if len(depreciation_journal)>0:
            xero_depreciation_journal.insert_many(depreciation_journal)
    
    except Exception as ex:
        step_name = "Something went wrong"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def add_xero_depreciation_journal(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_depreciation_journal")
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        print(url)
        xero_depreciation_journal1 = dbname["xero_depreciation_journal"].find({"job_id":job_id})
        xero_depreciation_journal = []
        for p1 in xero_depreciation_journal1:
            xero_depreciation_journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

       
        QuerySet11 = xero_depreciation_journal

            
        for i in range(0, len(QuerySet11)):
            QuerySet2 = {"Line": []}
        
            QuerySet1=QuerySet11[i]['journal']
            QuerySet2["DocNumber"] = f"Depreciation-{QuerySet1['JournalNumber']}"
            QuerySet2["TxnDate"] = QuerySet1['JournalDate']
                
            for j in range(0,len(QuerySet1['Lines'])):
                print(j)
                account={}
                
                for j11 in range(0, len(QBO_coa)):
                    if QuerySet1['Lines'][j]['AccountName'] == QBO_coa[j11]['Name']:
                        account['value'] = QBO_coa[j11]['Id']
                        account['name'] = QBO_coa[j11]['Name']
                
                JournalEntryLineDetail={}
                QuerySet3={}
                QuerySet3["DetailType"] = "JournalEntryLineDetail"
                if QuerySet1['Lines'][j]['NetAmount'] >0:
                    JournalEntryLineDetail["PostingType"] = "Debit"
                else:
                    JournalEntryLineDetail["PostingType"] = "Credit"

                QuerySet3["Amount"] = abs(QuerySet1['Lines'][j]['NetAmount'])
                JournalEntryLineDetail['AccountRef'] = account
                QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                QuerySet2['Line'].append(QuerySet3)
                
            payload = json.dumps(QuerySet2)
            print(payload,"payload--------------------------------")

            print(QuerySet1['JournalDate'])
            print(start_date1)

            journal_date = QuerySet1['JournalDate'][0:10]
            journal_date1 = datetime.strptime(journal_date, "%Y-%m-%d")

            if start_date1 is not None and end_date1 is not None:
                if (journal_date1 >= start_date1) and (journal_date1 <= end_date1):
                    response = requests.request("POST", url, headers=headers, data=payload)
                    print(response.status_code)
                    print(response.text)
                    
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_xero_invoice_payment", ex)
