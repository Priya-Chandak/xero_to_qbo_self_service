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
from datetime import date
from apps.util.qbo_util import post_data_in_qbo
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.log_file import log_config
import logging
from apps.util.log_file import log_config
import logging


def add_xero_payrun(job_id,task_id):
    log_config1=log_config(job_id)
    
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_payrun")
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        print(url)
        xero_payrun1 = dbname["xero_payrun"].find({"job_id":job_id})
        xero_payrun = []
        for p1 in xero_payrun1:
            xero_payrun.append(p1)

        # xero_payslip1 = dbname["xero_payslip"].find({"job_id":job_id})
        # xero_payslip = []
        # for p1 in xero_payslip1:
        #     xero_payslip.append(p1)

        xero_payrun_setting1 = dbname["xero_payrun_setting"].find({"job_id":job_id})
        xero_payrun_setting = []
        for p1 in xero_payrun_setting1:
            xero_payrun_setting.append(p1)

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

        QuerySet1 = xero_payrun

        # QuerySet2 = {"Line": []}
            
        for i in range(0, len(QuerySet1)):
            print(i)
            _id = QuerySet1[i]['_id']
                            
            QuerySet2 = {"Line": []}
            print(QuerySet1[i]['payrun']['PayRunStatus'])
            if QuerySet1[i]['payrun']['PayRunStatus'] == 'POSTED':
                print("Posted")
                date_string = QuerySet1[i]['payrun']['PaymentDate']
                match = re.search(r'\d+', date_string)
                if match:
                    timestamp = int(match.group())
                    timestamp /= 1000
                    datetime_obj = datetime.utcfromtimestamp(timestamp)
                    print(datetime_obj,start_date1)
                    xero_payrun_date1 = datetime_obj.strftime("%Y-%m-%d")
                
                
                entity={}
                EntityRef={}
                QuerySet2["DocNumber"] = f"Payrun-{i+1}"
                QuerySet2["TxnDate"] = xero_payrun_date1
                wages_account={}
                super_account={}
                superannuation_payable_liability={}
                wages_payable_liability={}
                tax_account={}

                for d1 in range(0,len(xero_payrun_setting)):
                    for j11 in range(0, len(QBO_coa)):
                        if xero_payrun_setting[d1]['Type'] == 'WAGESEXPENSE':
                            if xero_payrun_setting[d1]['Name'] == QBO_coa[j11]['Name']:
                                wages_account['value'] = QBO_coa[j11]['Id']
                                wages_account['name'] = QBO_coa[j11]['Name']
                        if xero_payrun_setting[d1]['Type'] == 'SUPERANNUATIONEXPENSE':
                            if xero_payrun_setting[d1]['Name'] == QBO_coa[j11]['Name']:
                                super_account['value'] = QBO_coa[j11]['Id']
                                super_account['name'] = QBO_coa[j11]['Name']
                        if xero_payrun_setting[d1]['Type'] == 'WAGESPAYABLELIABILITY':
                            if xero_payrun_setting[d1]['Name'] == QBO_coa[j11]['Name']:
                                wages_payable_liability['value'] = QBO_coa[j11]['Id']
                                wages_payable_liability['name'] = QBO_coa[j11]['Name']
                        if xero_payrun_setting[d1]['Type'] == 'SUPERANNUATIONLIABILITY':
                            if xero_payrun_setting[d1]['Name'] == QBO_coa[j11]['Name']:
                                superannuation_payable_liability['value'] = QBO_coa[j11]['Id']
                                superannuation_payable_liability['name'] = QBO_coa[j11]['Name']
                        if xero_payrun_setting[d1]['Type'] == 'PAYGLIABILITY':
                            if xero_payrun_setting[d1]['Name'] == QBO_coa[j11]['Name']:
                                tax_account['value'] = QBO_coa[j11]['Id']
                                tax_account['name'] = QBO_coa[j11]['Name']
                        
                
                if float(QuerySet1[i]['payrun']['Tax'])!=0:
                    JournalEntryLineDetail={}
                    QuerySet3={}
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    if float(QuerySet1[i]['payrun']['Wages']) > 0:
                        JournalEntryLineDetail["PostingType"] = "Credit"
                    else:
                        JournalEntryLineDetail["PostingType"] = "Debit"
                    
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]['payrun']['Tax']))
                    JournalEntryLineDetail['AccountRef'] = tax_account
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    QuerySet2['Line'].append(QuerySet3)

                if float(QuerySet1[i]['payrun']['Wages'])!=0:
                    JournalEntryLineDetail={}
                    QuerySet3={}
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    if float(QuerySet1[i]['payrun']['Wages']) > 0:
                        JournalEntryLineDetail["PostingType"] = "Debit"
                    else:
                        JournalEntryLineDetail["PostingType"] = "Credit"

                    QuerySet3["Amount"] = abs(float(QuerySet1[i]['payrun']['Wages']))
                    JournalEntryLineDetail['AccountRef'] = wages_account
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    QuerySet2['Line'].append(QuerySet3)
                   
                if float(QuerySet1[i]['payrun']['Super'])!=0:
                    JournalEntryLineDetail={}
                    QuerySet3={}
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    JournalEntryLineDetail["PostingType"] = "Debit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]['payrun']['Super']))
                    JournalEntryLineDetail['AccountRef'] = super_account
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    
                    QuerySet2['Line'].append(QuerySet3)

                if float(QuerySet1[i]['payrun']['NetPay'])!=0:
                    JournalEntryLineDetail={}
                    QuerySet3={}
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    if float(QuerySet1[i]['payrun']['NetPay']) > 0:
                        JournalEntryLineDetail["PostingType"] = "Credit"
                    else:
                        JournalEntryLineDetail["PostingType"] = "Debit"

                    QuerySet3["Amount"] = abs(float(QuerySet1[i]['payrun']['NetPay']))
                    JournalEntryLineDetail['AccountRef'] = wages_payable_liability
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    
                    QuerySet2['Line'].append(QuerySet3)

                if float(QuerySet1[i]['payrun']['Super'])!=0:
                    JournalEntryLineDetail={}
                    QuerySet3={}
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    JournalEntryLineDetail["PostingType"] = "Credit"
                    QuerySet3["Amount"] = abs(float(QuerySet1[i]['payrun']['Super']))
                    JournalEntryLineDetail['AccountRef'] = superannuation_payable_liability
                    QuerySet3['JournalEntryLineDetail'] = JournalEntryLineDetail
                    
                    QuerySet2['Line'].append(QuerySet3)


                
            payload = json.dumps(QuerySet2)
            print(payload,"payload--------------------------------")

            # response = requests.request("POST", url, headers=headers, data=payload)
            if start_date1 is not None and end_date1 is not None:
                if (datetime_obj >= start_date1) and (datetime_obj <= end_date1):
                    post_data_in_qbo(url, headers, payload,dbname['xero_payrun'],_id, job_id,task_id, QuerySet1[i]['payrun'])
            
            # print(response.status_code)
            # print(response.text)
                
    except Exception as ex:
        logging.error(ex, exc_info=True)