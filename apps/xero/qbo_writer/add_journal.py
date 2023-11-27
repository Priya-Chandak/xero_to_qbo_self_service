from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import *
from apps.home.models import Jobs, JobExecutionStatus
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from apps.util.qbo_util import post_data_in_qbo



def add_xero_journal(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        myclient = MongoClient("mongodb://localhost:27017/")
        db = myclient["MMC"]
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1=db['xero_manual_journal']
        
        journal = []
        for p1 in db['xero_manual_journal'].find({"job_id": job_id}):
            journal.append(p1)

        QBO_COA = db['QBO_COA'].find({"job_id": job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Class = db['QBO_Class'].find({"job_id": job_id})
        QBO_class = []
        for p3 in QBO_Class:
            QBO_class.append(p3)

        QBO_Tax = db['QBO_Tax'].find({"job_id": job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)
        
        Xero_COA = db['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        QuerySet1 = journal
        
        for i in range(0, len(QuerySet1)):
            try:
                journal_date = QuerySet1[i]["Date"]
                journal_date11 = int(journal_date[6:16])
                journal_date12 = datetime.utcfromtimestamp(journal_date11).strftime('%Y-%m-%d')
            except Exception as ex:
                print(ex)

            journal_date1 = datetime.strptime(journal_date12,'%Y-%m-%d')
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']
            
            QuerySet2 = {"Line": []}
            QuerySet10 = {'TaxLine': []}
            QuerySet2['DocNumber'] = "Journal-" + QuerySet1[i]["ManualJournalID"][-6:]
            QuerySet2['TxnDate'] = str(journal_date1)[0:10]
            
            a=[]
            b=[]

            sales_tax = 0
            purchase_tax = 0

            for j in range(0, len(QuerySet1[i]['Line'])):
                if 'TaxType' in QuerySet1[i]['Line'][j]:
                    if QuerySet1[i]['Line'][j]['LineAmount'] > 0:
                        a.append(QuerySet1[i]['Line'][j]['TaxType'])
                    else:
                        b.append(QuerySet1[i]['Line'][j]['TaxType'])
                        
                QuerySet3 = {}
                QuerySet4 = {}
                QuerySet5 = {}
                QuerySet6 = {}
                QuerySet7 = {}
                QuerySet8 = {}
                QuerySet9 = {}

                QuerySet11 = {}
                QuerySet12 = {}
                QuerySet13 = {}
                QuerySet14 = {}
                QuerySet15 = {}

                QuerySet2['TxnTaxDetail'] = QuerySet10
                # QuerySet2['DocNumber'] = QuerySet1[i]['Referrence_No']
                QuerySet2['PrivateNote'] = QuerySet1[i]['Narration']
                QuerySet11['DetailType'] = "TaxLineDetail"
                QuerySet11['TaxLineDetail'] = QuerySet12
                QuerySet12['TaxRateRef'] = QuerySet13
                QuerySet12['PercentBased'] = True
                QuerySet10['TaxLine'].append(QuerySet11)

                taxrate1 = 0

                sales = ['OUTPUT','EXEMPTEXPENSES','INPUTTAXED']
                purchase = ['EXEMPTOUTPUT','BASEXCLUDED',"INPUT","CAPEXINPUT","TAX001"]

                if QuerySet1[i]['Line'][j]['TaxType'] in sales:
                    QuerySet4['TaxApplicableOn'] = 'Sales'
                    QuerySet7['TaxApplicableOn'] = 'Sales'
                    
                elif QuerySet1[i]['Line'][j]['TaxType'] in purchase:
                    QuerySet4['TaxApplicableOn'] = 'Purchase'
                    QuerySet7['TaxApplicableOn'] = 'Purchase'
                    
                for j4 in range(0, len(QBO_tax)):
                    if 'TaxType' in QuerySet1[i]['Line'][j]:
                        if QuerySet1[i]['Line'][j]['TaxType'] == "BASEXCLUDED":
                            if 'taxrate_name' in QBO_tax[j4]:
                                if "NOTAXS" == QBO_tax[j4]['taxrate_name']:
                                    QuerySet13['value'] = QBO_tax[j4]['taxrate_id']
                                    QuerySet15['value'] = QBO_tax[j4]['taxcode_id']
                                    taxrate = QBO_tax[j4]['Rate']
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]['Rate']
                                    taxrate1 = taxrate
                            
                        elif QuerySet1[i]['Line'][j]['TaxType'] in ["INPUT","CAPEXINPUT","TAX001"]:
                            if 'taxrate_name' in QBO_tax[j4]:
                                if "GST (purchases)" in QBO_tax[j4]['taxrate_name']:
                                    QuerySet13['value'] = QBO_tax[j4]['taxrate_id']
                                    QuerySet15['value'] = QBO_tax[j4]['taxcode_id']
                                    taxrate = QBO_tax[j4]['Rate']
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]['Rate']
                                    taxrate1 = taxrate

                        elif QuerySet1[i]['Line'][j]['TaxType'] == "OUTPUT":
                            if QuerySet1[i]['Line'][j]['LineAmount'] > 0:
                                if 'taxrate_name' in QBO_tax[j4]:
                                    if 'GST (purchases)' in QBO_tax[j4]['taxrate_name']:
                                        QuerySet13['value'] = QBO_tax[j4]['taxrate_id']
                                        QuerySet15['value'] = QBO_tax[j4]['taxcode_id']
                                        taxrate = QBO_tax[j4]['Rate']
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]['Rate']
                                        taxrate1 = taxrate
                            else:
                                if 'taxrate_name' in QBO_tax[j4]:
                                    if 'GST (purchases)' == QBO_tax[j4]['taxrate_name']:
                                        QuerySet13['value'] = QBO_tax[j4]['taxrate_id']
                                        QuerySet15['value'] = QBO_tax[j4]['taxcode_id']
                                        taxrate = QBO_tax[j4]['Rate']
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]['Rate']
                                        taxrate1 = taxrate

                        elif QuerySet1[i]['Line'][j]['TaxType'] in ["EXEMPTEXPENSES","INPUTTAXED"]:
                            if 'taxrate_name' in QBO_tax[j4]:
                                if 'GST free (sales)' in QBO_tax[j4]['taxrate_name']:
                                    QuerySet13['value'] = QBO_tax[j4]['taxrate_id']
                                    QuerySet15['value'] = QBO_tax[j4]['taxcode_id']
                                    taxrate = QBO_tax[j4]['Rate']
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]['Rate']
                                    taxrate1 = taxrate

                        elif QuerySet1[i]['Line'][j]['TaxType'] == "EXEMPTOUTPUT" :
                            if 'taxrate_name' in QBO_tax[j4]:
                                if "GST (purchases)" in QBO_tax[j4]['taxrate_name']:
                                    QuerySet13['value'] = QBO_tax[j4]['taxrate_id']
                                    QuerySet15['value'] = QBO_tax[j4]['taxcode_id']
                                    taxrate = QBO_tax[j4]['Rate']
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]['Rate']
                                    taxrate1 = taxrate

                        elif QuerySet1[i]['Line'][j]['TaxType'] == QBO_tax[j4]['taxcode_name']:
                            QuerySet13['value'] = QBO_tax[j4]['taxrate_id']
                            QuerySet15['value'] = QBO_tax[j4]['taxcode_id']
                            taxrate = QBO_tax[j4]['Rate']
                            QuerySet12["TaxPercent"] = QBO_tax[j4]['Rate']
                            taxrate1 = taxrate

                if QuerySet1[i]['Line'][j]['LineAmount'] >= 0:
                    if QuerySet1[i]['LineAmountTypes'] == 'Inclusive':
                        QuerySet12['NetAmountTaxable'] = round(QuerySet1[i]['Line'][j]['LineAmount']/(100+taxrate1)*100,2)
                        QuerySet11['Amount'] = abs(QuerySet1[i]['Line'][j]['TaxAmount'])
                        QuerySet3['Amount'] = round(abs(QuerySet1[i]['Line'][j]['LineAmount']/(100+taxrate1)*100),2)
                    elif (QuerySet1[i]['LineAmountTypes'] == 'Exclusive') or (QuerySet1[i]['LineAmountTypes'] == 'NoTax'):
                        QuerySet12['NetAmountTaxable'] = round(QuerySet1[i]['Line'][j]['LineAmount'],2)
                        QuerySet11['Amount'] = abs(QuerySet1[i]['Line'][j]['TaxAmount'])
                        QuerySet3['Amount'] = abs(round(QuerySet1[i]['Line'][j]['LineAmount'],2))
        
                    if 'Description' in QuerySet1[i]['Line'][j]:
                        QuerySet3['Description'] = QuerySet1[i]['Line'][j]['Description']
                    QuerySet3['DetailType'] = 'JournalEntryLineDetail'
                    QuerySet4['PostingType'] = 'Debit'
                    QuerySet3['JournalEntryLineDetail'] = QuerySet4

                    # for k in range(0, len(QBO_coa)):
                    #     for k1 in range(0,len(xero_coa)):
                    #         if 'Code' in xero_coa[k1]:
                    #             if QuerySet1[i]['Line'][j]['AccountCode'] == xero_coa[k1]['Code']:
                    #                 if xero_coa[k1]['Name'] == QBO_coa[k]['Name']:
                    #                     QuerySet5['value'] = QBO_coa[k]["Id"]
                    #                     QuerySet5['name'] = QBO_coa[k]["Name"]

                    for k1 in range(0, len(QBO_coa)):
                        if 'AcctNum' in QBO_coa[k1]:
                            if QuerySet1[i]['Line'][j]['AccountCode'] == QBO_coa[k1]['AcctNum']:
                                QuerySet5['value'] = QBO_coa[k1]["Id"]
                                QuerySet5['name'] = QBO_coa[k1]["Name"]
                                break
                            elif QuerySet1[i]['Line'][j]['AccountCode'].lower() == QBO_coa[k1]['AcctNum'].lower():
                                QuerySet5['value'] = QBO_coa[k1]["Id"]
                                QuerySet5['name'] = QBO_coa[k1]["Name"]
                                break

                            
                    QuerySet4['AccountRef'] = QuerySet5
                    QuerySet4['TaxCodeRef'] = QuerySet15
                    QuerySet4['TaxAmount'] = QuerySet1[i]['Line'][j]['TaxAmount']
                    sales_tax = sales_tax + QuerySet4['TaxAmount']
                    QuerySet4['ClassRef'] = QuerySet9
                    QuerySet2['Line'].append(QuerySet3)

                elif QuerySet1[i]['Line'][j]['LineAmount'] < 0:
                    if QuerySet1[i]['LineAmountTypes'] == 'Inclusive':
                        QuerySet12['NetAmountTaxable'] = round(QuerySet1[i]['Line'][j]['LineAmount']/(100+taxrate1)*100,2)
                        QuerySet11['Amount'] = QuerySet1[i]['Line'][j]['TaxAmount']
                        QuerySet6['Amount'] = round(abs(QuerySet1[i]['Line'][j]['LineAmount']/(100+taxrate1)*100),2)
                        if 'Description' in QuerySet1[i]['Line'][j]:
                            QuerySet6['Description'] = QuerySet1[i]['Line'][j]['Description']
                        
                    elif (QuerySet1[i]['LineAmountTypes'] == 'Exclusive') or ((QuerySet1[i]['LineAmountTypes'] == 'NoTax')):
                        QuerySet12['NetAmountTaxable'] = round(QuerySet1[i]['Line'][j]['LineAmount'],2)
                        QuerySet11['Amount'] = QuerySet1[i]['Line'][j]['TaxAmount']
                        QuerySet6['Amount'] = abs(round(QuerySet1[i]['Line'][j]['LineAmount'],2))
                        if 'Description' in QuerySet1[i]['Line'][j]:
                            QuerySet6['Description'] = QuerySet1[i]['Line'][j]['Description']
                    
                    QuerySet7['PostingType'] = 'Credit'
                    QuerySet6['DetailType'] = 'JournalEntryLineDetail'
                    QuerySet6['JournalEntryLineDetail'] = QuerySet7
                    # for p in range(0, len(QBO_coa)):
                    #     for k1 in range(0,len(xero_coa)):
                    #         if 'Code' in xero_coa[k1]:
                    #             if QuerySet1[i]['Line'][j]['AccountCode'] == xero_coa[k1]['Code']:
                    #                 if xero_coa[k1]['Name'] == QBO_coa[p]['Name']:
                    #                     QuerySet8['value'] = QBO_coa[p]["Id"]
                    #                     QuerySet8['name'] = QBO_coa[p]["Name"]
                                    
                    for k1 in range(0, len(QBO_coa)):
                        if 'AcctNum' in QBO_coa[k1]:
                            if QuerySet1[i]['Line'][j]['AccountCode'] == QBO_coa[k1]['AcctNum']:
                                QuerySet8['value'] = QBO_coa[k1]["Id"]
                                QuerySet8['name'] = QBO_coa[k1]["Name"]
                                break
                            elif QuerySet1[i]['Line'][j]['AccountCode'].lower() == QBO_coa[k1]['AcctNum'].lower():
                                QuerySet8['value'] = QBO_coa[k1]["Id"]
                                QuerySet8['name'] = QBO_coa[k1]["Name"]
                                break

                    QuerySet7['AccountRef'] = QuerySet8
                    QuerySet7['TaxCodeRef'] = QuerySet15
                    QuerySet7['TaxAmount'] = abs(QuerySet1[i]['Line'][j]['TaxAmount'])
                    purchase_tax = purchase_tax + QuerySet7['TaxAmount']
                    QuerySet7['ClassRef'] = QuerySet9
                    QuerySet2['Line'].append(QuerySet6)


            arr = QuerySet10['TaxLine']
            b1 = {'TaxLine': []}
            
            b=[]
            for i2 in range(0,len(arr)):
                if arr[i2]['TaxLineDetail']['TaxRateRef']!={}:
                    b.append(arr[i2]['TaxLineDetail']['TaxRateRef']['value'])

            e={}
            for i1 in range(0,len(b)):
                e[b[i1]] = b.count(b[i1])

            multiple=dict((k, v) for k, v in e.items() if v > 1)
            single=dict((k, v) for k, v in e.items() if v == 1)


            e1=[]
            for keys in e.keys():
                e1.append(keys)

            new_arr=[]
            for k in range(0,len(multiple)):
                e={}
                TaxLineDetail = {}
                TaxRateRef={}
                amt = 0
                net_amt = 0
                
                for i3 in range(0,len(arr)): 
                    if 'value' in arr[i3]['TaxLineDetail']['TaxRateRef']: 
                        if arr[i3]['TaxLineDetail']['TaxRateRef']['value'] == e1[k]:
                            e['DetailType'] = 'TaxLineDetail'
                            TaxLineDetail['TaxRateRef'] = TaxRateRef
                            TaxLineDetail['TaxPercent'] = arr[i3]['TaxLineDetail']['TaxPercent']
                            TaxRateRef['value'] = e1[k]

                            amt = amt + arr[i3]['Amount']
                            net_amt = net_amt + arr[i3]['TaxLineDetail']['NetAmountTaxable']
                            e['Amount'] = round(amt,2)
                            TaxLineDetail['NetAmountTaxable'] = round(net_amt,2)
                            e['TaxLineDetail'] = TaxLineDetail
                        
                new_arr.append(e)
            
            for k3 in range(0,len(arr)):
                if 'TaxRateRef' in arr[k3]['TaxLineDetail']:
                    if 'value' in arr[k3]['TaxLineDetail']['TaxRateRef']: 
                        if arr[k3]['TaxLineDetail']['TaxRateRef']['value'] in single:
                            new_arr.append(arr[k3])
            
            
            b1['TaxLine'] = new_arr
            
            # QuerySet2['TxnDate'] = journal_date1
            QuerySet2['TxnTaxDetail'] = b1
            
            payload = json.dumps(QuerySet2)
            print(payload)

            if (start_date != '' and end_date != ''):
                if (journal_date1 >= start_date1) and (journal_date1 <= end_date1):
                    post_data_in_qbo(url, headers, payload,journal1,_id, job_id,task_id, QuerySet1[i]["ManualJournalID"])
                else:
                    print("No Journal Available in between these dates")
            else:
                post_data_in_qbo(url, headers, payload,journal1,_id, job_id,task_id, QuerySet1[i]["ManualJournalID"])
                            
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)