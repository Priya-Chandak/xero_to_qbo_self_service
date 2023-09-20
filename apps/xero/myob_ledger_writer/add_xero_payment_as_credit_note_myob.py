import asyncio
import datetime
import json
from multiprocessing import Pool

from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_payment_as_creditnote_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        xero_invoice = dbname['xero_invoice_payment'].find({"job_id": job_id})

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

        xero_archived_coa1 = dbname['xero_archived_coa'].find({"job_id":job_id})
        xero_archived_coa = []
        for k4 in range(0, dbname['xero_archived_coa'].count_documents({"job_id":job_id})):
            xero_archived_coa.append(xero_archived_coa1[k4])

        job11 = dbname['job'].find({"job_id": job_id})
        job1 = []
        for k8 in range(0, dbname['job'].count_documents({"job_id": job_id})):
            job1.append(job11[k8])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        xero_coa1 = dbname['xero_coa'].find({'job_id': job_id})
        xero_coa = []
        for k4 in range(0, dbname['xero_coa'].count_documents({'job_id': job_id})):
            xero_coa.append(xero_coa1[k4])

        xero_item1 = dbname['xero_items'].find({"job_id": job_id})
        xero_item = []
        for p51 in xero_item1:
            xero_item.append(p51)

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
                                "Account_Type"].lower().strip() != "bank")]

        multiple_invoice = multiple_invoice

        for i in range(0, len(multiple_invoice)): 
            if "AccountCode" in multiple_invoice[i] and multiple_invoice[i]["AccountCode"] in account_ids:
                xero_temp_data = xero_account_id_name_mappings_dict.get(multiple_invoice[i]["AccountCode"])
                for b in range(0, len(coa_refined_data)):
                    if xero_temp_data == coa_refined_data[b]["Name"].lower().strip():
                        _id = multiple_invoice[i]['_id']
                        task_id = multiple_invoice[i]['task_id']
                        QuerySet1 = {"Lines": []}
                        Customer = {}

                        if 'Reference' in multiple_invoice[i] and multiple_invoice[i]['Reference'] != "":
                            QuerySet1["Number"] = multiple_invoice[i]["Reference"]
                        else:
                            QuerySet1["Number"] = f"multiple_invoice-{i}"

                        QuerySet1["Date"] = multiple_invoice[i]["Date"]

                        for c1 in range(0, len(myob_customer)):
                            if myob_customer[c1]["Company_Name"] !=None and myob_customer[c1]["Company_Name"] !="":
                                if myob_customer[c1]["Company_Name"].strip().lower() == multiple_invoice[i]["Contact"].strip().lower():
                                    Customer['UID'] = myob_customer[c1]["UID"]
                                elif myob_customer[c1]["Company_Name"].startswith(multiple_invoice[i]["Contact"]) and \
                                        myob_customer[c1]["Company_Name"].endswith("- C"):
                                    Customer['UID'] = myob_customer[c1]["UID"]

                        QuerySet1["Customer"] = Customer
                        # if 'InvoiceID' in multiple_invoice[i]:

                        if 'AccountCode' in multiple_invoice[i] :
                            QuerySet3 = {}
                            taxcode = {}
                            account = {"UID": coa_refined_data[b]["UID"]}
                            QuerySet3["Account"] = account
                            for j3 in range(0, len(taxcode_myob1)):
                                if taxcode_myob1[j3]['Code'] == 'N-T':
                                    taxcode['UID'] = taxcode_myob1[j3]['UID']

                            QuerySet3['TaxCode'] = taxcode

                            if multiple_invoice[i]["Amount"] < 0:
                                QuerySet3['ShipQuantity'] = -1
                                QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Amount"])
                                QuerySet3["Total"] = QuerySet3["UnitPrice"]*QuerySet3["UnitCount"]
                                QuerySet3['UnitCount'] = -1
                            else:
                                QuerySet3['ShipQuantity'] = 1
                                QuerySet3["UnitPrice"] = abs(multiple_invoice[i]["Amount"])
                                QuerySet3["Total"] = QuerySet3["UnitPrice"]*QuerySet3["UnitCount"]
                                QuerySet3['UnitCount'] = 1
                        
                        QuerySet3['Type'] = "Transaction"
                        QuerySet1["Lines"].append(QuerySet3)

                        
                payload = json.dumps(QuerySet1)
                print(payload)

                id_or_name_value_for_error = (
                    multiple_invoice[i]["InvoiceID"]
                    if multiple_invoice[i]["InvoiceID"] is not None
                    else multiple_invoice[i]['Date'])
                payload1, base_url, headers = get_settings_myob(job_id)
                url1 = f"{base_url}/Sale/Invoice/Item"

                asyncio.run(post_data_in_myob(url1, headers, payload, dbname['xero_invoice_payment'], _id, job_id, task_id,
                                                id_or_name_value_for_error))


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
