import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_bill_credit_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}
        bill1 = dbname['xero_bill_payment'].find({"job_id": job_id})

        bill = []
        for p1 in bill1:
            bill.append(p1)

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

        xero_coa1 = dbname['xero_coa'].find({'job_id': job_id})
        xero_coa = []
        for k4 in range(0, dbname['xero_coa'].count_documents({'job_id': job_id})):
            xero_coa.append(xero_coa1[k4])

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

        for i in range(0, len(bill)):

            if "AccountCode" in bill[i] and bill[i]["AccountCode"] in account_ids:
                xero_temp_data = xero_account_id_name_mappings_dict.get(bill[i]["AccountCode"])
                for b in range(0, len(coa_refined_data)):
                    if xero_temp_data == coa_refined_data[b]["Name"].lower().strip():

                        _id = bill[i]['_id']
                        task_id = bill[i]['task_id']
                        QuerySet1 = {"Lines": []}

                        Supplier = {}
                        FreightTaxCode = {}
                        terms = {}
                        line_job = {}

                        QuerySet1["Number"] = bill[i]["InvoiceNumber"][-13:]

                        journal_date = bill[i]["Date"]
                        journal_date11 = int(journal_date[6:16])
                        journal_date12 = datetime.utcfromtimestamp(journal_date11).strftime('%Y-%m-%d')
                        QuerySet1["Date"] = journal_date12

                        QuerySet1['AppliedToDate'] = 0

                        # terms['PaymentIsDue'] = "OnADayOfTheMonth"
                        # if "DueDate" in bill[i]:
                        #     duedate = datetime.strptime(bill[i]["DueDate"][0:10], '%Y-%m-%d')
                        #     terms['BalanceDueDate'] = duedate.day
                        #     terms["DueDate"] = bill[i]["DueDate"]
                        #     terms['DiscountDate'] = 0

                        #     QuerySet1['Terms'] = terms

                        for k1 in range(0, len(myob_supplier)):

                            if myob_supplier[k1]["CompanyName"] == bill[i]["Contact"][0:50]:
                                Supplier['UID'] = myob_supplier[k1]["UID"]
                                break
                            elif 'CompanyName' in myob_supplier[k1] and myob_supplier[k1]["CompanyName"] != None:
                                if myob_supplier[k1]["CompanyName"].startswith(bill[i]["Contact"]) and \
                                        myob_supplier[k1]["CompanyName"].endswith("- S"):
                                    Supplier['UID'] = myob_supplier[k1]["UID"]
                                    break

                            QuerySet1["Supplier"] = Supplier

                        if 'AccountCode' in bill[i]:
                            taxcode = {}
                            QuerySet3 = {}
                            account = {"UID": coa_refined_data[b]["UID"]}
                            QuerySet3["account"] = account

                            for j3 in range(0, len(taxcode_myob)):
                                if taxcode_myob[j3]['Code'] == 'N-T':
                                    taxcode['UID'] = taxcode_myob[j3]['UID']

                            if bill[i]["Amount"] < 0:
                                QuerySet3["ReceivedQuantity"] = -1
                                QuerySet3["BillQuantity"] = -1
                                QuerySet3["UnitCount"] = -1
                                QuerySet3["UnitPrice"] = abs(bill[i]["Amount"])
                                QuerySet3["Total"] = QuerySet3["UnitPrice"] * QuerySet3["UnitCount"]
                            else:
                                QuerySet3["ReceivedQuantity"] = 1
                                QuerySet3["BillQuantity"] = 1
                                QuerySet3["UnitCount"] = 1
                                QuerySet3["UnitPrice"] = abs(bill[i]["Amount"])
                                QuerySet3["Total"] = QuerySet3["UnitPrice"] * QuerySet3["UnitCount"]

                            QuerySet3['TaxCode'] = taxcode
                            QuerySet1["Lines"].append(QuerySet3)

                        for j3 in range(0, len(taxcode_myob)):
                            if taxcode_myob[j3]['Code'] == 'N-T':
                                FreightTaxCode['UID'] = taxcode_myob[j3]['UID']
                        QuerySet1['FreightTaxCode'] = FreightTaxCode

            payload = json.dumps(QuerySet1)
            print(payload, "-----------------payload")

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
            if bill[i]['is_pushed'] == 0:
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
