import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_spend_overpayment_as_billcredit_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        spend_money = dbname['xero_spend_overpayment'].find({"job_id": job_id})
        xero_spend_overpayment = []
        for p1 in spend_money:
            xero_spend_overpayment.append(p1)

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

        myob_job1 = dbname['job'].find({"job_id": job_id})
        myob_job = []
        for p7 in myob_job1:
            myob_job.append(p7)

        myob_supplier1 = dbname['supplier'].find({"job_id": job_id})
        myob_supplier = []
        for k10 in range(0, dbname['supplier'].count_documents({"job_id": job_id})):
            myob_supplier.append(myob_supplier1[k10])

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for k4 in range(0, dbname['xero_coa'].count_documents({"job_id": job_id})):
            xero_coa.append(xero_coa1[k4])

        for i in range(0, len(xero_spend_overpayment)):
            for a in range(0, len(xero_coa)):
                if xero_spend_overpayment[i]["BankAccountID"] == xero_coa[a]["AccountID"]:
                    for b in range(0, len(chart_of_account)):
                        if xero_coa[a]["Name"].lower().strip() == chart_of_account[b]["Name"].lower().strip():
                            if chart_of_account[b]["Account_Type"] in ['Bank', 'BANK']:

                                _id = xero_spend_overpayment[i]['_id']
                                task_id = xero_spend_overpayment[i]['task_id']
                                QuerySet1 = {"Lines": []}
                                Supplier = {}
                                FreightTaxCode = {}
                                terms = {}
                                line_job = {}

                                if 'Reference' in xero_spend_overpayment[i] and xero_spend_overpayment[i][
                                    'Reference'] != "":
                                    if len(xero_spend_overpayment[i] and xero_spend_overpayment[i]['Reference']) > 15:
                                        QuerySet1["Number"] = "so-" + xero_spend_overpayment[i]["Reference"][:-13]
                                    else:
                                        QuerySet1["Number"] = "so-" + xero_spend_overpayment[i]["Reference"]
                                else:
                                    QuerySet1["Number"] = "so-" + f"xero_spend_overpayment-{i}"

                                journal_date = xero_spend_overpayment[i]["Date"]
                                journal_date11 = int(journal_date[6:16])
                                journal_date12 = datetime.utcfromtimestamp(journal_date11).strftime('%Y-%m-%d')
                                QuerySet1["Date"] = journal_date12

                                terms['PaymentIsDue'] = "OnADayOfTheMonth"
                                if "DueDate" in xero_spend_overpayment[i]:
                                    terms['BalanceDueDate'] = journal_date12.day
                                    terms["DueDate"] = journal_date12
                                    terms['DiscountDate'] = 0

                                    QuerySet1['Terms'] = terms

                                QuerySet1['IsTaxInclusive'] = False
                                QuerySet1['SupplierInvoiceNumber'] = xero_spend_overpayment[i]['BankTransactionID']

                                for k1 in range(0, len(myob_supplier)):

                                    if myob_supplier[k1]["CompanyName"] == xero_spend_overpayment[i]["ContactName"][
                                                                           0:50]:
                                        Supplier['UID'] = myob_supplier[k1]["UID"]
                                        break
                                    elif 'CompanyName' in myob_supplier[k1] and myob_supplier[k1][
                                        "CompanyName"] != None:
                                        if myob_supplier[k1]["CompanyName"].startswith(
                                                xero_spend_overpayment[i]["ContactName"]) and myob_supplier[k1][
                                            "CompanyName"].endswith("- S"):
                                            Supplier['UID'] = myob_supplier[k1]["UID"]
                                            break

                                    QuerySet1["Supplier"] = Supplier

                                for j in range(0, len(xero_spend_overpayment[i]["Line"])):
                                    taxcode = {}
                                    QuerySet3 = {}

                                    for j3 in range(0, len(myob_job)):
                                        if 'TrackingID' in xero_spend_overpayment[i]["Line"][j]:
                                            if myob_job[j3]['Name'] == xero_spend_overpayment[i]["Line"][j][
                                                "TrackingID"]:
                                                line_job['UID'] = myob_job[j3]['UID']

                                    if line_job == {}:
                                        QuerySet3['Job'] = None
                                    else:
                                        QuerySet3['Job'] = line_job

                                    if 'AccountCode' in xero_spend_overpayment[i]['Line'][j]:
                                        Account = {}
                                        if 'AccountCode' in xero_spend_overpayment[i]["Line"][j]:
                                            for j5 in range(0, len(chart_of_account)):
                                                for j51 in range(0, len(xero_coa)):
                                                    if xero_spend_overpayment[i]["Line"][j]["AccountCode"] == \
                                                            xero_coa[j51]['Code']:
                                                        if xero_coa[j51]['Name'].lower().strip() == \
                                                                chart_of_account[j5][
                                                                    "Name"].lower().strip():
                                                            Account["UID"] = chart_of_account[j5]["UID"]

                                            for j3 in range(0, len(taxcode_myob)):
                                                for k1 in range(0, len(xero_tax)):

                                                    if 'TaxType' in xero_spend_overpayment[i]["Line"][j]:
                                                        if xero_spend_overpayment[i]["Line"][j]["TaxType"] != None and \
                                                                xero_spend_overpayment[i]["Line"][j][
                                                                    "TaxType"] != 'NONE':
                                                            if xero_spend_overpayment[i]["Line"][j]["TaxType"] == \
                                                                    xero_tax[k1]['TaxType']:

                                                                if xero_tax[k1]['TaxType'] in ['CAPEXINPUT', 'OUTPUT',
                                                                                               'INPUT']:
                                                                    if taxcode_myob[j3]['Code'] == 'GST':
                                                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                                                        break

                                                                elif xero_tax[k1]['TaxType'] in ['TAX001']:
                                                                    if taxcode_myob[j3]['Code'] == 'CAP':
                                                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                                                        break

                                                                elif xero_tax[k1]['TaxType'] in ["EXEMPTCAPITAL",
                                                                                                 'EXEMPTEXPENSES',
                                                                                                 'EXEMPTOUTPUT',
                                                                                                 'EXEMPTEXPORT']:
                                                                    if taxcode_myob[j3]['Code'] == 'FRE':
                                                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                                                        break

                                                                elif xero_tax[k1]['TaxType'] in ["INPUTTAXED"]:
                                                                    if taxcode_myob[j3]['Code'] == 'INP':
                                                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                                                        break

                                                                elif xero_tax[k1]['TaxType'] in ["BASEXCLUDED",
                                                                                                 "BAS-W1", "BAS-W2"]:
                                                                    if taxcode_myob[j3]['Code'] == 'N-T':
                                                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                                                        break
                                                        else:
                                                            if taxcode_myob[j3]['Code'] == 'N-T':
                                                                taxcode['UID'] = taxcode_myob[j3]['UID']
                                                                break

                                            QuerySet3['TaxCode'] = taxcode
                                            QuerySet3['account'] = Account

                                        if "Description" in xero_spend_overpayment[i]["Line"][j]:
                                            QuerySet3["Description"] = xero_spend_overpayment[i]["Line"][j][
                                                "Description"]

                                        if 'Quantity' in xero_spend_overpayment[i]["Line"][j]:
                                            if xero_spend_overpayment[i]["Line"][j]["LineAmount"] < 0:
                                                QuerySet3["ReceivedQuantity"] = -xero_spend_overpayment[i]["Line"][j][
                                                    "Quantity"]
                                                QuerySet3["BillQuantity"] = -xero_spend_overpayment[i]["Line"][j][
                                                    "Quantity"]
                                                QuerySet3["UnitCount"] = -xero_spend_overpayment[i]["Line"][j][
                                                    "Quantity"]
                                                QuerySet3["UnitPrice"] = abs(
                                                    xero_spend_overpayment[i]["Line"][j]["UnitAmount"])
                                                QuerySet3["Total"] = QuerySet3["UnitPrice"] * QuerySet3["UnitCount"]
                                            else:
                                                QuerySet3["ReceivedQuantity"] = xero_spend_overpayment[i]["Line"][j][
                                                    "Quantity"]
                                                QuerySet3["BillQuantity"] = xero_spend_overpayment[i]["Line"][j][
                                                    "Quantity"]
                                                QuerySet3["UnitCount"] = xero_spend_overpayment[i]["Line"][j][
                                                    "Quantity"]
                                                QuerySet3["UnitPrice"] = xero_spend_overpayment[i]["Line"][j][
                                                    "UnitAmount"]
                                                QuerySet3["Total"] = QuerySet3["UnitPrice"] * QuerySet3["UnitCount"]
                                        else:
                                            if xero_spend_overpayment[i]["Line"][j]["LineAmount"] < 0:
                                                QuerySet3["ReceivedQuantity"] = -1
                                                QuerySet3["BillQuantity"] = -1
                                                QuerySet3["UnitCount"] = -1
                                                QuerySet3["UnitPrice"] = abs(
                                                    xero_spend_overpayment[i]["Line"][j]["UnitAmount"])
                                                QuerySet3["Total"] = QuerySet3["UnitPrice"] * QuerySet3["UnitCount"]
                                            else:
                                                QuerySet3["ReceivedQuantity"] = 1
                                                QuerySet3["BillQuantity"] = 1
                                                QuerySet3["UnitCount"] = 1
                                                QuerySet3["UnitPrice"] = abs(
                                                    xero_spend_overpayment[i]["Line"][j]["UnitAmount"])
                                                QuerySet3["Total"] = QuerySet3["UnitPrice"] * QuerySet3["UnitCount"]

                                    QuerySet1["Lines"].append(QuerySet3)

                                    payload = json.dumps(QuerySet1)
                                    print(payload)

                                    id_or_name_value_for_error = (
                                        xero_spend_overpayment[i]['BankTransactionID']
                                        if xero_spend_overpayment[i]['BankTransactionID'] is not None
                                        else None)

                                    payload1, base_url, headers = get_settings_myob(job_id)
                                    url = f"{base_url}/Purchase/Bill/Item"
                                    if xero_spend_overpayment[i]['is_pushed'] == 0:
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
