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
from apps.mmc_settings.all_settings import get_settings_qbo

from apps.home.data_util import add_job_status
from pymongo import MongoClient


def get_qbo_archived_vendor(job_id,task_id):
    try:
        myclient = MongoClient("mongodb://localhost:27017/")
        db1 = myclient["MMC"]
        QBO_ARCHIVED_VENDOR1 = db1['QBO_ARCHIVED_VENDOR']
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db1['QBO_ARCHIVED_VENDOR'].count_documents({'job_id':job_id})

        payload = f"select * from vendor where Active=false startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['QueryResponse']['Vendor']
        
        archivedvendor=[]
        for archived_vendor in JsonResponse1:
            archived_vendor['job_id']=job_id
            archived_vendor['task_id']=task_id
            archived_vendor['error']=None
            archived_vendor['is_pushed']=0
            archived_vendor['table_name']="QBO_ARCHIVED_COA"

            archivedvendor.append(archived_vendor)
        
        QBO_ARCHIVED_VENDOR1.insert_many(archivedvendor)

        if JsonResponse['QueryResponse']['maxResults'] < 1000:
            Break
        else:
            get_qbo_archived_vendor(job_id)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


