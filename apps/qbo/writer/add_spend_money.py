import json
from datetime import datetime

from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_spend_money(job_id, task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        spend_money_data = db['myob_spend_money']

        spend_money1 = []
        for q in db['myob_spend_money'].find({'job_id': job_id}):
            spend_money1.append(q)

        purchase_url = f"{base_url}/purchase?minorversion={minorversion}"

        QBO_COA1 = db['QBO_COA'].find({'job_id': job_id})
        QBO_COA = []
        for k2 in range(0, db['QBO_COA'].count_documents({'job_id': job_id})):
            QBO_COA.append(QBO_COA1[k2])

        QBO_Supplier1 = db['QBO_Supplier'].find({'job_id': job_id})
        QBO_Supplier = []
        for k3 in range(0, db['QBO_Supplier'].count_documents({'job_id': job_id})):
            QBO_Supplier.append(QBO_Supplier1[k3])

        QBO_Customer1 = db['QBO_Customer'].find({'job_id': job_id})
        QBO_Customer = []
        for m in range(0, db['QBO_Customer'].count_documents({'job_id': job_id})):
            QBO_Customer.append(QBO_Customer1[m])

        QBO_Class1 = db['QBO_Class'].find({'job_id': job_id})
        QBO_Class = []
        for n in range(0, db['QBO_Class'].count_documents({'job_id': job_id})):
            QBO_Class.append(QBO_Class1[n])

        Myob_Job = db['job'].find({'job_id': job_id})
        Myob_Job1 = []
        for n in range(0, db['job'].count_documents({'job_id': job_id})):
            Myob_Job1.append(Myob_Job[n])

        QBO_Tax = []
        QBO_tax1 = db['QBO_Tax'].find({'job_id': job_id})
        for p in range(0, db['QBO_Tax'].count_documents({'job_id': job_id})):
            QBO_Tax.append(QBO_tax1[p])

        QuerySet = spend_money1

        for i in range(0, len(QuerySet)):
            print(QuerySet[i]['payment_no'])
            _id = QuerySet[i]['_id']
            task_id = QuerySet[i]['task_id']

            if QuerySet[i]['Total_Amount'] >= 0:

                QuerySet1 = {'Line': []}
                for j in range(0, len(QuerySet[i]['Lines'])):

                    QuerySet1['TotalAmt'] = QuerySet[i]['Total_Amount']
                    QuerySet2 = {}
                    QuerySet3 = {}
                    QuerySet4 = {}
                    QuerySet5 = {}
                    QuerySet8 = {}
                    QuerySet9 = {}

                    QuerySet1['AccountRef'] = QuerySet2
                    for j1 in range(0, len(QBO_COA)):
                        if QuerySet[i]['pay_from'].lower().strip() == QBO_COA[j1]['Name'].lower().strip():
                            QuerySet2['name'] = QBO_COA[j1]['Name']
                            QuerySet2['value'] = QBO_COA[j1]['Id']

                    QuerySet4['TaxCodeRef'] = QuerySet8

                    taxrate1 = 0
                    for j4 in range(0, len(QBO_Tax)):
                        if QuerySet[i]['Lines'][j]['taxcode'] == "GST":
                            if 'taxrate_name' in QBO_Tax[j4]:
                                if "GST (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                    QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                    taxrate = QBO_Tax[j4]['Rate']
                                    taxrate1 = taxrate
                                    print(taxrate1, "in-------")

                        elif QuerySet[i]['Lines'][j]['taxcode'] == "CAP":
                            if 'taxrate_name' in QBO_Tax[j4]:
                                if "GST (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                    QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                    taxrate = QBO_Tax[j4]['Rate']
                                    taxrate1 = taxrate

                        elif QuerySet[i]['Lines'][j]['taxcode'] in ["FRE", "GNR", "INP"]:
                            if 'taxrate_name' in QBO_Tax[j4]:
                                if "GST-free (purchases)" in QBO_Tax[j4]['taxrate_name']:
                                    QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                    taxrate = QBO_Tax[j4]['Rate']
                                    taxrate1 = taxrate

                        elif QuerySet[i]['Lines'][j]['taxcode'] == "N-T":
                            if 'taxrate_name' in QBO_Tax[j4]:
                                if 'NOTAXP' in QBO_Tax[j4]['taxrate_name']:
                                    QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                                    taxrate = QBO_Tax[j4]['Rate']
                                    taxrate1 = taxrate

                        elif QuerySet[i]['Lines'][j]['taxcode'] == QBO_Tax[j4]['taxcode_name']:
                            QuerySet8['value'] = QBO_Tax[j4]['taxcode_id']
                            taxrate = QBO_Tax[j4]['Rate']
                            taxrate1 = taxrate

                    QuerySet1['PrivateNote'] = QuerySet[i]['memo']

                    if QuerySet[i]['IsTaxInclusive'] == True:
                        QuerySet1['GlobalTaxCalculation'] = "TaxInclusive"
                        QuerySet4['TaxInclusiveAmt'] = round(QuerySet[i]['Lines'][j]['line_amount'], 2)
                        QuerySet3['Amount'] = QuerySet[i]['Lines'][j]['line_amount'] / (100 + taxrate1) * 100
                    elif QuerySet[i]['IsTaxInclusive'] == False:
                        QuerySet1['GlobalTaxCalculation'] = "TaxExcluded"
                        QuerySet4['TaxInclusiveAmt'] = round(
                            QuerySet[i]['Lines'][j]['line_amount'] / (100 + taxrate1) * 100, 2)
                        QuerySet3['Amount'] = round(QuerySet[i]['Lines'][j]['line_amount'], 2)

                    QuerySet1['PaymentType'] = "Cash"
                    QuerySet1['TxnDate'] = QuerySet[i]['date']

                    if QuerySet[i]['Lines'][j]['memo'] != None:
                        QuerySet3['Description'] = QuerySet[i]['Lines'][j]['memo']
                    else:
                        QuerySet3['Description'] = QuerySet[i]['memo']

                    QuerySet3['DetailType'] = "AccountBasedExpenseLineDetail"
                    QuerySet3['AccountBasedExpenseLineDetail'] = QuerySet4

                    # if QuerySet[i]['Lines'][j]['job'] != None:
                    #     for j2 in range(0, len(QBO_Class)):
                    #         for j4 in range(0,len(Myob_Job1)):
                    #             if QuerySet[i]['Lines'][j]['job'] == Myob_Job1[j4]['Name']:
                    #                 if (QBO_Class[j2]['FullyQualifiedName'].startswith(Myob_Job1[j4]['Name'])) and (QBO_Class[j2]['FullyQualifiedName'].endswith(Myob_Job1[j4]['Number'])):
                    #                     QuerySet7['value'] = QBO_Class[j2]['Id']
                    #                     QuerySet7['name'] = QBO_Class[j2]['Name']

                    # QuerySet4['ClassRef'] = QuerySet7

                    QuerySet4['AccountRef'] = QuerySet5

                    for j3 in range(0, len(QBO_COA)):
                        if (QBO_COA[j3]['Name'].startswith(QuerySet[i]['Lines'][j]['account_name'])) and (
                        QBO_COA[j3]['Name'].endswith(QuerySet[i]['Lines'][j]['DisplayID'])):
                            QuerySet5['name'] = QBO_COA[j3]['Name']
                            QuerySet5['value'] = QBO_COA[j3]['Id']

                        elif QuerySet[i]['Lines'][j]['account_name'].strip().lower() == QBO_COA[j3][
                            'Name'].strip().lower():
                            QuerySet5['name'] = QBO_COA[j3]['Name']
                            QuerySet5['value'] = QBO_COA[j3]['Id']

                        elif 'AcctNum' in QBO_COA[j3]:
                            if QuerySet[i]['Lines'][j]['DisplayID'] == QBO_COA[j3]['AcctNum']:
                                QuerySet5['name'] = QBO_COA[j3]['Name']
                                QuerySet5['value'] = QBO_COA[j3]['Id']

                    QuerySet1['DocNumber'] = QuerySet[i]['payment_no']
                    QuerySet1['EntityRef'] = QuerySet9

                    if QuerySet[i]['contact_type'] == "Supplier":
                        QuerySet9['name'] = QuerySet[i]['contact_name']
                        QuerySet9['type'] = "vendor"
                        for k1 in range(0, len(QBO_Supplier)):
                            if QuerySet[i]['contact_name'] == QBO_Supplier[k1]['DisplayName']:
                                QuerySet9['value'] = QBO_Supplier[k1]['Id']

                    QuerySet1['Line'].append(QuerySet3)

                payload = json.dumps(QuerySet1)

                spend_money_date = QuerySet[i]['date'][0:10]
                spend_money_date1 = datetime.strptime(spend_money_date, '%Y-%m-%d')
                if (start_date != '' and end_date != ''):
                    if (spend_money_date1 >= start_date1) and (spend_money_date1 <= end_date1):
                        post_data_in_qbo(purchase_url, headers, payload, spend_money_data, _id, job_id, task_id,
                                         QuerySet[i]['payment_no'])
                    else:
                        print("No Spend Money Transaction Within these dates")
                else:
                    post_data_in_qbo(purchase_url, headers, payload, spend_money_data, _id, job_id, task_id,
                                     QuerySet[i]['payment_no'])

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)
