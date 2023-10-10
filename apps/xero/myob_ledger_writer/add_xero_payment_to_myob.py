import asyncio
import datetime
import json
from multiprocessing import Pool

from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_payment_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        # url = f"{base_url}/Sale/CustomerPayment"

        payment1 = dbname['xero_invoice_payment'].find({"job_id":job_id})

        payment = []
        for p1 in payment1:
            payment.append(p1)

        xero_coa1 = dbname['xero_coa'].find({"job_id":job_id})
        xero_coa = []
        for k4 in range(0, dbname['xero_coa'].count_documents({"job_id":job_id})):
            xero_coa.append(xero_coa1[k4])

        
        xero_archived_coa1 = dbname['xero_archived_coa'].find({"job_id":job_id})
        xero_archived_coa = []
        for k4 in range(0, dbname['xero_archived_coa'].count_documents({"job_id":job_id})):
            xero_archived_coa.append(xero_archived_coa1[k4])

        chart_of_account1 = dbname['chart_of_account'].find({"job_id":job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({"job_id":job_id})):
            chart_of_account.append(chart_of_account1[k3])

        myob_customer1 = dbname['customer'].find({"job_id":job_id})
        myob_customer = []
        for k5 in range(0, dbname['customer'].count_documents({"job_id":job_id})):
            myob_customer.append(myob_customer1[k5])

        xero_invoice1 = dbname['xero_invoice'].find({"job_id":job_id})
        xero_invoice = []
        for k10 in range(0, dbname['xero_invoice'].count_documents({"job_id":job_id})):
            xero_invoice.append(xero_invoice1[k10])

        batch_payment1 = dbname['xero_invoice_batchpayment'].find({"job_id":job_id})
        batch_payment = []
        for k14 in range(0, dbname['xero_invoice_batchpayment'].count_documents({"job_id":job_id})):
            batch_payment.append(batch_payment1[k14])

        myob_invoice1 = dbname['all_invoice'].find({"job_id":job_id})
        myob_invoice = []
        for k11 in range(0, dbname['all_invoice'].count_documents({"job_id":job_id})):
            myob_invoice.append(myob_invoice1[k11])

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
                                "Account_Type"].lower().strip() == ["bank","CreditCard"])]

        payment = payment
        for i in range(0, len(payment)):
            print(i)
            print(payment[i])
            # if "AccountCode" in payment[i] and payment[i]["AccountCode"] in account_ids:
            #     xero_temp_data = xero_account_id_name_mappings_dict.get(payment[i]["AccountCode"])
            #     for b in range(0, len(coa_refined_data)):
            #         if xero_temp_data == coa_refined_data[b]["Name"].lower().strip():
            _id = payment[i]['_id']
            task_id = payment[i]['task_id']
            Customer = {}
            QuerySet1 = {"Invoices": []}
            # account = {"UID": coa_refined_data[b]["UID"]}
            account={}
            # QuerySet1["account"] = account
            QuerySet1["Date"] = payment[i]["Date"]
            if 'Reference' in payment[i] and payment[i]['Reference'] != "":
                QuerySet1["PaymentNumber"] = payment[i]["Reference"]
            else:
                QuerySet1["PaymentNumber"] = f"payment-{i}"

            for m in range(0,len(xero_coa)):
                for p in range(0,len(chart_of_account)):
                    if payment[i]['AccountCode'] == xero_coa[m]['AccountID']:
                        if xero_coa[m]['Name'] == chart_of_account[p]["Name"]:
                            account['UID'] = chart_of_account[p]["UID"]    

            for n in range(0,len(xero_archived_coa)):    
                for p1 in range(0,len(chart_of_account)):
                    if payment[i]['AccountCode'] == xero_archived_coa[n]['AccountID']:
                        if xero_archived_coa[n]['Name'] == chart_of_account[p1]["Name"]:
                            account['UID'] = chart_of_account[p1]["UID"]

            if account != {} and account != None:
                QuerySet1["account"] = account


            for k in range(0, len(myob_customer)):
                if myob_customer[k]["Company_Name"]!=None:
                    if payment[i]["Contact"][0:50].strip().lower() == myob_customer[k]["Company_Name"].strip().lower():
                        Customer["UID"] = myob_customer[k]["UID"]
                        break
                    elif myob_customer[k]["Company_Name"].startswith(payment[i]["Contact"]) and myob_customer[k][
                        "Company_Name"].endswith("- C"):
                        Customer["UID"] = myob_customer[k]["UID"]
                        break
                    # elif payment[i]["Contact"][0:50].strip().lower() == myob_customer[k]["Company_Name"][
                    #                                                     0:50].strip().lower():
                        # Customer["UID"] = myob_customer[k]["UID"]

            QuerySet1["Customer"] = Customer

            invoice = {}
            invoice["Type"] = 'Invoice'
            for m in range(0, len(myob_invoice)):
                if payment[i]["InvoiceID"] == myob_invoice[m]['Customer_po_number']:
                    invoice["UID"] = myob_invoice[m]["UID"]
                    invoice["AmountApplied"] = payment[i]["Amount"]
                    QuerySet1["Invoices"].append(invoice)
                

            payload = json.dumps(QuerySet1)
            print(payload)
            id_or_name_value_for_error =(str(payment[i]['InvoiceNumber'] )+ "-" + str(payment[i]["Date"])+ "-"+ str(payment[i]["Amount"]))
                
            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/Sale/CustomerPayment"

            if payment[i]['is_pushed']==0:
                asyncio.run(post_data_in_myob(url, headers, payload, dbname['xero_invoice_payment'], _id, job_id,
                                                task_id,
                                                id_or_name_value_for_error))
            else:
                pass

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
