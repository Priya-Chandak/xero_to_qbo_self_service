from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import *
from pymongo import MongoClient
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo

from datetime import datetime, timedelta, timezone


def add_xero_receive_money(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')
        
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        deposit_url = "{}/deposit?minorversion=14".format(base_url)
        
        xero_receive_money1 = db["xero_receive_money"]
        xero_receive_money = []
        for p2 in db["xero_receive_money"].find({"job_id":job_id}):
            xero_receive_money.append(p2)
        
        # new=[]
        # for exp in range(0,len(xero_receive_money)):
        #     if xero_receive_money[exp]['BankTransactionID'] in ['f39b15b1-b2f1-4a3d-83c5-9c587fc2b23a']:
        #         new.append(xero_receive_money[exp])

        QBO_COA1 = db["QBO_COA"].find({"job_id":job_id})
        QBO_COA = []
        for p2 in QBO_COA1:
            QBO_COA.append(p2)

        QBO_Supplier1 = db["QBO_Supplier"].find({"job_id":job_id})
        QBO_Supplier = []
        for p2 in QBO_Supplier1:
            QBO_Supplier.append(p2)

        QBO_Customer1 = db["QBO_Customer"].find({"job_id":job_id})
        QBO_Customer = []
        for p2 in QBO_Customer1:
            QBO_Customer.append(p2)

        QBO_Class1 = db["QBO_Class"].find({"job_id":job_id})
        QBO_Class = []
        for p2 in QBO_Class1:
            QBO_Class.append(p2)

        QBO_tax = []
        QBO_tax1 = db["QBO_Tax"].find({"job_id": job_id})
        for p2 in QBO_tax1:
            QBO_tax.append(p2)
        
        xero_coa = db["xero_coa"].find({"job_id":job_id})
        xero_coa1 = []
        for p2 in xero_coa:
            xero_coa1.append(p2)
        
        QuerySet = xero_receive_money
        # QuerySet = new
       
        for i in range(0, len(QuerySet)):
            for m1 in range(0,len(xero_coa1)):
                if QuerySet[i]['BankAccountID'] ==  xero_coa1[m1]['AccountID']:
                    if xero_coa1[m1]['BankAccountType'] != 'CREDITCARD':
                        if len(QuerySet[i]['Line']) >= 1 and QuerySet[i]['Line'] != [{}]:
                            _id = QuerySet[i]['_id']
                            task_id = QuerySet[i]['task_id']
                            QuerySet1 = {'Line': []}
                            QuerySet9 = {'TaxLine': []}
                            for j in range(0, len(QuerySet[i]['Line'])):
                                if 'AccountCode' in QuerySet[i]['Line'][j]: 
                                
                                    QuerySet2 = {}
                                    QuerySet3 = {}
                                    QuerySet4 = {}
                                    QuerySet5 = {}
                                    QuerySet6 = {}
                                    QuerySet7 = {}
                                    QuerySet8 = {}

                                    QuerySet10 = {}
                                    QuerySet11 = {}
                                    QuerySet12 = {}

                                    taxrate1 = 0
                                    for j4 in range(0, len(QBO_tax)):
                                        if QuerySet[i]['Line'][j]['TaxType'] in ["NONE","BASEXCLUDED","TAX001",None] :
                                            if 'taxrate_name' in QBO_tax[j4]:
                                                if "NOTAXS" in QBO_tax[j4]['taxrate_name']:
                                                    QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                    taxrate = QBO_tax[j4]['Rate']
                                                    taxrate1 = taxrate
                                                    QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                        elif QuerySet[i]['Line'][j]['TaxType'] in ["EXEMPTCAPITAL","EXEMPTEXPENSES","EXEMPTEXPORT","EXEMPTOUTPUT","GSTONCAPIMPORTS","GSTONIMPORTS","INPUTTAXED"] :
                                            if 'taxrate_name' in QBO_tax[j4]:
                                                if "GST free (sales)" in QBO_tax[j4]['taxrate_name']:
                                                    QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                    taxrate = QBO_tax[j4]['Rate']
                                                    taxrate1 = taxrate
                                                    QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                        elif QuerySet[i]['Line'][j]['TaxType'] in ["CAPEXINPUT","INPUT","OUTPUT","INPUT2"]:
                                            if 'taxrate_name' in QBO_tax[j4]:
                                                if "GST (sales)" in QBO_tax[j4]['taxrate_name']:
                                                    QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                    taxrate = QBO_tax[j4]['Rate']
                                                    taxrate1 = taxrate
                                                    QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                        elif QuerySet[i]['Line'][j]['TaxType'] == QBO_tax[j4]['taxcode_name']:
                                            QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                            taxrate = QBO_tax[j4]['Rate']
                                            taxrate1 = taxrate
                                            QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                    QuerySet4['TaxCodeRef'] = QuerySet8

                                    # QuerySet1['TxnTaxDetail'] = QuerySet9
                                    QuerySet9['TotalTax'] = QuerySet[i]['TotalTax']

                                    QuerySet10['DetailType'] = "TaxLineDetail"
                                    QuerySet10['TaxLineDetail'] = QuerySet11
                                    QuerySet11['PercentBased'] = True
                                    QuerySet11['TaxPercent'] = taxrate1
                                    QuerySet11['NetAmountTaxable'] = round(
                                        (QuerySet[i]['Line'][j]['LineAmount'])/(100+taxrate1)*100, 2)
                                    QuerySet11['TaxRateRef'] = QuerySet12
                                    if taxrate1 != 0:
                                        QuerySet10['Amount'] = round(
                                            (QuerySet11['NetAmountTaxable'])/taxrate1, 2)
                                    else:
                                        QuerySet10['Amount'] = 0
                                    QuerySet9['TaxLine'].append(QuerySet10)
                                    
                                    
                                    for j1 in range(0,len(QBO_COA)):
                                        for j11 in range(0,len(xero_coa1)):
                                            if QuerySet[i]['BankAccountID'] == xero_coa1[j11]['AccountID']:
                                                if xero_coa1[j11]['Name'].lower().strip() == QBO_COA[j1]['Name'].lower().strip():
                                                    QuerySet2['name'] = QBO_COA[j1]['Name']
                                                    QuerySet2['value'] = QBO_COA[j1]['Id']  
                                                    break
                                                elif xero_coa1[j11]['Code'] not in ["",None]:
                                                    if QBO_COA[j1]['Name'].startswith(xero_coa1[j11]['Name']) and QBO_COA[j1]['Name'].endswith(xero_coa1[j11]['Code']):
                                                        QuerySet2['name'] = QBO_COA[j1]['Name']
                                                        QuerySet2['value'] = QBO_COA[j1]['Id']
                                                        break
                                                
                                            elif QuerySet[i]['BankAccountName'].replace(":","-") == QBO_COA[j1]['Name']:
                                                QuerySet2['name'] = QBO_COA[j1]['Name']
                                                QuerySet2['value'] = QBO_COA[j1]['Id']  
                                                break
                                            elif QuerySet[i]['BankAccountName'].lower().strip() == QBO_COA[j1]['Name'].lower().strip():
                                                QuerySet2['name'] = QBO_COA[j1]['Name']
                                                QuerySet2['value'] = QBO_COA[j1]['Id']  
                                                break
                                            
                                    QuerySet1['DepositToAccountRef'] = QuerySet2

                                    # QuerySet1['PrivateNote'] = QuerySet[i]['notes']

                                    QuerySet1['TxnDate'] = QuerySet[i]['Date']
                                    if QuerySet[i]['LineAmountTypes'] == 'Inclusive':
                                        QuerySet3['Amount'] = round(
                                            (QuerySet[i]['Line'][j]['LineAmount'])/(100+taxrate1)*100, 2)
                                    else:
                                        QuerySet3['Amount'] = QuerySet[i]['Line'][j]['LineAmount']


                                    if 'Description' in QuerySet[i]['Line'][j]:
                                        if QuerySet[i]['Line'][j]['Description'] != None:
                                            QuerySet3['Description'] = QuerySet[i]['Line'][j]['Description']
                                        else:
                                            QuerySet3['Description'] = 'NA'

                                    QuerySet3['DetailType'] = "DepositLineDetail"
                                    QuerySet3['DepositLineDetail'] = QuerySet4

                                    QuerySet4['ClassRef'] = QuerySet7
                                    if 'TrackingName' in QuerySet[i]['Line'][j]:
                                        for j2 in range(0, len(QBO_Class)):
                                            if QuerySet[i]['Line'][j]['TrackingName'] != None:
                                                if QuerySet[i]['Line'][j]['TrackingName'] == QBO_Class[j2]['Name']:
                                                    QuerySet7['value'] = QBO_Class[j2]['Id']
                                                    QuerySet7['name'] = QBO_Class[j2]['Name']
                                                    break

                                    
                                    
                                    for j31 in range(0, len(QBO_Customer)):
                                        if QBO_Customer[j31]["FullyQualifiedName"].startswith(QuerySet[i]["ContactName"]) and QBO_Customer[j31]["DisplayName"].endswith(" - C"):
                                            QuerySet7["value"] = QBO_Customer[j31]['Id']
                                            QuerySet7['name'] = QBO_Customer[j31]['FullyQualifiedName']
                                            QuerySet7['type'] = 'CUSTOMER'
                                            break
                                        elif QuerySet[i]["ContactName"].lower().strip() == QBO_Customer[j31]["FullyQualifiedName"].lower().strip():
                                            QuerySet7["value"] = QBO_Customer[j31]['Id']
                                            QuerySet7['name'] = QBO_Customer[j31]["FullyQualifiedName"]
                                            QuerySet7['type'] = 'CUSTOMER'
                                            break

                                    
                                    for j3 in range(0, len(QBO_Supplier)):
                                        if QBO_Supplier[j3]["DisplayName"].startswith(QuerySet[i]["ContactName"]) and QBO_Supplier[j3]["DisplayName"].endswith(" - S"):
                                            QuerySet6["value"] = QBO_Supplier[j3]['Id']
                                            QuerySet6['name'] = QBO_Supplier[j3]['DisplayName']
                                            QuerySet6['type'] = 'VENDOR'
                                            break
                                        elif QuerySet[i]["ContactName"] == QBO_Supplier[j3]["DisplayName"]:
                                            QuerySet6["value"] = QBO_Supplier[j3]['Id']
                                            QuerySet6['name'] = QBO_Supplier[j3]["DisplayName"]
                                            QuerySet6['type'] = 'VENDOR'
                                            break
                                        

                                    
                                    if QuerySet6 != {} :
                                        QuerySet4['Entity'] = QuerySet6
                                    elif QuerySet7 != {} :
                                        QuerySet4['Entity'] = QuerySet7


                                    for j3 in range(0, len(QBO_COA)):
                                        for j31 in range(0, len(xero_coa1)):
                                            if 'Code' in xero_coa1[j31]:
                                                if QuerySet[i]['Line'][j]['AccountCode'] == xero_coa1[j31]["Code"]:
                                                    if xero_coa1[j31]["Name"].lower().strip()== QBO_COA[j3]['Name'].lower().strip():
                                                        QuerySet5['value'] = QBO_COA[j3]["Id"]
                                                        QuerySet5['name'] = QBO_COA[j3]["Name"]
                                                    elif QBO_COA[j3]['Name'].startswith(xero_coa1[j31]["Name"]) and QBO_COA[j3]['Name'].endswith(xero_coa1[j31]["Code"]):
                                                        QuerySet5['value'] = QBO_COA[j3]["Id"]
                                                        QuerySet5['name'] = QBO_COA[j3]["Name"]
                                                    elif QBO_COA[j3]['Name'].endswith(xero_coa1[j31]["Code"]):
                                                        QuerySet5['value'] = QBO_COA[j3]["Id"]
                                                        QuerySet5['name'] = QBO_COA[j3]["Name"]
                                                elif 'AcctNum' in QBO_COA[j3]:
                                                    if QuerySet[i]['Line'][j]['AccountCode'] == QBO_COA[j3]['AcctNum']:
                                                        QuerySet5['value'] = QBO_COA[j3]["Id"]
                                                        QuerySet5['name'] = QBO_COA[j3]["Name"]
                                                    elif str(QuerySet[i]['Line'][j]['AccountCode']).lower() == str(QBO_COA[j3]['AcctNum']).lower():
                                                        QuerySet5['value'] = QBO_COA[j3]["Id"]
                                                        QuerySet5['name'] = QBO_COA[j3]["Name"]
                                    
                                

                                    if QuerySet[i]['Reference']!= None and QuerySet[i]['Reference']!="":
                                        QuerySet4['CheckNum'] = QuerySet[i]['Reference'][0:21]
                                    else:
                                        QuerySet4['CheckNum'] = QuerySet[i]['Type']+"-"+QuerySet[i]['BankTransactionID'][-6:]

                                    QuerySet4['AccountRef'] = QuerySet5
                                    QuerySet4['TaxApplicableOn'] = "Sales"
                                    QuerySet1['Line'].append(QuerySet3)

                            payload = json.dumps(QuerySet1)
                            print(payload)
                            
                            if QuerySet[i]['TotalAmount']>=0:
                                receive_money_date = QuerySet[i]['Date'][0:10]
                                receive_money_date1 = datetime.strptime(receive_money_date, '%Y-%m-%d')
                                if (start_date != '' and end_date != ''):
                                    if (receive_money_date1 >= start_date1) and (receive_money_date1 <= end_date1):
                                        post_data_in_qbo(deposit_url, headers, payload,xero_receive_money1,_id, job_id,task_id, QuerySet[i]['BankTransactionID'])
                                        
                                    else:
                                        print("No Receive Money Transaction Within these dates")

                                else:
                                    post_data_in_qbo(deposit_url, headers, payload,xero_receive_money1,_id, job_id,task_id, QuerySet[i]['BankTransactionID'])
                                    
                
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        
        print(ex)