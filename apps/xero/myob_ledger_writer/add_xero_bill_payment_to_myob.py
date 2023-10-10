import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_bill_payment_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        payment1 = dbname['xero_bill_payment'].find({'job_id': job_id})

        payment = []
        for p1 in payment1:
            payment.append(p1)

        taxcode_myob1 = dbname['taxcode_myob'].find({'job_id': job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({'job_id': job_id})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_coa1 = dbname['xero_coa'].find({'job_id': job_id})
        xero_coa = []
        for k4 in range(0, dbname['xero_coa'].count_documents({'job_id': job_id})):
            xero_coa.append(xero_coa1[k4])

        chart_of_account1 = dbname['chart_of_account'].find({'job_id': job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({'job_id': job_id})):
            chart_of_account.append(chart_of_account1[k3])

        myob_supplier1 = dbname['supplier'].find({'job_id': job_id})
        myob_supplier = []
        for k5 in range(0, dbname['supplier'].count_documents({'job_id': job_id})):
            myob_supplier.append(myob_supplier1[k5])

        xero_bill1 = dbname['xero_bill'].find({'job_id': job_id})
        xero_bill_data = []
        for k10 in range(0, dbname['xero_bill'].count_documents({'job_id': job_id})):
            xero_bill_data.append(xero_bill1[k10])

        all_bill1 = dbname['all_bill'].find({'job_id': job_id})
        all_bill = []
        for k11 in range(0, dbname['all_bill'].count_documents({'job_id': job_id})):
            all_bill.append(all_bill1[k11])

        account_ids = [record.get('AccountID') for record in xero_coa]
        xero_names = [{"Name": record.get('Name').lower().strip(), "AccountID": record.get('AccountID')} for record in
                      xero_coa]
        xero_account_id_name_mappings = [{record.get('AccountID'): record.get('Name').lower().strip()} for record in
                                         xero_coa]
        xero_account_id_name_mappings_dict = {}
        for dct in xero_account_id_name_mappings:
            xero_account_id_name_mappings_dict.update(dct)
        xero_only_names = [record.get('Name').lower().strip() for record in xero_coa]
        xero_data_dict = {item['Name']: item for item in xero_names}
        coa_refined_data = [{"Name": record.get('Name').lower().strip(), "UID": record.get('UID'),
                             "Account_Type": record.get('Account_Type'),
                             "job_id": record.get('job_id')} for record in chart_of_account if (
                                    record["Name"].lower().strip() in xero_only_names and record[
                                "Account_Type"].lower().strip() == ["bank", "CreditCard"])]

        for i in range(0, len(payment)):
            print(i)
            # # for i in range(31, 200):
            #     if "AccountCode" in payment[i] and payment[i]["AccountCode"] in account_ids:
            #         print("inside account code")
            #         xero_temp_data = xero_account_id_name_mappings_dict.get(payment[i]["AccountCode"])
            #         print(xero_temp_data,"xero account data -----")
            #         print(coa_refined_data,"coa_refined_data ---------")

            #         for b in range(0, len(coa_refined_data)):

            #             if xero_temp_data == coa_refined_data[b]["Name"].lower().strip():
            for a in range(0, len(xero_coa)):
                if payment[i]["AccountCode"] == xero_coa[a]["AccountID"]:
                    for b in range(0, len(chart_of_account)):
                        if xero_coa[a]["Name"].lower().strip() == chart_of_account[b]["Name"].lower().strip():
                            print(chart_of_account[b]["Name"])
                            if chart_of_account[b]["Account_Type"] in ['Bank', 'BANK', "CreditCard"]:
                                _id = payment[i]['_id']
                                task_id = payment[i]['task_id']
                                QuerySet1 = {"Lines": []}
                                Supplier = {}
                                account = {}

                                purchase = {}
                                invoice = {'Purchase': purchase, "Type": 'Bill'}

                                journal_date = payment[i]["Date"]
                                journal_date11 = int(journal_date[6:16])
                                journal_date12 = datetime.utcfromtimestamp(journal_date11).strftime('%Y-%m-%d')

                                QuerySet1["Date"] = journal_date12
                                if 'InvoiceNumber' in payment[i]:
                                    QuerySet1["PaymentNumber"] = payment[i]["InvoiceNumber"][-13:]

                                for k in range(0, len(myob_supplier)):
                                    if payment[i]["Contact"][0:50] == myob_supplier[k]["CompanyName"]:
                                        Supplier["UID"] = myob_supplier[k]["UID"]

                                    elif 'CompanyName' in myob_supplier[k] and myob_supplier[k]['CompanyName'] != None:
                                        if myob_supplier[k]["CompanyName"].startswith(payment[i]["Contact"][0:50]) and \
                                                myob_supplier[k][
                                                    "CompanyName"].endswith("- S"):
                                            Supplier["UID"] = myob_supplier[k]["UID"]
                                    QuerySet1["Supplier"] = Supplier

                                for j5 in range(0, len(chart_of_account)):
                                    for j51 in range(0, len(xero_coa)):
                                        if payment[i]["AccountCode"] == xero_coa[j51]['AccountID']:
                                            if xero_coa[j51]['Name'].lower().strip() == chart_of_account[j5][
                                                "Name"].lower().strip():
                                                account["UID"] = chart_of_account[j5]["UID"]

                                QuerySet1["account"] = account

                                for m in range(0, len(all_bill)):
                                    # for m23 in range(0, len(xero_bill_data)):

                                    if payment[i]["InvoiceID"] == all_bill[m]['supplier_invoice_no']:
                                        purchase["UID"] = all_bill[m]["UID"]
                                        invoice["AmountApplied"] = payment[i]["Amount"]

                                QuerySet1["Lines"].append(invoice)

                                payload = json.dumps(QuerySet1)
                                print(payload)
                                print(payment[i])

                                id_or_name_value_for_error = (str(payment[i]["InvoiceNumber"]) + "-" + str(
                                    payment[i]["Date"]) + "-" + str(payment[i]["Amount"]))

                                payload1, base_url, headers = get_settings_myob(job_id)
                                url = f"{base_url}/Purchase/SupplierPayment"
                                if payment[i]['is_pushed'] == 0:
                                    asyncio.run(
                                        post_data_in_myob(url, headers, payload, dbname['xero_bill_payment'], _id,
                                                          job_id, task_id,
                                                          id_or_name_value_for_error))
                                else:
                                    pass
                            else:
                                print("Supplier Credits")

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
