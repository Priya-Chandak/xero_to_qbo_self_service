from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.home.models import Jobs, JobExecutionStatus
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from apps.util.qbo_util import post_data_in_qbo



def add_xero_negative_received_money(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')
        
        base_url, headers, company_id, minorversion,get_data_header,report_headers = get_settings_qbo(job_id)
        myclient = MongoClient("mongodb://localhost:27017/")
        db = myclient["MMC"]
        
        spend_money1 = []
        for q in db['xero_receive_money'].find({'job_id':job_id}):
            spend_money1.append(q)


        QuerySet = spend_money1

        # m1=[]
        # for m in range(0,len(spend_money1)):
        #     # if multiple_invoice[m]['LineAmountTypes']=="Exclusive":
        #     if spend_money1[m]['SubTotal'] == -742.21:
        #         m1.append(spend_money1[m])
        
        # QuerySet = m1

        purchase_url = f"{base_url}/purchase?minorversion={minorversion}"
        
        QBO_COA1 = db['QBO_COA'].find({'job_id':job_id})
        QBO_COA = []
        for k2 in range(0,db['QBO_COA'].count_documents({'job_id':job_id})):
            QBO_COA.append(QBO_COA1[k2])

        QBO_Supplier1 = db['QBO_Supplier'].find({'job_id':job_id})
        QBO_Supplier = []
        for k3 in range(0,db['QBO_Supplier'].count_documents({'job_id':job_id})):
            QBO_Supplier.append(QBO_Supplier1[k3])

        QBO_Customer1 = db['QBO_Customer'].find({'job_id':job_id})
        QBO_Customer = []
        for m in range(0,db['QBO_Customer'].count_documents({'job_id':job_id})):
            QBO_Customer.append(QBO_Customer1[m])

        QBO_Class1 = db['QBO_Class'].find({'job_id':job_id})
        QBO_Class = []
        for n in range(0,db['QBO_Class'].count_documents({'job_id':job_id})):
            QBO_Class.append(QBO_Class1[n])

        QBO_Tax = []
        QBO_tax1 = db['QBO_Tax'].find({'job_id':job_id})
        for p in range(0,db['QBO_Tax'].count_documents({'job_id':job_id})):
            QBO_Tax.append(QBO_tax1[p])
        
        XERO_COA = db['xero_coa'].find({'job_id':job_id})
        xero_coa1 = []
        for p7 in XERO_COA:
            xero_coa1.append(p7)

        for i in range(0, len(QuerySet)):
            if QuerySet[i]['TotalAmount']<0:
                print(i)
                _id = QuerySet[i]['_id']
                task_id = QuerySet[i]['task_id']
                    
                if len(QuerySet[i]['Line']) >= 1:
                    QuerySet1 = {'Line': []}
                    for j in range(0, len(QuerySet[i]['Line'])):

                        QuerySet1['TotalAmt'] = abs(QuerySet[i]['TotalAmount'])
                        QuerySet2 = {}
                        QuerySet3 = {}
                        QuerySet4 = {}
                        QuerySet5 = {}
                        QuerySet6 = {}
                        QuerySet7 = {}
                        QuerySet8 = {}
                        QuerySet9 = {}

                        QuerySet1['AccountRef'] = QuerySet2

                        for j1 in range(0, len(QBO_COA)):
                            if QuerySet[i]['BankAccountName'].lower().strip() == QBO_COA[j1]["FullyQualifiedName"].lower().strip():
                                QuerySet2['name'] = QBO_COA[j1]['Name']
                                QuerySet2['value'] = QBO_COA[j1]['Id']
                    
                        QuerySet4['TaxCodeRef'] = QuerySet8

                        taxrate1 = 0
                        if 'TaxType' in QuerySet[i]['Line'][j]:
                            for j4 in range(0, len(QBO_Tax)):
                                if QuerySet[i]['Line'][j]['TaxType'] == "BASEXCLUDED" or QuerySet[i]['Line'][j]['TaxType'] == None or QuerySet[i]['Line'][j]['TaxType'] == "NONE": 
                                    if 'taxrate_name' in QBO_Tax[j4]:
                                        if "NOTAXS" in QBO_Tax[j4]['taxrate_name']:
                                            QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                            taxrate = QBO_Tax[j4]['Rate']
                                            taxrate1 = taxrate

                                elif QuerySet[i]['Line'][j]['TaxType'] == "OUTPUT":
                                    if 'taxrate_name' in QBO_Tax[j4]:
                                        if "GST (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                            QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                            taxrate = QBO_Tax[j4]['Rate']
                                            taxrate1 = taxrate

                                elif QuerySet[i]['Line'][j]['TaxType'] in ['INPUTTAXED','EXEMPTCAPITAL','EXEMPTEXPENSES','EXEMPTEXPORT'] :
                                    if 'taxrate_name' in QBO_Tax[j4]:
                                        if "GST-free (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                            QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                            taxrate = QBO_Tax[j4]['Rate']
                                            taxrate1 = taxrate
                                        
                                elif QuerySet[i]['Line'][j]['TaxType'] == "EXEMPTOUTPUT":
                                    if 'taxrate_name' in QBO_Tax[j4]:
                                        if "GST-free (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                            QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                            taxrate = QBO_Tax[j4]['Rate']
                                            taxrate1 = taxrate
                                            
                                elif QuerySet[i]['Line'][j]['TaxType'] == "CAPEXINPUT" or QuerySet[i]['Line'][j]['TaxType'] == "INPUT" :
                                    if 'taxrate_name' in QBO_Tax[j4]:
                                        if "GST (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                            QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                            taxrate = QBO_Tax[j4]['Rate']
                                            taxrate1 = taxrate
                                            
                                elif QuerySet[i]['Line'][j]['TaxType'] == "GSTONCAPIMPORTS" or QuerySet[i]['Line'][j]['TaxType'] == "GSTONIMPORTS" :
                                    if 'taxrate_name' in QBO_Tax[j4]:
                                        if "GST-free (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                            QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                            taxrate = QBO_Tax[j4]['Rate']
                                            taxrate1 = taxrate
                                            
                                elif QuerySet[i]['Line'][j]['TaxType'] == QBO_Tax[j4]['taxcode_name']:
                                    QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                    taxrate = QBO_Tax[j4]['Rate']
                                    taxrate1 = taxrate

                                    
                        # QuerySet1['PrivateNote'] = QuerySet[i]['memo']

                        if QuerySet[i]['LineAmountTypes'] == 'Inclusive':
                            QuerySet1['GlobalTaxCalculation'] = "TaxInclusive"
                            QuerySet4['TaxInclusiveAmt'] = abs(round((QuerySet[i]['Line'][j]['LineAmount'])*(100+taxrate1)/100, 2))
                            QuerySet3['Amount'] = abs(round((QuerySet[i]['Line'][j]['LineAmount'])/(100+taxrate1)*100,2))
                            
                        elif QuerySet[i]['LineAmountTypes'] == 'NoTax' or QuerySet[i]['LineAmountTypes'] == 'Exclusive':
                            QuerySet1['GlobalTaxCalculation'] = "TaxExcluded"
                            QuerySet4['TaxInclusiveAmt'] = abs(round(QuerySet[i]['Line'][j]['LineAmount']))
                            QuerySet3['Amount'] = abs(round(QuerySet[i]['Line'][j]['LineAmount'],2))
                            

                        
                        QuerySet1['PaymentType'] = "Cash"
                        QuerySet1['TxnDate'] = QuerySet[i]['Date']

                        if 'Description' in QuerySet[i]['Line'][j]:
                            QuerySet3['Description'] = QuerySet[i]['Line'][j]['Description']

                        QuerySet3['DetailType'] = "AccountBasedExpenseLineDetail"
                        QuerySet3['AccountBasedExpenseLineDetail'] = QuerySet4

                        for j2 in range(0, len(QBO_Class)):
                            if 'job' in QuerySet[i]['Line'][j] and QuerySet[i]['Line'][j]['job'] != None:
                                if QuerySet[i]['Line'][j]['job'] == QBO_Class[j2]['Name']:
                                    QuerySet7['value'] = QBO_Class[j2]['Id']
                                    QuerySet7['name'] = QBO_Class[j2]['Name']

                        QuerySet4['ClassRef'] = QuerySet7
                        
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


                        QuerySet4['AccountRef'] = QuerySet5
                        QuerySet1['EntityRef'] = QuerySet9
                        
                        for k1 in range(0, len(QBO_Supplier)):
                            if QBO_Supplier[k1]["DisplayName"].startswith(QuerySet[i]["ContactName"]) and QBO_Supplier[k1]["DisplayName"].endswith(" - S"):
                                QuerySet9["value"] = QBO_Supplier[k1]["Id"]
                                QuerySet9['name'] = QBO_Supplier[k1]["DisplayName"]
                            elif QuerySet[i]["ContactName"] == QBO_Supplier[k1]["DisplayName"]:
                                QuerySet9["value"] = QBO_Supplier[k1]["Id"]
                                QuerySet9['name'] = QBO_Supplier[k1]["DisplayName"]
                        
                        QuerySet1['Line'].append(QuerySet3)

                    payload = json.dumps(QuerySet1)
                    spend_money_date = QuerySet[i]['Date'][0:10]
                    spend_money_date1 = datetime.strptime(spend_money_date, '%Y-%m-%d')
                    if (start_date != '' and end_date != ''):
                        if (spend_money_date1 >= start_date1) and (spend_money_date1 <= end_date1):
                            post_data_in_qbo(purchase_url, headers, payload,db["xero_receive_money"],_id, job_id,task_id, QuerySet[i]["BankTransactionID"])
                    
                        else:
                            print("No Spend Money Transaction Within these dates")
                    else:
                        post_data_in_qbo(purchase_url, headers, payload,db["xero_receive_money"],_id, job_id,task_id, QuerySet[i]["BankTransactionID"])
                    
                    
                
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)
        