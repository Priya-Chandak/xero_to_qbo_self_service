from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
from datetime import datetime, timedelta, timezone


def add_negative_spend_money(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')
        
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        deposit_url = "{}/deposit?minorversion=14".format(base_url)
        C1 = db['myob_spend_money']
        
        received_money_data = C1.find({'job_id':job_id})
        received_money1 = []
        for q in received_money_data:
            received_money1.append(q)

        deposit_url = f"{base_url}/deposit?minorversion={minorversion}"

        QBO_COA1 = db['QBO_COA'].find({'job_id':job_id})
        QBO_COA = []
        for k2 in range(0, db['QBO_COA'].count_documents({'job_id':job_id})):
            QBO_COA.append(QBO_COA1[k2])

        QBO_Supplier1 = db['QBO_Supplier'].find({'job_id':job_id})
        QBO_Supplier = []
        for k3 in range(0, db['QBO_Supplier'].count_documents({'job_id':job_id})):
            QBO_Supplier.append(QBO_Supplier1[k3])

        QBO_Customer1 = db['QBO_Customer'].find({'job_id':job_id})
        QBO_Customer = []
        for m in range(0, db['QBO_Customer'].count_documents({'job_id':job_id})):
            QBO_Customer.append(QBO_Customer1[m])

        QBO_Class1 = db['QBO_Class'].find({'job_id':job_id})
        QBO_Class = []
        for n in range(0, db['QBO_Class'].count_documents({'job_id':job_id})):
            QBO_Class.append(QBO_Class1[n])

        Myob_Job = db['job'].find({'job_id':job_id})
        Myob_Job1 = []
        for n1 in range(0,db['job'].count_documents({'job_id':job_id})):
            Myob_Job1.append(Myob_Job[n1])

        QBO_tax = []
        QBO_tax1 = db['QBO_Tax'].find({'job_id':job_id})
        for p in range(0, db['QBO_Tax'].count_documents({'job_id':job_id})):
            QBO_tax.append(QBO_tax1[p])

        
        QuerySet = received_money1
        
        for i in range(0, len(QuerySet)):
            _id=QuerySet[i]['_id']
            task_id=QuerySet[i]['task_id']
            
            if QuerySet[i]['Total_Amount']<0 and QuerySet[i]['UID'] in ['a571928a-34e8-4678-916a-1a34a2cd94e2','8060821b-43af-43cc-8473-7ede5c68cb11']:
                print(i)
                            
                for j11 in range(0, len(QBO_COA)):
                    if QuerySet[i]['pay_from'].lower().strip() == QBO_COA[j11]['Name'].lower().strip():
                        print(QBO_COA[j11]['AccountType'])
                        if QBO_COA[j11]['AccountType'] != 'Credit Card':
                            if len(QuerySet[i]['Lines']) >= 1 and QuerySet[i]['Lines'] != [{}]:
                                QuerySet1 = {'Line': []}
                                QuerySet9 = {'TaxLine': []}
                                for j in range(0, len(QuerySet[i]['Lines'])):
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
                                        if QuerySet[i]['Lines'][j]['taxcode'] == "GST":
                                            if 'taxrate_name' in QBO_tax[j4]:
                                                if 'GST (sales)' in QBO_tax[j4]['taxrate_name']:
                                                    QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                    taxrate = QBO_tax[j4]['Rate']
                                                    taxrate1 = taxrate
                                                    QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                        elif QuerySet[i]['Lines'][j]['taxcode'] == "CAP":
                                            if 'taxrate_name' in QBO_tax[j4]:
                                                if 'GST (sales)' in QBO_tax[j4]['taxrate_name']:
                                                    QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                    taxrate = QBO_tax[j4]['Rate']
                                                    taxrate1 = taxrate
                                                    QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                        elif (QuerySet[i]['Lines'][j]['taxcode'] == "FRE") or (QuerySet[i]['Lines'][j]['taxcode'] == "GNR"):
                                            if 'taxrate_name' in QBO_tax[j4]:
                                                if 'GST free (sales)' in QBO_tax[j4]['taxrate_name']:
                                                    QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                    taxrate = QBO_tax[j4]['Rate']
                                                    taxrate1 = taxrate
                                                    QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                        elif QuerySet[i]['Lines'][j]['taxcode'] == "N-T" or QuerySet[i]['Lines'][j]['taxcode'] == None :
                                            if 'taxrate_name' in QBO_tax[j4]:
                                                if 'NOTAXS' in QBO_tax[j4]['taxrate_name']:
                                                    QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                                    taxrate = QBO_tax[j4]['Rate']
                                                    taxrate1 = taxrate
                                                    QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                        elif QuerySet[i]['Lines'][j]['taxcode'] == QBO_tax[j4]['taxcode_name']:
                                            QuerySet8['value'] = QBO_tax[j4]['taxcode_id']
                                            taxrate = QBO_tax[j4]['Rate']
                                            taxrate1 = taxrate
                                            QuerySet12['value'] = QBO_tax[j4]['taxrate_id']

                                    QuerySet4['TaxCodeRef'] = QuerySet8

                                    QuerySet1['TxnTaxDetail'] = QuerySet9
                                    QuerySet9['TotalTax'] = QuerySet[i]['Total_Tax']

                                    QuerySet10['DetailType'] = "TaxLineDetail"
                                    QuerySet10['TaxLineDetail'] = QuerySet11
                                    QuerySet11['PercentBased'] = True
                                    QuerySet11['TaxPercent'] = taxrate1
                                    QuerySet11['NetAmountTaxable'] = round(
                                        abs(QuerySet[i]['Lines'][j]['line_amount'])/(100+taxrate1)*100, 2)
                                    QuerySet11['TaxRateRef'] = QuerySet12
                                    if taxrate1 != 0:
                                        QuerySet10['Amount'] = round(
                                            abs(QuerySet11['NetAmountTaxable'])/taxrate1, 2)
                                    else:
                                        QuerySet10['Amount'] = 0
                                    QuerySet9['TaxLine'].append(QuerySet10)
                                
                                    QuerySet1['DepositToAccountRef'] = QuerySet2

                                    for j1 in range(0, len(QBO_COA)):
                                        if QuerySet[i]['pay_from'].lower().strip() == QBO_COA[j1]['Name'].lower().strip():
                                            QuerySet2['name'] = QBO_COA[j1]['Name']
                                            QuerySet2['value'] = QBO_COA[j1]['Id']

                                    QuerySet1['PrivateNote'] = QuerySet[i]['memo']

                                    QuerySet1['TxnDate'] = QuerySet[i]['date']
                                    QuerySet3['Amount'] = round(
                                        abs(QuerySet[i]['Lines'][j]['line_amount'])/(100+taxrate1)*100, 2)

                                    if QuerySet[i]['Lines'][0]['memo'] != None:
                                        QuerySet3['Description'] = QuerySet[i]['Lines'][j]['memo']
                                    else:
                                        QuerySet3['Description'] = QuerySet[i]['memo']

                                    QuerySet3['DetailType'] = "DepositLineDetail"
                                    QuerySet3['DepositLineDetail'] = QuerySet4

                                    if QuerySet[i]['Lines'][j]['job'] != None:
                                        for j2 in range(0, len(QBO_Class)):
                                            for j4 in range(0,len(Myob_Job1)):
                                                if QuerySet[i]['Lines'][j]['job'] == Myob_Job1[j4]['Name']:
                                                    if (QBO_Class[j2]['FullyQualifiedName'].startswith(Myob_Job1[j4]['Name'])) and (QBO_Class[j2]['FullyQualifiedName'].endswith(Myob_Job1[j4]['Number'])):
                                                        QuerySet7['value'] = QBO_Class[j2]['Id']
                                                        QuerySet7['name'] = QBO_Class[j2]['Name']
                                    
                                    QuerySet4['ClassRef'] = QuerySet7
                                    
                                    QuerySet4['Entity'] = QuerySet6

                                    if (QuerySet[i]['contact_name'] != None and QuerySet[i]['contact_type'] == "Supplier"):
                                        for j3 in range(0, len(QBO_Customer)):
                                            if QuerySet[i]['contact_name'] == QBO_Customer[j3]['DisplayName']:
                                                QuerySet6['name'] = QBO_Customer[j3]['DisplayName']
                                                QuerySet6['value'] = QBO_Customer[j3]['Id']
                                    else:
                                        QuerySet6['name'] = None
                                        QuerySet6['value'] = None

                                    QuerySet4['AccountRef'] = QuerySet5

                                    for j3 in range(0, len(QBO_COA)):
                                        if (QBO_COA[j3]['Name'].startswith(QuerySet[i]['Lines'][j]['account_name'])) and (QBO_COA[j3]['Name'].endswith(QuerySet[i]['Lines'][j]['DisplayID'])):
                                            QuerySet5['name'] = QBO_COA[j3]['Name']
                                            QuerySet5['value'] = QBO_COA[j3]['Id']

                                        elif QuerySet[i]['Lines'][j]['account_name'].strip().lower() == QBO_COA[j3]['Name'].strip().lower():
                                            QuerySet5['name'] = QBO_COA[j3]['Name']
                                            QuerySet5['value'] = QBO_COA[j3]['Id']
                                        
                                        elif 'AcctNum' in QBO_COA[j3]:
                                            if QuerySet[i]['Lines'][j]['DisplayID'] == QBO_COA[j3]['AcctNum']:
                                                QuerySet5['name'] = QBO_COA[j3]['Name']
                                                QuerySet5['value'] = QBO_COA[j3]['Id']

                                    QuerySet4['CheckNum'] = QuerySet[i]['payment_no']
                                    QuerySet4['TaxApplicableOn'] = "Sales"
                                    QuerySet1['Line'].append(QuerySet3)

                                payload = json.dumps(QuerySet1)
                                
                                receive_money_date = QuerySet[i]['date'][0:10]
                                receive_money_date1 = datetime.strptime(receive_money_date, '%Y-%m-%d')
                                print(receive_money_date1)
                                if (start_date != '' and end_date != ''):
                                    if (receive_money_date1 >= start_date1) and (receive_money_date1 <= end_date1):
                                        post_data_in_qbo(deposit_url, headers, payload,db['myob_spend_money'],_id,job_id,task_id,QuerySet[i]['payment_no'])
                                    else:
                                        print("No Receive Money Transaction Within these dates")

                                else:
                                    post_data_in_qbo(deposit_url, headers, payload,db['myob_spend_money'],_id,job_id,task_id,QuerySet[i]['payment_no'])
                                    
                        else:
                            print("CRC")
                            print(QuerySet[i])
                             
                
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)