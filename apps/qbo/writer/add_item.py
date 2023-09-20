import json
import requests
from math import expm1
from apps.mmc_settings.all_settings import *
from apps.home.data_util import add_job_status
from apps.home.models import Jobs, JobExecutionStatus
from pymongo import MongoClient
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
import logging
from datetime import date
import traceback

logger = logging.getLogger(__name__)


def add_duplicate_item(job_id,task_id):
    
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)
        dbname=get_mongodb_database()
        url = f"{base_url}/item?minorversion={minorversion}"

        qbo_coa1 = dbname['QBO_COA'].find({'job_id':job_id})
        qbo_coa = []
        for p21 in qbo_coa1:
            qbo_coa.append(p21)

        
        item = db["item"]
        Collection = db["duplicate_item"]
        x = item.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        a = data

        b = []
        for i in range(0, len(a)):
            b.append(a[i]["Name"])

        a1 = {i: b.count(i) for i in b}
        
        b = []
        for i in a1.keys():
            if a1[i] > 1:
                b.append(i)
        print(b)
        
        c1 = []

        for j in range(0, len(b)):
            for i in range(0, len(a)):
                
                e = {}
                if b[j] == a[i]["Name"]:
                    e["Name"] = a[i]["Name"] + "-" + a[i]["Number"]
                    e["Sku"] = a[i]["Number"]
                    e["Description"] = a[i]["Description"]
                    e["PurchaseDesc"] = a[i]["Description"]
                    e["PurchaseCost"] = a[i]["AverageCost"]
                    e["UnitPrice"] = a[i]["BaseSellingPrice"]

                    for j1 in range(0, len(qbo_coa)):
                        QuerySet3={}
                        QuerySet4={}
                        QuerySet5={}
                        print(a[i]['IncomeAccount'])
                        if a[i]['IncomeAccount'] != None:
                            if 'AcctNum' in qbo_coa[j1]:
                                if a[i]['IncomeAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                    QuerySet3["value"] = qbo_coa[j1]['Id']
                                    QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                                    break
                            elif a[i]['IncomeAccount']['Name'].lower().strip() == qbo_coa[j1]['FullyQualifiedName'].lower().strip():
                                QuerySet3["value"] = qbo_coa[j1]['Id']
                                QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break
                            elif (qbo_coa[j1]['FullyQualifiedName'].startswith(a[i]['IncomeAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(QuerySet[i]['IncomeAccount']['DisplayID'])):
                                QuerySet3["value"] = qbo_coa[j1]['Id']
                                QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break
                            # elif qbo_coa[j1]['FullyQualifiedName'] == 'Sales':
                            #     QuerySet3["value"] = qbo_coa[j1]['Id']
                            #     QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        else:
                            if qbo_coa[j1]['FullyQualifiedName'] == 'Sales':
                                QuerySet3["value"] = qbo_coa[j1]['Id']
                                QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break

                        
                        if a[i]['ExpenseAccount'] != None:
                            if 'AcctNum' in qbo_coa[j1]:
                                if a[i]['ExpenseAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                    QuerySet4["value"] = qbo_coa[j1]['Id']
                                    QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                                    break
                            elif a[i]['ExpenseAccount']['Name'].lower().strip() == qbo_coa[j1]['FullyQualifiedName'].lower().strip():
                                QuerySet4["value"] = qbo_coa[j1]['Id']
                                QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break
                            elif (qbo_coa[j1]['FullyQualifiedName'].startswith(a[i]['ExpenseAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(a[i]['ExpenseAccount']['DisplayID'])):
                                QuerySet4["value"] = qbo_coa[j1]['Id']
                                QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break
                            # elif qbo_coa[j1]['FullyQualifiedName'] == 'Purchases':
                            #     QuerySet4["value"] = qbo_coa[j1]['Id']
                            #     QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                        else:
                            if qbo_coa[j1]['FullyQualifiedName'] == 'Purchases':
                                QuerySet4["value"] = qbo_coa[j1]['Id']
                                QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break
                                
                        if a[i]['AssetAccount'] != None:
                            if 'AcctNum' in qbo_coa[j1]:
                                if a[i]['AssetAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                    QuerySet5["value"] = qbo_coa[j1]['Id']
                                    QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                                    break
                            elif a[i]['AssetAccount']['Name'] == qbo_coa[j1]['FullyQualifiedName']:
                                QuerySet5["value"] = qbo_coa[j1]['Id']
                                QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break
                            elif (qbo_coa[j1]['FullyQualifiedName'].startswith(a[i]['AssetAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(a[i]['AssetAccount']['DisplayID'])):
                                QuerySet5["value"] = qbo_coa[j1]['Id']
                                QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                                break
                        
                            
                        e["IncomeAccountRef"] = QuerySet3
                        e["ExpenseAccountRef"] = QuerySet4
                        e["AssetAccountRef"] = QuerySet5

                    if a[i]["TrackQtyOnHand"] == True:
                        e["Type"] = "NonInventory"
                    else:
                        e["Type"] = "Service"

                    e["TrackQtyOnHand"] = a[i]["TrackQtyOnHand"]
                    e["QtyOnHand"] = a[i]["Quantity_On_Hand"]
                    e["InvStartDate"] = a[i]["LastModified"]
                    


                        
                    c1.append(e)
        
        db["duplicate_item"].insert_many(c1)

        duplicate_coa = db["duplicate_item"]
        x = duplicate_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        QuerySet1 = data
        
    except Exception as ex:
        traceback.print_exc()

def add_item(job_id,task_id):
    try:
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)
        dbname=get_mongodb_database()
        Collection = dbname['item']
        income_acc1 = dbname['QBO_income_acc']
        expense_acc1 = dbname['QBO_expense_acc']
        asset_acc1 = dbname['QBO_asset_acc']

        x = Collection.find({'job_id':job_id})
        data1 = []
        for p1 in x:
            data1.append(p1)
        
        # b1=[]
        # for d1 in range(0,len(data1)):
        #     if data1[d1]['Name'] in ['SHELL ULTRA PRO','SUBLET LABOUR TO REPAIR PUNCTU']:
        #         b1.append(data1[d1])

        qbo_coa1 = dbname['QBO_COA'].find({'job_id':job_id})
        qbo_coa = []
        for p21 in qbo_coa1:
            qbo_coa.append(p21)

        
        income_acc1 = dbname['QBO_income_acc'].find({'job_id':job_id})
        income_acc = []
        for p2 in income_acc1:
            income_acc.append(p2)

        expense_acc1 = dbname['QBO_expense_acc'].find({'job_id':job_id})
        expense_acc = []
        for p3 in expense_acc1:
            expense_acc.append(p3)

        asset_acc1 = dbname['QBO_asset_acc'].find({'job_id':job_id})
        asset_acc = []
        for p4 in asset_acc1:
            asset_acc.append(p4)

        #API = item
        url = f"{base_url}/item?minorversion={minorversion}"

        QuerySet = data1
        
        for i in range(0, len(QuerySet)):
            _id=QuerySet[i]['_id']
            task_id=QuerySet[i]['task_id']
            QuerySet1 = {}
            QuerySet3 = {}
            QuerySet4 = {}
            QuerySet5 = {}
            QuerySet1["Name"] = QuerySet[i]["Name"].replace(":","-")
            QuerySet1["Description"] = QuerySet[i]["Description"]
            QuerySet1["PurchaseDesc"] = QuerySet[i]["Description"]
            QuerySet1["PurchaseCost"] = QuerySet[i]["AverageCost"]
            QuerySet1["UnitPrice"] = QuerySet[i]["BaseSellingPrice"]
            QuerySet1["Sku"] = QuerySet[i]["Number"]

            if QuerySet[i]["TrackQtyOnHand"] == True:
                for j1 in range(0, len(qbo_coa)):
                    
                    if QuerySet[i]['IncomeAccount'] != None:
                        if 'AcctNum' in qbo_coa[j1]:
                            if QuerySet[i]['IncomeAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                QuerySet3["value"] = qbo_coa[j1]['Id']
                                QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif QuerySet[i]['IncomeAccount']['Name'].lower().strip() == qbo_coa[j1]['FullyQualifiedName'].lower().strip():
                            QuerySet3["value"] = qbo_coa[j1]['Id']
                            QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif (qbo_coa[j1]['FullyQualifiedName'].startswith(QuerySet[i]['IncomeAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(QuerySet[i]['IncomeAccount']['DisplayID'])):
                            QuerySet3["value"] = qbo_coa[j1]['Id']
                            QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        # elif qbo_coa[j1]['FullyQualifiedName'] == 'Sales':
                        #     QuerySet3["value"] = qbo_coa[j1]['Id']
                        #     QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                    else:
                        if qbo_coa[j1]['FullyQualifiedName'] == 'Sales':
                            QuerySet3["value"] = qbo_coa[j1]['Id']
                            QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']

                    
                    if QuerySet[i]['ExpenseAccount'] != None:
                        if 'AcctNum' in qbo_coa[j1]:
                            if QuerySet[i]['ExpenseAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                QuerySet4["value"] = qbo_coa[j1]['Id']
                                QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                            
                        elif QuerySet[i]['ExpenseAccount']['Name'].lower().strip() == qbo_coa[j1]['FullyQualifiedName'].lower().strip():
                            QuerySet4["value"] = qbo_coa[j1]['Id']
                            QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif (qbo_coa[j1]['FullyQualifiedName'].startswith(QuerySet[i]['ExpenseAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(QuerySet[i]['ExpenseAccount']['DisplayID'])):
                            QuerySet4["value"] = qbo_coa[j1]['Id']
                            QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                        # elif qbo_coa[j1]['FullyQualifiedName'] == 'Purchases':
                        #     QuerySet4["value"] = qbo_coa[j1]['Id']
                        #     QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                    else:
                        if qbo_coa[j1]['FullyQualifiedName'] == 'Purchases':
                            QuerySet4["value"] = qbo_coa[j1]['Id']
                            QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                            
                    if QuerySet[i]['AssetAccount'] != None:
                        if 'AcctNum' in qbo_coa[j1]:
                            if QuerySet[i]['AssetAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                QuerySet5["value"] = qbo_coa[j1]['Id']
                                QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif QuerySet[i]['AssetAccount']['Name'] == qbo_coa[j1]['FullyQualifiedName']:
                            QuerySet5["value"] = qbo_coa[j1]['Id']
                            QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif (qbo_coa[j1]['FullyQualifiedName'].startswith(QuerySet[i]['AssetAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(QuerySet[i]['AssetAccount']['DisplayID'])):
                            QuerySet5["value"] = qbo_coa[j1]['Id']
                            QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                        else:
                            pass

                QuerySet1["Type"] = "NonInventory"
                QuerySet1["TrackQtyOnHand"] = QuerySet[i]["TrackQtyOnHand"]
                QuerySet1["QtyOnHand"] = QuerySet[i]["Quantity_On_Hand"]
                QuerySet1["InvStartDate"] = QuerySet[i]["LastModified"]

            else:
                for j1 in range(0, len(qbo_coa)):
                    
                    if QuerySet[i]['IncomeAccount'] != None:
                        if QuerySet[i]['IncomeAccount']['Name'].lower().strip() == qbo_coa[j1]['FullyQualifiedName'].lower().strip():
                            QuerySet3["value"] = qbo_coa[j1]['Id']
                            QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif 'AcctNum' in qbo_coa[j1]:
                            if QuerySet[i]['IncomeAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                QuerySet3["value"] = qbo_coa[j1]['Id']
                                QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif (qbo_coa[j1]['FullyQualifiedName'].startswith(QuerySet[i]['IncomeAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(QuerySet[i]['IncomeAccount']['DisplayID'])):
                            QuerySet3["value"] = qbo_coa[j1]['Id']
                            QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        # elif qbo_coa[j1]['FullyQualifiedName'] == 'Sales':
                        #     print("last elif")
                        #     QuerySet3["value"] = qbo_coa[j1]['Id']
                        #     QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']
                        
                    else:
                        if qbo_coa[j1]['FullyQualifiedName'] == 'Sales':
                            QuerySet3["value"] = qbo_coa[j1]['Id']
                            QuerySet3["name"] = qbo_coa[j1]['FullyQualifiedName']

                    
                    if QuerySet[i]['ExpenseAccount'] != None:
                        if 'AcctNum' in qbo_coa[j1]:
                            if QuerySet[i]['ExpenseAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                QuerySet4["value"] = qbo_coa[j1]['Id']
                                QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                            
                        elif QuerySet[i]['ExpenseAccount']['Name'].lower().strip() == qbo_coa[j1]['FullyQualifiedName'].lower().strip():
                            QuerySet4["value"] = qbo_coa[j1]['Id']
                            QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif (qbo_coa[j1]['FullyQualifiedName'].startswith(QuerySet[i]['ExpenseAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(QuerySet[i]['ExpenseAccount']['DisplayID'])):
                            QuerySet4["value"] = qbo_coa[j1]['Id']
                            QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                        # elif qbo_coa[j1]['FullyQualifiedName'] == 'Purchases':
                        #     QuerySet4["value"] = qbo_coa[j1]['Id']
                        #     QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                    else:
                        if qbo_coa[j1]['FullyQualifiedName'] == 'Purchases':
                            QuerySet4["value"] = qbo_coa[j1]['Id']
                            QuerySet4["name"] = qbo_coa[j1]['FullyQualifiedName']
                    
                    if QuerySet[i]['AssetAccount'] != None:
                        if 'AcctNum' in qbo_coa[j1]:
                        
                            if QuerySet[i]['AssetAccount']['DisplayID'] == qbo_coa[j1]['AcctNum']:
                                QuerySet5["value"] = qbo_coa[j1]['Id']
                                QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                            
                        elif QuerySet[i]['AssetAccount']['Name'].strip().lower() == qbo_coa[j1]['FullyQualifiedName'].strip().lower():
                            QuerySet5["value"] = qbo_coa[j1]['Id']
                            QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                        elif (qbo_coa[j1]['FullyQualifiedName'].startswith(QuerySet[i]['AssetAccount']['Name'])) and (qbo_coa[j1]['FullyQualifiedName'].endswith(QuerySet[i]['AssetAccount']['DisplayID'])):
                            QuerySet5["value"] = qbo_coa[j1]['Id']
                            QuerySet5["name"] = qbo_coa[j1]['FullyQualifiedName']
                        else:
                            pass
                
                            
            QuerySet1["Type"] = "Service"

            QuerySet1["IncomeAccountRef"] = QuerySet3
            QuerySet1["ExpenseAccountRef"] = QuerySet4
            QuerySet1["AssetAccountRef"] = QuerySet5

            payload = json.dumps(QuerySet1)
            
            post_data_in_qbo(url, headers, payload,Collection,_id,job_id,task_id, QuerySet[i]["Name"])
            
                
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)