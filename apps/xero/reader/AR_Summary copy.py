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

from apps.mmc_settings.all_settings import *

from apps.home.data_util import add_job_status,get_job_details
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import  write_task_execution_step,update_task_execution_status
import sys
import time
from datetime import datetime, timedelta
from datetime import date


def get_aged_receivable_summary(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_ar_summary = dbname['xero_AR']
        payload, base_url, headers = get_settings_xero(job_id)
        
        xero_customer1 = dbname['xero_open_customer']
        x = xero_customer1.find({"job_id":job_id})
        xero_customer = []
        for p1 in x:
            xero_customer.append(p1)
        
        print(start_date,type(start_date))
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)

        for i in range(0,len(xero_customer)):
            y1=int(result_string[0:4])
            m1=int(result_string[5:7])
            d1=int(result_string[8:])
            main_url = f"{base_url}/Reports/AgedReceivablesByContact?contactId={xero_customer[i]['ContactID']}&fromDate=2010-01-01&toDate={y1}-{m1}-{d1}"
                
            print(main_url)
            
            response1 = requests.request(
                "GET", main_url, headers=headers, data=payload)
            time.sleep(1)
            
            AR=[]
            if response1.status_code == 200:
                a = response1.json()
                b={}
                b['job_id'] = job_id
                b['ContactID'] = xero_customer[i]['ContactID']
                b['ContactName'] = xero_customer[i]['ContactName']
                if a['Reports'][0]['Rows'][(len(a['Reports'][0]['Rows'])-1)]['Rows'][0]['RowType']=="SummaryRow":
                    b['xero_balance']=a['Reports'][0]['Rows'][(len(a['Reports'][0]['Rows'])-1)]['Rows'][0]['Cells'][len(a['Reports'][0]['Rows'][(len(a['Reports'][0]['Rows'])-1)]['Rows'][0]['Cells'])-1]["Value"]
                    AR.append(b)

            print(AR,"AR---------------------------------")  
            
            if len(AR)>0:
                xero_ar_summary.insert_many(AR)
                
            step_name = "Reading data from xero AR Report"
            write_task_execution_step(task_id, status=1, step=step_name)
                

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_aged_payable_summary(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_ap_summary = dbname['xero_AP']
        payload, base_url, headers = get_settings_xero(job_id)
        
        xero_supplier1 = dbname['xero_open_supplier']
        x = xero_supplier1.find({"job_id":job_id})
        xero_supplier = []
        for p1 in x:
            xero_supplier.append(p1)
        
        print(start_date,type(start_date))
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)

        for i in range(0,len(xero_supplier)):
            y1=int(result_string[0:4])
            m1=int(result_string[5:7])
            d1=int(result_string[8:])
            main_url = f"{base_url}/Reports/AgedPayablesByContact?contactId={xero_supplier[i]['ContactID']}&fromDate=2010-01-01&toDate={y1}-{m1}-{d1}"
                
            print(main_url)
            
            response1 = requests.request(
                "GET", main_url, headers=headers, data=payload)
            time.sleep(1)
            
            AP=[]
            if response1.status_code == 200:
                a = response1.json()
                b={}
                b['job_id'] = job_id
                b['ContactID'] = xero_supplier[i]['ContactID']
                b['ContactName'] = xero_supplier[i]['ContactName']
                if a['Reports'][0]['Rows'][(len(a['Reports'][0]['Rows'])-1)]['Rows'][0]['RowType']=="SummaryRow":
                    b['xero_balance']=a['Reports'][0]['Rows'][(len(a['Reports'][0]['Rows'])-1)]['Rows'][0]['Cells'][len(a['Reports'][0]['Rows'][(len(a['Reports'][0]['Rows'])-1)]['Rows'][0]['Cells'])-1]["Value"]
                    AP.append(b)

            print(AP,"AP---------------------------------")  
            
            if len(AP)>0:
                xero_ap_summary.insert_many(AP)
                
            step_name = "Reading data from xero AP Report"
            write_task_execution_step(task_id, status=1, step=step_name)
                

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_qbo_ar_customer(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        qbo_ar_summary = dbname['QBO_AR']
        
        Xero_AR_Customer1 = dbname["xero_AR"].find({"job_id":job_id})
        Xero_AR_Customer = []
        for p4 in Xero_AR_Customer1:
            Xero_AR_Customer.append(p4)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p5 in QBO_Customer:
            QBO_customer.append(p5)

        qbo_ar=[]
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
                    
        for i in range(0,len(Xero_AR_Customer)):
            print(i)
            for j in range(0,len(QBO_customer)):
                if (Xero_AR_Customer[i]['ContactName'] == QBO_customer[j]['DisplayName']): 
                    queryset={}
                    url = f"{base_url}/reports/CustomerBalance?customer={QBO_customer[j]['Id']}&report_date={result_string}&minorversion={minorversion}"
                    print(url)
                    payload = {}
                    
                    response = requests.request("GET", url, headers=get_data_header, data=payload)
                    data=response.json()
                    queryset["ContactName"] = data['Rows']['Row'][0]['ColData'][0]['value']
                    queryset["qbo_balance"] = data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']
                    queryset['job_id'] = job_id
                    queryset['diff'] = True if Xero_AR_Customer[i]['xero_balance']!=data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value'] else False
                    try:
                        queryset['posting_type'] = "Credit" if float(Xero_AR_Customer[i]['xero_balance']) < float(queryset["qbo_balance"]) else "Debit"
                        queryset['diff_amount'] = float(Xero_AR_Customer[i]['xero_balance']) - float(queryset["qbo_balance"])
                    except ValueError:
                        queryset['posting_type'] = "Undefined"
                        queryset['diff_amount'] = 0 
                    dbname["xero_AR"].update_one(
                        {
                        "ContactName": f"{Xero_AR_Customer[i]['ContactName']}"
                        },
                        {
                            "$set": 
                            {
                                "qbo_balance": f"{data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']}",
                                "QBO_ContactID":f"{QBO_customer[j]['Id']}",
                                "diff": f"{queryset['diff']}",
                                "posting_type":f"{queryset['posting_type']}",
                                "diff_amount":f"{queryset['diff_amount']}"
                            }
                        }
                        )
                    break

                elif (QBO_customer[j]['DisplayName'].startswith(Xero_AR_Customer[i]['ContactName']) and (QBO_customer[j]['DisplayName']).endswith("- C") ):
                    queryset={}
                    url = f"{base_url}/reports/CustomerBalance?customer={QBO_customer[j]['Id']}&report_date={result_string}&minorversion={minorversion}"
                    print(url)
                    payload = {}
                    
                    response = requests.request("GET", url, headers=get_data_header, data=payload)
                    data=response.json()
                    queryset["ContactName"] = data['Rows']['Row'][0]['ColData'][0]['value']
                    queryset["qbo_balance"] = data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']
                    queryset['job_id'] = job_id
                    queryset['diff'] = True if Xero_AR_Customer[i]['xero_balance']!=data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value'] else False
                    try:
                        queryset['posting_type'] = "Credit" if float(Xero_AR_Customer[i]['xero_balance']) < float(queryset["qbo_balance"]) else "Debit"
                        queryset['diff_amount'] = float(Xero_AR_Customer[i]['xero_balance']) - float(queryset["qbo_balance"])
                    except ValueError:
                        queryset['posting_type'] = "Undefined"
                        queryset['diff_amount'] = 0 
                    dbname["xero_AR"].update_one(
                        {
                        "ContactName": f"{Xero_AR_Customer[i]['ContactName']}"
                        },
                        {
                            "$set": 
                            {
                                "qbo_balance": f"{data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']}",
                                "QBO_ContactID":f"{QBO_customer[j]['Id']}",
                                "diff": f"{queryset['diff']}",
                                "posting_type":f"{queryset['posting_type']}",
                                "diff_amount":f"{queryset['diff_amount']}"
                            }
                        }
                        )
                    break
                
        if len(qbo_ar)>0:
            qbo_ar_summary.insert_many(qbo_ar)
                

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)



