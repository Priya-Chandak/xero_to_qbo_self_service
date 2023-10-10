import asyncio
import json

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_bill_credit_refund(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        bill_credit_memo_refund1 = dbname['xero_supplier_credit_cash_refund'].find({"job_id": job_id})

        bill_credit_memo_refund = []
        for p1 in bill_credit_memo_refund1:
            bill_credit_memo_refund.append(p1)

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

        xero_archived_coa1 = dbname['xero_archived_coa'].find({"job_id": job_id})
        xero_archived_coa = []
        for k4 in range(0, dbname['xero_archived_coa'].count_documents({"job_id": job_id})):
            xero_archived_coa.append(xero_archived_coa1[k4])

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({"job_id": job_id})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax_data = []
        for p5 in xero_tax1:
            xero_tax_data.append(p5)

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

        bill_credit_memo_refund = bill_credit_memo_refund

        for i in range(0, len(bill_credit_memo_refund)):
            # for a in range(0, len(xero_account)):
            #     if bill_credit_memo_refund[i]["AccountCode"] == xero_account[a]["AccountID"]:
            #             for b in range(0, len(chart_of_account)):
            #                 if xero_account[a]["Name"].lower().strip() == chart_of_account[b]["Name"].lower().strip():
            #                     if chart_of_account[b]["Account_Type"] in ['Bank','BANK']:

            print(bill_credit_memo_refund[i])
            print("-----------")

            _id = bill_credit_memo_refund[i]['_id']
            task_id = bill_credit_memo_refund[i]['task_id']
            QuerySet1 = {"Lines": []}
            Supplier = {}
            FreightTaxCode = {}
            terms = {}

            QuerySet1["Number"] = bill_credit_memo_refund[i]["InvoiceNumber"][-13:]
            QuerySet1["Date"] = bill_credit_memo_refund[i]["Date"]
            QuerySet1['SupplierInvoiceNumber'] = bill_credit_memo_refund[i]['InvoiceID']
            QuerySet1['AppliedToDate'] = 0

            # terms['PaymentIsDue'] = "OnADayOfTheMonth"
            # duedate = datetime.strptime(bill_credit_memo_refund[i]["DueDate"][0:10], '%Y-%m-%d')
            # terms['BalanceDueDate'] = duedate.day
            # terms["DueDate"] = bill_credit_memo_refund[i]["DueDate"]
            # terms['DiscountDate'] = 0

            # QuerySet1['Terms'] = terms

            QuerySet1['IsTaxInclusive'] = True

            for k1 in range(0, len(myob_supplier)):

                if myob_supplier[k1]["CompanyName"] == bill_credit_memo_refund[i]["Contact"][0:50]:
                    Supplier['UID'] = myob_supplier[k1]["UID"]

                elif 'CompanyName' in myob_supplier[k1] and myob_supplier[k1]["CompanyName"] != None:
                    if myob_supplier[k1]["CompanyName"].startswith(bill_credit_memo_refund[i]["Contact"]) and \
                            myob_supplier[k1]["CompanyName"].endswith("- S"):
                        Supplier['UID'] = myob_supplier[k1]["UID"]

            QuerySet1["Supplier"] = Supplier

            if 'AccountCode' in bill_credit_memo_refund[i]:
                Item = {}
                Account = {}
                QuerySet3 = {}
                line_job = {}
                taxcode = {}

                # for j3 in range(0,len(job)):
                #     if 'TrackingID' in bill_credit_memo_refund[i]:
                #         if job[j3]['Name'] == bill_credit_memo_refund[i]["Line"][j]["TrackingID"]:
                #             line_job['UID']=job[j3]['UID']

                # if line_job=={}:
                #     QuerySet3['Job']=None
                # else:
                #     QuerySet3['Job']=line_job

                # if 'ItemCode' in bill_credit_memo_refund[i]:
                #     for j5 in range(0, len(myob_item)):
                #         if bill_credit_memo_refund[i]["Line"][j]["ItemCode"] == myob_item[j5]["Number"]:
                #             Item["UID"] = myob_item[j5]["UID"]
                # else:
                #     Item =None                        

                for j5 in range(0, len(chart_of_account)):
                    for j51 in range(0, len(xero_account)):
                        if bill_credit_memo_refund[i]["AccountCode"] == xero_account[j51]['AccountID']:
                            if xero_account[j51]['Name'].lower().strip() == chart_of_account[j5][
                                "Name"].lower().strip():
                                Account["UID"] = chart_of_account[j5]["UID"]

                for n in range(0, len(xero_archived_coa)):
                    for p1 in range(0, len(chart_of_account)):
                        if bill_credit_memo_refund[i]["AccountCode"] == xero_archived_coa[n]['AccountID']:
                            if xero_archived_coa[n]['Name'] == chart_of_account[p1]["Name"]:
                                Account["UID"] = chart_of_account[p1]["UID"]

                if Account != {} and Account != None:
                    QuerySet3['account'] = Account

                for j3 in range(0, len(taxcode_myob)):
                    if taxcode_myob[j3]['Code'] == 'N-T':
                        taxcode['UID'] = taxcode_myob[j3]['UID']
                        taxrate1 = taxcode_myob[j3]['Rate']

                QuerySet3['TaxCode'] = taxcode

                QuerySet1["Lines"].append(QuerySet3)
                QuerySet3["Type"] = "Transaction"

                if 'Quantity' in bill_credit_memo_refund[i]:
                    if bill_credit_memo_refund[i]["Amount"] < 0:
                        QuerySet3["ReceivedQuantity"] = -bill_credit_memo_refund[i]["Quantity"]
                        QuerySet3["Bill_credit_memo_refundQuantity"] = -bill_credit_memo_refund[i]["Quantity"]
                        QuerySet3["UnitCount"] = -bill_credit_memo_refund[i]["Quantity"]
                        QuerySet3["UnitPrice"] = abs(bill_credit_memo_refund[i]["Amount"])
                        QuerySet3["Total"] = round(QuerySet3["UnitPrice"] * QuerySet3["UnitCount"], 2)
                        QuerySet3["BackorderQuantity"] = -bill_credit_memo_refund[i]["Quantity"]

                    else:
                        QuerySet3["ReceivedQuantity"] = bill_credit_memo_refund[i]["Quantity"]
                        QuerySet3["Bill_credit_memo_refundQuantity"] = bill_credit_memo_refund[i]["Quantity"]
                        QuerySet3["UnitCount"] = bill_credit_memo_refund[i]["Quantity"]
                        QuerySet3["UnitPrice"] = bill_credit_memo_refund[i]["Amount"]
                        QuerySet3["Total"] = round(QuerySet3["UnitPrice"] * QuerySet3["UnitCount"], 2)
                        QuerySet3["BackorderQuantity"] = bill_credit_memo_refund[i]["Quantity"]

                else:
                    if bill_credit_memo_refund[i]["Amount"] < 0:
                        QuerySet3["ReceivedQuantity"] = -1
                        QuerySet3["Bill_credit_memo_refundQuantity"] = -1
                        QuerySet3["UnitCount"] = -1
                        QuerySet3["UnitPrice"] = abs(bill_credit_memo_refund[i]["Amount"])
                        QuerySet3["Total"] = round(QuerySet3["UnitPrice"] * QuerySet3["UnitCount"], 2)
                        QuerySet3["BackorderQuantity"] = -1
                    else:
                        QuerySet3["ReceivedQuantity"] = 1
                        QuerySet3["Bill_credit_memo_refundQuantity"] = 1
                        QuerySet3["UnitCount"] = 1
                        QuerySet3["UnitPrice"] = abs(bill_credit_memo_refund[i]["Amount"])
                        QuerySet3["Total"] = round(QuerySet3["UnitPrice"] * QuerySet3["UnitCount"], 2)
                        QuerySet3["BackorderQuantity"] = 1

            for j3 in range(0, len(taxcode_myob)):
                if taxcode_myob[j3]['Code'] == 'N-T':
                    FreightTaxCode['UID'] = taxcode_myob[j3]['UID']
                    FreightTaxCode['Code'] = taxcode_myob[j3]['Code']
            QuerySet1['FreightTaxCode'] = FreightTaxCode

            if (bill_credit_memo_refund[i]["Status"] != 'SUBMITTED') and (
                    bill_credit_memo_refund[i]['Status'] != "DRAFT") and (
                    bill_credit_memo_refund[i]['Status'] != "VOIDED") and (
                    bill_credit_memo_refund[i]['Status'] != "DELETED"):
                # if  bill_credit_memo_refund[i]["Inv_No"] in  ["405 - I52832810"]:
                payload = json.dumps(QuerySet1)
                print(payload)
                print(i)
                # if 'ItemCode' in bill_credit_memo_refund[i]["Line"][j]:
                #     url1 = f"{base_url}/Purchase/Bill_credit_memo_refund/Item"
                # else:bill_credit_memo_refund[i]["Inv_No"]
                #     url1 = f"{base_url}/Purchase/Bill_credit_memo_refund/Service"

                id_or_name_value_for_error = (
                    bill_credit_memo_refund[i]['InvoiceNumber']
                    if bill_credit_memo_refund[i]['InvoiceNumber'] is not None
                    else None)

                payload1, base_url, headers = get_settings_myob(job_id)
                url1 = f"{base_url}/Purchase/bill/Item"
                asyncio.run(
                    post_data_in_myob(url1, headers, payload, dbname['xero_supplier_credit_cash_refund'], _id, job_id,
                                      task_id,
                                      id_or_name_value_for_error))


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
