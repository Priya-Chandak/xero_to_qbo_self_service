import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_overpayment_as_credit_memo_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}


        receive_money = dbname['xero_receive_overpayment'].find({"job_id": job_id})
        xero_receive_overpayment = []
        for p1 in receive_money:
            xero_receive_overpayment.append(p1)


        myob_item1 = dbname['item'].find({"job_id": job_id})
        myob_item = []
        for k4 in range(0, dbname['item'].count_documents({"job_id": job_id})):
            myob_item.append(myob_item1[k4])

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({"job_id": job_id})):
            chart_of_account.append(chart_of_account1[k3])

        xero_archived_coa1 = dbname['xero_archived_coa'].find({"job_id":job_id})
        xero_archived_coa = []
        for k4 in range(0, dbname['xero_archived_coa'].count_documents({"job_id":job_id})):
            xero_archived_coa.append(xero_archived_coa1[k4])

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({"job_id": job_id})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        myob_supplier1 = dbname['supplier'].find({"job_id": job_id})
        myob_supplier = []
        for k10 in range(0, dbname['supplier'].count_documents({"job_id": job_id})):
            myob_supplier.append(myob_supplier1[k10])
    
        myob_customer1 = dbname['customer'].find({"job_id": job_id})
        myob_customer = []
        for k5 in range(0, dbname['customer'].count_documents({"job_id": job_id})):
            myob_customer.append(myob_customer1[k5])

        myob_invoice1 = dbname['all_invoice'].find({"job_id":job_id})
        myob_invoice = []
        for k11 in range(0, dbname['all_invoice'].count_documents({"job_id":job_id})):
            myob_invoice.append(myob_invoice1[k11])

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for k4 in range(0, dbname['xero_coa'].count_documents({"job_id": job_id})):
            xero_coa.append(xero_coa1[k4])


        for i in range(0, len(xero_receive_overpayment)):
            for a in range(0, len(xero_coa)):
                if xero_receive_overpayment[i]["BankAccountID"] == xero_coa[a]["AccountID"]:
                        for b in range(0, len(chart_of_account)):
                            if xero_coa[a]["Name"].lower().strip() == chart_of_account[b]["Name"].lower().strip():
                                if chart_of_account[b]["Account_Type"] in ['Bank','BANK']:
                                    _id = xero_receive_overpayment[i]['_id']
                                    task_id = xero_receive_overpayment[i]['task_id']
                                    Queryset1 = {"Lines": []}
                                    Customer = {}
                                    terms = {}
                                    account ={}
                                    QuerySet2 = {}

                                    if 'Reference' in xero_receive_overpayment[i] and xero_receive_overpayment[i]['Reference'] != "":
                                        if len(xero_receive_overpayment[i] and xero_receive_overpayment[i]['Reference'])>15:
                                            Queryset1["Number"] ="so-"+ xero_receive_overpayment[i]["Reference"][:-13]
                                        else:
                                            Queryset1["Number"] ="so-"+ xero_receive_overpayment[i]["Reference"]
                                    else:
                                        Queryset1["Number"] ="so-"+ f"xero_receive_overpayment-{i}"


                                    journal_date = xero_receive_overpayment[i]["Date"]
                                    journal_date11 = int(journal_date[6:16])
                                    journal_date12 = datetime.utcfromtimestamp(journal_date11).strftime('%Y-%m-%d')
                                    Queryset1["Date"] = journal_date12


                                    terms['PaymentIsDue'] = "OnADayOfTheMonth"
                                    if "DueDate" in xero_receive_overpayment[i]:
                                    
                                        terms['BalanceDueDate'] = journal_date12.day
                                        terms["DueDate"] = journal_date12
                                        terms['DiscountDate'] = 0

                                        Queryset1['Terms'] = terms

                                    Queryset1['IsTaxInclusive'] = False  
                                    Queryset1['CustomerPurchaseOrderNumber'] = xero_receive_overpayment[i]['BankTransactionID']


                                    for c1 in range(0, len(myob_customer)): 
                                        if myob_customer[c1]["Company_Name"] == xero_receive_overpayment[i]['ContactName'][0:50]:
                                            Customer['UID'] = myob_customer[c1]["UID"]
                                        elif myob_customer[c1]["Company_Name"].startswith(xero_receive_overpayment[i]['ContactName']) and \
                                                myob_customer[c1]["Company_Name"].endswith("- C"):
                                            Customer['UID'] = myob_customer[c1]["UID"]

                                    Queryset1["Customer"] = Customer

                                    for j in range(0, len(xero_receive_overpayment[i]['Line'])):
                                        lineitem = {}
                                        lineaccount = {}
                                        taxcode = {}
                                        tracking = {}
                                        if "Description" in xero_receive_overpayment[i]['Line'][j]:
                                            lineitem['Memo'] = xero_receive_overpayment[i]['Line'][j]['Description']

                                        if xero_receive_overpayment[i]['Line'][j]['LineAmount']< 0:
                                            lineitem['ShipQuantity'] = -xero_receive_overpayment[i]['Line'][j]['Quantity']
                                            lineitem["UnitPrice"] = abs(xero_receive_overpayment[i]['Line'][j]['LineAmount'])
                                            lineitem["Total"] = lineitem["UnitPrice"]*lineitem['UnitCount']
                                            lineitem['UnitCount'] = -xero_receive_overpayment[i]['Line'][j]['Quantity']
                                        else:
                                            lineitem['ShipQuantity'] = xero_receive_overpayment[i]['Line'][j]['Quantity']
                                            lineitem["UnitPrice"] = abs(xero_receive_overpayment[i]['Line'][j]['LineAmount'])
                                            lineitem["Total"] = lineitem["UnitPrice"]*lineitem['UnitCount']
                                            lineitem['UnitCount'] = xero_receive_overpayment[i]['Line'][j]['Quantity']

                                        lineitem['Type'] = "Transaction"


                                        for i2 in range(0, len(chart_of_account)):
                                            for j6 in range(0, len(xero_coa)):
                                                if xero_receive_overpayment[i]['Line'][j]['AccountCode'] == xero_coa[j6]["Code"]:
                                                    if xero_coa[j6]["Name"] == chart_of_account[i2]["Name"]:
                                                        lineaccount['UID'] = chart_of_account[i2]['UID']
                                                        break

                                                elif xero_receive_overpayment[i]['Line'][j]['AccountCode'] == chart_of_account[i2]['DisplayId']:
                                                    lineaccount['UID'] = chart_of_account[i2]['UID']
                                                    break

                                        for n in range(0,len(xero_archived_coa)):    
                                            for p1 in range(0,len(chart_of_account)):
                                                if xero_receive_overpayment[i]['Line'][j]['AccountCode'] == xero_archived_coa[n]['Code']:
                                                    if xero_archived_coa[n]['Name'] == chart_of_account[p1]["Name"]:
                                                        lineaccount['UID'] = chart_of_account[p1]["UID"]


                                        if lineaccount != {} and lineaccount != None:
                                            lineitem['account'] = lineaccount
                                            


                                        # for i21 in range(0, len(chart_of_account)):
                                        #     if 'TrackingName' in xero_spend_overpayment[i]['Line'][j]:
                                        #         if xero_spend_overpayment[i]['Line'][j]['TrackingName'] == chart_of_account[i21]['Name']:
                                        #             tracking['UID'] = chart_of_account[i21]['UID']
                                        #             tracking['Name'] = chart_of_account[i21]['Name']
                                        #             tracking['Number'] = chart_of_account[i21]['Number']

                                        # if tracking != {} and tracking != None:
                                        #     lineitem['Job'] = tracking
                                        # else:
                                        #     lineitem['Job'] = None

                                        for j3 in range(0, len(taxcode_myob)):
                                            for j2 in range(0, len(xero_tax)):
                                                if 'TaxType' in xero_receive_overpayment[i]['Line'][j]:
                                                    if xero_receive_overpayment[i]['Line'][j]["TaxType"] != None and xero_spend_overpayment[i]['Line'][j][
                                                        "TaxType"] != 'NONE':
                                                        if xero_receive_overpayment[i]['Line'][j]['TaxType'] == xero_tax[j2]['TaxType']:
                                                            if xero_tax[j2]['TaxType'] in ['CAPEXINPUT', 'INPUT', 'OUTPUT', "INPUT2",
                                                                                        "OUTPUT2"]:
                                                                if taxcode_myob[j3]['Code'] == 'GST' or taxcode_myob1[j3]['Code'] == 'S15':
                                                                    taxcode['UID'] = taxcode_myob[j3]['UID']

                                                            elif xero_tax[j2]['TaxType'] in ['EXEMPTCAPITAL', 'EXEMPTEXPENSES', 'EXEMPTEXPORT',
                                                                                            'EXEMPTOUTPUT']:
                                                                if taxcode_myob[j3]['Code'] == 'FRE':
                                                                    taxcode['UID'] = taxcode_myob[j3]['UID']

                                                            elif xero_tax[j2]['TaxType'] in ["INPUTTAXED"]:
                                                                if taxcode_myob[j3]['Code'] == 'INP':
                                                                    taxcode['UID'] = taxcode_myob[j3]['UID']

                                                            elif xero_tax[j2]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2", "NONE"]:
                                                                if taxcode_myob[j3]['Code'] == 'N-T':
                                                                    taxcode['UID'] = taxcode_myob[j3]['UID']

                                                    elif xero_receive_overpayment[i]['Line'][j]['TaxType'] in ['NONE', None]:
                                                        if taxcode_myob[j3]['Code'] == 'N-T':
                                                            taxcode['UID'] = taxcode_myob[j3]['UID']

                                        lineitem['TaxCode'] = taxcode


                                        Queryset1['Lines'].append(lineitem)

                                        payload = json.dumps(Queryset1)

                                        id_or_name_value_for_error = (
                                        xero_receive_overpayment[i]['Date']
                                        if xero_receive_overpayment[i]['Date'] is not None
                                        else "")

                                        payload1, base_url, headers = get_settings_myob(job_id)
                                        url1 = f"{base_url}/Sale/Invoice/Item"
                                        if xero_receive_overpayment[i]['is_pushed']==0:
                                            asyncio.run(
                                                post_data_in_myob(url1, headers, payload, dbname['xero_receive_overpayment'], _id, job_id, task_id,
                                                                    id_or_name_value_for_error))
                                        else:
                                            pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
