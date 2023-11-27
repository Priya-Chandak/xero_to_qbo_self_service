from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import *
from apps.home.models import Jobs, JobExecutionStatus
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from apps.util.qbo_util import post_data_in_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
import logging
logger = logging.getLogger(__name__)



def add_xero_negative_spend_money_as_receive_money(job_id,task_id):
    try:
        logger.info(
            "Started executing xero -> qbowriter -> add_spend_money -> add_xero_negative_spend_money_as_receive_money")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        deposit_url = "{}/deposit?minorversion=14".format(base_url)
        
        xero_spend_money1 = db['xero_spend_money']
        
        x1 = xero_spend_money1.find()
        received_money1 = []
        for q in x1:
            received_money1.append(q)

        deposit_url = f"{base_url}/deposit?minorversion={minorversion}"

        QBO_COA1 = db['QBO_COA'].find()
        QBO_COA = []
        for k2 in range(0, db['QBO_COA'].count_documents({'job_id':job_id})):
            QBO_COA.append(QBO_COA1[k2])

        QBO_Supplier1 = db['QBO_Supplier'].find()
        QBO_Supplier = []
        for k3 in range(0, db['QBO_Supplier'].count_documents({'job_id':job_id})):
            QBO_Supplier.append(QBO_Supplier1[k3])

        QBO_Customer1 = db['QBO_Customer'].find()
        QBO_Customer = []
        for m in range(0, db['QBO_Customer'].count_documents({'job_id':job_id})):
            QBO_Customer.append(QBO_Customer1[m])

        QBO_Class1 = db['QBO_Class'].find()
        QBO_Class = []
        for n in range(0, db['QBO_Class'].count_documents({'job_id':job_id})):
            QBO_Class.append(QBO_Class1[n])

        QBO_tax = []
        QBO_tax1 = db['QBO_Tax'].find()
        for p in range(0, db['QBO_Tax'].count_documents({'job_id':job_id})):
            QBO_tax.append(QBO_tax1[p])
        
        XERO_COA = db['xero_coa'].find()
        xero_coa1 = []
        for p7 in XERO_COA:
            xero_coa1.append(p7)

        # m1=[]
        # for m in range(0,len(received_money1)):
        #     # if multiple_invoice[m]['LineAmountTypes']=="Exclusive":
        #     if received_money1[m]['SubTotal'] == -742.21:
        #         m1.append(received_money1[m])
        
        # QuerySet = m1
        
        QuerySet = received_money1
        for i in range(0, len(QuerySet)):
            if QuerySet[i]['TotalAmount']<0:
                a11=db["QBO_COA"].find({"FullyQualifiedName": QuerySet[i]["BankAccountName"].strip(),'job_id':job_id})
                for x3 in a11:
                    if x3.get("AccountType") != "Credit Card":
                        if len(QuerySet[i]['Line']) >= 1 and QuerySet[i]['Line'] != [{}]:
                            _id = QuerySet[i]['_id']
                            task_id = QuerySet[i]['task_id']
                        
                            QuerySet1 = {'Line': []}
                            QuerySet9 = {'TaxLine': []}
                            for j in range(0, len(QuerySet[i]['Line'])):
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
                                    if QuerySet[i]['Line'][j]['TaxType'] in ['NONE',None,'BASEXCLUDED']:
                                        if 'taxrate_name' in QBO_tax[j4]:
                                            if "NOTAXS" in QBO_tax[j4]['taxrate_name']:
                                                QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                taxrate = QBO_tax[j4]['Rate']
                                                taxrate1 = taxrate
                                                QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                    elif QuerySet[i]['Line'][j]['TaxType'] in ["OUTPUT",'CAPEXINPUT','INPUT','INPUT2']:
                                        if 'taxrate_name' in QBO_tax[j4]:
                                            if "GST (sales)" in QBO_tax[j4]['taxrate_name']:
                                                QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                taxrate = QBO_tax[j4]['Rate']
                                                taxrate1 = taxrate
                                                QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                    elif QuerySet[i]['Line'][j]['TaxType'] in ['EXEMPTOUTPUT','INPUTTAXED','EXEMPTCAPITAL','EXEMPTEXPENSES','EXEMPTEXPORT','GSTONCAPIMPORTS','GSTONIMPORTS']:
                                        if 'taxrate_name' in QBO_tax[j4]:
                                            if "GST free (sales)" in QBO_tax[j4]['taxrate_name']:
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

                                QuerySet1['TxnTaxDetail'] = QuerySet9
                                QuerySet9['TotalTax'] = QuerySet[i]['TotalTax']

                                QuerySet10['DetailType'] = "TaxLineDetail"
                                QuerySet10['TaxLineDetail'] = QuerySet11
                                QuerySet11['PercentBased'] = True
                                QuerySet11['TaxPercent'] = taxrate1
                                QuerySet11['NetAmountTaxable'] = abs(round(
                                    (QuerySet[i]['Line'][j]['LineAmount'])/(100+taxrate1)*100, 2))
                                QuerySet11['TaxRateRef'] = QuerySet12
                                if taxrate1 != 0:
                                    QuerySet10['Amount'] = abs(round(
                                        (QuerySet11['NetAmountTaxable'])/taxrate1, 2))
                                else:
                                    QuerySet10['Amount'] = 0
                                QuerySet9['TaxLine'].append(QuerySet10)
                                
                                
                                a1=db["QBO_COA"].find({"FullyQualifiedName": QuerySet[i]['BankAccountName'],'job_id':job_id})
                                for x in a1:
                                    QuerySet2["value"] = x.get("Id")
                                    QuerySet2["name"] = x.get("Name")

                                QuerySet1['DepositToAccountRef'] = QuerySet2

                                # for j1 in range(0,len(QBO_COA)):
                                #     for j11 in range(0,len(xero_coa1)):
                                #         if QuerySet[i]['BankAccountID'] == xero_coa1[j11]['AccountID']:
                                #             if xero_coa1[j11]['Name'].lower().strip() == QBO_COA[j1]['Name'].lower().strip():
                                #                 QuerySet2['name'] = QBO_COA[j1]['Name']
                                #                 QuerySet2['value'] = QBO_COA[j1]['Id']  
                                #             elif QBO_COA[j1]['Name'].startswith(xero_coa1[j11]['Name']) and QBO_COA[j1]['Name'].endswith(xero_coa1[j11]['Code']):
                                #                 QuerySet2['name'] = QBO_COA[j1]['Name']
                                #                 QuerySet2['value'] = QBO_COA[j1]['Id']

                                # QuerySet1['PrivateNote'] = QuerySet[i]['notes']

                                QuerySet1['TxnDate'] = QuerySet[i]['Date']
                                QuerySet3['Amount'] = abs(round(
                                    (QuerySet[i]['Line'][j]['LineAmount'])/(100+taxrate1)*100, 2))


                                if 'Description' in QuerySet[i]['Line'][j]:
                                    if QuerySet[i]['Line'][0]['Description'] != None:
                                        QuerySet3['Description'] = QuerySet[i]['Line'][j]['Description']
                                    else:
                                        QuerySet3['Description'] = 'NA'

                                QuerySet3['DetailType'] = "DepositLineDetail"
                                QuerySet3['DepositLineDetail'] = QuerySet4

                                # QuerySet4['ClassRef'] = QuerySet7
                                # for j2 in range(0, len(QBO_Class)):
                                #     if QuerySet[i]['Line'][j]['job'] != None:
                                #         if QuerySet[i]['Line'][j]['job'] == QBO_Class[j2]['Name']:
                                #             QuerySet7['value'] = QBO_Class[j2]['Id']
                                #             QuerySet7['name'] = QBO_Class[j2]['Name']

                                
                                
                                for j31 in range(0, len(QBO_Customer)):
                                    if QBO_Customer[j31]["DisplayName"].startswith(QuerySet[i]["ContactName"]) and QBO_Customer[j31]["DisplayName"].endswith(" - C"):
                                        QuerySet7["value"] = QBO_Customer[j31]['Id']
                                        QuerySet7['name'] = QBO_Customer[j31]['DisplayName']
                                        QuerySet7['type'] = 'CUSTOMER'
                                    elif QuerySet[i]["ContactName"].lower().strip() == QBO_Customer[j31]["DisplayName"].lower().strip():
                                        QuerySet7["value"] = QBO_Customer[j31]['Id']
                                        QuerySet7['name'] = QBO_Customer[j31]["DisplayName"]
                                        QuerySet7['type'] = 'CUSTOMER'

                                
                                for j3 in range(0, len(QBO_Supplier)):
                                    if QBO_Supplier[j3]["DisplayName"].startswith(QuerySet[i]["ContactName"]) and QBO_Supplier[j3]["DisplayName"].endswith(" - S"):
                                        QuerySet6["value"] = QBO_Supplier[j3]['Id']
                                        QuerySet6['name'] = QBO_Supplier[j3]['DisplayName']
                                        QuerySet6['type'] = 'VENDOR'
                                    elif QuerySet[i]["ContactName"] == QBO_Supplier[j3]["DisplayName"]:
                                        QuerySet6["value"] = QBO_Supplier[j3]['Id']
                                        QuerySet6['name'] = QBO_Supplier[j3]["DisplayName"]
                                        QuerySet6['type'] = 'VENDOR'
                                    

                                QuerySet4['AccountRef'] = QuerySet5

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


                                if QuerySet[i]['Reference']!= None and QuerySet[i]['Reference']!="":
                                    QuerySet4['CheckNum'] = QuerySet[i]['Reference'][0:21]
                                else:
                                    QuerySet4['CheckNum'] = QuerySet[i]['Type']+"-"+QuerySet[i]['BankTransactionID'][-6:]

                                QuerySet4['TaxApplicableOn'] = "Sales"
                                QuerySet1['Line'].append(QuerySet3)

                            payload = json.dumps(QuerySet1)
                            print(payload)
                            id_or_name_value_for_error = (
                            str(QuerySet[i]["Date"])+"-"+str(QuerySet[i]["TotalAmount"])+"-"+str(QuerySet[i]["ContactName"])
                            )

                            receive_money_date = QuerySet[i]['Date'][0:10]
                            receive_money_date1 = datetime.strptime(receive_money_date, '%Y-%m-%d')
                            if (start_date1 != '' and end_date1 != ''):
                                if (receive_money_date1 >= start_date1) and (receive_money_date1 <= end_date1):
                                    post_data_in_qbo(deposit_url, headers, payload,xero_spend_money1,_id, job_id,task_id, id_or_name_value_for_error)
                                    
                                else:
                                    print("No Receive Money Transaction Within these dates")

                            else:
                                post_data_in_qbo(deposit_url, headers, payload,xero_spend_money1,_id, job_id,task_id, id_or_name_value_for_error)
                            
    except Exception as ex:
        logger.error(
            "Error in xero -> qbowriter -> add_negative_spend_money -> add_xero_negative_spend_money_as_receive_money", ex)
        

