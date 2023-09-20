import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_vendorcredit_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        bill1 = dbname['xero_vendorcredit'].find({"job_id": job_id})

        bill = []
        for p1 in bill1:
            bill.append(p1)

        # bills = []
        # for p1 in bill1:
        #     bills.append(p1)

        # bill=[]
        # for m in range(0, len(bills)):
        #     if bills[m]["Inv_ID"] in ["d0374e4f-cb59-4595-bbdd-ed51ab0d6659"]:
        #         bill.append(bills[m])

        
        myob_item1 = dbname['item'].find({"job_id": job_id})
        myob_item = []
        for k4 in range(0, dbname['item'].count_documents({"job_id": job_id})):
            myob_item.append(myob_item1[k4])

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({"job_id": job_id})):
            chart_of_account.append(chart_of_account1[k3])


        myob_customer1 = dbname['customer'].find({"job_id": job_id})
        myob_customer = []
        for k5 in range(0, dbname['customer'].count_documents({"job_id": job_id})):
            myob_customer.append(myob_customer1[k5])

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

        xero_account1 = dbname["xero_coa"].find({"job_id": job_id})
        xero_account = []
        for k9 in range(0, dbname['xero_coa'].count_documents({"job_id": job_id})):
            xero_account.append(xero_account1[k9])

        job11 = dbname['job'].find({"job_id": job_id})
        job = []
        for k8 in range(0, dbname['job'].count_documents({"job_id": job_id})):
            job.append(job11[k8])

        for i in range(0, len(bill)):

            print(bill[i])
            _id = bill[i]['_id']
            task_id = bill[i]['task_id']
            QuerySet1 = {"Lines": []}
            
            Supplier = {}
            FreightTaxCode = {}
            terms = {}
            line_job = {}

            QuerySet1["Number"] = bill[i]["Inv_No"][-13:]
            QuerySet1["Date"] = bill[i]["TxnDate"]
            QuerySet1['SupplierInvoiceNumber'] = bill[i]['Inv_ID']
            QuerySet1['AppliedToDate'] = 0

            terms['PaymentIsDue'] = "OnADayOfTheMonth"
            if "DueDate" in bill[i]:
                duedate = datetime.strptime(bill[i]["DueDate"][0:10], '%Y-%m-%d')
                terms['BalanceDueDate'] = duedate.day
                terms["DueDate"] = bill[i]["DueDate"]
                terms['DiscountDate'] = 0

                QuerySet1['Terms'] = terms

            if bill[i]['LineAmountTypes'] == 'Inclusive':
                QuerySet1['IsTaxInclusive'] = True
            else:
                QuerySet1['IsTaxInclusive'] = False

            for k1 in range(0, len(myob_supplier)):

                if myob_supplier[k1]["CompanyName"] == bill[i]["ContactName"][0:50]:
                    Supplier['UID'] = myob_supplier[k1]["UID"]
                    break
                elif 'CompanyName' in myob_supplier[k1] and myob_supplier[k1]["CompanyName"]!= None:
                    if myob_supplier[k1]["CompanyName"].startswith(bill[i]["ContactName"]) and myob_supplier[k1]["CompanyName"].endswith("- S"):
                        Supplier['UID'] = myob_supplier[k1]["UID"]
                        break

                QuerySet1["Supplier"] = Supplier

            for j in range(0, len(bill[i]["Line"])):
                taxcode = {}
                QuerySet3 = {}

            
                for j3 in range(0, len(job)):
                    if 'TrackingID' in bill[i]["Line"][j]:
                        if job[j3]['Name'] == bill[i]["Line"][j]["TrackingID"]:
                            line_job['UID'] = job[j3]['UID']

                if line_job == {}:
                    QuerySet3['Job'] = None
                else:
                    QuerySet3['Job'] = line_job

                if 'AccountCode' in bill[i]['Line'][j]:
                    Item = {}
                    Account = {}

                    if 'ItemCode' in bill[i]["Line"][j]:
                        for j5 in range(0, len(myob_item)):
                            if bill[i]["Line"][j]["ItemCode"] == myob_item[j5]["Number"]:
                                Item["UID"] = myob_item[j5]["UID"]
                            QuerySet3["Item"] = Item

                    if 'AccountCode' in bill[i]["Line"][j]:
                        
                        for j5 in range(0, len(chart_of_account)):
                            for j51 in range(0, len(xero_account)):
                                if bill[i]["Line"][j]["AccountCode"] == xero_account[j51]['Code']:
                                    if xero_account[j51]['Name'].lower().strip() == chart_of_account[j5][
                                        "Name"].lower().strip():
                                        Account["UID"] = chart_of_account[j5]["UID"]

                        for j3 in range(0, len(taxcode_myob)):
                            for k1 in range(0, len(xero_tax)):

                                if 'TaxType' in bill[i]["Line"][j]:
                                    if bill[i]["Line"][j]["TaxType"] != None and bill[i]["Line"][j][
                                        "TaxType"] != 'NONE':
                                        if bill[i]["Line"][j]["TaxType"] == xero_tax[k1]['TaxType']:

                                            if xero_tax[k1]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT',"TAX008", 'OUTPUT2', 'INPUT2']:
                                                if taxcode_myob[j3]['Code'] == 'GST' or taxcode_myob1[j3]['Code'] == 'S15':
                                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                                    taxrate1 = taxcode_myob[j3]['Rate']
                                            elif xero_tax[k1]['TaxType'] in ['TAX001']:
                                                if taxcode_myob[j3]['Code'] == 'CAP':
                                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                                    taxrate1 = taxcode_myob[j3]['Rate']
                                            elif xero_tax[k1]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES',
                                                                             'EXEMPTOUTPUT', 'EXEMPTEXPORT']:
                                                if taxcode_myob[j3]['Code'] == 'FRE':
                                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                                    taxrate1 = taxcode_myob[j3]['Rate']
                                            elif xero_tax[k1]['TaxType'] in ["INPUTTAXED"]:
                                                if taxcode_myob[j3]['Code'] == 'INP':
                                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                                    taxrate1 = taxcode_myob[j3]['Rate']
                                            elif xero_tax[k1]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2",None,"NONE"]:
                                                if taxcode_myob[j3]['Code'] == 'N-T':
                                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                                    taxrate1 = taxcode_myob[j3]['Rate']
                                    else:
                                        if taxcode_myob[j3]['Code'] == 'N-T':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']
                                            taxrate1 = taxcode_myob[j3]['Rate']

                        QuerySet3['TaxCode'] = taxcode
                        QuerySet3['Account'] = Account
                        QuerySet1["Lines"].append(QuerySet3)
                        QuerySet3["Type"] ="Transaction"

                    if "Description" in bill[i]["Line"][j]:
                        QuerySet3["Description"] = bill[i]["Line"][j]["Description"]
                    
                    if 'ItemCode' in bill[i]["Line"][j]:
                        if 'Quantity' in bill[i]["Line"][j]:
                            if bill[i]["Line"][j]["LineAmount"] < 0:
                                QuerySet3["ReceivedQuantity"] = bill[i]["Line"][j]["Quantity"]
                                QuerySet3["BillQuantity"] = bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitCount"] = bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] = bill[i]["Line"][j]["Quantity"]  


                            else:
                                QuerySet3["ReceivedQuantity"] = -bill[i]["Line"][j]["Quantity"]
                                QuerySet3["BillQuantity"] = -bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitCount"] = -bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitPrice"] = bill[i]["Line"][j]["UnitAmount"]
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] = -bill[i]["Line"][j]["Quantity"]  
                        else:
                            if bill[i]["Line"][j]["LineAmount"] < 0:
                                QuerySet3["ReceivedQuantity"] = 1
                                QuerySet3["BillQuantity"] = 1
                                QuerySet3["UnitCount"] = 1
                                QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] = 1
                            else:
                                QuerySet3["ReceivedQuantity"] =-1
                                QuerySet3["BillQuantity"] = -1
                                QuerySet3["UnitCount"] = -1
                                QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] =-1
                    else:
                        if 'Quantity' in bill[i]["Line"][j]:
                            if bill[i]["Line"][j]["LineAmount"] < 0:
                                QuerySet3["ReceivedQuantity"] = bill[i]["Line"][j]["Quantity"]
                                QuerySet3["BillQuantity"] = bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitCount"] = bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] = bill[i]["Line"][j]["Quantity"]    
                               
                            else:
                                QuerySet3["ReceivedQuantity"] = -bill[i]["Line"][j]["Quantity"]
                                QuerySet3["BillQuantity"] = -bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitCount"] = -bill[i]["Line"][j]["Quantity"]
                                QuerySet3["UnitPrice"] = bill[i]["Line"][j]["UnitAmount"]
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] = -bill[i]["Line"][j]["Quantity"]
                        else:
                            if bill[i]["Line"][j]["LineAmount"] < 0:
                                QuerySet3["ReceivedQuantity"] = 1
                                QuerySet3["BillQuantity"] = 1
                                QuerySet3["UnitCount"] = 1
                                QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] = 1
                            else:
                                QuerySet3["ReceivedQuantity"] = -1
                                QuerySet3["BillQuantity"] = -1
                                QuerySet3["UnitCount"] = -1
                                QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                                QuerySet3["Total"] = round(QuerySet3["UnitPrice"]*QuerySet3["UnitCount"],2)
                                QuerySet3["BackorderQuantity"] = -1
                    


                    # if 'ItemCode' in bill[i]["Line"][j]:
                    #     if 'Quantity' in bill[i]["Line"][j]:
                    #         if bill[i]["Line"][j]["LineAmount"] < 0:
                    #             QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                    #             QuerySet3["Total"] = -abs(bill[i]["Line"][j]["LineAmount"])
                    #             if "Quantity" in bill[i]["Line"][j]:
                    #                 QuerySet3["ReceivedQuantity"] = -bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["BillQuantity"] = -bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["UnitCount"] = bill[i]["Line"][j]["Quantity"]
                                    

                    #             else:
                    #                 QuerySet3["ReceivedQuantity"] = -1
                    #                 QuerySet3["BillQuantity"] = -1
                    #                 QuerySet3["UnitCount"] = bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["Type"] ="Transaction"


                    #         else:

                    #             QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                    #             QuerySet3["Total"] = -abs(bill[i]["Line"][j]["LineAmount"])

                    #             if "Quantity" in bill[i]["Line"][j]:
                    #                 QuerySet3["ReceivedQuantity"] = bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["BillQuantity"] = -bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["UnitCount"] = bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["Type"] ="Transaction"
                                   
                    #             else:
                    #                 QuerySet3["ReceivedQuantity"] = 1
                    #                 QuerySet3["BillQuantity"] = -1
                    #                 QuerySet3["UnitCount"] = bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["Type"] ="Transaction"
                    #     else:
                    #         QuerySet3["Total"] = bill[i]["Line"][j]["LineAmount"]
                    #         QuerySet3["BillQuantity"] = 1
                    #         QuerySet3["ReceivedQuantity"] = 1
                    #         QuerySet3["UnitCount"] = 1
                    #         QuerySet3["Type"] ="Transaction"
                    #         QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])

                                   
                    # else:
                    #     if 'Quantity' in bill[i]["Line"][j]:
                    #         if bill[i]["Line"][j]["LineAmount"] < 0:
                    #             QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                    #             QuerySet3["Total"] = -abs(bill[i]["Line"][j]["LineAmount"])

                    #             if "Quantity" in bill[i]["Line"][j]:
                    #                 QuerySet3["ReceivedQuantity"] = 0
                    #                 QuerySet3["UnitCount"] = -bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["BackorderQuantity"] = 0
                    #                 QuerySet3["BillQuantity"]=0
            
                    #             else:
                    #                 QuerySet3["ReceivedQuantity"] = 0
                    #                 QuerySet3["UnitCount"] = -1
                    #                 QuerySet3["BackorderQuantity"] = 0
                    #                 QuerySet3["BillQuantity"]=0
            
                    #         else:

                    #             QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])
                    #             QuerySet3["Total"] = -abs(bill[i]["Line"][j]["LineAmount"])

                    #             if "Quantity" in bill[i]["Line"][j]:
                    #                 QuerySet3["ReceivedQuantity"] = 0
                    #                 QuerySet3["UnitCount"] = -bill[i]["Line"][j]["Quantity"]
                    #                 QuerySet3["BackorderQuantity"] = 0
                    #                 QuerySet3["BillQuantity"]=0
                    #             else:
                    #                 QuerySet3["ReceivedQuantity"] = 0
                    #                 QuerySet3["UnitCount"] = -1
                    #                 QuerySet3["BackorderQuantity"] = 0
                    #                 QuerySet3["BillQuantity"]=0

                    #     else:
                        
                    #         QuerySet3["Total"] = bill[i]["Line"][j]["LineAmount"]
                    #         QuerySet3["ReceivedQuantity"] = 0
                    #         QuerySet3["UnitCount"] = 1
                    #         QuerySet3["BackorderQuantity"] = 0
                    #         QuerySet3["BillQuantity"]=0
                    #         QuerySet3["UnitPrice"] = abs(bill[i]["Line"][j]["UnitAmount"])



                    
                for j3 in range(0, len(taxcode_myob)):
                    if taxcode_myob[j3]['Code'] == 'N-T':
                        FreightTaxCode['UID'] = taxcode_myob[j3]['UID']
                QuerySet1['FreightTaxCode'] = FreightTaxCode

                

            if (bill[i]["Status"] != 'SUBMITTED') and (bill[i]['Status'] != "DRAFT") and (
                    bill[i]['Status'] != "VOIDED") and (bill[i]['Status'] != "DELETED"):
                payload = json.dumps(QuerySet1)
                print(payload,"-----------------payload")

                # if 'ItemCode' in bill[i]["Line"][j]:
                #     url = f"{base_url}/Purchase/Bill/Item"
                # else:
                #     url = f"{base_url}/Purchase/Bill/Service"

                id_or_name_value_for_error = (
                    bill[i]['Inv_No']
                    if bill[i]['Inv_No'] is not None
                    else None)

                payload1, base_url, headers = get_settings_myob(job_id)
                url = f"{base_url}/Purchase/Bill/Item"
                if bill[i]['is_pushed']==0:
                    asyncio.run(
                        post_data_in_myob(url, headers, payload, dbname['xero_vendorcredit'], _id, job_id, task_id,
                                        id_or_name_value_for_error))
                else:
                    pass


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
