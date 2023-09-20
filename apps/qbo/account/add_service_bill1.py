from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
from datetime import datetime, timedelta, timezone


def add_service_bill1(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(
            job_id)
        url1 = f"{base_url}/bill?minorversion=14"
        url2 = f"{base_url}/vendorcredit?minorversion=14"

        db = get_mongodb_database()

        final_bill1 = db['final_bill'].find({'job_id':job_id})

        final_bill = []
        for p1 in final_bill1:
            final_bill.append(p1)

        m1=[]
        for m in range(0,len(final_bill)):
            # if final_bill[m]['LineAmountTypes']=="Exclusive":
            if final_bill[m]['invoice_no'] in ['00000013']:
                m1.append(final_bill[m])
        
        final_bill = m1

        Myob_Job = db['job'].find()
        Myob_Job1 = []
        for n in range(0,db['job'].count_documents({"job_id":job_id})):
            Myob_Job1.append(Myob_Job[n])

        QBO_COA = db['QBO_COA'].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Supplier = db['QBO_Supplier'].find({"job_id":job_id})
        QBO_supplier = []
        for p3 in QBO_Supplier:
            QBO_supplier.append(p3)

        QBO_Item = db['QBO_Item'].find({"job_id":job_id})
        QBO_item = []
        for p4 in QBO_Item:
            QBO_item.append(p4)

        QBO_Class = db['QBO_Class'].find({"job_id":job_id})
        QBO_class = []
        for p5 in QBO_Class:
            QBO_class.append(p5)

        QBO_Tax = db['QBO_Tax'].find({"job_id":job_id})
        QBO_tax = []
        for p6 in QBO_Tax:
            QBO_tax.append(p6)

        bill_arr = []
        vendor_credit_arr = []

        final_bill = final_bill

        for i in range(0, len(final_bill)):
            print(final_bill[i])
            
            if 'account' in final_bill[i]:
                _id=final_bill[i]['_id']
                task_id=final_bill[i]['task_id']
                        
                if final_bill[i]['Total_Amount'] >= 0:
                    if len(final_bill[i]['account']) >= 1:
                        QuerySet = {"Line": []}
                        QuerySet['DocNumber'] = (final_bill[i]['invoice_no'])
                        TxnTaxDetail = {'TaxLine': []}

                        for j in range(0, len(final_bill[i]['account'])):
                            if 'Item_name' in final_bill[i]['account'][j]:
                                QuerySet1 = {}
                                QuerySet2 = {}
                                QuerySet3 = {}
                                QuerySet4 = {}
                                QuerySet5 = {}
                                TaxLineDetail = {}
                                TaxRate = {}
                                Tax = {}
                                Tax['DetailType'] = "TaxLineDetail"
                                Tax['TaxLineDetail'] = TaxLineDetail
                                TxnTaxDetail['TotalTax'] = abs(
                                    final_bill[i]['TotalTax'])
                                TaxLineDetail['TaxRateRef'] = TaxRate
                                TaxLineDetail['PercentBased'] = True
                                TxnTaxDetail['TaxLine'].append(Tax)
                                QuerySet['TxnTaxDetail'] = TxnTaxDetail
                                TaxCodeRef = {}
                                QuerySet['TotalAmt'] = abs(
                                    final_bill[i]['TotalAmount'])

                                for k1 in range(0, len(QBO_tax)):
                                    if (final_bill[i]['account'][j]['Tax_Code'] == 'GST') or (final_bill[i]['account'][j]['Tax_Code'] == 'GCA'):
                                        if "GST on purchases" == QBO_tax[k1]['taxcode_name']:
                                            print("here")
                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                            taxrate1 = QBO_tax[k1]['Rate']
                                            TaxLineDetail['NetAmountTaxable'] = abs(
                                                QBO_tax[k1]['Rate'] * final_bill[i]['TotalTax'])
                                            Tax['Amount'] = final_bill[i]['TotalTax']
                                
                                    if (final_bill[i]['account'][j]['Tax_Code'] == 'N-T') or (final_bill[i]['account'][j]['Tax_Code'] == None):
                                        if 'taxrate_name' in QBO_tax[k1]: 
                                            if "NOTAXP" == QBO_tax[k1]['taxrate_name']:
                                                TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                taxrate1 = QBO_tax[k1]['Rate']
                                                TaxLineDetail['NetAmountTaxable'] = abs(
                                                    QBO_tax[k1]['Rate'] * final_bill[i]['TotalTax'])
                                                Tax['Amount'] = 0
                                

                                    elif (final_bill[i]['account'][j]['Tax_Code'] == 'GNR') or (final_bill[i]['account'][j]['Tax_Code'] == 'FRE'):
                                        if 'taxrate_name' in QBO_tax[k1]: 
                                            if "GST free purchases" == QBO_tax[k1]['taxrate_name']:
                                                TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                taxrate1 = QBO_tax[k1]['Rate']
                                                TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Total_Amount']
                                                Tax['Amount'] = final_bill[i]['TotalTax']
                                

                                if final_bill[i]['Is_Tax_Inclusive'] == True:
                                    QuerySet['GlobalTaxCalculation'] = 'TaxInclusive'
                                    QuerySet1['Amount'] = (final_bill[i]['account'][j]['Quantity']*final_bill[i]['account'][j]['Unit_Price'])/(100+taxrate1)*100
                                    print(QuerySet1['Amount'])
                                else:
                                    QuerySet['GlobalTaxCalculation'] = 'TaxExcluded'
                                    QuerySet1['Amount'] = final_bill[i]['account'][j]['Quantity']*final_bill[i]['account'][j]['Unit_Price']

                               
                                if ('Comment' in final_bill[i]) and ('supplier_invoice_no' in final_bill[i]):
                                    if (final_bill[i]['supplier_invoice_no'] != None) and (final_bill[i]['supplier_invoice_no'] != "") and (final_bill[i]['Comment'] != None) and (final_bill[i]['Comment'] != ""):
                                        QuerySet['PrivateNote'] = final_bill[i]['Comment'] + " Supplier Invoice Number is:" + final_bill[i]['supplier_invoice_no']
                                elif 'Comment' in final_bill[i]:
                                    QuerySet['PrivateNote'] = final_bill[i]['Comment']
                                
                                elif 'supplier_invoice_no' in final_bill[i]:
                                    if final_bill[i]['supplier_invoice_no']!=None:
                                        QuerySet['PrivateNote'] = " Supplier Invoice Number is:" + final_bill[i]['supplier_invoice_no']
                                   


                                QuerySet2['TaxCodeRef'] = TaxCodeRef
                                QuerySet['TxnDate'] = final_bill[i]['Bill_Date']
                                QuerySet['DueDate'] = final_bill[i]['Due_Date']
                                QuerySet1['Description'] = final_bill[i]['account'][j]['Description']
                                QuerySet1['DetailType'] = "ItemBasedExpenseLineDetail"
                                QuerySet1['ItemBasedExpenseLineDetail'] = QuerySet2
                                QuerySet2['ItemRef'] = QuerySet3
                                QuerySet2['Qty'] = abs(final_bill[i]['account'][j]['Quantity'])
                                QuerySet2['UnitPrice'] = final_bill[i]['account'][j]['Unit_Price']

                                print(final_bill[i]['invoice_no'])

                                for j1 in range(0, len(QBO_item)):
                                    if 'Item_name' in final_bill[i]['account'][j]:
                                        if final_bill[i]['account'][j]['Item_name'].lower().strip() == QBO_item[j1]["Name"].lower().strip():
                                            QuerySet3['value'] = QBO_item[j1]["Id"]
                                            break
                                    # elif final_bill[i]['account'][j]['DisplayID'] == QBO_item[j1]["Name"]:
                                    #     QuerySet3['value'] = QBO_item[j1]["Id"]
                                    #     break
                                
                                QuerySet['VendorRef'] = QuerySet4

                                for j3 in range(0, len(QBO_supplier)):
                                    if final_bill[i]['Supplier_Name'].lower().strip() == QBO_supplier[j3]['DisplayName'].lower().strip():
                                        QuerySet4['value'] = QBO_supplier[j3]['Id']
                                    elif (QBO_supplier[j3]["DisplayName"]).startswith(final_bill[i]["Supplier_Name"]) and ((QBO_supplier[j3]["DisplayName"]).endswith("-S")):
                                        QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                

                                QuerySet2['ClassRef'] = QuerySet5
                               
                                for j2 in range(0, len(QBO_class)):
                                    for j4 in range(0,len(Myob_Job1)):
                                        if ('Job' in final_bill[i]['account'][j]) and (final_bill[i]['account'][j]['Job']!=None):
                                            if final_bill[i]['account'][j]['Job']['Name'] == Myob_Job1[j4]['Name']:
                                                if (QBO_class[j2]['FullyQualifiedName'].startswith(Myob_Job1[j4]['Name'])) and (QBO_class[j2]['FullyQualifiedName'].endswith(Myob_Job1[j4]['Number'])):
                                                    QuerySet5['value'] = QBO_class[j2]['Id']
                                                    QuerySet5['name'] = QBO_class[j2]['Name']

                                if QuerySet2['ItemRef']!={}:
                                    QuerySet['Line'].append(QuerySet1)
                                
                               
                        if 'TxnTaxDetail' in QuerySet:
                            arr = QuerySet['TxnTaxDetail']['TaxLine']
                      
                            new_arr=[]
                            for r in range(0,len(arr)):
                                if arr[r] in new_arr:
                                    pass
                                else:
                                    new_arr.append(arr[r])

                            QuerySet['TxnTaxDetail']['TaxLine'] = new_arr
                            
                        payload = json.dumps(QuerySet)
                        print(payload)
                        bill_date = final_bill[i]['Bill_Date'][0:10]

                        bill_date1 = datetime.strptime(bill_date, '%Y-%m-%d')
                        if (start_date != '' and end_date != ''):
                            if (bill_date1 >= start_date1) and (bill_date1 <= end_date1):
                                
                                post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])
                            else:
                                print("No Bill Available")
                        else:
                            post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])
                            print("----Multiple Item Bill------")
                            

                else:

                    if len(final_bill[i]['account']) >= 1:

                        QuerySet = {"Line": []}
                        QuerySet['DocNumber'] = (final_bill[i]['invoice_no'])
                                
                        TxnTaxDetail = {'TaxLine': []}

                        for j in range(0, len(final_bill[i]['account'])):
                            QuerySet1 = {}
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            TaxLineDetail = {}
                            TaxRate = {}
                            Tax = {}
                            Tax['DetailType'] = "TaxLineDetail"
                            Tax['TaxLineDetail'] = TaxLineDetail
                            TxnTaxDetail['TotalTax'] = abs(
                                final_bill[i]['TotalTax'])
                            TaxLineDetail['TaxRateRef'] = TaxRate
                            TaxLineDetail['PercentBased'] = True
                            TxnTaxDetail['TaxLine'].append(Tax)
                            QuerySet['TxnTaxDetail'] = TxnTaxDetail
                            TaxCodeRef = {}
                            QuerySet['TotalAmt'] = abs(
                                final_bill[i]['TotalAmount'])

                            for k1 in range(0, len(QBO_tax)):
                                if (final_bill[i]['account'][j]['Tax_Code'] == 'GST') or (final_bill[i]['account'][j]['Tax_Code'] == 'GCA'):
                                    if "GST on purchases" == QBO_tax[k1]['taxcode_name']:
                                        TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                        TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                        taxrate1 = QBO_tax[k1]['Rate']
                                        Tax['Amount'] = abs(
                                            final_bill[i]['TotalTax'])
                                
                                if (final_bill[i]['account'][j]['Tax_Code'] == 'N-T') or (final_bill[i]['account'][j]['Tax_Code'] == None):
                                    if 'taxrate_name' in QBO_tax[k1]: 
                                        if "NOTAXP" == QBO_tax[k1]['taxrate_name']:
                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                            taxrate1 = QBO_tax[k1]['Rate']
                                            Tax['Amount'] = 0

                                elif (final_bill[i]['account'][j]['Tax_Code'] == 'GNR')or(final_bill[i]['account'][j]['Tax_Code'] == 'FRE'):
                                    if 'taxrate_name' in QBO_tax[k1]: 
                                        if "GST free purchases" == QBO_tax[k1]['taxrate_name']:
                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                            taxrate1 = QBO_tax[k1]['Rate']
                                            Tax['Amount'] = abs(
                                                final_bill[i]['TotalTax'])*taxrate1

                                else:
                                    pass

                            if final_bill[i]['Is_Tax_Inclusive'] == True:
                                QuerySet['GlobalTaxCalculation'] = 'TaxInclusive'
                                QuerySet1['Amount'] = abs(final_bill[i]['account'][j]['Quantity']*final_bill[i]['account'][j]['Unit_Price'])
                                TaxLineDetail['NetAmountTaxable'] = abs(
                                    taxrate1 * final_bill[i]['TotalTax'])/(100+taxrate1)*100

                            else:
                                QuerySet['GlobalTaxCalculation'] = 'TaxExcluded'
                                QuerySet1['Amount'] = abs(final_bill[i]['account'][j]['Quantity']*final_bill[i]['account'][j]['Unit_Price'])
                                TaxLineDetail['NetAmountTaxable'] = abs(
                                    taxrate1 * final_bill[i]['TotalTax'])

                            # if 'supplier_invoice_no' in final_bill[i]:
                            #     if final_bill[i]['supplier_invoice_no'] == None or final_bill[i]['supplier_invoice_no'] == '':
                            #         if type(final_bill[i]['invoice_no'])==int:
                            #             QuerySet['DocNumber'] = str(int(final_bill[i]['invoice_no']))
                            #         else:
                            #             QuerySet['DocNumber'] = final_bill[i]['invoice_no']
                                
                            #     elif final_bill[i]['supplier_invoice_no'] != '' or final_bill[i]['supplier_invoice_no'] != None:
                            #         QuerySet['DocNumber'] = (str(int(final_bill[i]['invoice_no'])) + "-" + final_bill[i]['supplier_invoice_no'])[0:20]
                            # else:
                            #     QuerySet['DocNumber'] = final_bill[i]['invoice_no']
                            
                            if ('Comment' in final_bill[i]) and ('supplier_invoice_no' in final_bill[i]):
                                if (final_bill[i]['supplier_invoice_no'] != None) and (final_bill[i]['supplier_invoice_no'] != "") and (final_bill[i]['Comment'] != None) and (final_bill[i]['Comment'] != ""):
                                    QuerySet['PrivateNote'] = final_bill[i]['Comment'] + " Supplier Invoice Number is:" + final_bill[i]['supplier_invoice_no']
                            elif 'Comment' in final_bill[i]:
                                QuerySet['PrivateNote'] = final_bill[i]['Comment']
                            elif 'supplier_invoice_no' in final_bill[i]:
                                if final_bill[i]['supplier_invoice_no']!=None:
                                    QuerySet['PrivateNote'] = " Supplier Invoice Number is:" + final_bill[i]['supplier_invoice_no']
                            else:
                                pass


                            QuerySet2['TaxCodeRef'] = TaxCodeRef
                            QuerySet['TxnDate'] = final_bill[i]['Bill_Date']
                            QuerySet1['Description'] = final_bill[i]['account'][j]['Description']
                            QuerySet1['DetailType'] = "ItemBasedExpenseLineDetail"
                            QuerySet1['ItemBasedExpenseLineDetail'] = QuerySet2
                            QuerySet2['ItemRef'] = QuerySet3
                            QuerySet2['Qty'] = abs(final_bill[i]['account'][j]['Quantity'])
                            QuerySet2['UnitPrice'] = abs(final_bill[i]['account'][j]['Unit_Price'])


                            for j1 in range(0, len(QBO_item)):
                                if 'Item_name' in final_bill[i]['account'][j]:
                                    if final_bill[i]['account'][j]['Item_name'].lower().strip() == QBO_item[j1]['Name'].lower().strip():
                                        QuerySet3['value'] = QBO_item[j1]['Id']
                                        break
                                # elif final_bill[i]['account'][j]['DisplayID'] == QBO_item[j1]["Name"]:
                                #     QuerySet3['value'] = QBO_item[j1]["Id"]

                            QuerySet['VendorRef'] = QuerySet4
                            for j3 in range(0, len(QBO_supplier)):
                                if final_bill[i]['Supplier_Name'] == QBO_supplier[j3]['DisplayName']:
                                    QuerySet4['value'] = QBO_supplier[j3]['Id']
                                elif (QBO_supplier[j3]["DisplayName"]).startswith(final_bill[i]["Supplier_Name"]) and ((QBO_supplier[j3]["DisplayName"]).endswith("-S")):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                          
                            QuerySet2['ClassRef'] = QuerySet5

                            for j2 in range(0, len(QBO_class)):
                                for j4 in range(0,len(Myob_Job1)):
                                    if ('Job' in final_bill[i]['account'][j]) and (final_bill[i]['account'][j]['Job']!=None):
                                        if final_bill[i]['account'][j]['Job']['Name'] == Myob_Job1[j4]['Name']:
                                            if (QBO_class[j2]['FullyQualifiedName'].startswith(Myob_Job1[j4]['Name'])) and (QBO_class[j2]['FullyQualifiedName'].endswith(Myob_Job1[j4]['Number'])):
                                                QuerySet5['value'] = QBO_class[j2]['Id']
                                                QuerySet5['name'] = QBO_class[j2]['Name']
                            if QuerySet2['ItemRef']!={}:
                                QuerySet['Line'].append(QuerySet1)

                        vendor_credit_arr.append(QuerySet)
                        payload = json.dumps(QuerySet)
                        bill_date = final_bill[i]['Bill_Date'][0:10]
                        bill_date1 = datetime.strptime(bill_date, '%Y-%m-%d')

                        if (start_date != '' and end_date != ''):
                            if (bill_date1 >= start_date1) and (bill_date1 <= end_date1):
                                post_data_in_qbo(url2, headers, payload,final_bill,_id,job_id,task_id, final_bill[i]['invoice_no'])
                                print("----Multiple Service Vendor Credit------")
                                print("-------------------------------")
                            else:
                                print("No Bill Available")

                        else:
                            post_data_in_qbo(url2, headers, payload,final_bill,_id,job_id,task_id, final_bill[i]['invoice_no'])

                            print("----Multiple Service Vendor Credit------")
                                
            else:
                print("This is not a Item Bill")

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)