def get_qbo_ap_supplier(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        qbo_ap_summary = dbname['QBO_AP']
        
        xero_AP_Supplier1 = dbname["xero_AP"].find({"job_id":job_id})
        xero_AP_Supplier = []
        for p4 in xero_AP_Supplier1:
            xero_AP_Supplier.append(p4)

        QBO_Supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        QBO_supplier = []
        for p5 in QBO_Supplier:
            QBO_supplier.append(p5)

        qbo_ap=[]
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
                    
        for i in range(0,len(xero_AP_Supplier)):
            print(i)
            for j in range(0,len(QBO_supplier)):
                if (xero_AP_Supplier[i]['ContactName'] == QBO_supplier[j]['DisplayName']): 
                    queryset={}
                    url = f"{base_url}/reports/VendorBalance?vendor={QBO_supplier[j]['Id']}&report_date={result_string}&minorversion={minorversion}"
                    print(url)
                    payload = {}
                    
                    response = requests.request("GET", url, headers=get_data_header, data=payload)
                    data=response.json()
                    queryset["ContactName"] = data['Rows']['Row'][0]['ColData'][0]['value']
                    queryset["qbo_balance"] = data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']
                    queryset['job_id'] = job_id
                    queryset['diff'] = True if xero_AP_Supplier[i]['xero_balance']!=data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value'] else False
                    try:
                        queryset['posting_type'] = "Credit" if float(xero_AP_Supplier[i]['xero_balance']) > float(queryset["qbo_balance"]) else "Debit"
                        queryset['diff_amount'] = float(xero_AP_Supplier[i]['xero_balance']) - float(queryset["qbo_balance"])
                    except ValueError:
                        queryset['posting_type'] = "Undefined"
                        queryset['diff_amount'] = 0 
                    dbname["xero_AP"].update_one(
                        {
                        "ContactName": f"{xero_AP_Supplier[i]['ContactName']}"
                        },
                        {
                            "$set": 
                            {
                                "qbo_balance": f"{data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']}",
                                "QBO_ContactID":f"{QBO_supplier[j]['Id']}",
                                "diff": f"{queryset['diff']}",
                                "posting_type":f"{queryset['posting_type']}",
                                "diff_amount":f"{queryset['diff_amount']}"
                            }
                        }
                        )
                    break

                elif (QBO_supplier[j]['DisplayName'].startswith(xero_AP_Supplier[i]['ContactName']) and ((QBO_supplier[j]['DisplayName']).endswith("- S") or (QBO_supplier[j]['DisplayName']).endswith("-S")) ):
                    queryset={}
                    url = f"{base_url}/reports/CustomerBalance?customer={QBO_supplier[j]['Id']}&report_date={result_string}&minorversion={minorversion}"
                    print(url)
                    payload = {}
                    
                    response = requests.request("GET", url, headers=get_data_header, data=payload)
                    data=response.json()
                    queryset["ContactName"] = data['Rows']['Row'][0]['ColData'][0]['value']
                    queryset["qbo_balance"] = data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']
                    queryset['job_id'] = job_id
                    queryset['diff'] = True if xero_AP_Supplier[i]['xero_balance']!=data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value'] else False
                    try:
                        queryset['posting_type'] = "Credit" if float(xero_AP_Supplier[i]['xero_balance']) < float(queryset["qbo_balance"]) else "Debit"
                        queryset['diff_amount'] = float(xero_AP_Supplier[i]['xero_balance']) - float(queryset["qbo_balance"])
                    except ValueError:
                        queryset['posting_type'] = "Undefined"
                        queryset['diff_amount'] = 0 
                    dbname["xero_AP"].update_one(
                        {
                        "ContactName": f"{xero_AP_Supplier[i]['ContactName']}"
                        },
                        {
                            "$set": 
                            {
                                "qbo_balance": f"{data['Rows']['Row'][0]['ColData'][len(data['Rows']['Row'][0]['ColData'])-1]['value']}",
                                "QBO_ContactID":f"{QBO_supplier[j]['Id']}",
                                "diff": f"{queryset['diff']}",
                                "posting_type":f"{queryset['posting_type']}",
                                "diff_amount":f"{queryset['diff_amount']}"
                            }
                        }
                        )
                    break
                
        if len(qbo_ap)>0:
            qbo_ap_summary.insert_many(qbo_ap)
    
    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_qbo_trial_balance(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        QBO_Trial_Balance = dbname['QBO_Trial_Balance']
        
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)
        y1=int(result_string[0:4])
        m1=int(result_string[5:7])
        d1=int(result_string[8:])
            
        url = f"{base_url}/reports/TrialBalance?&start_date=2020-01-01&end_date={y1}-{m1}-{d1}&minorversion={minorversion}"
        print(url)
        payload=""
        response = requests.request("GET", url, headers=headers, data=payload)
        data=response.json()

        trial_balance=[]
        for i in range(0,len(data['Rows']['Row'])-1):
            queryset={}
            queryset['job_id'] = job_id
            queryset['bankname'] = data['Rows']['Row'][i]['ColData'][0]['value']
            queryset['bankid'] = data['Rows']['Row'][i]['ColData'][0]['id']
            queryset['debit']= 0 if data['Rows']['Row'][i]['ColData'][1]['value'] =='' else data['Rows']['Row'][i]['ColData'][1]['value'] 
            queryset['credit']= 0 if data['Rows']['Row'][i]['ColData'][2]['value'] == '' else data['Rows']['Row'][i]['ColData'][2]['value'] 
            print(queryset['debit'],queryset['credit'])
            trial_balance.append(queryset)
                    
        if len(trial_balance)>0:
            QBO_Trial_Balance.insert_many(trial_balance)
            print("QBO_Trial_Balance Created")

                
    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)

