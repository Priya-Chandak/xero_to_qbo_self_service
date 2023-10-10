import asyncio
import json

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_credite_memo_refund_as_invoice(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        credit_memo_refund_payment1 = dbname['xero_credit_memo_refund_payment'].find({"job_id": job_id})

        credit_memo_refund_payment = []
        for p1 in credit_memo_refund_payment1:
            credit_memo_refund_payment.append(p1)

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

        supplier1 = dbname['supplier'].find({"job_id": job_id})
        supplier = []
        for k5 in range(0, dbname['supplier'].count_documents({"job_id": job_id})):
            supplier.append(supplier1[k5])

        xero_archived_coa1 = dbname['xero_archived_coa'].find({"job_id": job_id})
        xero_archived_coa = []
        for k4 in range(0, dbname['xero_archived_coa'].count_documents({"job_id": job_id})):
            xero_archived_coa.append(xero_archived_coa1[k4])

        xero_item1 = dbname['xero_items'].find({"job_id": job_id})
        xero_item = []
        for p51 in xero_item1:
            xero_item.append(p51)

        credit_memo_refund = credit_memo_refund_payment
        for i in range(0, len(credit_memo_refund)):
            # for a in range(0, len(xero_account)):
            #     if credit_memo_refund[i]["AccountCode"] == xero_account[a]["AccountID"]:
            #             for b in range(0, len(chart_of_account)):
            #                 if xero_account[a]["Name"].lower().strip() == chart_of_account[b]["Name"].lower().strip():
            #                     if chart_of_account[b]["Account_Type"] in ['Bank','BANK']:
            _id = credit_memo_refund[i]['_id']
            task_id = credit_memo_refund[i]['task_id']

            QuerySet1 = {"Lines": []}
            contact = {}
            terms = {}
            QuerySet2 = {}
            QuerySet1["Number"] = credit_memo_refund[i]["InvoiceNumber"][-13:]
            QuerySet1["Date"] = credit_memo_refund[i]["Date"]
            QuerySet1['CustomerPurchaseOrderNumber'] = credit_memo_refund[i]['InvoiceID']

            # terms['PaymentIsDue'] = "OnADayOfTheMonth"
            # duedate = datetime.strptime(credit_memo_refund[i]["DueDate"][0:10], '%Y-%m-%d')
            # terms['BalanceDueDate'] = duedate.day
            # terms["DueDate"] = credit_memo_refund[i]["DueDate"]
            # terms['DiscountDate'] = 0

            for c1 in range(0, len(myob_customer)):
                if myob_customer[c1]["Company_Name"] != None and myob_customer[c1]["Company_Name"] != "":
                    if myob_customer[c1]["Company_Name"][0:50] == credit_memo_refund[i]['Contact'][0:50]:
                        contact['UID'] = myob_customer[c1]["UID"]
                    elif myob_customer[c1]["Company_Name"].startswith(credit_memo_refund[i]['Contact']) and \
                            myob_customer[c1]["Company_Name"].endswith("- C"):
                        contact['UID'] = myob_customer[c1]["UID"]

            for c01 in range(0, len(supplier)):
                if supplier[c01]["CompanyName"] != None and supplier[c01]["CompanyName"] != "":
                    if supplier[c01]["CompanyName"][0:50] == credit_memo_refund[i]['Contact'][0:50]:
                        contact['UID'] = supplier[c01]["UID"]
                    elif supplier[c01]["CompanyName"].startswith(credit_memo_refund[i]['Contact']) and \
                            supplier[c01]["CompanyName"].endswith("- S"):
                        contact['UID'] = supplier[c01]["UID"]
            if contact != {} and contact != None:
                QuerySet1["Customer"] = contact
            QuerySet1['IsTaxInclusive'] = True

            if 'AccountCode' in credit_memo_refund[i]:

                QuerySet3 = {}
                Item = {}
                Account = {}
                taxcode = {}
                myob_job = {}

                for j3 in range(0, len(taxcode_myob1)):
                    if taxcode_myob1[j3]['Code'] == 'N-T':
                        taxcode['UID'] = taxcode_myob1[j3]['UID']
                        taxrate1 = taxcode_myob1[j3]['Rate']

                QuerySet2['TaxCode'] = taxcode
                QuerySet3['TaxCode'] = taxcode

                if 'Quantity' in credit_memo_refund[i]:
                    QuerySet3['UnitCount'] = credit_memo_refund[i]["Quantity"]
                    QuerySet3["UnitPrice"] = abs(credit_memo_refund[i]["Amount"])
                    QuerySet3['ShipQuantity'] = 0
                    QuerySet3['CostOfGoodsSold'] = 0

                    QuerySet3["Total"] = abs(credit_memo_refund[i]["Amount"])


                else:
                    QuerySet3['UnitCount'] = 1
                    QuerySet3["UnitPrice"] = abs(credit_memo_refund[i]["Amount"])
                    QuerySet3['ShipQuantity'] = 0
                    QuerySet3['CostOfGoodsSold'] = 0

                    QuerySet3["Total"] = abs(credit_memo_refund[i]["Amount"])

                for j9 in range(0, len(xero_account)):
                    if credit_memo_refund[i]["AccountCode"] == xero_account[j9]["AccountID"]:
                        for j5 in range(0, len(chart_of_account)):
                            if xero_account[j9]["Name"] == chart_of_account[j5]["Name"]:
                                Account["UID"] = chart_of_account[j5]["UID"]
                            else:
                                pass
                for n in range(0, len(xero_archived_coa)):
                    for p1 in range(0, len(chart_of_account)):
                        if credit_memo_refund[i]["AccountCode"] == xero_archived_coa[n]['AccountID']:
                            if xero_archived_coa[n]['Name'] == chart_of_account[p1]["Name"]:
                                Account["UID"] = chart_of_account[p1]["UID"]

                if Account != {} and Account != None:
                    QuerySet3['account'] = Account

                QuerySet3['TaxCode'] = taxcode
                QuerySet3['Type'] = "Transaction"

                QuerySet1["Lines"].append(QuerySet3)

            if (credit_memo_refund[i]["Status"] != 'SUBMITTED') and (credit_memo_refund[i]['Status'] != "DRAFT") and (
                    credit_memo_refund[i]['Status'] != "VOIDED") and (credit_memo_refund[i]['Status'] != "DELETED"):
                payload = json.dumps(QuerySet1)
                print(payload)

                id_or_name_value_for_error = (
                    credit_memo_refund[i]['InvoiceNumber']
                    if credit_memo_refund[i]['InvoiceNumber'] is not None
                    else "")

                payload1, base_url, headers = get_settings_myob(job_id)
                url1 = f"{base_url}/Sale/Invoice/Item"
                if credit_memo_refund[i]['is_pushed'] == 0:
                    asyncio.run(
                        post_data_in_myob(url1, headers, payload, dbname['xero_credit_memo_refund_payment'], _id,
                                          job_id, task_id,
                                          id_or_name_value_for_error))
                else:
                    pass


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
