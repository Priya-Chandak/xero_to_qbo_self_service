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


def get_qbo_taxcode(job_id,task_id):
    try:
        myclient = MongoClient("mongodb://localhost:27017/")
        db1 = myclient["MMC"]
        QBO_Taxcode = db1['QBO_Taxcode']
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db1['QBO_Taxcode'].count_documents({'job_id':job_id})

        payload = f"select * from taxcode startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['QueryResponse']['TaxCode']
        
        taxcode=[]
        for tax_data in JsonResponse1:
            tax_data['job_id']=job_id
            tax_data['task_id']=task_id
            tax_data['error']=None
            tax_data['is_pushed']=0
            tax_data['table_name']="QBO_Taxcode"

            taxcode.append(tax_data)
        
        QBO_Taxcode.insert_many(taxcode)

        if JsonResponse['QueryResponse']['maxResults'] < 1000:
            Break
        else:
            get_qbo_taxcode(job_id)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


def get_qbo_taxrate(job_id):
    try:
        myclient = MongoClient("mongodb://localhost:27017/")
        db1= myclient["MMC"]
        QBO_Taxrate = db1['QBO_Taxrate']
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/query?minorversion={minorversion}"
        no_of_records = db1['QBO_Taxrate'].count_documents({})

        payload = f"select * from taxrate startposition {no_of_records} maxresults 1000"

        response = requests.request("POST", url, headers=get_data_header, data=payload)
        JsonResponse = response.json()
        JsonResponse1 = JsonResponse['QueryResponse']['TaxRate']

        arr = []
        for i in range(0, len(JsonResponse1)):
            QuerySet = {}

            QuerySet['Name'] = JsonResponse1[i]['Name']
            QuerySet['Description'] = JsonResponse1[i]['Description']
            QuerySet['Id'] = JsonResponse1[i]['Id']
            QuerySet['SpecialTaxType'] = JsonResponse1[i]['SpecialTaxType']

            if "RateValue" in JsonResponse1[i]:
                QuerySet['Rate'] = JsonResponse1[i]['RateValue']
            else:
                QuerySet['Rate'] = None

            arr.append(QuerySet)

        QBO_Taxrate.insert_many(arr)

        if JsonResponse['QueryResponse']['maxResults'] < 1000:
            Break
        else:
            get_qbo_taxrate(job_id)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


def get_qbo_tax(job_id):
    try:
        myclient = MongoClient("mongodb://localhost:27017/")
        db = myclient["MMC"]
        QBO_Tax = db['QBO_Tax']

        Collection1 = db['QBO_Taxrate']
        Collection2 = db['QBO_Taxcode']

        qbo_taxrate1 = Collection1.find({"job_id": job_id})
        QBO_taxrate = []
        for p1 in qbo_taxrate1:
            QBO_taxrate.append(p1)

        qbo_taxcode1 = Collection2.find({"job_id": job_id})
        QBO_taxcode = []
        for p2 in qbo_taxcode1:
            QBO_taxcode.append(p2)

        arr = []
        for i in range(0,len(QBO_taxcode)):
            QuerySet = {}
            QuerySet1 = {}
            QuerySet['taxcode_id'] = QBO_taxcode[i]['Id']
            QuerySet['taxcode_name'] = QBO_taxcode[i]['Name']
            
            if QBO_taxcode[i]['SalesTaxRateList'] != {'TaxRateDetail': []}:
                QuerySet['taxrate_id'] = QBO_taxcode[i]['SalesTaxRateList']['TaxRateDetail'][0]['TaxRateRef']['value']
                QuerySet['taxrate_name'] = QBO_taxcode[i]['SalesTaxRateList']['TaxRateDetail'][0]['TaxRateRef']['name']
                
                for j in range(0,len(QBO_taxrate)):
                    
                    if QuerySet['taxrate_name'] == QBO_taxrate[j]['Name']:
                        QuerySet1 = QBO_taxrate[j]['Rate']
                    QuerySet['Rate']=QuerySet1
        
                arr.append(QuerySet)
       
        for i1 in range(0,len(QBO_taxcode)):
            QuerySet = {}
            QuerySet1 = {}
            QuerySet['taxcode_id'] = QBO_taxcode[i1]['Id']
            QuerySet['taxcode_name'] = QBO_taxcode[i1]['Name']
            
            if QBO_taxcode[i1]['PurchaseTaxRateList'] != {'TaxRateDetail': []}:
                QuerySet['taxrate_id'] = QBO_taxcode[i1]['PurchaseTaxRateList']['TaxRateDetail'][0]['TaxRateRef']['value']
                QuerySet['taxrate_name'] = QBO_taxcode[i1]['PurchaseTaxRateList']['TaxRateDetail'][0]['TaxRateRef']['name']
                
                for j1 in range(0,len(QBO_taxrate)):
                    
                    if QuerySet['taxrate_name'] == QBO_taxrate[j1]['Name']:
                        QuerySet1 = QBO_taxrate[j1]['Rate']
                
                    QuerySet['Rate']=QuerySet1
            
                arr.append(QuerySet)
            
            else:
                pass
     

        QBO_Tax.insert_many(arr)


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)