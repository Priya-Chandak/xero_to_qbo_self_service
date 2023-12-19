from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo

from apps.home.models import Jobs, JobExecutionStatus
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from apps.util.qbo_util import post_data_in_qbo
from collections import Counter



def add_xero_bill(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')
        
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(
            job_id)
        url1 = f"{base_url}/bill?minorversion=14"
        url2 = f"{base_url}/vendorcredit?minorversion=14"

        myclient = MongoClient("mongodb://localhost:27017/")
        db = myclient["MMC"]

        final_bill1 = db['xero_bill'].find({'job_id':job_id})

        final_bill = []
        for p1 in final_bill1:
            final_bill.append(p1)

        # m1=[]
        # for m in range(0,len(final_bill)):
        #     # if final_bill[m]['LineAmountTypes']=="Exclusive":
        #     if final_bill[m]['Inv_No'] in ["HD 384760992"]: #'Martin Van Eldik','William Lane','June Lane']:#, '51 Artedomus Pickup VDW', '52 Nthside Pick up 99 Emerald', '2396200', '33921 Project: Stone Dev', '2405725', '2415018', '2423617', '0200', '58 99 Design Pick Up', '70 CDK Pick up', 'CMS Waterjet', '3100 Mirador', '2432910', '128 Emerald Repair', '430', '2442386', '0461']:
        #         m1.append(final_bill[m])
        
        # final_bill = m1

        blank=[]

        QBO_COA = db['QBO_COA'].find({'job_id':job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Supplier = db['QBO_Supplier'].find({'job_id':job_id})
        QBO_supplier = []
        for p31 in QBO_Supplier:
            QBO_supplier.append(p31)

        QBO_Item = db['QBO_Item'].find({'job_id':job_id})
        QBO_item = []
        for p4 in QBO_Item:
            QBO_item.append(p4)

        
        QBO_Class = db['QBO_Class'].find({'job_id':job_id})
        QBO_class = []
        for p5 in QBO_Class:
            QBO_class.append(p5)

        QBO_Tax = db['QBO_Tax'].find({'job_id':job_id})
        QBO_tax = []
        for p6 in QBO_Tax:
            QBO_tax.append(p6)

        XERO_COA = db['xero_coa'].find({'job_id':job_id})
        xero_coa1 = []
        for p7 in XERO_COA:
            xero_coa1.append(p7)

        Xero_Items = db['xero_items'].find({'job_id':job_id})
        xero_items = []
        for p8 in Xero_Items:
            xero_items.append(p8)

        bill_arr = []
        vendor_credit_arr = [] 

        bill_bumbers=[]
        for b1 in range(0,len(final_bill)):
            bill_bumbers.append(final_bill[b1]['Inv_No'])

        data1=[]

        frequency_counter = Counter(bill_bumbers)
        for number, count in frequency_counter.items():
            if count>1:
                data1.append({number:count})
        
        key_list = []

        for item in data1:
            keys = list(item.keys())  # Get the keys from the dictionary
            key_list.extend(keys)  # Append the keys to the key_list

        print(key_list,"key_list---------------")

        for i in range(0, len(final_bill)):
            print(final_bill[i])
            _id = final_bill[i]['_id']
            task_id = final_bill[i]['task_id']
            if final_bill[i]["Status"] not in ["VOIDED","DELETED","SUBMITTED","DRAFT"]:
                if 'Line' in final_bill[i]:
                    if final_bill[i]['TotalAmount'] >= 0:
                        if (len(final_bill[i]['Line']) >= 1):
                            QuerySet = {"Line": []}
                            TxnTaxDetail = {'TaxLine': []}
                                
                            for j in range(0, len(final_bill[i]['Line'])):
                                if 'AccountCode' in final_bill[i]['Line'][j]:
                                    if 'ItemCode' in final_bill[i]['Line'][j]:
                                        QuerySet1 = {}
                                        QuerySet2 = {}
                                        QuerySet3 = {}
                                        QuerySet4 = {}
                                        QuerySet5 = {}
                                        TaxLineDetail = {}
                                        TaxRate = {}
                                        Tax = {}
                                        Tax['DetailType'] = "TaxLineDetail"
                                        TxnTaxDetail['TotalTax'] = abs(
                                            final_bill[i]['TotalTax'])
                                        TaxLineDetail['TaxRateRef'] = TaxRate
                                        TaxLineDetail['PercentBased'] = True
                                        Tax['TaxLineDetail'] = TaxLineDetail
                                        TaxCodeRef = {}
                                        ItemRef={}
                                        QuerySet['TotalAmt'] = abs(
                                            final_bill[i]['TotalAmount'])
                                        taxrate1 = 0
                                        QuerySet2['Qty'] = final_bill[i]['Line'][j]['Quantity']
                                        

                                        for k1 in range(0, len(QBO_tax)):
                                            if (final_bill[i]['Line'][j]['TaxType'] == 'BASEXCLUDED')or (final_bill[i]['Line'][j]['TaxType'] == None) or (final_bill[i]['Line'][j]['TaxType'] == "NONE"):
                                                if 'taxrate_name' in QBO_tax[k1]:
                                                    if "NOTAXP" in QBO_tax[k1]['taxrate_name']:
                                                        TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                        TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                        taxrate1 = QBO_tax[k1]['Rate']
                                                        TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                        Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']

                                            elif final_bill[i]['Line'][j]['TaxType'] in ['EXEMPTEXPENSES' ,"EXEMPTOUTPUT","INPUTTAXED","TAX001"]:
                                                if 'taxrate_name' in QBO_tax[k1]:
                                                    if "GST-free (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                        TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                        TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                        taxrate1 = QBO_tax[k1]['Rate']
                                                        TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                        Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                            
                                            elif final_bill[i]['Line'][j]['TaxType'] == 'OUTPUT':
                                                if 'taxrate_name' in QBO_tax[k1]:
                                                    if "GST (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                        TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                        TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                        taxrate1 = QBO_tax[k1]['Rate']
                                                        TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                        Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                            

                                            elif final_bill[i]['Line'][j]['TaxType'] in ['INPUT',"CAPEXINPUT","INPUT2"]:
                                                if 'taxrate_name' in QBO_tax[k1]:
                                                    if "GST (purchases)" in QBO_tax[k1]['taxrate_name'] or "SI" in QBO_tax[k1]['taxrate_name']:
                                                        TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                        TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                        taxrate1 = QBO_tax[k1]['Rate']
                                                        TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                        Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                                        break
                                            

                                            elif final_bill[i]['Line'][j]['TaxType'] in ['EXEMPTEXPENSES' ,"EXEMPTOUTPUT","INPUTTAXED","TAX001"]:
                                                if 'taxrate_name' in QBO_tax[k1]:
                                                    if "GST-free (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                        TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                        TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                        taxrate1 = QBO_tax[k1]['Rate']
                                                        TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                        Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']

                                            else:
                                                pass

                                        if final_bill[i]['LineAmountTypes'] == 'Inclusive':
                                            QuerySet['GlobalTaxCalculation'] = 'TaxInclusive'
                                            QuerySet2['UnitPrice'] = final_bill[i]['Line'][j]['UnitAmount']/(100+taxrate1)*100
                                            QuerySet1['Amount'] = QuerySet2['UnitPrice']*QuerySet2['Qty']
                                        
                                            # QuerySet1['Amount'] = (
                                            #     final_bill[i]['Line'][j]['LineAmount'])/(100+taxrate1)*100
                                            # QuerySet1['Amount'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']

                                        else:
                                            QuerySet['GlobalTaxCalculation'] = 'TaxExcluded'
                                            QuerySet2['UnitPrice'] = final_bill[i]['Line'][j]['UnitAmount']
                                        
                                            # QuerySet1['Amount'] = final_bill[i]['Line'][j]['LineAmount']
                                            QuerySet1['Amount'] = QuerySet2['UnitPrice']*QuerySet2['Qty']

                                            

                                        QuerySet['DocNumber'] = final_bill[i]['Inv_No'][0:21] if final_bill[i]['Inv_No'] not in key_list else final_bill[i]['Inv_No'][0:14]+"-"+final_bill[i]['Inv_ID'][-6:]

                                        if 'Comment' in final_bill[i]:
                                            QuerySet['PrivateNote'] = final_bill[i]['Comment']

                                        QuerySet2['TaxCodeRef'] = TaxCodeRef
                                        QuerySet['TxnDate'] = final_bill[i]['TxnDate']
                                        QuerySet['DueDate'] = final_bill[i]['DueDate']
                                        if 'Description' in final_bill[i]['Line'][j]:
                                            QuerySet1['Description'] = final_bill[i]['Line'][j]['Description']
                                        
                                        QuerySet1['DetailType'] = "ItemBasedExpenseLineDetail"
                                        QuerySet1['ItemBasedExpenseLineDetail'] = QuerySet2
                                        
                                        # for j1 in range(0, len(QBO_coa)):
                                        #     for j2 in range(0, len(xero_coa1)):
                                        #         if 'Code' in xero_coa1[j2]:
                                        #             if 'AccountCode' in final_bill[i]['Line'][j]:
                                        #                 if final_bill[i]['Line'][j]['AccountCode'] == xero_coa1[j2]["Code"]:
                                        #                     if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                                        #                         QuerySet3['value'] = QBO_coa[j1]["Id"]

                                        # QuerySet2['AccountRef'] = QuerySet3

                                        for j3 in range(0, len(QBO_supplier)):
                                            if QBO_supplier[j3]["DisplayName"].startswith(final_bill[i]["ContactName"]) and QBO_supplier[j3]["DisplayName"].endswith(" - S"):
                                                QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                                continue
                                            elif final_bill[i]['ContactName'] == QBO_supplier[j3]['DisplayName']:
                                                QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                                continue
                                            elif final_bill[i]['ContactName'].replace(":","-") == QBO_supplier[j3]['DisplayName'].replace(":","-"):
                                                QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                                continue
                                            else:
                                                pass

                                        # for c1 in range(0, len(QBO_item)):
                                            
                                                
                                        #     if 'AccountCode' in final_bill[i]['Line'][j]:
                                        #         if final_bill[i]['Line'][j]['ItemCode'].replace(":","-")+"-"+final_bill[i]['Line'][j]['AccountCode'] == QBO_item[c1]["Name"]:
                                        #             print("fst if")
                                        #             ItemRef['value'] = QBO_item[c1]["Id"]
                                        #             print(ItemRef)
                                        #             break
                                                
                                                
                                        
                                        
                                        # for p3 in range(0, len(QBO_item)):
                                        #     if "ItemCode" in final_bill[i]["Line"][j] and "AccountCode" in final_bill[i]["Line"][j]:
                                                
                                        #         if "Sku" in QBO_item[p3]:
                                        #             if (
                                        #                 final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                        #                 + "-"
                                        #                 + final_bill[i]["Line"][j]["AccountCode"]
                                        #                 == QBO_item[p3]["Sku"]
                                        #             ):
                                        #                 ItemRef["name"] = QBO_item[p3]["Name"]
                                        #                 ItemRef["value"] = QBO_item[p3]["Id"]
                                        #                 break

                                        #             elif (
                                        #                 final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                        #                 == QBO_item[p3]["Sku"]
                                        #             ):
                                        #                 ItemRef["name"] = QBO_item[p3]["Name"]
                                        #                 ItemRef["value"] = QBO_item[p3]["Id"]
                                        #                 break

                                                
                                        #         elif (
                                        #                 final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                        #                 + "-"
                                        #                 + final_bill[i]["Line"][j]["AccountCode"]
                                        #                 == QBO_item[p3]["FullyQualifiedName"]
                                        #             ):
                                        #             ItemRef["name"] = QBO_item[p3]["Name"]
                                        #             ItemRef["value"] = QBO_item[p3]["Id"]
                                        #             break
                                                
                                        #         elif (
                                        #             final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                        #             == QBO_item[p3]["FullyQualifiedName"]
                                        #         ):
                                        #             ItemRef["name"] = QBO_item[p3]["Name"]
                                        #             ItemRef["value"] = QBO_item[p3]["Id"]
                                        #             break

                                        #     elif "ItemCode" not in final_bill[i]["Line"][j] and "AccountCode" in final_bill[i]["Line"][j]:
                                        #         if "Sku" in QBO_item[p3]:
                                        #             if (
                                        #                 final_bill[i]["Line"][j]["AccountCode"]
                                        #                 == QBO_item[p3]["Sku"]
                                        #             ):
                                        #                 ItemRef["name"] = QBO_item[p3]["Name"]
                                        #                 ItemRef["value"] = QBO_item[p3]["Id"]
                                        #                 break
                                        #         else:
                                        #             for p5 in range(0, len(QBO_coa)):
                                        #                 if "AcctNum" in QBO_coa[p5]:
                                        #                     if (
                                        #                         final_bill[i]["Line"][j][
                                        #                             "AccountCode"
                                        #                         ]
                                        #                         == QBO_coa[p5]["AcctNum"]
                                        #                     ):
                                        #                         if (
                                        #                             QBO_coa[p5]["Name"]
                                        #                             == QBO_item[p3]["Name"]
                                        #                         ):
                                        #                             ItemRef["name"] = QBO_item[p3]["Name"]
                                        #                             ItemRef["value"] = QBO_item[p3]["Id"]
                                        #                             break
                                        ItemRef1={}
                                        for p4 in range(0, len(QBO_item)):
                                            if "ItemCode" in final_bill[i]["Line"][j] and "AccountCode" in final_bill[i]["Line"][j]:
                                                if QBO_item[p4]["Name"].startswith(final_bill[i]["Line"][j]["ItemCode"]) and QBO_item[p4]["Name"].endswith(final_bill[i]["Line"][j]["AccountCode"]):
                                                    ItemRef1["name"] = QBO_item[p4]["Name"]
                                                    ItemRef1["value"] = QBO_item[p4]["Id"]
                                                    print(ItemRef1)
                                                    break

                                        for p3 in range(0, len(QBO_item)):
                                            if "ItemCode" in final_bill[i]["Line"][j]:
                                                if 'Sku' in final_bill[i]["Line"][j]:
                                                    if (
                                                        final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                                        == QBO_item[p3]["Sku"]
                                                    ):
                                                        ItemRef["name"] = QBO_item[p3]["Name"]
                                                        ItemRef["value"] = QBO_item[p3]["Id"]
                                                        break

                                                    elif (
                                                        final_bill[i]["Line"][j]["ItemCode"]==QBO_item[p3]["Sku"]
                                                    ):
                                                        ItemRef["name"] = QBO_item[p3]["Name"]
                                                        ItemRef["value"] = QBO_item[p3]["Id"]
                                                        break
                                                else:
                                                    if (
                                                        final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                                        == QBO_item[p3]["FullyQualifiedName"]
                                                    ):
                                                        ItemRef["name"] = QBO_item[p3]["Name"]
                                                        ItemRef["value"] = QBO_item[p3]["Id"]
                                                        break

                                            elif "ItemCode" not in final_bill[i]["Line"][j] and "AccountCode" in final_bill[i]["Line"][j]:
                                                if "Sku" in QBO_item[p3]:
                                                    print("Sku")
                                                    if (
                                                        final_bill[i]["Line"][j]["AccountCode"]
                                                        == QBO_item[p3]["Sku"]
                                                    ):
                                                        ItemRef["name"] = QBO_item[p3]["Name"]
                                                        ItemRef["value"] = QBO_item[p3]["Id"]
                                                        print(ItemRef)
                                                        break
                                                else:
                                                    for p5 in range(0, len(QBO_coa)):
                                                        if "AcctNum" in QBO_coa[p5]:
                                                            if (
                                                                final_bill[i]["Line"][j][
                                                                    "AccountCode"
                                                                ]
                                                                == QBO_coa[p5]["AcctNum"]
                                                            ):
                                                                if (
                                                                    QBO_coa[p5]["Name"]
                                                                    == QBO_item[p3]["Name"]
                                                                ):
                                                                    ItemRef["name"] = QBO_item[p3]["Name"]
                                                                    ItemRef["value"] = QBO_item[p3]["Id"]
                                                                    break

                                        
                                        if ItemRef1 != {}:
                                            QuerySet2['ItemRef'] = ItemRef1
                                        else:
                                            QuerySet2['ItemRef'] = ItemRef

                                        print(QuerySet2['ItemRef'])
                                        
                                        QuerySet['VendorRef'] = QuerySet4
                                        
                                        # TxnTaxDetail['TaxLine'].append(Tax)
                                        
                                        
                                        arr = TxnTaxDetail['TaxLine']
                                        b1 = {'TaxLine': []}
                                        
                                        b=[]
                                        for i2 in range(0,len(arr)):
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
                                            
                                            for i4 in range(0,len(arr)): 
                                                if arr[i4]['TaxLineDetail']['TaxRateRef']['value'] == e1[k]:
                                                    e['DetailType'] = 'TaxLineDetail'
                                                    TaxLineDetail['TaxRateRef'] = TaxRateRef
                                                    TaxLineDetail['TaxPercent'] = arr[i4]['TaxLineDetail']['TaxPercent']
                                                    TaxRateRef['value'] = e1[k]

                                                    amt = amt + arr[i4]['Amount']
                                                    net_amt = net_amt + arr[i4]['TaxLineDetail']['NetAmountTaxable']
                                                    e['Amount'] = round(amt,2)
                                                    TaxLineDetail['NetAmountTaxable'] = round(net_amt,2)
                                                    e['TaxLineDetail'] = TaxLineDetail
                                                    
                                            new_arr.append(e)
                                        
                                        for k3 in range(0,len(arr)):
                                            if arr[k3]['TaxLineDetail']['TaxRateRef']['value'] in single:
                                                new_arr.append(arr[k3])
                                        
                                        
                                        b1['TaxLine'] = new_arr
                                        # QuerySet['TxnTaxDetail'] = b1
                                        QuerySet['Line'].append(QuerySet1)
                                        
                                        QuerySet2['ClassRef'] = QuerySet5
                                        for j2 in range(0, len(QBO_class)):
                                            if final_bill[i]['Line'][j]['TrackingID'] == QBO_class[j2]['Name']:
                                                QuerySet5['value'] = QBO_class[j2]['Id']
                                                QuerySet5['name'] = QBO_class[j2]['Name']
                                                break
                                    else:
                                        if 'ItemCode' not in final_bill[i]['Line'][j]:
                                            print("Service Bill")
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
                                            # TxnTaxDetail['TotalTax'] = abs(
                                            #     final_bill[i]['TotalTax'])
                                            # TaxLineDetail['TaxRateRef'] = TaxRate
                                            # TaxLineDetail['PercentBased'] = True
                                            # TxnTaxDetail['TaxLine'].append(Tax)
                                            # QuerySet2['Qty'] = final_bill[i]['Line'][j]['Quantity']

                                            # QuerySet['TxnTaxDetail'] = TxnTaxDetail
                                            TaxCodeRef = {}
                                            QuerySet['TotalAmt'] = abs(
                                                final_bill[i]['TotalAmount'])
                                            taxrate1 = 0

                                            for k1 in range(0, len(QBO_tax)):
                                                if (final_bill[i]['Line'][j]['TaxType'] == 'BASEXCLUDED')or (final_bill[i]['Line'][j]['TaxType'] == None) or (final_bill[i]['Line'][j]['TaxType'] == "NONE"):
                                                    if 'taxrate_name' in QBO_tax[k1]:
                                                        if "NOTAXP" in QBO_tax[k1]['taxrate_name']:
                                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                            taxrate1 = QBO_tax[k1]['Rate']
                                                            TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                            Tax['Amount'] = abs(
                                                                final_bill[i]['TotalTax'])

                                                elif final_bill[i]['Line'][j]['TaxType'] in ['EXEMPTEXPENSES' ,"EXEMPTOUTPUT","INPUTTAXED","TAX001"]:
                                                    if 'taxrate_name' in QBO_tax[k1]:
                                                        if "GST-free (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                            taxrate1 = QBO_tax[k1]['Rate']
                                                            TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                            Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                                
                                                elif final_bill[i]['Line'][j]['TaxType'] == 'OUTPUT':
                                                    if 'taxrate_name' in QBO_tax[k1]:
                                                        if "GST (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                            taxrate1 = QBO_tax[k1]['Rate']
                                                            TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                            Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                                

                                                elif final_bill[i]['Line'][j]['TaxType'] in ['INPUT',"CAPEXINPUT",'INPUT2']:
                                                    if 'taxrate_name' in QBO_tax[k1]:
                                                        if "GST (purchases)" in QBO_tax[k1]['taxrate_name'] or "SI" in QBO_tax[k1]['taxrate_name']:
                                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                            taxrate1 = QBO_tax[k1]['Rate']
                                                            TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                            Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                                

                                                elif final_bill[i]['Line'][j]['TaxType'] in ['EXEMPTEXPENSES' ,"EXEMPTOUTPUT","INPUTTAXED","TAX001"]:
                                                    if 'taxrate_name' in QBO_tax[k1]:
                                                        if "GST-free (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                            TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                            TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                            taxrate1 = QBO_tax[k1]['Rate']
                                                            TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                            Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']

                                                else:
                                                    pass

                                            if final_bill[i]['LineAmountTypes'] == 'Inclusive':
                                                QuerySet['GlobalTaxCalculation'] = 'TaxInclusive'
                                                print(final_bill[i]['Line'][j]['LineAmount'])
                                                print(taxrate1)
                                                # QuerySet1['Amount'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                # QuerySet2['UnitPrice'] = final_bill[i]['Line'][j]['UnitAmount']/(100+taxrate1)*100
                                                QuerySet1['Amount'] = final_bill[i]['Line'][j]['LineAmount']/(100+taxrate1)*100

                                            else:
                                                QuerySet['GlobalTaxCalculation'] = 'TaxExcluded'
                                                QuerySet1['Amount'] = final_bill[i]['Line'][j]['LineAmount']
                                            
                                            QuerySet['DocNumber'] = final_bill[i]['Inv_No'][0:21] if final_bill[i]['Inv_No'] not in key_list else final_bill[i]['Inv_No'][0:14]+"-"+final_bill[i]['Inv_ID'][-6:]

                                            if 'Comment' in final_bill[i]:
                                                QuerySet['PrivateNote'] = final_bill[i]['Comment']

                                            QuerySet2['TaxCodeRef'] = TaxCodeRef
                                            QuerySet['TxnDate'] = final_bill[i]['TxnDate']
                                            QuerySet['DueDate'] = final_bill[i]['DueDate']
                                            if 'Description' in final_bill[i]['Line'][j]:
                                                QuerySet1['Description'] = final_bill[i]['Line'][j]['Description']
                                            
                                            QuerySet1['DetailType'] = "AccountBasedExpenseLineDetail"
                                            QuerySet1['AccountBasedExpenseLineDetail'] = QuerySet2
                                            
                                            for j1 in range(0, len(QBO_coa)):
                                                for j2 in range(0, len(xero_coa1)):
                                                    if 'Code' in xero_coa1[j2]:
                                                        if 'AccountCode' in final_bill[i]['Line'][j]:
                                                            if 'AcctNum' in QBO_coa[j1]:
                                                                if final_bill[i]['Line'][j]['AccountCode'] == QBO_coa[j1]["AcctNum"]:
                                                                    QuerySet3['value'] = QBO_coa[j1]["Id"]
                                                                
                                                            elif final_bill[i]['Line'][j]['AccountCode'] == xero_coa1[j2]["Code"]:
                                                                if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                                                                    QuerySet3['value'] = QBO_coa[j1]["Id"]

                                            QuerySet2['AccountRef'] = QuerySet3

                                            for j3 in range(0, len(QBO_supplier)):
                                                if QBO_supplier[j3]["DisplayName"].startswith(final_bill[i]["ContactName"]) and QBO_supplier[j3]["DisplayName"].endswith("- S"):
                                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                                    break
                                                elif final_bill[i]['ContactName'] == QBO_supplier[j3]['DisplayName']:
                                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                                    break
                                                else:
                                                    pass


                                            QuerySet['VendorRef'] = QuerySet4

                                            arr = TxnTaxDetail['TaxLine']
                                            b1 = {'TaxLine': []}
                                            
                                            b=[]
                                            for i2 in range(0,len(arr)):
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
                                                
                                                for i4 in range(0,len(arr)): 
                                                    if arr[i4]['TaxLineDetail']['TaxRateRef']['value'] == e1[k]:
                                                        e['DetailType'] = 'TaxLineDetail'
                                                        TaxLineDetail['TaxRateRef'] = TaxRateRef
                                                        TaxLineDetail['TaxPercent'] = arr[i4]['TaxLineDetail']['TaxPercent']
                                                        TaxRateRef['value'] = e1[k]

                                                        amt = amt + arr[i4]['Amount']
                                                        net_amt = net_amt + arr[i4]['TaxLineDetail']['NetAmountTaxable']
                                                        e['Amount'] = round(amt,2)
                                                        TaxLineDetail['NetAmountTaxable'] = round(net_amt,2)
                                                        e['TaxLineDetail'] = TaxLineDetail
                                                        
                                                new_arr.append(e)
                                            
                                            for k3 in range(0,len(arr)):
                                                if arr[k3]['TaxLineDetail']['TaxRateRef']['value'] in single:
                                                    new_arr.append(arr[k3])
                                            
                                            
                                            b1['TaxLine'] = new_arr
                                            # QuerySet['TxnTaxDetail'] = b1
                                            QuerySet['Line'].append(QuerySet1)
                                        

                                    a = []
                                    for p2 in range(0,len(TxnTaxDetail['TaxLine'])):
                                        if TxnTaxDetail['TaxLine'][p2] in a:
                                            pass
                                        else:
                                            a.append(TxnTaxDetail['TaxLine'][p2])
                                            
                                    TxnTaxDetail['TaxLine'] = a
                                    
                            payload = json.dumps(QuerySet)
                            print(payload)

                            bill_date = final_bill[i]['TxnDate'][0:10]
                            bill_date1 = datetime.strptime(
                                bill_date, '%Y-%m-%d')
                            if (start_date != '' and end_date != ''):
                                if (bill_date1 >= start_date1) and (bill_date1 <= end_date1):
                                    post_data_in_qbo(url1, headers, payload, db["xero_bill"], _id, job_id, task_id, final_bill[i]['Inv_No'])
                                    
                                else:
                                    print("No Bill Available")
                            else:
                                post_data_in_qbo(url1, headers, payload, db["xero_bill"], _id, job_id, task_id, final_bill[i]['Inv_No'])

                        else:

                            QuerySet = {"Line": []}
                            TxnTaxDetail = {'TaxLine': []}
                            
                            for j in range(0, len(final_bill[i]['Line'])):
                                if 'AccountCode' in final_bill[i]['Line']:
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
                                    ItemRef={}
                                    ItemRef1={}
                                    QuerySet['TotalAmt'] = abs(
                                        final_bill[i]['TotalAmount'])
                                    taxrate1 = 0
                                    
                                    for j1 in range(0, len(QBO_item)):
                                        if ('ItemCode' in final_bill[i]['Line'][j]) and ('AccountCode' in final_bill[i]['Line'][j]):
                                            if final_bill[i]['Line'][j]['ItemCode'] == xero_items[j2]['Code']:
                                                
                                                if (final_bill[i]['Line'][j]['Name'].replace(":","-")+"-"+final_bill[i]['Line'][j]['AccountCode']).endswith(QBO_item[j1]["Name"]):
                                                    ItemRef['value'] = QBO_item[j1]["Id"]
                                                    break

                                                elif xero_items[j2]['Name'].replace(":","-")+"-"+final_bill[i]['Line'][j]['AccountCode'] == QBO_item[j1]["Name"]:
                                                    ItemRef['value'] = QBO_item[j1]["Id"]
                                                    break
            
                                                elif xero_items[j2]['Name'].replace(":","-") == QBO_item[j1]["Name"]:
                                                    ItemRef['value'] = QBO_item[j1]["Id"]
                                                    break

                                                elif final_bill[i]['Line'][j]['Name'].replace(":","-").endswith(QBO_item[j1]["Name"]):
                                                    ItemRef['value'] = QBO_item[j1]["Id"]
                                                    break

                                       
                                        elif ('ItemCode' not in final_bill[i]['Line'][j]) and ('AccountCode' in final_bill[i]['Line'][j]):
                                            if final_bill[i]['Line'][j]['AccountCode'] == QBO_item[j1]['Name']:
                                                ItemRef['value'] = QBO_item[j1]["Id"]
                                                break

                                        
                                    QuerySet2['Qty'] = final_bill[i]['Line'][j]['Quantity']
                                        
                                    if ItemRef != {}:
                                        QuerySet2['ItemRef'] = ItemRef

                                    for k1 in range(0, len(QBO_tax)):
                                        if (final_bill[i]['Line'][j]['TaxType'] == 'BASEXCLUDED')or (final_bill[i]['Line'][j]['TaxType'] == None) or (final_bill[i]['Line'][j]['TaxType'] == "NONE"):
                                            if 'taxrate_name' in QBO_tax[k1]:
                                                if "NOTAXP" in QBO_tax[k1]['taxrate_name']:
                                                    TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                    TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                    TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                    taxrate1 = QBO_tax[k1]['Rate']
                                                    Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                                
                                        elif final_bill[i]['Line'][j]['TaxType']in ['INPUT',"CAPEXINPUT"]:
                                            if 'taxrate_name' in QBO_tax[k1]:
                                                if "GST (purchases)" in QBO_tax[k1]['taxrate_name'] or "SI" in QBO_tax[k1]['taxrate_name']:
                                                    TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                    TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                    TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                    taxrate1 = QBO_tax[k1]['Rate']
                                                    TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                    Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                            
                                        elif final_bill[i]['Line'][j]['TaxType'] == 'OUTPUT':
                                            if 'taxrate_name' in QBO_tax[k1]:
                                                if "GST (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                    TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                    TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                    TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                    taxrate1 = QBO_tax[k1]['Rate']
                                                    TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']
                                                    Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']
                                            

                                        elif final_bill[i]['Line'][j]['TaxType'] in ['EXEMPTEXPENSES' ,"EXEMPTOUTPUT","INPUTTAXED","TAX001"]:
                                            if 'taxrate_name' in QBO_tax[k1]:
                                                if "GST-free (purchases)" in QBO_tax[k1]['taxrate_name']:
                                                    TaxRate['value'] = QBO_tax[k1]['taxrate_id']
                                                    TaxCodeRef['value'] = QBO_tax[k1]['taxcode_id']
                                                    TaxLineDetail["TaxPercent"] = QBO_tax[k1]['Rate']
                                                    taxrate1 = QBO_tax[k1]['Rate']
                                                    Tax['Amount'] = final_bill[i]['Line'][j]['TaxAmount']

                                        else:
                                            pass

                                    if final_bill[i]['LineAmountTypes'] == "Inclusive":
                                        QuerySet['GlobalTaxCalculation'] = 'TaxInclusive'
                                        QuerySet2['UnitPrice'] = final_bill[i]['Line'][j]['UnitAmount']/(100+taxrate1)*100
                                        QuerySet1['Amount'] = QuerySet2['UnitPrice']*QuerySet2['Qty']
                                        TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']

                                    else:
                                        QuerySet['GlobalTaxCalculation'] = 'TaxExcluded'
                                        QuerySet2['UnitPrice'] = final_bill[i]['Line'][j]['UnitAmount']
                                    
                                        QuerySet1['Amount'] = abs(
                                            final_bill[i]['Line'][j]['LineAmount'])
                                        TaxLineDetail['NetAmountTaxable'] = final_bill[i]['Line'][j]['UnitAmount']-final_bill[i]['Line'][j]['TaxAmount']

                                    QuerySet['DocNumber'] = final_bill[i]['Inv_No'][0:21] if final_bill[i]['Inv_No'] not in key_list else final_bill[i]['Inv_No'][0:14]+"-"+final_bill[i]['Inv_ID'][-6:]

                                    if 'Comment' in final_bill[i]:
                                        QuerySet['PrivateNote'] = final_bill[i]['Comment']

                                    QuerySet2['TaxCodeRef'] = TaxCodeRef
                                    QuerySet['TxnDate'] = final_bill[i]['TxnDate']
                                    if 'Description' in final_bill[i]['Line'][j]:
                                        QuerySet1['Description'] = final_bill[i]['Line'][j]['Description']
                                    QuerySet1['DetailType'] = "ItemBasedExpenseLineDetail"
                                    QuerySet1['ItemBasedExpenseLineDetail'] = QuerySet2
                                    
                                    # for j1 in range(0, len(QBO_coa)):
                                    #     for j2 in range(0, len(xero_coa1)):
                                    #         if 'Code' in xero_coa1[j2]:
                                    #             if 'AccountCode' in final_bill[i]['Line'][j]:
                                    #                 if final_bill[i]['Line'][j]['AccountCode'] == xero_coa1[j2]["Code"]:
                                    #                     if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                                    #                         QuerySet3['value'] = QBO_coa[j1]["Id"]

                                    # QuerySet2['AccountRef'] = QuerySet3

                                    for j3 in range(0, len(QBO_supplier)):
                                        if QBO_supplier[j3]["DisplayName"].startswith(final_bill[i]["ContactName"]) and QBO_supplier[j3]["DisplayName"].endswith("- S"):
                                            QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                            break
                                        elif final_bill[i]['ContactName'] == QBO_supplier[j3]['DisplayName']:
                                            QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                            break
                                        else:
                                            pass
                                    QuerySet['VendorRef'] = QuerySet4
                                    arr = TxnTaxDetail['TaxLine']
                                    b1 = {'TaxLine': []}
                                    
                                    b=[]
                                    for i2 in range(0,len(arr)):
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
                                        
                                        for i4 in range(0,len(arr)): 
                                            if arr[i4]['TaxLineDetail']['TaxRateRef']['value'] == e1[k]:
                                                e['DetailType'] = 'TaxLineDetail'
                                                TaxLineDetail['TaxRateRef'] = TaxRateRef
                                                TaxLineDetail['TaxPercent'] = arr[i4]['TaxLineDetail']['TaxPercent']
                                                TaxRateRef['value'] = e1[k]

                                                amt = amt + arr[i4]['Amount']
                                                net_amt = net_amt + arr[i4]['TaxLineDetail']['NetAmountTaxable']
                                                e['Amount'] = round(amt,2)
                                                TaxLineDetail['NetAmountTaxable'] = round(net_amt,2)
                                                e['TaxLineDetail'] = TaxLineDetail
                                                
                                        new_arr.append(e)
                                    
                                    for k3 in range(0,len(arr)):
                                        if arr[k3]['TaxLineDetail']['TaxRateRef']['value'] in single:
                                            new_arr.append(arr[k3])
                                    
                                    
                                    b1['TaxLine'] = new_arr
                                    # QuerySet['TxnTaxDetail'] = b1
                                    

                                    QuerySet2['ClassRef'] = QuerySet5

                                    for j2 in range(0, len(QBO_class)):
                                        if final_bill[i]['Line'][j]['TrackingID'] == QBO_class[j2]['Name']:
                                            QuerySet5['value'] = QBO_class[j2]['Id']
                                            QuerySet5['name'] = QBO_class[j2]['Name']
                                            break
                                
                                    QuerySet['Line'].append(QuerySet1)

                                vendor_credit_arr.append(QuerySet)

                                payload = json.dumps(QuerySet)
                                print(payload)
                                bill_date = final_bill[i]['TxnDate'][0:10]
                                bill_date1 = datetime.strptime(bill_date, '%Y-%m-%d')

                                if (start_date != '' and end_date != ''):
                                    if (bill_date1 >= start_date1) and (bill_date1 <= end_date1):
                                        post_data_in_qbo(url2, headers, payload, db["xero_bill"], _id, job_id, task_id, final_bill[i]['Inv_No'])
                                        
                                    else:
                                        print("No Bill Available")
                                else:
                                    post_data_in_qbo(url2, headers, payload, db["xero_bill"], _id, job_id, task_id, final_bill[i]['Inv_No'])

                else:
                    print("This is not a Item Bill")

            else:
                # pass
                print("This is Deleted or Voided Bill")

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex, "error")
        print(ex)