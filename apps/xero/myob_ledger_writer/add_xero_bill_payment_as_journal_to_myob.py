import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_billpayment_as_vendorcredit_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        bill1 = dbname['xero_bill_payment'].find({"job_id": job_id})

        payment = []
        for p1 in bill1:
            payment.append(p1)

        myob_item1 = dbname['item'].find({"job_id": job_id})
        myob_item = []
        for k4 in range(0, dbname['item'].count_documents({"job_id": job_id})):
            myob_item.append(myob_item1[k4])

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({"job_id": job_id})):
            chart_of_account.append(chart_of_account1[k3])

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

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for k4 in range(0, dbname['xero_coa'].count_documents({"job_id": job_id})):
            xero_coa.append(xero_coa1[k4])

        for i in range(0, len(payment)):
            for a in range(0, len(xero_coa)):
                if payment[i]["AccountCode"] == xero_coa[a]["AccountID"]:
                    for b in range(0, len(chart_of_account)):
                        if xero_coa[a]["Name"].lower().strip() == chart_of_account[b]["Name"].lower().strip():
                            if chart_of_account[b]["Account_Type"] not in ['Bank', 'BANK', "CreditCard"]:
                                # if "AccountCode" in payment[i] and payment[i]["AccountCode"] in account_ids:
                                #     xero_temp_data = xero_account_id_name_mappings_dict.get(payment[i]["AccountCode"])
                                #     for b in range(0, len(coa_refined_data)):
                                #         if xero_temp_data == coa_refined_data[b]["Name"].lower().strip():
                                _id = payment[i]['_id']
                                task_id = payment[i]['task_id']
                                QuerySet1 = {"Lines": []}
                                QuerySet3 = {}
                                Supplier = {}
                                account = {}
                                # account = {"UID": coa_refined_data[b]["UID"]}
                                # QuerySet3["account"] = account
                                terms = {}

                                QuerySet1["Number"] = "P-" + payment[i]["InvoiceNumber"][-11:]
                                journal_date = payment[i]["Date"]
                                journal_date11 = int(journal_date[6:16])
                                journal_date12 = datetime.utcfromtimestamp(journal_date11).strftime('%Y-%m-%d')
                                QuerySet1["Date"] = journal_date12

                                QuerySet1['AppliedToDate'] = 0

                                terms['PaymentIsDue'] = "OnADayOfTheMonth"
                                if "DueDate" in payment[i]:
                                    terms['BalanceDueDate'] = journal_date12.day
                                    terms["DueDate"] = journal_date12
                                    terms['DiscountDate'] = 0

                                    QuerySet1['Terms'] = terms

                                QuerySet1['IsTaxInclusive'] = False

                                for k1 in range(0, len(myob_supplier)):

                                    if myob_supplier[k1]["CompanyName"] == payment[i]["Contact"][0:50]:
                                        Supplier['UID'] = myob_supplier[k1]["UID"]
                                        break
                                    elif 'CompanyName' in myob_supplier[k1] and myob_supplier[k1][
                                        "CompanyName"] != None:
                                        if myob_supplier[k1]["CompanyName"].startswith(payment[i]["Contact"]) and \
                                                myob_supplier[k1]["CompanyName"].endswith("- S"):
                                            Supplier['UID'] = myob_supplier[k1]["UID"]
                                            break

                                    QuerySet1["Supplier"] = Supplier

                                taxcode = {}

                                for j5 in range(0, len(chart_of_account)):
                                    for j51 in range(0, len(xero_coa)):
                                        if payment[i]["AccountCode"] == xero_coa[j51]['AccountID']:
                                            if xero_coa[j51]['Name'].lower().strip() == chart_of_account[j5][
                                                "Name"].lower().strip():
                                                account["UID"] = chart_of_account[j5]["UID"]

                                QuerySet3["account"] = account

                                for j3 in range(0, len(taxcode_myob)):
                                    if taxcode_myob[j3]['Code'] == 'N-T':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']

                                QuerySet3['TaxCode'] = taxcode
                                QuerySet1['FreightTaxCode'] = taxcode

                                QuerySet3["Description"] = payment[i]["InvoiceID"]

                                QuerySet3["BillQuantity"] = -1
                                QuerySet3["UnitCount"] = -1
                                QuerySet3["UnitPrice"] = payment[i]["BankAmount"]

                                QuerySet1['Lines'].append(QuerySet3)

                                payload = json.dumps(QuerySet1)
                                print(payload)

                                id_or_name_value_for_error = (
                                    payment[i]['InvoiceNumber']
                                    if payment[i]['InvoiceNumber'] is not None
                                    else None)

                                payload1, base_url, headers = get_settings_myob(job_id)
                                url = f"{base_url}/Purchase/Bill/Item"
                                if payment[i]['is_pushed'] == 0:
                                    asyncio.run(
                                        post_data_in_myob(url, headers, payload, dbname['xero_bill_payment'], _id,
                                                          job_id, task_id,
                                                          id_or_name_value_for_error))
                                else:
                                    pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
