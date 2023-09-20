from math import expm1
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
from collections import Counter


import logging
logger = logging.getLogger(__name__)
    
def add_bill_payment(job_id, task_id):
    logger.info("Started executing myob -> qbo -> add_bill_payment")

    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(
            job_id)
        url = f"{base_url}/billpayment?minorversion={minorversion}"

        bill_payment_data = db['bill_payment'].find({'job_id':job_id})
        payment = []
        for k1 in bill_payment_data:
            payment.append(k1)

        x2 = db['QBO_Bill'].find({'job_id':job_id})
        QBO_Bill = []
        for k2 in x2:
            QBO_Bill.append(k2)

        x3 = db['QBO_CreditMemo'].find({'job_id':job_id})
        QBO_CreditMemo = []
        for k3 in x3:
            QBO_CreditMemo.append(k3)

        x4 = db['QBO_Supplier'].find({'job_id':job_id})
        QBO_supplier = []
        for k4 in x4:
            QBO_supplier.append(k4)

        x5 = db['QBO_COA'].find({'job_id':job_id})
        qbo_coa = []
        for k5 in x5:
            qbo_coa.append(k5)

        x6 = db['all_bill'].find({'job_id':job_id})
        all_bill = []
        for k6 in x6:
            all_bill.append(k6)

        QuerySet = []
        for j in range(0, len(payment)):
            _id=payment[j]['_id']
            task_id=payment[j]['task_id']
            
            QuerySet21 = {'Line':[]}
            QuerySet21["_id"]=payment[j]['_id']
            QuerySet21["task_id"]=payment[j]['task_id']
            QuerySet21['supplier'] = payment[j]['supplier']
            QuerySet21['Date'] = payment[j]['Date']
            QuerySet21['AccName'] = payment[j]['AccName']
            QuerySet21['AccId'] = payment[j]['AccId']
            QuerySet21['Memo'] = payment[j]['Memo']
            QuerySet21['CreditMemo'] = payment[j]['CreditMemo']+"-"+payment[j]['Line'][0]['UID'][-6:]
            print(QuerySet21['CreditMemo'])
            for j1 in range(0,len(payment[j]['Line'])):
                Q1={}
                Q1['UID'] = payment[j]['Line'][j1]['UID']
                Q1['Invoice'] = payment[j]['Line'][j1]['Invoice']
                Q1['Type'] = payment[j]['Line'][j1]['Type']
                Q1['paid_amount'] = payment[j]['Line'][j1]['paid_amount']
                QuerySet21['Line'].append(Q1)
                
            QuerySet.append(QuerySet21)
        
        for p2 in range(0, len(QuerySet)):
            _id=QuerySet[p2]['_id']
            task_id=QuerySet[p2]['task_id']
            QuerySet2 = {}
            QuerySet21 = {}
            BankAccountRef={}

            for k11 in range(0, len(QBO_supplier)):
                if (QBO_supplier[k11]['DisplayName'].startswith(QuerySet[p2]['supplier'])) and (QBO_supplier[k11]['DisplayName'].endswith("-S")):
                    QuerySet2['name'] = QBO_supplier[k11]['DisplayName']
                    QuerySet2['value'] = QBO_supplier[k11]['Id']
                    continue
                elif QuerySet[p2]['supplier'].strip().lower() == QBO_supplier[k11]['DisplayName'].strip().lower():
                    QuerySet2['name'] = QBO_supplier[k11]['DisplayName']
                    QuerySet2['value'] = QBO_supplier[k11]['Id']
                    break

            for k12 in range(0, len(qbo_coa)):
                if (qbo_coa[k12]["FullyQualifiedName"].startswith(payment[p2]['AccName'])) and (qbo_coa[k12]["FullyQualifiedName"].endswith(payment[p2]['AccId'])):
                    QuerySet21['name'] = qbo_coa[k12]['Name']
                    QuerySet21['value'] = qbo_coa[k12]['Id']
                elif QuerySet[p2]['AccName'].lower().strip() == qbo_coa[k12]["FullyQualifiedName"].lower().strip():
                    QuerySet21['name'] = qbo_coa[k12]['Name']
                    QuerySet21['value'] = qbo_coa[k12]['Id']
                
            
            BankAccountRef['BankAccountRef'] = QuerySet21
                        
            for k14 in range(0,len(QuerySet[p2]['Line'])):
                QuerySet1 = {'Line': []}
                QuerySet4 = {'LinkedTxn': []}
                QuerySet5 = {}
                
                QuerySet1['VendorRef'] = QuerySet2
                QuerySet1['CheckPayment'] = BankAccountRef
                QuerySet1['PayType'] = 'Check'
                
                QuerySet1['TxnDate'] = QuerySet[p2]['Date'][0:10]
                QuerySet1['PrivateNote'] = QuerySet[p2]['Memo']
                
                QuerySet1['TotalAmt'] = QuerySet[p2]['Line'][k14]['paid_amount']
                
                QuerySet4['Amount'] = QuerySet[p2]['Line'][k14]['paid_amount']
                
                QuerySet1['DocNumber'] = QuerySet[p2]['CreditMemo']

                
                for k12 in range(0, len(QBO_Bill)):
                    for k13 in range(0,len(all_bill)):
                        if 'UID' in QuerySet[p2]['Line'][k14]: 
                            if QuerySet[p2]['Line'][k14]['UID']==all_bill[k13]['UID']:
                                if all_bill[k13]['invoice_no']== QBO_Bill[k12]['DocNumber']:
                                    QuerySet5['TxnId'] = QBO_Bill[k12]['Id']
                                    QuerySet5['TxnType'] = 'Bill'
                                    continue
                                
                                elif all_bill[k13]['invoice_no'][0:14]+"-"+all_bill[k13]['UID'][-6:]== QBO_Bill[k12]['DocNumber']:
                                    QuerySet5['TxnId'] = QBO_Bill[k12]['Id']
                                    QuerySet5['TxnType'] = 'Bill'
                                    break
                QuerySet4['LinkedTxn'].append(QuerySet5)
                QuerySet1['Line'].append(QuerySet4)
                payload = json.dumps(QuerySet1)
                print("-----------")
                post_data_in_qbo(url, headers, payload,db['bill_payment'],_id,job_id,task_id, QuerySet[p2]['CreditMemo'])
                        
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)