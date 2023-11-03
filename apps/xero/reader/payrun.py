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



def get_payrun(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_payrun = dbname['xero_payrun']
        payload, base_url, headers = get_settings_xero(job_id)

        url = "https://api.xero.com/payroll.xro/1.0/PayRuns"

        response = requests.request("GET", url, headers=headers, data=payload)

        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['PayRuns']
        payrun_list=[]
        for i in range(0, len(JsonResponse1)):
            payrun_list.append(JsonResponse1[i]['PayRunID'])

        print(payrun_list)   
        
        all_payrun=[]
        for j in range(0,len(payrun_list)):
            url1=f"https://api.xero.com/payroll.xro/1.0/PayRuns/{payrun_list[j]}" 
            print(url1)
            response = requests.request("GET", url1, headers=headers, data=payload)

            JsonResponse = response.json()
            JsonResponse1 = JsonResponse['PayRuns']
            queryset1={}
            queryset1['job_id']=job_id
            queryset1['payrun'] = JsonResponse1[0]
            all_payrun.append(queryset1)

        if len(all_payrun)>0:
            xero_payrun.insert_many(all_payrun)
                
        step_name = "Reading data from xero payrun"
        write_task_execution_step(task_id, status=1, step=step_name)
                    

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_payslip(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()
        xero_payslip = dbname["xero_payslip"]
        xero_payrun = dbname["xero_payrun"]
        x = xero_payrun.find({"job_id":job_id})
        data = []
        for i in x:
            data.append(i)
        payload, base_url, headers = get_settings_xero(job_id)

        all_payrun=[]
            
        for k in range(0,len(data)):
            url = f"https://api.xero.com/payroll.xro/1.0/Payslip/{data[k]['payrun']['Payslips'][0]['PayslipID']}"
            print(url)
        
            response = requests.request("GET", url, headers=headers, data=payload)

            JsonResponse = response.json()
            JsonResponse1 = JsonResponse['Payslip']
            queryset1={}
            queryset1['job_id']=job_id
            queryset1 = JsonResponse1
        
            all_payrun.append(queryset1)

        if len(all_payrun)>0:
            xero_payslip.insert_many(all_payrun)

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_payrun_setting(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        xero_payrun_setting = dbname["xero_payrun_setting"]
        payload, base_url, headers = get_settings_xero(job_id)

        all_settings=[]
            
        url = "https://api.xero.com/payroll.xro/1.0/Settings"
        print(url)
    
        response = requests.request("GET", url, headers=headers, data=payload)

        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['Settings']['Accounts']
        for i in range(0,len(JsonResponse1)):
            queryset1={}
            queryset1['job_id']=job_id
            queryset1['AccountID'] = JsonResponse1[i]['AccountID']
            queryset1['Type'] = JsonResponse1[i]['Type']
            queryset1['Code'] = JsonResponse1[i]['Code']
            queryset1['Name'] = JsonResponse1[i]['Name']
    
            all_settings.append(queryset1)
        
        if len(all_settings)>0:
            xero_payrun_setting.insert_many(all_settings)

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status( task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)