def get_qbo_current_trial_balance(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        QBO_Trial_Balance = dbname['QBO_Current_Trial_Balance']
        
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)
        y1=int(result_string[0:4])
        m1=int(result_string[5:7])
        d1=int(result_string[8:])
            
        url = f"{base_url}/reports/TrialBalance?&start_date={y1}-07-01&end_date={y1}-{m1}-{d1}&minorversion={minorversion}"
        print(url)
        payload=""
        response = requests.request("GET", url, headers=headers, data=payload)
        data=response.json()

        trial_balance=[]
        for i in range(0,len(data['Rows']['Row'])-1):
            queryset={}
            queryset['job_id'] = job_id
            queryset['bankname'] = data['Rows']['Row'][i]['ColData'][0]['value']
            queryset['bankid'] = data['Rows']['Row'][i]['ColData'][0]['id']
            queryset['debit']= 0 if data['Rows']['Row'][i]['ColData'][1]['value'] =='' else data['Rows']['Row'][i]['ColData'][1]['value'] 
            queryset['credit']= 0 if data['Rows']['Row'][i]['ColData'][2]['value'] == '' else data['Rows']['Row'][i]['ColData'][2]['value'] 
            print(queryset['debit'],queryset['credit'])
            trial_balance.append(queryset)
                    
        if len(trial_balance)>0:
            QBO_Trial_Balance.insert_many(trial_balance)
            print("QBO_Trial_Balance Created")

                
    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)

    
