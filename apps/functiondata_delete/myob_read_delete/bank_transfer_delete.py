import traceback
from ast import Break
import asyncio

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import delete_data_in_myob

def delete_bank_transfer(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)
        
        bank_transfer1 =dbname["bank_transfer"]
        
        x = bank_transfer1.find({"job_id":job_id})
        myob_bank_transfer = []
        for k in x:
            myob_bank_transfer.append(k)

        arr=[]
        for i in range(0,len(myob_bank_transfer)):
            Queryset1={}
            Queryset1["UID"]=myob_bank_transfer[i]['UID']
            Queryset1["_id"]=myob_bank_transfer[i]['_id']
            Queryset1["task_id"]=myob_bank_transfer[i]['task_id']
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
            url = f"{base_url}/Banking/TransferMoneyTxn/{UID_data}"
            asyncio.run(delete_data_in_myob(url, headers, payload,dbname["bank_transfer"],_id, task_id, id_or_name_value_for_error))

            
    except Exception as ex:
        traceback.print_exc()
        