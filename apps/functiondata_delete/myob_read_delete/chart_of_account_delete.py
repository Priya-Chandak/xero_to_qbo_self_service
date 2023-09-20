import traceback
from ast import Break
import asyncio

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import delete_data_in_myob

def delete_chart_of_account(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)
        
        chart_of_accounts = dbname["chart_of_account"]
        
        x = chart_of_accounts.find({"job_id":job_id})
        myob_coa = []
        for k in x:
            myob_coa.append(k)

        arr=[]
        for i in range(0,len(myob_coa)):
            Queryset1={}
            Queryset1["UID"]=myob_coa[i]['UID']
            Queryset1["_id"]=myob_coa[i]['_id']
            Queryset1["task_id"]=myob_coa[i]['task_id']
            arr.append(Queryset1)
            


        for f in range(0,len(arr)):
            _id = arr[f]["_id"]
            task_id = arr[f]["task_id"]
            payload ={}

            UID_data=arr[f]["UID"]
            
            id_or_name_value_for_error = (
                arr[f]['UID']
                if arr[f]['UID'] is not None
                else arr[f]['UID'])

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/GeneralLedger/Account/{UID_data}"
            asyncio.run(delete_data_in_myob(url, headers, payload,dbname["chart_of_account"],_id, task_id, id_or_name_value_for_error))

            
    except Exception as ex:
        traceback.print_exc()
        