def get_xero_trial_balance(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_trial_balance = dbname['xero_trial_balance']
        payload, base_url, headers = get_settings_xero(job_id)
        
        print(start_date,type(start_date))
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)
        y1=int(result_string[0:4])
        m1=int(result_string[5:7])
        d1=int(result_string[8:])
        main_url = f"{base_url}/Reports/TrialBalance?date={y1}-{m1}-{d1}"
        print(main_url)
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
            
        print(main_url)
        a = response1.json()
        
        data=[]
        for i in range(1,len(a['Reports'][0]['Rows'])-1):
            for j in range(0,len(a['Reports'][0]['Rows'][i]['Rows'])):
                queryset={}
                queryset['job_id'] = job_id
                queryset['bankname']=a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][0]['Value']
                queryset['bankid']=a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][1]['Attributes'][0]['Value']
                queryset['credit']= 0 if a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][3]['Value']=='' else a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][3]['Value']
                queryset['debit']=0 if a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][4]['Value']=='' else a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][4]['Value']
                # queryset['debit']= 0 if a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][3]['Value']=='' else a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][3]['Value']
                # queryset['credit']=0 if a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][4]['Value']=='' else a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][4]['Value']
                data.append(queryset)    
                
        if len(data)>0:
            xero_trial_balance.insert_many(data)
            
    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_xero_current_trial_balance(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_trial_balance = dbname['xero_current_trial_balance']
        payload, base_url, headers = get_settings_xero(job_id)
        
        print(start_date,type(start_date))
        date_object = datetime.strptime(start_date, '%Y-%m-%d')
        one_day_before = date_object - timedelta(days=1)
        result_string = one_day_before.strftime('%Y-%m-%d')
        print(result_string)
        y1=int(result_string[0:4])
        m1=int(result_string[5:7])
        d1=int(result_string[8:])
        main_url = f"{base_url}/Reports/TrialBalance?date={y1}-{m1}-{d1}"
        print(main_url)
        response1 = requests.request(
            "GET", main_url, headers=headers, data=payload)
            
        print(main_url)
        a = response1.json()
        
        data=[]
        for i in range(1,len(a['Reports'][0]['Rows'])-1):
            for j in range(0,len(a['Reports'][0]['Rows'][i]['Rows'])):
                queryset={}
                queryset['job_id'] = job_id
                queryset['bankname']=a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][0]['Value']
                queryset['bankid']=a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][1]['Attributes'][0]['Value']
                queryset['debit']= 0 if a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][3]['Value']=='' else a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][3]['Value']
                queryset['credit']=0 if a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][4]['Value']=='' else a['Reports'][0]['Rows'][i]['Rows'][j]['Cells'][4]['Value']
                
                data.append(queryset)    
                
        if len(data)>0:
            xero_trial_balance.insert_many(data)
            
    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def match_trial_balance(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_trial_balance = dbname['xero_current_trial_balance']
        qbo_trial_balance = dbname['QBO_Current_Trial_Balance']
        unmatched_trial_balance = dbname['unmatched_trial_balance']

        xero_trial_balance = dbname["xero_current_trial_balance"].find({"job_id":job_id})
        xero_trial_balance1 = []
        for p4 in xero_trial_balance:
            xero_trial_balance1.append(p4)

        qbo_trial_balance = dbname["QBO_Current_Trial_Balance"].find({"job_id":job_id})
        qbo_trial_balance1 = []
        for p4 in qbo_trial_balance:
            qbo_trial_balance1.append(p4)
        
        unmatched_data=[]
        for i in range(0,len(xero_trial_balance1)):
            print(i)
            
            if xero_trial_balance1[i]['bankname'].split(" (")[0] in ['Payroll Wages & Salaries','Depreciation','Superannuation','Payroll  Wages & Salaries']:
                print(xero_trial_balance1[i]['bankname'].split(" (")[0],"if")
                queryset={}
                queryset['job_id']=job_id
                queryset['bankname'] = xero_trial_balance1[i]['bankname']
                    
                if float(xero_trial_balance1[i]['debit']) != 0:
                    queryset['debit_diff'] = True
                    queryset['debit_diff_amount'] = float(xero_trial_balance1[i]['debit'])
                    queryset['credit_diff'] = False
                    queryset['credit_diff_amount'] = 0                
                elif float(xero_trial_balance1[i]['credit']) != 0:
                    queryset['credit_diff'] = True
                    queryset['credit_diff_amount'] = float(xero_trial_balance1[i]['credit'])
                    queryset['debit_diff'] = False
                    queryset['debit_diff_amount'] = 0

                dbname["xero_current_trial_balance"].update_one(
                    {
                    "bankname": f"{xero_trial_balance1[i]['bankname']}"
                    },
                    {
                        "$set": 
                        {
                            "credit_diff": queryset['credit_diff'],
                            "debit_diff":queryset['debit_diff'],
                            "credit_diff_amount": queryset['credit_diff_amount'],
                            "debit_diff_amount":queryset['debit_diff_amount'] ,
                            }
                    }
                    )
                
                unmatched_data.append(queryset)
            
            for j in range(0,len(qbo_trial_balance1)):
                queryset={}
                queryset['job_id']=job_id

                if (xero_trial_balance1[i]['bankname'].split(" (")[1][:-1] + " " + xero_trial_balance1[i]['bankname'].split(" (")[0] == qbo_trial_balance1[j]['bankname']):
                    queryset['bankname'] = xero_trial_balance1[i]['bankname']
                    if xero_trial_balance1[i]['debit'] == qbo_trial_balance1[j]['debit']:
                        queryset['debit_diff'] = False
                        queryset['debit_diff_amount'] = 0
                    else:
                        queryset['debit_diff'] = True
                        queryset['debit_diff_amount'] = float(xero_trial_balance1[i]['debit'])-float(qbo_trial_balance1[j]['debit'])
            
                    if xero_trial_balance1[i]['credit'] == qbo_trial_balance1[j]['credit']:
                        queryset['credit_diff'] = False
                        queryset['credit_diff_amount'] = 0
                    else:
                        queryset['credit_diff'] = True
                        queryset['credit_diff_amount'] = float(xero_trial_balance1[i]['credit'])-float(qbo_trial_balance1[j]['credit'])
                    
                    if queryset['credit_diff']==False and queryset['debit_diff']==False:
                        print("Both False so we can skip")
                    # elif queryset['credit_diff']==True and queryset['debit_diff']==True:
                    #     print("Revrese the entry")
                    else:
                        dbname["xero_current_trial_balance"].update_one(
                        {
                        "bankname": f"{xero_trial_balance1[i]['bankname']}"
                        },
                        {
                            "$set": 
                            {
                                "credit_diff": queryset['credit_diff'],
                                "debit_diff":queryset['debit_diff'],
                                "credit_diff_amount": queryset['credit_diff_amount'],
                                "debit_diff_amount":queryset['debit_diff_amount'] ,
                              }
                        }
                        )
                    
                        unmatched_data.append(queryset)

                elif (xero_trial_balance1[i]['bankname'].split(" (")[0] == 'GST'):
                    print(xero_trial_balance1[i]['bankname'].split(" (")[0])
                    if qbo_trial_balance1[j]['bankname']=='820 GST Liabilities Payable':
                        print(qbo_trial_balance1[j]['bankname'])
                        print("matched")
                        queryset['bankname'] = xero_trial_balance1[i]['bankname']
                        if xero_trial_balance1[i]['debit'] == qbo_trial_balance1[j]['debit']:
                            queryset['debit_diff'] = False
                            queryset['debit_diff_amount'] = 0
                        else:
                            queryset['debit_diff'] = True
                            queryset['debit_diff_amount'] = float(xero_trial_balance1[i]['debit'])-float(qbo_trial_balance1[j]['debit'])
                
                        if xero_trial_balance1[i]['credit'] == qbo_trial_balance1[j]['credit']:
                            queryset['credit_diff'] = False
                            queryset['credit_diff_amount'] = 0
                        else:
                            queryset['credit_diff'] = True
                            queryset['credit_diff_amount'] = float(xero_trial_balance1[i]['credit'])-float(qbo_trial_balance1[j]['credit'])
                        
                        if queryset['credit_diff']==False and queryset['debit_diff']==False:
                            print("Both False so we can skip")
                        # elif queryset['credit_diff']==True and queryset['debit_diff']==True:
                        #     print("Revrese the entry")
                        else:
                            dbname["xero_current_trial_balance"].update_one(
                            {
                            "bankname": f"{xero_trial_balance1[i]['bankname']}"
                            },
                            {
                                "$set": 
                                {
                                    "credit_diff": queryset['credit_diff'],
                                    "debit_diff":queryset['debit_diff'],
                                    "credit_diff_amount": queryset['credit_diff_amount'],
                                    "debit_diff_amount":queryset['debit_diff_amount'] ,
                                }
                            }
                            )
                        
                            unmatched_data.append(queryset)
                            print(queryset)
                            break

                    
                
        if len(unmatched_data)>0:
            unmatched_trial_balance.insert_many(unmatched_data)

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
