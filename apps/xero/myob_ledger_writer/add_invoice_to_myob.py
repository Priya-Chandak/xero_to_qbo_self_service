import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_invoice_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        xero_invoice = dbname['xero_invoice'].find({"job_id": job_id})

        multiple_invoice = []
        for p1 in xero_invoice:
            multiple_invoice.append(p1)

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({"job_id": job_id})):
            chart_of_account.append(chart_of_account1[k3])

        xero_account1 = dbname["xero_coa"].find({"job_id": job_id})
        xero_account = []
        for k9 in range(0, dbname['xero_coa'].count_documents({"job_id": job_id})):
            xero_account.append(xero_account1[k9])

        myob_item1 = dbname['item'].find({"job_id": job_id})
        myob_item = []
        for k4 in range(0, dbname['item'].count_documents({"job_id": job_id})):
            myob_item.append(myob_item1[k4])

        myob_customer1 = dbname['customer'].find({"job_id": job_id})
        myob_customer = []
        for k5 in range(0, dbname['customer'].count_documents({"job_id": job_id})):
            myob_customer.append(myob_customer1[k5])

        taxcode_myob = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob1 = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({"job_id": job_id})):
            taxcode_myob1.append(taxcode_myob[k7])

        job11 = dbname['job'].find({"job_id": job_id})
        job1 = []
        for k8 in range(0, dbname['job'].count_documents({"job_id": job_id})):
            job1.append(job11[k8])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        xero_item1 = dbname['xero_items'].find({"job_id": job_id})
        xero_item = []
        for p51 in xero_item1:
            xero_item.append(p51)

        multiple_invoice = multiple_invoice
        for i in range(0, len(multiple_invoice)):
            _id = multiple_invoice[i]['_id']
            task_id = multiple_invoice[i]['task_id']

            QuerySet1 = {"Lines": []}
            Customer = {}
            terms = {}
            QuerySet2 = {}
            QuerySet1["Number"] = multiple_invoice[i]["Inv_No"][-13:]
            QuerySet1["Date"] = multiple_invoice[i]["TxnDate"]
            QuerySet1['CustomerPurchaseOrderNumber'] = multiple_invoice[i]['Inv_ID']
           
            terms['PaymentIsDue'] = "OnADayOfTheMonth"
            duedate = datetime.strptime(multiple_invoice[i]["DueDate"][0:10], '%Y-%m-%d')
            terms['BalanceDueDate'] = duedate.day
            terms["DueDate"] = multiple_invoice[i]["DueDate"]
            terms['DiscountDate'] = 0

            for c1 in range(0, len(myob_customer)):
                if myob_customer[c1]["Company_Name"] != None and myob_customer[c1]["Company_Name"] != "":
                    if myob_customer[c1]["Company_Name"] == multiple_invoice[i]['ContactName'][0:50]:
                        Customer['UID'] = myob_customer[c1]["UID"]
                    elif myob_customer[c1]["Company_Name"].startswith(multiple_invoice[i]['ContactName']) and \
                            myob_customer[c1]["Company_Name"].endswith("- C"):
                        Customer['UID'] = myob_customer[c1]["UID"]

            if multiple_invoice[i]['LineAmountTypes'] == 'Exclusive' or multiple_invoice[i][
                'LineAmountTypes'] == 'NoTax':
                QuerySet1['IsTaxInclusive'] = False
            else:
                QuerySet1['IsTaxInclusive'] = True

            for j in range(0, len(multiple_invoice[i]["Line"])):
                if 'AccountCode' in multiple_invoice[i]["Line"][j]:
                    
                    QuerySet3 = {}
                    Item = {}
                    Account = {}
                    taxcode = {}
                    myob_job = {}
                    QuerySet3["Description"] = multiple_invoice[i]["Line"][j]["Description"]

                    for j3 in range(0, len(taxcode_myob1)):
                        for k1 in range(0, len(xero_tax)):
                            if 'TaxType' in multiple_invoice[i]["Line"][j]:
                                if multiple_invoice[i]["Line"][j]["TaxType"] == xero_tax[k1]['TaxType']:
                                    if xero_tax[k1]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT', 'OUTPUT2', 'INPUT2']:
                                        if taxcode_myob1[j3]['Code'] == 'GST' or taxcode_myob1[j3]['Code'] == 'S15':
                                            taxcode['UID'] = taxcode_myob1[j3]['UID']
                                            taxrate1 = taxcode_myob1[j3]['Rate']

                                    elif xero_tax[k1]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES', 'EXEMPTOUTPUT',
                                                                    'EXEMPTEXPORT']:
                                        if taxcode_myob1[j3]['Code'] == 'FRE':
                                            taxcode['UID'] = taxcode_myob1[j3]['UID']
                                            taxrate1 = taxcode_myob1[j3]['Rate']
                                    elif xero_tax[k1]['TaxType'] in ['TAX001']:
                                        if taxcode_myob[j3]['Code'] == 'CAP':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']
                                            taxrate1 = taxcode_myob[j3]['Rate']
                                    elif xero_tax[k1]['TaxType'] in ["INPUTTAXED"]:
                                        if taxcode_myob1[j3]['Code'] == 'INP':
                                            taxcode['UID'] = taxcode_myob1[j3]['UID']
                                            taxrate1 = taxcode_myob1[j3]['Rate']
                                    elif xero_tax[k1]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2"]:
                                        if taxcode_myob1[j3]['Code'] == 'N-T':
                                            taxcode['UID'] = taxcode_myob1[j3]['UID']
                                            taxrate1 = taxcode_myob1[j3]['Rate']

                                elif multiple_invoice[i]["Line"][j]["TaxType"] in ["NONE"]:
                                    if taxcode_myob1[j3]['Code'] == 'N-T':
                                        taxcode['UID'] = taxcode_myob1[j3]['UID']
                                        taxrate1 = taxcode_myob1[j3]['Rate']

                    QuerySet2['TaxCode'] = taxcode
                    QuerySet3['TaxCode'] = taxcode

                    if 'ItemCode' in multiple_invoice[i]["Line"][j]:
                        if 'UnitAmount' in multiple_invoice[i]["Line"][j]:
                            if multiple_invoice[i]["Line"][j]["UnitAmount"] < 0:
                                if 'Quantity' in multiple_invoice[i]["Line"][j]:
                                    QuerySet3['ShipQuantity'] = -multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['UnitCount'] = multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["Total"] = -abs(multiple_invoice[i]["Line"][j]["LineAmount"])

                                else:
                                    QuerySet3['ShipQuantity'] = -1
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['UnitCount'] = multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["Total"] = -abs(multiple_invoice[i]["Line"][j]["LineAmount"])



                            else:
                                if 'Quantity' in multiple_invoice[i]["Line"][j]:
                                    QuerySet3['ShipQuantity'] = multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['UnitCount'] = multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["Total"] = abs(multiple_invoice[i]["Line"][j]["LineAmount"])
                                else:
                                    QuerySet3['ShipQuantity'] = 1
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['UnitCount'] = multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["Total"] = abs(multiple_invoice[i]["Line"][j]["LineAmount"])

                    else:
                        if 'UnitAmount' in multiple_invoice[i]["Line"][j]:
                            if multiple_invoice[i]["Line"][j]["UnitAmount"] < 0:
                                if 'Quantity' in multiple_invoice[i]["Line"][j]:
                                    QuerySet3['UnitCount'] = -multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['ShipQuantity'] = 0
                                    QuerySet3['CostOfGoodsSold'] = 0
                                    QuerySet3["Total"] = -abs(multiple_invoice[i]["Line"][j]["LineAmount"])
                                else:
                                    QuerySet3['UnitCount'] = -1
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['ShipQuantity'] = 0
                                    QuerySet3['CostOfGoodsSold'] = 0
                                    QuerySet3["Total"] = -abs(multiple_invoice[i]["Line"][j]["LineAmount"])

                            else:
                                if 'Quantity' in multiple_invoice[i]["Line"][j]:
                                    QuerySet3['UnitCount'] = multiple_invoice[i]["Line"][j]["Quantity"]
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['ShipQuantity'] = 0
                                    QuerySet3['CostOfGoodsSold'] = 0

                                    QuerySet3["Total"] = abs(multiple_invoice[i]["Line"][j]["LineAmount"])


                                else:
                                    QuerySet3['UnitCount'] = 1
                                    QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Line"][j]["UnitAmount"])
                                    QuerySet3['ShipQuantity'] = 0
                                    QuerySet3['CostOfGoodsSold'] = 0

                                    QuerySet3["Total"] = abs(multiple_invoice[i]["Line"][j]["LineAmount"])


                     

                    # if "Inv_No" : "INV-10286"'LineAmount' in multiple_invoice[i]["Line"][j]:
                    #     if multiple_invoice[i]["Line"][j]["LineAmount"]<0:
                    #         QuerySet3["UnitPrice"]=abs(multiple_invoice[i]["Line"][j]['UnitAmount'])
                    #         QuerySet3['UnitCount']= -multiple_invoice[i]["Line"][j]["Quantity"]
                    #     else:
                    #         QuerySet3["UnitPrice"]=multiple_invoice[i]["Line"][j]['UnitAmount']
                    #         QuerySet3['UnitCount']= multiple_invoice[i]["Line"][j]["Quantity"]

                    if "Discount" in multiple_invoice[i]["Line"][j]:
                        QuerySet3['DiscountPercent'] = multiple_invoice[i]["Line"][j]["Discount"]
                    else:
                        QuerySet3['DiscountPercent'] = 0

                    if 'ItemCode' in multiple_invoice[i]["Line"][j]:
                        for j4 in range(0, len(myob_item)):
                            for j41 in range(0, len(xero_item)):

                                if multiple_invoice[i]["Line"][j]["ItemCode"] == myob_item[j4]["Number"]:
                                    Item["UID"] = myob_item[j4]["UID"]
                                # elif xero_item[j41]['Name'] == myob_item[j4]['Name']:
                                #     Item["UID"] = myob_item[j4]["UID"]

                    if 'ClassRef' in multiple_invoice[i]["Line"][j]:
                        for j8 in range(0, len(job1)):
                            if multiple_invoice[i]["Line"][j]["ClassRef"]["name"] == job1[j8]["Name"]:
                                myob_job['UID'] = job1[j8]["UID"]

                    for j9 in range(0, len(xero_account)):
                        if multiple_invoice[i]["Line"][j]["AccountCode"] == xero_account[j9]["Code"]:
                            for j5 in range(0, len(chart_of_account)):
                                if xero_account[j9]["Name"] == chart_of_account[j5]["Name"]:
                                    Account["UID"] = chart_of_account[j5]["UID"]
                                else:
                                    pass
                        

                    if Item != {}:
                        QuerySet3["Item"] = Item

                    QuerySet3["Account"] = Account
                    QuerySet3['TaxCode'] = taxcode
                    QuerySet3['Type'] = "Transaction"
                    if myob_job != {}:
                        QuerySet3['Job'] = myob_job
                    else:
                        QuerySet3['Job'] = None

                    QuerySet1["Lines"].append(QuerySet3)

            QuerySet1["Customer"] = Customer

            # if multiple_invoice[i]['Inv_No'] in ['I-20017']:
            if (multiple_invoice[i]["Status"] != 'SUBMITTED') and (multiple_invoice[i]['Status'] != "DRAFT") and (
                    multiple_invoice[i]['Status'] != "VOIDED") and (multiple_invoice[i]['Status'] != "DELETED"):
                payload = json.dumps(QuerySet1)
                print(payload)

                # if 'ItemCode' in multiple_invoice[i]["Line"][j]:
                #     url1 = f"{base_url}/Sale/Invoice/Item"
                # else:
                #     url1 = f"{base_url}//Sale/Invoice/Service"

                id_or_name_value_for_error = (
                    multiple_invoice[i]['Inv_No']
                    if multiple_invoice[i]['Inv_No'] is not None
                    else "")

                payload1, base_url, headers = get_settings_myob(job_id)
                url1 = f"{base_url}/Sale/Invoice/Item"
                if multiple_invoice[i]['is_pushed']==0:
                    asyncio.run(
                        post_data_in_myob(url1, headers, payload, dbname['xero_invoice'], _id, job_id, task_id,
                                        id_or_name_value_for_error))
                else:
                    pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
