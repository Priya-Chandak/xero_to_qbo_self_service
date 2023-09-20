from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
from datetime import datetime, timedelta, timezone
from collections import Counter



def add_multiple_service_invoice1(job_id, task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(
            job_id)
        
        db = get_mongodb_database()

        multiple_service_invoice = db['service_invoice'].find({'job_id':job_id})
        
        multiple_invoice = []
        for p1 in multiple_service_invoice:
            multiple_invoice.append(p1)

        # m1=[]
        # for m in range(0,len(multiple_invoice)):
        #     # if multiple_invoice[m]['LineAmountTypes']=="Exclusive":
        #     if multiple_invoice[m]['invoice_no'] in ['00002439']:
        #         m1.append(multiple_invoice[m])        
        
        # multiple_invoice = m1

        QBO_Item = db['QBO_Item'].find()
        QBO_item = []
        for p1 in QBO_Item:
            QBO_item.append(p1)

        QBO_Class = db['QBO_Class'].find()
        QBO_class = []
        for p2 in QBO_Class:
            QBO_class.append(p2)

        Myob_Job = db['job'].find()
        Myob_Job1 = []
        for n in range(0,db['job'].count_documents({'job_id':job_id})):
            Myob_Job1.append(Myob_Job[n])


        QBO_Tax = db['QBO_Tax'].find()
        QBO_tax = []
        for p3 in QBO_Tax:
            QBO_tax.append(p3)

        QBO_COA = db['QBO_COA'].find()
        QBO_coa = []
        for p4 in QBO_COA:
            QBO_coa.append(p4)

        QBO_Customer = db['QBO_Customer'].find()
        QBO_customer = []
        for p5 in QBO_Customer:
            QBO_customer.append(p5)

       
        d=[]
        bill_bumbers=[]
        for b1 in range(0,len(multiple_invoice)):
            bill_bumbers.append(multiple_invoice[b1]['invoice_no'])

        data1=[]

        frequency_counter = Counter(bill_bumbers)
        for number, count in frequency_counter.items():
            if count>1:
                data1.append({number:count})
        
        key_list = []
        

        for i in range(0, len(multiple_invoice)):
            print(multiple_invoice[i]['invoice_no'])
            print(i)
            _id=multiple_invoice[i]['_id']
            task_id=multiple_invoice[i]['task_id']
            
            
            invoice = {'Line': []}
            CustomerRef = {}
            BillEmail = {}
            TxnTaxDetail = {'TaxLine': []}
            invoice["TxnDate"] = multiple_invoice[i]["invoice_date"] 
            invoice["DueDate"] = multiple_invoice[i]["due_date"]
            
            invoice['DocNumber'] = multiple_invoice[i]['invoice_no']+"-"+multiple_invoice[i]['UID'][-6:] if multiple_invoice[i]['invoice_no'] in key_list else multiple_invoice[i]['invoice_no'][0:21]
            
            invoice['TotalAmt'] = abs(multiple_invoice[i]['TotalAmount'])
            invoice['HomeTotalAmt'] = abs(multiple_invoice[i]['TotalAmount'])

            subtotal = {}

            print(multiple_invoice[i]["customer_name"])
            for p1 in range(0, len(QBO_customer)):

                if "customer_name" in multiple_invoice[i]:
                    if multiple_invoice[i]["customer_name"].lower().strip() == QBO_customer[p1]["DisplayName"].lower().strip():
                        print("if")
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                    elif (QBO_customer[p1]["DisplayName"]).startswith(multiple_invoice[i]["customer_name"]) and ((QBO_customer[p1]["DisplayName"]).endswith("- C")):
                        print("elif")
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break


            # if 'PrimaryEmailAddr' in QBO_customer[i]:
            #     BillEmail['Address'] = QBO_customer[i][
            #         'PrimaryEmailAddr']['Address']

            if multiple_invoice[i]['IsTaxInclusive'] == True:
                invoice['GlobalTaxCalculation'] = 'TaxInclusive'
            else:
                invoice['GlobalTaxCalculation'] = 'TaxExcluded'

            total_val = 0
            taxrate1 = 0
            line_amount = 0

            for j in range(len(multiple_invoice[i]['account'])):
                if multiple_invoice[i]['account'][j]['discount'] == None:
                    discount_value = 0
                else:
                    discount_value = multiple_invoice[i]['account'][j]['discount']
                
                if (multiple_invoice[i]['account'][j]['unit_count']==0) or (multiple_invoice[i]['account'][j]['unit_count']==None):
                    multiple_invoice[i]['account'][j]['unit_count']=1
                else:
                    multiple_invoice[i]['account'][j]['unit_count']=multiple_invoice[i]['account'][j]['unit_count']

                if "DisplayID" in multiple_invoice[i]['account'][j]:
                    TaxLineDetail = {}
                    CustomerMemo = {}
                    salesitemline = {}
                    discount = {}
                    rounding = {}
                    SalesItemLineDetail = {}
                    discount_SalesItemLineDetail = {}
                    rounding_SalesItemLineDetail = {}
                    ItemRef = {}
                    ClassRef = {}
                    TaxCodeRef = {}
                    ItemAccountRef = {}
                    TaxRate = {}
                    SubTotalLineDetail = {}
                    TaxDetail = {}
                    salesitemline["DetailType"] = "SalesItemLineDetail"
                    discount['Description'] = 'Discount'
    
                    for p3 in range(0, len(QBO_item)):
                        salesitemline['Description'] = multiple_invoice[i]['account'][j]['description']
                        if 'acc_id' in multiple_invoice[i]['account'][j]: 
                            if multiple_invoice[i]['account'][j]['acc_id'] == QBO_item[
                                    p3]['Name']:
                                ItemRef['name'] = QBO_item[p3]['Name']
                                ItemRef['value'] = QBO_item[p3]['Id']
                                break
                        
                    
                    for p4 in range(0, len(QBO_class)):
                        for j4 in range(0,len(Myob_Job1)):
                            if ('job' in multiple_invoice[i]['account'][j]) and (multiple_invoice[i]['account'][j]['job']!=None):
                                if multiple_invoice[i]['account'][j]['job']['Name'] == Myob_Job1[j4]['Name']:
                                    if (QBO_class[p4]['FullyQualifiedName'].startswith(Myob_Job1[j4]['Name'])) and (QBO_class[p4]['FullyQualifiedName'].endswith(Myob_Job1[j4]['Number'])):
                                        ClassRef['value'] = QBO_class[p4]['Id']
                                        ClassRef['name'] = QBO_class[p4]['Name']


                    for p5 in range(0, len(QBO_coa)):
                        if 'account_name' in multiple_invoice[i]['account'][j]:
                            if multiple_invoice[i]['account'][j]['account_name'] == QBO_coa[p5]['Name']:
                                ItemAccountRef['name'] = QBO_coa[p5]['Name']
                                ItemAccountRef['value'] = QBO_coa[p5]['Id']

                    for p6 in range(0, len(QBO_tax)):
                        if 'taxcode' in multiple_invoice[i]['account'][j]:
                            if (multiple_invoice[i]['account'][j]['taxcode'] == "GST") or (multiple_invoice[i]['account'][j]['taxcode'] == "GCA"):
                                if 'taxrate_name' in QBO_tax[p6]:
                                    if 'GST (sales)' in QBO_tax[p6]['taxrate_name']:
                                        TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                        taxrate = QBO_tax[p6]['Rate']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6][
                                            'Rate']
                                        TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                        taxrate1 = taxrate
                                        total_val = total_val + \
                                            multiple_invoice[i]['account'][j]['amount'] / \
                                            (100+taxrate1)*100

                            elif multiple_invoice[i]['account'][j]['taxcode'] == "CAP":
                                if 'taxrate_name' in QBO_tax[p6]:
                                    if 'GST (sales)' in QBO_tax[p6]['taxrate_name']:
                                        TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                        taxrate = QBO_tax[p6]['Rate']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6]['Rate']
                                        TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                        taxrate1 = taxrate
                                        total_val += multiple_invoice[i]['account'][j][
                                            'amount'] / (100 + taxrate1) * 100

                            elif multiple_invoice[i]['account'][j]['taxcode'] in ["FRE","EXP"]:
                                if 'taxrate_name' in QBO_tax[p6]:
                                    if 'GST free (sales)' in QBO_tax[p6][
                                            'taxrate_name']:
                                        TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                        taxrate = QBO_tax[p6]['Rate']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6][
                                            'Rate']
                                        TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                        taxrate1 = taxrate
                                        total_val += multiple_invoice[i]['account'][j]['amount'] / \
                                            (100+taxrate1)*100

                            elif multiple_invoice[i]['account'][j]['taxcode'] == "N-T":
                                if 'taxrate_name' in QBO_tax[p6]:
                                    if 'NOTAXS' in QBO_tax[p6][
                                            'taxrate_name']:
                                        TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                        taxrate = QBO_tax[p6]['Rate']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6]['Rate']
                                        TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                        taxrate1 = taxrate
                                        total_val += multiple_invoice[i]['account'][j][
                                            'amount'] / (100 + taxrate1) * 100

                            elif multiple_invoice[i]['account'][j]['taxcode'] == QBO_tax[
                                    p6]['taxcode_name']:
                                TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                taxrate = QBO_tax[p6]['Rate']
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]['Rate']
                                TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                taxrate1 = taxrate
                                total_val += multiple_invoice[i]['account'][j]['amount'] / \
                                    (100+taxrate1)*100
                            else:
                                pass

                            if multiple_invoice[i]['IsTaxInclusive'] == False:

                                if multiple_invoice[i]['Subtotal'] >= 0:
                                    SalesItemLineDetail['Qty'] = 1
                                    SalesItemLineDetail[
                                        'UnitPrice'] = multiple_invoice[i]['account'][j][
                                            'amount']
                                    salesitemline["Amount"] = SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                    subtotal['Amount'] = multiple_invoice[i][
                                        'Subtotal']
                                    TxnTaxDetail['TotalTax'] = multiple_invoice[i][
                                        'TotalTax']
                                
                                    if taxrate1 != 0:
                                        TaxDetail['Amount'] = multiple_invoice[i][
                                            'TotalTax']
                                        TaxLineDetail[
                                            'NetAmountTaxable'] = multiple_invoice[i][
                                                'Subtotal'] - multiple_invoice[i][
                                                    'TotalTax']
                                    else:
                                        TaxDetail['Amount'] = 0
                                        TaxLineDetail['NetAmountTaxable'] = 0

                                        
                                    if ('discount' in multiple_invoice[i]['account'][j]) and (discount_value!=None):
            
                                        discount_SalesItemLineDetail['Qty'] = 1
                                        discount_SalesItemLineDetail['UnitPrice'] = -(
                                            1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value
                                        ) / 100
                                        discount['Amount'] = -(
                                            1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value
                                        ) / 100

                                        
                                else:
                                    if ('discount' in multiple_invoice[i]['account'][j]) and (discount_value!=None):
            
                                        discount_SalesItemLineDetail['Qty'] = -1
                                        discount_SalesItemLineDetail['UnitPrice'] = (
                                            1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value
                                        ) / 100
                                        discount['Amount'] = (
                                            1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value
                                        ) / 100

                                        # SalesItemLineDetail['Qty'] = -1
                                        # SalesItemLineDetail[
                                        #     'UnitPrice'] = multiple_invoice[i]['account'][j][
                                        #         'amount']
                                        # salesitemline["Amount"] = SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                        
                                        # subtotal[
                                        #     'Amount'] = -multiple_invoice[i]['Subtotal']
                                        # TxnTaxDetail[
                                        #     'TotalTax'] = -multiple_invoice[i]['TotalTax']

                                        # if taxrate1 != 0:
                                        #     TaxDetail['Amount'] = multiple_invoice[i][
                                        #         'TotalTax']
                                        #     TaxLineDetail[
                                        #         'NetAmountTaxable'] = multiple_invoice[i][
                                        #             'Subtotal'] - multiple_invoice[i][
                                        #                 'TotalTax']
                                        # else:
                                        #     if (multiple_invoice[i]['account'][j]['taxcode'] == 'GST') or (multiple_invoice[i]['account'][j]['taxcode'] == 'GCA'):
                                        #         TaxDetail['Amount'] = -multiple_invoice[i][
                                        #             'TotalTax']
                                        #         TaxLineDetail[
                                        #             'NetAmountTaxable'] = -round(multiple_invoice[
                                        #                 i]['Account'][j]['amount'] / (
                                        #                     100 + taxrate1) * 100,2)
                                        #     elif multiple_invoice[i]['account'][j][
                                        #             'taxcode'] in ["FRE","EXP"]:
                                        #         TaxDetail['Amount'] = 0
                                        #         TaxLineDetail[
                                        #             'NetAmountTaxable'] = -round(multiple_invoice[
                                        #                 i]['Account'][j]['amount'],2)
                                        #     elif multiple_invoice[i]['account'][j][
                                        #             'taxcode'] == "N-T":
                                        #         TaxDetail['Amount'] = 0
                                        #         TaxLineDetail[
                                        #             'NetAmountTaxable'] = -round(multiple_invoice[
                                        #                 i]['Account'][j]['amount'],2)

                                    invoice['TxnTaxDetail'] = TxnTaxDetail
                                    TaxDetail['DetailType'] = "TaxLineDetail"
                                    TaxDetail['TaxLineDetail'] = TaxLineDetail
                                    TaxLineDetail['TaxRateRef'] = TaxRate
                                    TaxLineDetail['PercentBased'] = True

                            else:
                               
                                
                                if multiple_invoice[i]['Subtotal'] >= 0:
                                    SalesItemLineDetail['Qty'] = 1
                                        #                 SalesItemLineDetail['UnitPrice'] = abs(multiple_invoice[i]['account'][j]['amount'])
                                    SalesItemLineDetail['UnitPrice'] = round(
                                        multiple_invoice[i]['account'][j]['amount'] /
                                        (100 + taxrate1) * 100, 2)
                                    salesitemline["Amount"] = SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                    
                                    subtotal['Amount'] = multiple_invoice[i][
                                        'Subtotal'] - multiple_invoice[i]['TotalTax']
                                    TxnTaxDetail['TotalTax'] = multiple_invoice[i][
                                        'TotalTax']

                                        
                                    if ('discount' in multiple_invoice[i]['account'][j]) and (discount_value!=None):
            
                                        discount_SalesItemLineDetail['Qty'] = 1
                                        discount_SalesItemLineDetail['UnitPrice'] = -round(
                                            (1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value /
                                            (100 + taxrate1)), 2)
                                        discount['Amount'] = -round(
                                            (1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value /
                                            (100 + taxrate1)), 2)

                                else:
                                    SalesItemLineDetail['Qty'] = -1
                                    #                 SalesItemLineDetail['UnitPrice'] = abs(multiple_invoice[i]['account'][j]['amount'])
                                    SalesItemLineDetail['UnitPrice'] = round(
                                        multiple_invoice[i]['account'][j]['amount'] /
                                        (100 + taxrate1) * 100, 2)
                                    salesitemline["Amount"] = SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                    
                                    
                                    
                                    subtotal['Amount'] = -(
                                        multiple_invoice[i]['Subtotal'] -
                                        multiple_invoice[i]['TotalTax'])
                                    TxnTaxDetail[
                                        'TotalTax'] = -multiple_invoice[i]['TotalTax']

                                    if ('discount' in multiple_invoice[i]['account'][j]) and (discount_value!=None):
            
                                        discount_SalesItemLineDetail['Qty'] = -1
                                        discount_SalesItemLineDetail['UnitPrice'] = round(
                                            (1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value /
                                            (100 + taxrate1)), 2)
                                        discount['Amount'] = round(
                                            (1 *
                                            multiple_invoice[i]['account'][j]['amount'] *
                                            discount_value /
                                            (100 + taxrate1)), 2)

            #                 salesitemline["Amount"] = abs(round(
            #                     (multiple_invoice[i]['account'][j]['amount']*1/(100+taxrate1)*100), 2))
            #                 subtotal['Amount'] = abs(round((total_val), 2))
                            invoice['TxnTaxDetail'] = TxnTaxDetail
                            TaxDetail['DetailType'] = "TaxLineDetail"
                            TaxDetail['TaxLineDetail'] = TaxLineDetail
                            TaxLineDetail['TaxRateRef'] = TaxRate
                            TaxLineDetail['PercentBased'] = True

                            if multiple_invoice[i]['Subtotal'] >= 0:
                                if (multiple_invoice[i]['account'][j]['taxcode'] == 'GST') or (multiple_invoice[i]['account'][j]['taxcode'] == 'GCA'):

                                    TaxDetail['Amount'] = multiple_invoice[i][
                                        'TotalTax']
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = multiple_invoice[i][
                                            'Account'][j]['amount'] / (100 +
                                                                    taxrate1) * 100
                                elif multiple_invoice[i]['account'][j]['taxcode'] in ["FRE","EXP"]:
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = multiple_invoice[i][
                                            'Account'][j]['amount']
                                elif multiple_invoice[i]['account'][j][
                                        'taxcode'] == "N-T":
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = multiple_invoice[i][
                                            'Account'][j]['amount']
                                else:
                                    pass
                            else:
                                
                                if (multiple_invoice[i]['account'][j]['taxcode'] == 'GST') or (multiple_invoice[i]['account'][j]['taxcode'] == 'GCA'):

                                    TaxDetail['Amount'] = -multiple_invoice[i][
                                        'TotalTax']
                                    TaxLineDetail['NetAmountTaxable'] = TaxDetail[
                                        'Amount'] * taxrate1
                                elif multiple_invoice[i]['account'][j]['taxcode'] in ["FRE","EXP"]:
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = -multiple_invoice[i][
                                            'Account'][j]['amount']
                                elif multiple_invoice[i]['account'][j][
                                        'taxcode'] == "N-T":
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = -multiple_invoice[i][
                                            'Account'][j]['amount']
                                else:
                                    pass

                    subtotal['DetailType'] = "SubTotalLineDetail"
                    subtotal['SubTotalLineDetail'] = SubTotalLineDetail
                    salesitemline["DetailType"] = "SalesItemLineDetail"
                    salesitemline["SalesItemLineDetail"] = SalesItemLineDetail
                    
                    SalesItemLineDetail["ItemRef"] = ItemRef
                    SalesItemLineDetail["ClassRef"] = ClassRef
                    SalesItemLineDetail['TaxCodeRef'] = TaxCodeRef
                    SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                    discount["DetailType"] = "SalesItemLineDetail"
                    discount["SalesItemLineDetail"] = discount_SalesItemLineDetail
                    discount_SalesItemLineDetail["ItemRef"] = ItemRef
                    discount_SalesItemLineDetail["ClassRef"] = ClassRef
                    discount_SalesItemLineDetail['TaxCodeRef'] = TaxCodeRef
                    discount_SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                    invoice["BillEmail"] = BillEmail
                    invoice["CustomerRef"] = CustomerRef

                    print("salesitemline",salesitemline)
                    invoice['Line'].append(salesitemline)
                   
                    if ('discount' in multiple_invoice[i]['account'][j]) and (discount_value!=None):

                        if 'discount' in multiple_invoice[i]['account'][j]: 
                            if discount_value > 0:
                                
                                invoice["Line"].append(discount)
                    
                    if ('discount' in multiple_invoice[i]['account'][j]) and (discount_value==None):
                        discount['Amount']=0
                        if multiple_invoice[i]['IsTaxInclusive'] == False:
                            salesitemline["Amount"]=multiple_invoice[i]['account'][j]['amount']
                        else:
                            salesitemline["Amount"]=multiple_invoice[i]['account'][j]['amount']/(100+taxrate1)*100

                        TxnTaxDetail['TaxLine'].append(TaxDetail)
                        line_amount = line_amount + salesitemline["Amount"] + discount['Amount']
                        line_amount1 = line_amount + multiple_invoice[i]['TotalTax']

            a = []

            for p2 in range(0, len(TxnTaxDetail['TaxLine'])):
                if TxnTaxDetail['TaxLine'][p2] in a:
                    pass
                else:
                    a.append(TxnTaxDetail['TaxLine'][p2])

            TxnTaxDetail['TaxLine'] = a
            invoice["Line"].append(subtotal)


            if len(a) >= 1:
                if multiple_invoice[i]['IsTaxInclusive'] == True:
                    if line_amount1 == multiple_invoice[i]['TotalAmount']:
                        pass
                    else:
                        line_amount == multiple_invoice[i][
                            'TotalAmount'] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}
                            rounding_SalesItemLineDetail['Qty'] = 1

                            if multiple_invoice[i]['Subtotal'] >= 0:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = round(
                                        abs(multiple_invoice[i]['TotalAmount'])
                                        - line_amount1, 2)
                                rounding['Amount'] = round(
                                    abs(multiple_invoice[i]['TotalAmount']) -
                                    line_amount1, 2)
                            else:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = round(
                                        abs(multiple_invoice[i]['TotalAmount']
                                            - multiple_invoice[i]['TotalTax'])
                                        - line_amount, 2)
                                rounding['Amount'] = round(
                                    abs(multiple_invoice[i]['TotalAmount'] -
                                        multiple_invoice[i]['TotalTax']) -
                                    line_amount, 2)

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"] = rounding_SalesItemLineDetail
                            
                            for p3 in range(0, len(QBO_item)):
                                if QBO_item[p3]["FullyQualifiedName"]=='Rounding':
                                    ItemRef['name'] = QBO_item[p3]["FullyQualifiedName"]
                                    ItemRef['value'] = QBO_item[p3]["Id"]
                                    ItemAccountRef['name'] = QBO_item[p3]["IncomeAccountRef"]["name"]
                                    ItemAccountRef['value'] = QBO_item[p3]["IncomeAccountRef"]["value"]
                            
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail[
                                'TaxCodeRef'] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"] = ItemAccountRef
                            TaxDetail['DetailType'] = "TaxLineDetail"
                            TaxDetail['TaxLineDetail'] = TaxLineDetail
                            TaxDetail['Amount'] = 0
                            TaxLineDetail['NetAmountTaxable'] = rounding[
                                'Amount']
                            
                            for p6 in range(0,len(QBO_tax)):
                                if 'GST free (sales)' in QBO_tax[p6][
                                        'taxrate_name']:
                                    TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                    TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                    TaxLineDetail['TaxPercent'] = QBO_tax[p6]['Rate']
                            
                            TaxLineDetail['TaxRateRef'] = TaxRate
                            TaxLineDetail['PercentBased'] = True
                            TxnTaxDetail['TaxLine'].append(TaxDetail)

                            invoice['Line'].append(rounding)

                else:
                    
                    if line_amount1 == multiple_invoice[i]['TotalAmount']:
                        pass
                    else:
                        line_amount == multiple_invoice[i][
                            'TotalAmount'] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}

                            rounding_SalesItemLineDetail['Qty'] = 1
                            if multiple_invoice[i]['Subtotal'] >= 0:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = multiple_invoice[i][
                                        'TotalAmount'] - line_amount1
                                rounding['Amount'] = multiple_invoice[i][
                                    'TotalAmount'] - line_amount1
                            else:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = multiple_invoice[i][
                                        'TotalAmount'] + line_amount1
                                rounding['Amount'] = multiple_invoice[i][
                                    'TotalAmount'] + line_amount1

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"] = rounding_SalesItemLineDetail
                                
                            for p3 in range(0, len(QBO_item)):
                                if QBO_item[p3]["FullyQualifiedName"]=='Rounding':
                                    ItemRef['name'] = QBO_item[p3]["FullyQualifiedName"]
                                    ItemRef['value'] = QBO_item[p3]["Id"]
                                    ItemAccountRef['name'] = QBO_item[p3]["IncomeAccountRef"]["name"]
                                    ItemAccountRef['value'] = QBO_item[p3]["IncomeAccountRef"]["value"]
                            
                            for p6 in range(0,len(QBO_tax)):
                                if 'GST free (sales)' in QBO_tax[p6][
                                        'taxrate_name']:
                                    TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                    TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                            
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail[
                                'TaxCodeRef'] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"] = ItemAccountRef
                            TaxDetail['DetailType'] = "TaxLineDetail"
                            TaxDetail['TaxLineDetail'] = TaxLineDetail
                            TaxDetail['Amount'] = 0
                            TaxLineDetail['NetAmountTaxable'] = rounding[
                                'Amount']
                            
                            TaxLineDetail['TaxRateRef'] = TaxRate
                            TaxLineDetail['PercentBased'] = True
                            TxnTaxDetail['TaxLine'].append(TaxDetail)

                            invoice['Line'].append(rounding)

            else:
                pass

            arr = TxnTaxDetail['TaxLine']
            print(arr)
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
                    
            # TxnTaxDetail['TxnTaxDetail'] = b1
            # TxnTaxDetail['TaxLine'].append(TaxDetail)

            invoice['TxnTaxDetail'] = b1
            
            

            invoice["Line"].append(subtotal)
            
            # if invoice['Line'][j-1]['SalesItemLineDetail']['ItemRef'] != {}:
            if len(invoice['Line'])>0:
                if multiple_invoice[i]['TotalAmount'] >= 0:
                    url1 = "{}/invoice?minorversion=14".format(base_url)
                    payload = json.dumps(invoice)
                    print(payload)
                    inv_date = multiple_invoice[i]["invoice_date"][0:10]
                    inv_date1 = datetime.strptime(inv_date, '%Y-%m-%d')
                    
                    if (start_date != '' and end_date != ''):
                    
                        if (inv_date1 >= start_date1) and (inv_date1 <= end_date1):
                            
                            post_data_in_qbo(url1, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                            
                            
                        else:
                            print("No Invoice Available in Between These dates")
                    else:
                        print("---")
                        post_data_in_qbo(url1, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                            
                
                else:
                    url2 = "{}/creditmemo?minorversion=14".format(base_url)
                    payload = json.dumps(invoice)
                    print(payload)
                    inv_date = multiple_invoice[i]["invoice_date"][0:10]
                    inv_date1 = datetime.strptime(inv_date, '%Y-%m-%d')
                    if (start_date != '' and end_date != ''):
                        if (inv_date1 >= start_date1) and (inv_date1 <= end_date1):
                        
                            post_data_in_qbo(url2, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                            
                        else:
                            print("No Creditmemo Available in Between These dates")

                    else:
                        post_data_in_qbo(url2, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                            
            else:
                add_job_status(job_id, "Unable to add invoice because Item is not present in QBO : {}".format(multiple_invoice[i]['invoice_no']) )
                print("Unable to add invoice because Item is not present in QBO")

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)



from math import expm1
import requests
import json
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from collections import Counter

from apps.util.qbo_util import post_data_in_qbo


from datetime import datetime, timedelta, timezone


def add_multiple_service_invoice(job_id,task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(
            job_id)
        
        db = get_mongodb_database()

        multiple_service_invoice = db['service_invoice']
        
        multiple_invoice = []
        for p1 in db['service_invoice'].find({"job_id":job_id}):
            multiple_invoice.append(p1)

        # a1=[]
        # for mi in range(0,len(multiple_invoice)):
        #     if multiple_invoice[mi]['invoice_no'] in ['IXP2016111717', 'IXP2016111765', 'IXP2016111766', 'IXP2016111817', 'IXP2016112158', 'IXP2016112233', '02021038', '02021344', '02021452', '02021482', '02021531', '02021531', '02021531', '02021541']:
        #         a1.append(multiple_invoice[mi])

        QBO_Item = db['QBO_Item'].find({"job_id":job_id})
        QBO_item = []
        for p1 in QBO_Item:
            QBO_item.append(p1)

        QBO_Class = db['QBO_Class'].find({"job_id":job_id})
        QBO_class = []
        for p2 in QBO_Class:
            QBO_class.append(p2)

        QBO_Tax = db['QBO_Tax'].find({"job_id":job_id})
        QBO_tax = []
        for p3 in QBO_Tax:
            QBO_tax.append(p3)

        QBO_COA = db['QBO_COA'].find({"job_id":job_id})
        QBO_coa = []
        for p4 in QBO_COA:
            QBO_coa.append(p4)

        QBO_Customer = db['QBO_Customer'].find({"job_id":job_id})
        QBO_customer = []
        for p5 in QBO_Customer:
            QBO_customer.append(p5)

        
        bill_bumbers=[]
        for b1 in range(0,len(multiple_invoice)):
            bill_bumbers.append(multiple_invoice[b1]['invoice_no'])

        data1=[]

        frequency_counter = Counter(bill_bumbers)
        for number, count in frequency_counter.items():
            if count>1:
                data1.append({number:count})
        
        key_list = []

        # multiple_invoice=a1
        
        blank=[]
        for i in range(0, len(multiple_invoice)):
            _id=multiple_invoice[i]['_id']
            task_id=multiple_invoice[i]['task_id']
            print(i)
            
            invoice = {'Line': []}
            CustomerRef = {}
            BillEmail = {}
            TxnTaxDetail = {'TaxLine': []}
            invoice["TxnDate"] = multiple_invoice[i]["invoice_date"]
            invoice["DueDate"] = multiple_invoice[i]["due_date"]
            invoice['DocNumber'] = multiple_invoice[i]['invoice_no']+"-"+multiple_invoice[i]['UID'][-6:] if multiple_invoice[i]['invoice_no'] in key_list else multiple_invoice[i]['invoice_no'][0:21]
            invoice['TotalAmt'] = abs(multiple_invoice[i]['TotalAmount'])
            invoice['HomeTotalAmt'] = abs(multiple_invoice[i]['TotalAmount'])

            subtotal = {}

            for p1 in range(0, len(QBO_customer)):

                if "customer_name" in multiple_invoice[i]:
                    if multiple_invoice[i]["customer_name"].strip() == QBO_customer[
                            p1]["DisplayName"].strip():
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                    elif (QBO_customer[p1]["DisplayName"]).startswith(multiple_invoice[i]["customer_name"]) and ((QBO_customer[p1]["DisplayName"]).endswith("-C")):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                    elif multiple_invoice[i]["customer_name"].replace("\n","") == QBO_customer[
                            p1]["DisplayName"].strip():
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                    elif multiple_invoice[i]["customer_name"].replace(":","-") == QBO_customer[
                            p1]["DisplayName"].strip():
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                    

            # if 'PrimaryEmailAddr' in QBO_customer[i]:
            #     BillEmail['Address'] = QBO_customer[i][
            #         'PrimaryEmailAddr']['Address']

            if multiple_invoice[i]['IsTaxInclusive'] == True:
                invoice['GlobalTaxCalculation'] = 'TaxInclusive'
            else:
                invoice['GlobalTaxCalculation'] = 'TaxExcluded'

            total_val = 0
            taxrate1 = 0
            line_amount = 0

            for j in range(len(multiple_invoice[i]['account'])):
                if multiple_invoice[i]['account'][j]['discount'] == None:
                    discount_value = 0
                else:
                    discount_value = multiple_invoice[i]['account'][j]['discount']
                
                if (multiple_invoice[i]['account'][j]['unit_count']==0) or (multiple_invoice[i]['account'][j]['unit_count']==None):
                    multiple_invoice[i]['account'][j]['unit_count']=1
                else:
                    multiple_invoice[i]['account'][j]['unit_count']=multiple_invoice[i]['account'][j]['unit_count']

                
                if "acc_id" in multiple_invoice[i]['account'][j]:
                    TaxLineDetail = {}
                    CustomerMemo = {}
                    salesitemline = {}
                    discount = {}
                    rounding = {}
                    SalesItemLineDetail = {}
                    discount_SalesItemLineDetail = {}
                    rounding_SalesItemLineDetail = {}
                    ItemRef = {}
                    ClassRef = {}
                    TaxCodeRef = {}
                    ItemAccountRef = {}
                    TaxRate = {}
                    SubTotalLineDetail = {}
                    TaxDetail = {}
                    salesitemline["DetailType"] = "SalesItemLineDetail"
                    discount['Description'] = 'Discount'

                    # if multiple_invoice[i]['account'][j]['unit_count'] == 0:
                    #     multiple_invoice[i]['account'][j]['unit_count'] = multiple_invoice[i]['account'][j]['unit_count']
                    # else:
                    #     multiple_invoice[i]['account'][j]['unit_count'] = multiple_invoice[i]['account'][j]['unit_count']
                    # if 'unit_count' in multiple_invoice[i]['account'][j]:
                    #     if multiple_invoice[i]['account'][j]['unit_count'] == 0:
                    #         multiple_invoice[i]['account'][j]['unit_count']=1
                    # else:
                    #     multiple_invoice[i]['account'][j]['unit_count']=0
                    
                    if multiple_invoice[i]['account'][j]['unit_price'] in [0, None]:
                        multiple_invoice[i]['account'][j]['unit_price']=multiple_invoice[i]['account'][j]['amount']
                    
                        
                    for p3 in range(0, len(QBO_item)):
                        salesitemline['Description'] = multiple_invoice[i]['account'][j]['description']
                        if 'acc_id' in multiple_invoice[i]['account'][j]:
                            if multiple_invoice[i]['account'][j]['acc_id'] == QBO_item[
                                    p3]['Name']:
                                ItemRef['name'] = QBO_item[p3]['Name']
                                ItemRef['value'] = QBO_item[p3]['Id']
                        
                    
                    # for p3 in range(0, len(QBO_item)):
                    #     salesitemline['Description'] = multiple_invoice[i]['account'][j]['description']
                    #     if 'item_name' in multiple_invoice[i]['account'][j]: 
                    #         if multiple_invoice[i]['account'][j]['item_name'].lower().strip() == QBO_item[
                    #                 p3]['Name'].lower().strip():
                    #             ItemRef['name'] = QBO_item[p3]['Name']
                    #             ItemRef['value'] = QBO_item[p3]['Id']
                    #     elif 'acc_id' in multiple_invoice[i]['account'][j]:
                    #         if multiple_invoice[i]['account'][j]['acc_id'] == QBO_item[
                    #                 p3]['Name']:
                    #             ItemRef['name'] = QBO_item[p3]['Name']
                    #             ItemRef['value'] = QBO_item[p3]['Id']
                    #     else:
                    #         pass

                    for p4 in range(0, len(QBO_class)):
                        if multiple_invoice[i]['account'][j]['job'] != None:
                            if multiple_invoice[i]['account'][j]['job'] == QBO_class[
                                    p4]["Name"]:
                                ClassRef['name'] = QBO_class[p4]["Name"]
                                ClassRef['value'] = QBO_class[p4]["Id"]
                            else:
                                pass

                    for p5 in range(0, len(QBO_coa)):
                        if 'acc_name' in multiple_invoice[i]['account'][j]:
                            if multiple_invoice[i]['account'][j]['acc_name'] == QBO_coa[p5]['Name']:
                                ItemAccountRef['name'] = QBO_coa[p5]['Name']
                                ItemAccountRef['value'] = QBO_coa[p5]['Id']

                    for p6 in range(0, len(QBO_tax)):
                        if 'taxcode' in multiple_invoice[i]['account'][j]:
                            if multiple_invoice[i]['account'][j]['taxcode'] == "GST":
                                if 'taxrate_name' in QBO_tax[p6]:
                                    if 'GST (sales)' in QBO_tax[p6]['taxrate_name']:
                                        TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                        taxrate = QBO_tax[p6]['Rate']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6][
                                            'Rate']
                                        TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                        taxrate1 = taxrate
                                        total_val = total_val + \
                                            multiple_invoice[i]['account'][j]['amount'] / \
                                            (100+taxrate1)*100

                            elif multiple_invoice[i]['account'][j]['taxcode'] == "CAP":
                                if 'GST (sales)' in QBO_tax[p6]['taxcode_name']:
                                    TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                    taxrate = QBO_tax[p6]['Rate']
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]['Rate']
                                    TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                    taxrate1 = taxrate
                                    total_val += multiple_invoice[i]['account'][j][
                                        'amount'] / (100 + taxrate1) * 100

                            elif multiple_invoice[i]['account'][j]['taxcode'] in ["FRE","EXP"]:
                                if 'taxrate_name' in QBO_tax[p6]:
                                    if 'GST free (sales)' in QBO_tax[p6][
                                            'taxrate_name']:
                                        TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                        taxrate = QBO_tax[p6]['Rate']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6][
                                            'Rate']
                                        TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                        taxrate1 = taxrate
                                        total_val += multiple_invoice[i]['account'][j]['amount'] / \
                                            (100+taxrate1)*100

                            elif multiple_invoice[i]['account'][j]['taxcode'] == "N-T":
                                if 'taxrate_name'in QBO_tax[p6]: 
                                    if 'NOTAXS' in QBO_tax[p6]['taxrate_name']:
                                        TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                        taxrate = QBO_tax[p6]['Rate']
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6]['Rate']
                                        TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                        taxrate1 = taxrate
                                        total_val += multiple_invoice[i]['account'][j][
                                            'amount'] / (100 + taxrate1) * 100

                            elif multiple_invoice[i]['account'][j]['taxcode'] == QBO_tax[
                                    p6]['taxcode_name']:
                                TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                taxrate = QBO_tax[p6]['Rate']
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]['Rate']
                                TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                taxrate1 = taxrate
                                total_val += multiple_invoice[i]['account'][j]['amount'] / \
                                    (100+taxrate1)*100
                            else:
                                pass

                            if multiple_invoice[i]['IsTaxInclusive'] == False:

                                if multiple_invoice[i]['Subtotal'] >= 0:
                                    if 'unit_count' not in multiple_invoice[i]['account'][j]:
                                        SalesItemLineDetail['Qty']=0
                                        multiple_invoice[i]['account'][j]['unit_count']=0
                                    else:
                                        SalesItemLineDetail['Qty'] = multiple_invoice[i]['account'][j]['unit_count']
                                    SalesItemLineDetail[
                                        'UnitPrice'] = multiple_invoice[i]['account'][j][
                                            'unit_price']
                                    salesitemline["Amount"]=SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                    # salesitemline["Amount"] = round(multiple_invoice[i][
                                    #     'account'][j]['unit_price'] * multiple_invoice[i][
                                    #         'account'][j]['unit_count'],2)
                                    SalesItemLineDetail['TaxInclusiveAmt'] = salesitemline["Amount"]*(100+taxrate1)/100
                                    
                                    subtotal['Amount'] = multiple_invoice[i][
                                        'Subtotal']
                                    TxnTaxDetail['TotalTax'] = multiple_invoice[i][
                                        'TotalTax']
                                    discount_SalesItemLineDetail['Qty'] = 1
                                    discount_SalesItemLineDetail['UnitPrice'] = -(
                                        multiple_invoice[i]['account'][j]['unit_count'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value
                                    ) / 100
                                    discount['Amount'] = -(
                                        multiple_invoice[i]['account'][j]['unit_count'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value
                                    ) / 100

                                    if taxrate1 != 0:
                                        TaxDetail['Amount'] = multiple_invoice[i][
                                            'TotalTax']
                                        TaxLineDetail[
                                            'NetAmountTaxable'] = round(multiple_invoice[i][
                                                'Subtotal'] - multiple_invoice[i][
                                                    'TotalTax'],2)
                                    else:
                                        TaxDetail['Amount'] = 0
                                        TaxLineDetail['NetAmountTaxable'] = 0

                                else:
                                    discount_SalesItemLineDetail['Qty'] = -1
                                    discount_SalesItemLineDetail['UnitPrice'] = (
                                        multiple_invoice[i]['account'][j]['unit_count'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value
                                    ) / 100
                                    discount['Amount'] = (
                                        multiple_invoice[i]['account'][j]['unit_count'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value
                                    ) / 100

                                    SalesItemLineDetail['Qty'] = -multiple_invoice[i][
                                        'account'][j]['unit_count']
                                    SalesItemLineDetail[
                                        'UnitPrice'] = multiple_invoice[i]['account'][j][
                                            'unit_price']
                                    salesitemline["Amount"]=SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                    
                                    # salesitemline["Amount"] = round(multiple_invoice[i][
                                    #     'account'][j]['unit_price'] * multiple_invoice[i][
                                    #         'account'][j]['unit_count'],2)
                                    SalesItemLineDetail['TaxInclusiveAmt'] = salesitemline["Amount"]*(100+taxrate1)/100
                                    
                                    
                                    subtotal[
                                        'Amount'] = -multiple_invoice[i]['Subtotal']
                                    TxnTaxDetail[
                                        'TotalTax'] = -multiple_invoice[i]['TotalTax']

                                    if taxrate1 != 0:
                                        TaxDetail['Amount'] = multiple_invoice[i][
                                            'TotalTax']
                                        TaxLineDetail[
                                            'NetAmountTaxable'] = multiple_invoice[i][
                                                'Subtotal'] - multiple_invoice[i][
                                                    'TotalTax']
                                    else:
                                        if multiple_invoice[i]['account'][j][
                                                'taxcode'] == 'GST':
                                            TaxDetail['Amount'] = -multiple_invoice[i][
                                                'TotalTax']
                                            TaxLineDetail[
                                                'NetAmountTaxable'] = -round(multiple_invoice[
                                                    i]['account'][j]['amount'] / (
                                                        100 + taxrate1) * 100,2)
                                        elif multiple_invoice[i]['account'][j][
                                                'taxcode'] in ["FRE","EXP"]:
                                            TaxDetail['Amount'] = 0
                                            TaxLineDetail[
                                                'NetAmountTaxable'] = -round(multiple_invoice[
                                                    i]['account'][j]['amount'],2)
                                        elif multiple_invoice[i]['account'][j][
                                                'taxcode'] == "N-T":
                                            TaxDetail['Amount'] = 0
                                            TaxLineDetail[
                                                'NetAmountTaxable'] = -round(multiple_invoice[
                                                    i]['account'][j]['amount'],2)

                                # invoice['TxnTaxDetail'] = TxnTaxDetail
                                TaxDetail['DetailType'] = "TaxLineDetail"
                                TaxDetail['TaxLineDetail'] = TaxLineDetail
                                TaxLineDetail['TaxRateRef'] = TaxRate
                                TaxLineDetail['PercentBased'] = True

                            else:
                                if multiple_invoice[i]['Subtotal'] >= 0:
                                    if 'unit_count' not in multiple_invoice[i]['account'][j]:
                                        SalesItemLineDetail['Qty'] = 0
                                    else:    
                                        SalesItemLineDetail['Qty'] = multiple_invoice[i][
                                            'account'][j]['unit_count']
                                    SalesItemLineDetail['UnitPrice'] = multiple_invoice[i]['account'][j]['unit_price'] /(100 + taxrate1) * 100
                                    
                                    salesitemline["Amount"] = (SalesItemLineDetail[
                                        'Qty'] * SalesItemLineDetail['UnitPrice'])
                                    SalesItemLineDetail['TaxInclusiveAmt'] = salesitemline["Amount"]*(100+taxrate1)/100
                                    
                                    
                                    subtotal['Amount'] = multiple_invoice[i][
                                        'Subtotal'] - multiple_invoice[i]['TotalTax']
                                    TxnTaxDetail['TotalTax'] = multiple_invoice[i][
                                        'TotalTax']
                                    discount_SalesItemLineDetail['Qty'] = 1
                                    discount_SalesItemLineDetail['UnitPrice'] = -(SalesItemLineDetail['Qty'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value /
                                        (100 + taxrate1))
                                    discount['Amount'] = -round(
                                        (SalesItemLineDetail['Qty'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value /
                                        (100 + taxrate1)), 2)

                                else:
                                    SalesItemLineDetail['Qty'] = -multiple_invoice[i][
                                        'account'][j]['unit_count']
                                    #                 SalesItemLineDetail['UnitPrice'] = abs(multiple_invoice[i]['account'][j]['unit_price'])
                                    SalesItemLineDetail['UnitPrice'] = multiple_invoice[i]['account'][j]['unit_price'] /(100 + taxrate1) * 100
                                    salesitemline["Amount"] = SalesItemLineDetail[
                                        'Qty'] * SalesItemLineDetail['UnitPrice']
                                    SalesItemLineDetail['TaxInclusiveAmt'] = salesitemline["Amount"]*(100+taxrate1)/100
                                    
                                    subtotal['Amount'] = -(
                                        multiple_invoice[i]['Subtotal'] -
                                        multiple_invoice[i]['TotalTax'])
                                    TxnTaxDetail[
                                        'TotalTax'] = -multiple_invoice[i]['TotalTax']
                                    discount_SalesItemLineDetail['Qty'] = -1
                                    discount_SalesItemLineDetail['UnitPrice'] = round(
                                        (multiple_invoice[i]['account'][j]['unit_count'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value /
                                        (100 + taxrate1)), 2)
                                    discount['Amount'] = round(
                                        (multiple_invoice[i]['account'][j]['unit_count'] *
                                        multiple_invoice[i]['account'][j]['unit_price'] *
                                        discount_value /
                                        (100 + taxrate1)), 2)

            #                 salesitemline["Amount"] = abs(round(
            #                     (multiple_invoice[i]['account'][j]['unit_price']*multiple_invoice[i]['account'][j]['unit_count']/(100+taxrate1)*100), 2))
            #                 subtotal['Amount'] = abs(round((total_val), 2))
                            # invoice['TxnTaxDetail'] = TxnTaxDetail
                            TaxDetail['DetailType'] = "TaxLineDetail"
                            TaxDetail['TaxLineDetail'] = TaxLineDetail
                            TaxLineDetail['TaxRateRef'] = TaxRate
                            TaxLineDetail['PercentBased'] = True

                            if multiple_invoice[i]['Subtotal'] > 0:
                                if multiple_invoice[i]['account'][j][
                                        'taxcode'] == 'GST':
                                    TaxDetail['Amount'] = multiple_invoice[i][
                                        'TotalTax']
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = round(multiple_invoice[i][
                                            'account'][j]['amount'] / (100 +
                                                                    taxrate1) * 100,2)
                                elif multiple_invoice[i]['account'][j][
                                        'taxcode'] in ["FRE","EXP"]:
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = round(multiple_invoice[i][
                                            'account'][j]['amount'],2)
                                elif multiple_invoice[i]['account'][j][
                                        'taxcode'] == "N-T":
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = round(multiple_invoice[i][
                                            'account'][j]['amount'],2)
                                else:
                                    pass
                            else:
                                
                                if multiple_invoice[i]['account'][j][
                                        'taxcode'] == 'GST':
                                    TaxDetail['Amount'] = -multiple_invoice[i][
                                        'TotalTax']
                                    TaxLineDetail['NetAmountTaxable'] = round(TaxDetail[
                                        'Amount'] * taxrate1,2)
                                elif multiple_invoice[i]['account'][j][
                                        'taxcode'] in ["FRE","EXP"]:
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = -round(multiple_invoice[i][
                                            'account'][j]['amount'],2)
                                elif multiple_invoice[i]['account'][j][
                                        'taxcode'] == "N-T":
                                    TaxDetail['Amount'] = 0
                                    TaxLineDetail[
                                        'NetAmountTaxable'] = -round(multiple_invoice[i][
                                            'account'][j]['amount'],2)
                                else:
                                    pass

                    subtotal['DetailType'] = "SubTotalLineDetail"
                    subtotal['SubTotalLineDetail'] = SubTotalLineDetail
                    salesitemline["DetailType"] = "SalesItemLineDetail"
                    salesitemline["SalesItemLineDetail"] = SalesItemLineDetail

                    SalesItemLineDetail["ItemRef"] = ItemRef
                    SalesItemLineDetail["ClassRef"] = ClassRef
                    SalesItemLineDetail['TaxCodeRef'] = TaxCodeRef
                    SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                    discount["DetailType"] = "SalesItemLineDetail"
                    discount["SalesItemLineDetail"] = discount_SalesItemLineDetail
                    discount_SalesItemLineDetail["ItemRef"] = ItemRef
                    discount_SalesItemLineDetail["ClassRef"] = ClassRef
                    discount_SalesItemLineDetail['TaxCodeRef'] = TaxCodeRef
                    discount_SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                    invoice["BillEmail"] = BillEmail
                    invoice["CustomerRef"] = CustomerRef

                    invoice['Line'].append(salesitemline)

                    if 'discount' in multiple_invoice[i]['account'][j]: 
                        if discount_value > 0:
                            invoice["Line"].append(discount)

                    TxnTaxDetail['TaxLine'].append(TaxDetail)
                    line_amount = line_amount + salesitemline["Amount"] + discount['Amount']
                    line_amount1 = line_amount + multiple_invoice[i]['TotalTax']

            a = []

            for p2 in range(0, len(TxnTaxDetail['TaxLine'])):
                if TxnTaxDetail['TaxLine'][p2] in a:
                    pass
                else:
                    a.append(TxnTaxDetail['TaxLine'][p2])

            TxnTaxDetail['TaxLine'] = a
            # invoice["Line"].append(subtotal)

            
            if len(a) >= 1:
                if multiple_invoice[i]['IsTaxInclusive'] == True:
                    if line_amount1 == multiple_invoice[i]['TotalAmount']:
                        pass
                    else:
                        line_amount == multiple_invoice[i][
                            'TotalAmount'] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}
                            rounding_SalesItemLineDetail['Qty'] = 1

                            if multiple_invoice[i]['Subtotal'] > 0:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = abs(multiple_invoice[i]['TotalAmount'])- line_amount1
                                rounding['Amount'] = round(
                                    abs(multiple_invoice[i]['TotalAmount']) - line_amount1, 2)
                            else:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = abs(multiple_invoice[i]['TotalAmount']
                                            - multiple_invoice[i]['TotalTax'])- line_amount
                                rounding['Amount'] = round(
                                    abs(multiple_invoice[i]['TotalAmount'] -
                                        multiple_invoice[i]['TotalTax']) -
                                    line_amount, 2)

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"] = rounding_SalesItemLineDetail
                            
                            for p3 in range(0, len(QBO_item)):
                                if QBO_item[p3]["FullyQualifiedName"]=='Rounding':
                                    ItemRef['name'] = QBO_item[p3]["FullyQualifiedName"]
                                    ItemRef['value'] = QBO_item[p3]["Id"]
                                    ItemAccountRef['name'] = QBO_item[p3]["IncomeAccountRef"]["name"]
                                    ItemAccountRef['value'] = QBO_item[p3]["IncomeAccountRef"]["value"]
                            
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail[
                                'TaxCodeRef'] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"] = ItemAccountRef
                            TaxDetail['DetailType'] = "TaxLineDetail"
                            TaxDetail['TaxLineDetail'] = TaxLineDetail
                            TaxDetail['Amount'] = 0
                            TaxLineDetail['NetAmountTaxable'] = rounding[
                                'Amount']
                            
                            for p6 in range(0,len(QBO_tax)):
                                if 'GST free (sales)' in QBO_tax[p6][
                                        'taxrate_name']:
                                    TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                    TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                                    TaxLineDetail['TaxPercent'] = QBO_tax[p6]['Rate']
                            
                            TaxLineDetail['TaxRateRef'] = TaxRate
                            TaxLineDetail['PercentBased'] = True
                            # TxnTaxDetail['TaxLine'].append(TaxDetail)
                            if rounding['Amount']>0:
                                invoice['Line'].append(rounding)

                else:
                    
                    if line_amount1 == multiple_invoice[i]['TotalAmount']:
                        pass
                    else:
                        line_amount == multiple_invoice[i][
                            'TotalAmount'] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}

                            rounding_SalesItemLineDetail['Qty'] = 1
                            if multiple_invoice[i]['Subtotal'] > 0:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = multiple_invoice[i][
                                        'TotalAmount'] - line_amount1
                                rounding['Amount'] = multiple_invoice[i][
                                    'TotalAmount'] - line_amount1
                            else:
                                rounding_SalesItemLineDetail[
                                    'UnitPrice'] = multiple_invoice[i][
                                        'TotalAmount'] + line_amount1
                                rounding['Amount'] = multiple_invoice[i][
                                    'TotalAmount'] + line_amount1

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"] = rounding_SalesItemLineDetail
                                
                            for p3 in range(0, len(QBO_item)):
                                if QBO_item[p3]["FullyQualifiedName"]=='Rounding':
                                    ItemRef['name'] = QBO_item[p3]["FullyQualifiedName"]
                                    ItemRef['value'] = QBO_item[p3]["Id"]
                                    ItemAccountRef['name'] = QBO_item[p3]["IncomeAccountRef"]["name"]
                                    ItemAccountRef['value'] = QBO_item[p3]["IncomeAccountRef"]["value"]
                            
                            for p6 in range(0,len(QBO_tax)):
                                if 'GST free (sales)' in QBO_tax[p6][
                                        'taxrate_name']:
                                    TaxCodeRef['value'] = QBO_tax[p6]['taxcode_id']
                                    TaxRate['value'] = QBO_tax[p6]['taxrate_id']
                            
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail[
                                'TaxCodeRef'] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"] = ItemAccountRef
                            TaxDetail['DetailType'] = "TaxLineDetail"
                            TaxDetail['TaxLineDetail'] = TaxLineDetail
                            TaxDetail['Amount'] = 0
                            TaxLineDetail['NetAmountTaxable'] = rounding[
                                'Amount']
                            
                            TaxLineDetail['TaxRateRef'] = TaxRate
                            TaxLineDetail['PercentBased'] = True
                            # TxnTaxDetail['TaxLine'].append(TaxDetail)
                            if rounding['Amount']>0:
                                invoice['Line'].append(rounding)

            arr = TxnTaxDetail['TaxLine']
            b1 = {'TaxLine': []}
            
            b=[]
            for i2 in range(0,len(arr)):
                if 'value' in arr[i2]['TaxLineDetail']['TaxRateRef']: 
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
                    if 'value' in arr[i4]['TaxLineDetail']['TaxRateRef']: 
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
                if 'value' in arr[k3]['TaxLineDetail']['TaxRateRef']: 
                    if arr[k3]['TaxLineDetail']['TaxRateRef']['value'] in single:
                        new_arr.append(arr[k3])
            
            
            b1['TaxLine'] = new_arr
                    
            # TxnTaxDetail['TxnTaxDetail'] = b1
            # TxnTaxDetail['TaxLine'].append(TaxDetail)

            invoice['TxnTaxDetail'] = b1
            
            invoice["Line"].append(subtotal)
            
          
            if multiple_invoice[i]['TotalAmount'] >= 0:
                if len(invoice['Line'])>0:
                # if invoice['Line'][0]['SalesItemLineDetail']['ItemRef'] != {}:
                    count_of_items_not_found=0
                    line_item_count=len(invoice['Line'])-1
                        
                    for line in range(0,len(invoice['Line'])-1):
                        if invoice['Line'][line]['SalesItemLineDetail']['ItemRef'] != {}:
                            count_of_items_not_found+=0
                        else:
                            count_of_items_not_found+=1

                    print(count_of_items_not_found)
                    if count_of_items_not_found>0:
                        print("Item Not Found")
                    else:
                        url1 = "{}/invoice?minorversion=14".format(base_url)
                        payload = json.dumps(invoice)
                        print(payload)
                        inv_date = multiple_invoice[i]["invoice_date"][0:10]
                        inv_date1 = datetime.strptime(inv_date, '%Y-%m-%d')
                        
                        if (start_date != '' and end_date != ''):
                        
                            if (inv_date1 >= start_date1) and (inv_date1 <= end_date1):
                                post_data_in_qbo(url1, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                                
                            else:
                                print("No Invoice Available in Between These dates")
                        else:
                            # if multiple_invoice[i]['invoice_no']=="3KD123":
                            post_data_in_qbo(url1, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                            
                else:
                    add_job_status(job_id, "Unable to add invoice because Item is not present in QBO : {}".format(multiple_invoice[i]['invoice_no']) )
                    print("Unable to add invoice because Item is not present in QBO")


                    
            else:
                count_of_items_not_found=0
                line_item_count=len(invoice['Line'])-1
                    
                for line in range(0,len(invoice['Line'])-1):
                    if invoice['Line'][line]['SalesItemLineDetail']['ItemRef'] != {}:
                        count_of_items_not_found+=0
                    else:
                        count_of_items_not_found+=1

                print(count_of_items_not_found)
                if count_of_items_not_found>0:
                    print("Item Not Found")
                else:
                    url2 = "{}/creditmemo?minorversion=14".format(base_url)
                    payload = json.dumps(invoice)
                    print(payload)

                    inv_date = multiple_invoice[i]["invoice_date"][0:10]
                    inv_date1 = datetime.strptime(inv_date, '%Y-%m-%d')
                    if (start_date != '' and end_date != ''):
                        if (inv_date1 >= start_date1) and (inv_date1 <= end_date1):
                        
                            post_data_in_qbo(url2, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                                
                        else:
                            print("No Creditmemo Available in Between These dates")

                    else:
                        print('credmemo')
                        post_data_in_qbo(url2, headers, payload,db['service_invoice'],_id,job_id,task_id, multiple_invoice[i]['invoice_no'])
                                

        
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)


