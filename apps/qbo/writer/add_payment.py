import json
import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_payment(job_id, task_id):
    
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/payment?minorversion={minorversion}"

        invoice_payment_data = db['invoice_payment']
        QBO_Customer = db['QBO_Customer']
        QBO_Invoice = db['QBO_Invoice']
        all_invoice = db['all_invoice']
        
        data1 = []
        for k in db['invoice_payment'].find({'job_id':job_id}):
            data1.append(k)

        cust = QBO_Customer.find({'job_id':job_id})
        cust1 = []
        for k in cust:
            cust1.append(k)

        QBO_Invoice = QBO_Invoice.find({'job_id':job_id})
        QBO_Invoice1 = []
        for k in QBO_Invoice:
            QBO_Invoice1.append(k)

        x5 = db['QBO_COA'].find({'job_id':job_id})
        qbo_coa = []
        for k5 in x5:
            qbo_coa.append(k5)

        all_invoice = db['all_invoice'].find({'job_id':job_id})
        all_invoice1 = []
        for k6 in all_invoice:
            all_invoice1.append(k6)


        QuerySet1 = data1
        for i in range(0, len(QuerySet1)):
            
            _id=QuerySet1[i]['_id']
            task_id=QuerySet1[i]['task_id']
            QuerySet2 = {"Line":[]}
            CustomerRef = {}
            QuerySet4 = {'LinkedTxn': []}
            QuerySet5={}
            QuerySet21={}
            QuerySet2['TxnDate'] = QuerySet1[i]['Date'][0:10]
            if 'CreditMemo' in QuerySet1[i] and QuerySet1[i]['CreditMemo']!=None: 
                QuerySet2['PaymentRefNum'] = QuerySet1[i]['CreditMemo']
            else:
                QuerySet2['PaymentRefNum'] = f"Payment-{i}"

            for j in range(0,len(cust1)):
                if QuerySet1[i]["customer"].lower().strip() == cust1[j]["DisplayName"].lower().strip():
                    CustomerRef['name'] = cust1[j]["DisplayName"]
                    CustomerRef['value'] = cust1[j]["Id"]
                    break
                elif (cust1[j]["DisplayName"].startswith(QuerySet1[i]["customer"])) and (cust1[j]["DisplayName"].endswith("-C")):
                    CustomerRef['name'] = cust1[j]["DisplayName"]
                    CustomerRef['value'] = cust1[j]["Id"]
                    break
                elif QuerySet1[i]["customer"].replace("\n","") == cust1[j]["DisplayName"]:
                    CustomerRef['name'] = cust1[j]["DisplayName"]
                    CustomerRef['value'] = cust1[j]["Id"]
                    break
                elif QuerySet1[i]["customer"].replace(":","-") == cust1[j]["DisplayName"]:
                    CustomerRef['name'] = cust1[j]["DisplayName"]
                    CustomerRef['value'] = cust1[j]["Id"]
                    break
                
            QuerySet2['TotalAmt'] = QuerySet1[i]["paid_amount"]
            QuerySet4['Amount'] = QuerySet1[i]["paid_amount"]
            
            # if QuerySet1[i]['InvoiceType']=="ACCREC":
            for k12 in range(0, len(QBO_Invoice1)):
                                    
                if 'DocNumber' in QBO_Invoice1[k12]:
                    if QuerySet1[i]['Invoice'] == QBO_Invoice1[k12]['DocNumber']:
                        QuerySet5['TxnId'] = QBO_Invoice1[k12]['Id']
                        QuerySet5['TxnType'] = 'Invoice'
                        break
                    else:
                        for k13 in range(0,len(all_invoice1)):
                            if QuerySet1[i]['Invoice']==all_invoice1[k13]['Invoice_Number']:
                                if (QBO_Invoice1[k12]['DocNumber'].startswith(QuerySet1[i]['Invoice'])) and (QBO_Invoice1[k12]['DocNumber'].endswith(all_invoice1[k13]['UID'][-6:])):
                                    QuerySet5['TxnId'] = QBO_Invoice1[k12]['Id']
                                    QuerySet5['TxnType'] = 'Invoice'
                                    break
                    
            for k13 in range(0, len(qbo_coa)):
                if (qbo_coa[k13]["FullyQualifiedName"].startswith(QuerySet1[i]['AccName'])) and (qbo_coa[k13]["FullyQualifiedName"].endswith(QuerySet1[i]['AccId'])):
                    QuerySet21['value'] = qbo_coa[k13]['Id']
                    break
                elif QuerySet1[i]['AccName'] == qbo_coa[k13]["FullyQualifiedName"]:
                    QuerySet21['value'] = qbo_coa[k13]['Id']
                    continue
                elif QuerySet1[i]['AccName'].strip().lower() == qbo_coa[k13]["FullyQualifiedName"].strip().lower():
                    QuerySet21['value'] = qbo_coa[k13]['Id']
                    continue
                else:
                    pass
            
            QuerySet2['DepositToAccountRef'] = QuerySet21
            
            QuerySet2['CustomerRef'] = CustomerRef
            QuerySet2['Line'].append(QuerySet4)
            QuerySet4['LinkedTxn'].append(QuerySet5)
            
            payload = json.dumps(QuerySet2)
            
            post_data_in_qbo(url, headers,payload,invoice_payment_data,_id,job_id,task_id, QuerySet1[i]['CreditMemo'])
                
            
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)