def add_xero_spend_money_as_credit_card_credit(job_id,task_id):
    try:
        logger.info(
            "Started executing xero -> qbowriter -> add_spend_money -> add_xero_spend_money_as_credit_card_credit")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        purchase_url = f"{base_url}/purchase?minorversion={minorversion}"

        spend_money_data = db["xero_spend_money"]
        spend_money = spend_money_data.find({"job_id": job_id})

        qbo_coa_data = db["QBO_COA"]
        qbo_coa = qbo_coa_data.find({"job_id": job_id})

        xero_coa_data = db["xero_coa"]
        xero_coa = xero_coa_data.find({"job_id": job_id})

        supplier_data = db["QBO_Supplier"]
        suppliers = supplier_data.find({"job_id": job_id})

        customer_data = db["QBO_Customer"]
        customers = customer_data.find({"job_id": job_id})

        qbo_class_data = db["QBO_Class"]
        qbo_class = qbo_class_data.find({"job_id": job_id})

        qbo_tax_data = db["QBO_Tax"]
        qbo_tax = qbo_tax_data.find({"job_id": job_id})

        
        for transaction in spend_money:
            if transaction["TotalAmount"] < 0:
                a11=db["QBO_COA"].find({"FullyQualifiedName": transaction.get("BankAccountName").strip(),'job_id':job_id})
                for x3 in a11:
                    if x3.get("AccountType") == "Credit Card":
                        _id= transaction.get('_id')
                        task_id = transaction.get('task_id')
                        line_items = transaction.get("Line")
                        QuerySet1 = {"Line": []}
                        if transaction.get("Reference")!= None:
                            QuerySet1['DocNumber'] = transaction.get("Reference")[0:20] 
                        for line_item in line_items:
                            QuerySet1["TotalAmt"] = abs(transaction.get("TotalAmount"))
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            QuerySet6 = {}
                            QuerySet7 = {}
                            QuerySet8 = {}
                            QuerySet91 = {}
                            QuerySet92 = {}

                            a1=db["QBO_COA"].find({"FullyQualifiedName": transaction.get("BankAccountName").strip(),'job_id':job_id})
                            for x in a1:
                                QuerySet2["value"] = x.get("Id")
                                QuerySet2["name"] = x.get("Name")

                            QuerySet1["AccountRef"] = QuerySet2
                            
                            taxrate1 = 0
                            if line_item.get("TaxType") == "BASEXCLUDED" or line_item.get("TaxType") == None or line_item.get("TaxType") == "NONE":
                                t1=db["QBO_Tax"].find({"taxrate_name": "NOTAXS",'job_id':job_id})
                                for x in t1:
                                    QuerySet8["value"] = x.get("taxcode_id")
                                    taxrate = x.get("Rate")
                                    taxrate1 = taxrate

                            elif (line_item.get("TaxType") == "OUTPUT" 
                                or line_item.get("TaxType") == "INPUT"
                                or line_item.get("TaxType") == "CAPEXINPUT"):
                                
                                t1=db["QBO_Tax"].find({"taxrate_name": "GST (purchases)",'job_id':job_id})
                                for x in t1:
                                    QuerySet8["value"] = x.get("taxcode_id")
                                    taxrate = x.get("Rate")
                                    taxrate1 = taxrate

                                
                            elif (
                                line_item.get("TaxType") == "EXEMPTCAPITAL"
                                or line_item.get("TaxType") == "EXEMPTEXPENSES"
                                or line_item.get("TaxType") == "EXEMPTEXPORT"
                                or line_item.get("TaxType") == "EXEMPTOUTPUT"
                                or line_item.get("TaxType") == "GSTONCAPIMPORTS"
                                or line_item.get("TaxType") == "GSTONIMPORTS"
                                or line_item.get("TaxType") == "INPUTTAXED"

                            ):
                                t1=db["QBO_Tax"].find({"taxrate_name": "GST-free (purchases)",'job_id':job_id})
                                for x in t1:
                                    QuerySet8["value"] = x.get("taxcode_id")
                                    taxrate = x.get("Rate")
                                    taxrate1 = taxrate
                            
                            # QuerySet1['PrivateNote'] = transaction['memo']

                            if transaction["LineAmountTypes"] == "Inclusive":
                                QuerySet1["GlobalTaxCalculation"] = "TaxInclusive"
                                QuerySet1["PaymentType"] = "CreditCard"
                                QuerySet1["Credit"] = True

                                QuerySet4['TaxCodeRef'] = QuerySet8
                                QuerySet4["TaxInclusiveAmt"] = abs(round(
                                        (line_item.get("LineAmount"))
                                        * (100 + taxrate1)
                                        / 100,
                                        2,
                                    ))
                                
                                QuerySet3["Amount"] = abs(round(
                                        (line_item.get("LineAmount"))
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    ))
                                

                            elif (
                                transaction["LineAmountTypes"] == "NoTax"
                                or transaction["LineAmountTypes"] == "Exclusive"
                            ):
                                QuerySet1["GlobalTaxCalculation"] = "TaxExcluded"
                                QuerySet1["PaymentType"] = "CreditCard"
                                QuerySet1["Credit"] = True

                                QuerySet4["TaxInclusiveAmt"] = abs(
                                    round(line_item.get("LineAmount"))
                                )
                                QuerySet3["Amount"] =abs(round(line_item.get("LineAmount"), 2))
                                
                                QuerySet4['TaxCodeRef'] = QuerySet8

                            QuerySet1["PaymentType"] = "CreditCard"
                            QuerySet1["TxnDate"] = transaction.get("Date")

                            QuerySet3["Description"] = line_item.get("Description")

                            QuerySet3["DetailType"] = "AccountBasedExpenseLineDetail"
                            QuerySet3["AccountBasedExpenseLineDetail"] = QuerySet4

                            c1=db["QBO_Class"].find({"Name": line_item.get("job"),'job_id':job_id})
                            for c in c1:
                                QuerySet7['value'] = c.get('Id')
                                QuerySet7['name'] = c.get('Name')

                            a1=db["QBO_COA"].find({"AcctNum": line_item.get("AccountCode"),'job_id':job_id})
                            for x in a1:
                                QuerySet5["value"] = x.get("Id")
                                QuerySet5["name"] = x.get("Name")
                            
                            QuerySet4["AccountRef"] = QuerySet5

                                
                            s1 = db["QBO_Supplier"].find({"DisplayName": transaction.get("ContactName"),'job_id':job_id})
                            # s2 = db["QBO_Supplier"].find({"DisplayName": transaction.get("ContactName")})
                            s2 = db["QBO_Supplier"].find({"DisplayName": {'$regex': '- S$','$regex': f'^{transaction.get("ContactName")}'},'job_id':job_id})
                            
                            for x1 in s1:
                                QuerySet91["value"] = x1.get("Id")
                                QuerySet91["name"] = x1.get("DisplayName")
                                break
                                
                            for x2 in s2:
                                QuerySet92["value"] = x2.get("Id")
                                QuerySet92["name"] = x2.get("DisplayName")
                                break

                            QuerySet1["EntityRef"] = QuerySet91 if QuerySet91 != {} else QuerySet92
                            QuerySet1["Line"].append(QuerySet3)
                        
                        # if transaction["BankTransactionID"] in ['72a2719c-b5ce-41f8-b1f1-c0b41aa82de5','1637b9a3-6974-40d1-b3b3-6d89dc894faa','68e0bf43-9f16-4042-b5c9-c888375aba08','aafe9632-0073-45f9-896e-b2647642cb83','e6de5cde-6de6-4e62-96eb-585f9429b91f','940c03ad-d799-409b-a04a-65e1d6197a34','f53abed2-0975-4c43-89a9-ab9dfc25af54','c4903136-5f13-4289-b34c-a81d59ce0774','3ef36371-d398-446e-a539-d8f51dc72f67','7602d5a3-59f6-4b2d-a8f5-960ac01ad35b','9bd97658-cccb-4c3c-8e2d-ee2ad160ee57','a8e43d91-4f74-4bb6-9301-79a7c7db3516','23f19997-ed4a-4367-9d41-6730ca6b3a6f','88b21f8c-a5f4-4782-871b-49e4cb358dfc']:
                        spend_money_date = transaction["Date"][0:10]
                        spend_money_date1 = datetime.strptime(spend_money_date, "%Y-%m-%d")
                        payload = json.dumps(QuerySet1)
                        print(payload)
                        id_or_name_value_for_error = (
                        str(transaction.get("Date"))+"-"+str(transaction.get("TotalAmount"))+"-"+str(transaction.get("ContactName"))
                        )

                        if start_date1 is not None and end_date1 is not None:
                            if (spend_money_date1 >= start_date1) and (
                                spend_money_date1 <= end_date1
                            ):
                                post_data_in_qbo(purchase_url, headers, payload,db["xero_spend_money"],_id, job_id,task_id, id_or_name_value_for_error)
                        else:
                            post_data_in_qbo(purchase_url, headers, payload,db["xero_spend_money"],_id, job_id,task_id, id_or_name_value_for_error)
                        
                                    
    except Exception as ex:
        logger.error(
            "Error in xero -> qbowriter  -> add_xero_spend_money_as_credit_card_credit", ex)
