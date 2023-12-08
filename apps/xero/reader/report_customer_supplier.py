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

from apps.home.data_util import add_job_status, get_job_details
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import write_task_execution_step, update_task_execution_status
import sys
import time
from datetime import datetime, timedelta
from datetime import date


def get_report_customer_summary(job_id, task_id):
    print("get_report_customer_summary")
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        final_report_cust_summary = dbname['xero_report_customer']
        payload, base_url, headers = get_settings_xero(job_id)

        xero_ar_customer = dbname['xero_AR_till_end_date']
        x = xero_ar_customer.find({"job_id": job_id})
        xero_customer_data = []
        for p1 in x:
            xero_customer_data.append(p1)
        qbo_customer = dbname['QBO_Customer']

        y = qbo_customer.find({"job_id": job_id})
        qbo_customer_data = []
        for p2 in y:
            qbo_customer_data.append(p2)

        customer_data = []
                
        for i in range(0, len(xero_customer_data)):
            for j in range(0, len(qbo_customer_data)):
                if (xero_customer_data[i]["ContactName"] == qbo_customer_data[j]["FullyQualifiedName"]) or (qbo_customer_data[j]["FullyQualifiedName"].startswith(xero_customer_data[i]["ContactName"]) and qbo_customer_data[j]["FullyQualifiedName"].endswith("- C")) :
                    b = {}
                    if 'ContactID' in xero_customer_data[i]: 
                        b['code'] = xero_customer_data[i]['ContactID']
                        b['Customer_name'] = xero_customer_data[i]['ContactName']
                        b['Xero'] = xero_customer_data[i]['xero_balance']
                        b['QBO'] = qbo_customer_data[j]["Balance"]
                        b['job_id']=job_id
                        customer_data.append(b)
                        print(customer_data,"customer_data-----------------")
                    else:
                        b['Customer_name'] = xero_customer_data[i]['ContactName']
                        b['Xero'] = 0
                        b['QBO'] = 0
                        b['job_id']=job_id
                        customer_data.append(b)
                        print(customer_data,"customer_data-----------------")
                    

            
        if len(customer_data) > 0:
            print("Data Inserted to xero_report_customer table")
            final_report_cust_summary.insert_many(customer_data)

        step_name = "Reading data from xero customer Report"
        write_task_execution_step(task_id, status=1, step=step_name)

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)


def get_report_supplier_summary(job_id, task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        dbname = get_mongodb_database()
        final_report_supp_summary = dbname['xero_AP_till_end_date']
        payload, base_url, headers = get_settings_xero(job_id)

        xero_ar_supplier = dbname['xero_AP']
        A = xero_ar_supplier.find({"job_id": job_id})
        xero_supplier_data = []
        for q1 in A:
            xero_supplier_data.append(q1)
        qbo_supplier = dbname['QBO_Supplier']

        B = qbo_supplier.find({"job_id": job_id})
        qbo_supplier_data = []
        for q2 in B:
            qbo_supplier_data.append(q2)

        supplier_data = []
                
        for i in range(0, len(xero_supplier_data)):
            for j in range(0, len(qbo_supplier_data)):
                if xero_supplier_data[i]["ContactNaxero_report_supplierme"] == qbo_supplier_data[j]["Name"]:
                    b = {}
                    if 'ContactID' in xero_supplier_data[i]:
                        b['code'] = xero_supplier_data[i]['ContactID']
                        b['Customer_name'] = xero_supplier_data[i]['ContactName']
                        b['Xero'] = xero_supplier_data[i]['xero_balance']
                        b['QBO'] = qbo_supplier_data[j]["Balance"]
                        b['job_id']=job_id
                        supplier_data.append(b)
                        print(supplier_data,"supp data -------------")
                    else:
                        b['Customer_name'] = xero_supplier_data[i]['ContactName']
                        b['Xero'] = 0
                        b['QBO'] = 0
                        b['job_id']=job_id
                        supplier_data.append(b)
        
        if len(supplier_data) > 0:
            print("data Inserted in table xero_report_supplier")
            final_report_supp_summary.insert_many(supplier_data)

        step_name = "Reading data from xero customer Report"
        write_task_execution_step(task_id, status=1, step=step_name)

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
