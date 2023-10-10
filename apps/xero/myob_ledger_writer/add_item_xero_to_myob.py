import asyncio
import json

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_item_xero_to_myob(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        xero_item1 = dbname['xero_items'].find({"job_id": job_id})
        xero_item = []
        for k1 in range(0, dbname['xero_items'].count_documents({"job_id": job_id})):
            xero_item.append(xero_item1[k1])

        Item = xero_item

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({"job_id": job_id})):
            chart_of_account.append(chart_of_account1[k3])

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for k3 in range(0, dbname['xero_coa'].count_documents({"job_id": job_id})):
            xero_coa.append(xero_coa1[k3])

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({"job_id": job_id})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        Item = Item

        for i in range(0, len(Item)):
            print(Item[i])
            _id = Item[i]["_id"]
            task_id = Item[i]["task_id"]
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet3 = {}
            QuerySet4 = {}
            taxcode = {}
            incomeacc = {}
            expenseacc = {}
            QuerySet1["Number"] = Item[i]["Code"]

            if 'Name' in Item[i]:
                QuerySet1["Name"] = Item[i]["Name"][0:30]
            else:
                QuerySet1["Name"] = Item[i]["Code"]

            if "Description" in Item[i]:
                QuerySet1["Description"] = Item[i]["Description"][0:250]

            if 'SalesDetails' in Item[i]:
                for j in range(0, len(chart_of_account)):
                    if Item[i]["SalesDetails"] != None and Item[i]["SalesDetails"] != [{}]:
                        if 'UnitPrice' in Item[i]["SalesDetails"][0]:
                            QuerySet4['BaseSellingPrice'] = Item[i]["SalesDetails"][0]["UnitPrice"]
                            for j7 in range(0, len(xero_coa)):
                                if "AccountCode" in Item[i]["SalesDetails"][0]:
                                    if Item[i]["SalesDetails"][0]["AccountCode"] == str(
                                            chart_of_account[j]["DisplayId"]):
                                        incomeacc["UID"] = chart_of_account[j]["UID"]
                                        QuerySet2 = incomeacc
                                        break

                                    elif Item[i]["SalesDetails"][0]["AccountCode"] == xero_coa[j7]["Code"]:
                                        if xero_coa[j7]["Name"] == chart_of_account[j]['Name']:
                                            incomeacc["UID"] = chart_of_account[j]["UID"]
                                            QuerySet2 = incomeacc
                                            break


                                else:
                                    if chart_of_account[j]['Name'] == "Item Sale":
                                        incomeacc["UID"] = chart_of_account[j]['UID']
                                        QuerySet2 = incomeacc
                                        break
                    else:
                        if chart_of_account[j]['Name'] == "Item Sale":
                            incomeacc["UID"] = chart_of_account[j]['UID']
                            QuerySet2 = incomeacc
                            break

            if 'PurchaseDetails' in Item[i]:
                for j1 in range(0, len(chart_of_account)):
                    for j8 in range(0, len(xero_coa)):
                        if "AccountCode" in Item[i]["PurchaseDetails"][0] or 'COGSAccountCode' in \
                                Item[i]["PurchaseDetails"][0]:
                            if Item[i]["PurchaseDetails"] != None and Item[i]["PurchaseDetails"] != [{}]:

                                if 'COGSAccountCode' in Item[i]["PurchaseDetails"][0]:
                                    if Item[i]["PurchaseDetails"][0]["COGSAccountCode"] == str(
                                            chart_of_account[j1]["Number"]):
                                        expenseacc["UID"] = chart_of_account[j1]["UID"]
                                        QuerySet3 = expenseacc
                                        break
                                    elif Item[i]["PurchaseDetails"][0]["COGSAccountCode"] == xero_coa[j8]["Code"]:
                                        if xero_coa[j8]["Name"] == chart_of_account[j1]['Name']:
                                            expenseacc["UID"] = chart_of_account[j1]["UID"]
                                            QuerySet3 = expenseacc
                                            break

                                elif 'AccountCode' in Item[i]["PurchaseDetails"][0]:

                                    if Item[i]["PurchaseDetails"][0]["AccountCode"] == str(
                                            chart_of_account[j1]["Number"]):
                                        expenseacc["UID"] = chart_of_account[j1]["UID"]
                                        QuerySet3 = expenseacc
                                        break
                                    elif Item[i]["PurchaseDetails"][0]["AccountCode"] == xero_coa[j8]["Code"]:
                                        if xero_coa[j8]["Name"] == chart_of_account[j1]['Name']:
                                            expenseacc["UID"] = chart_of_account[j1]["UID"]
                                            QuerySet3 = expenseacc
                                            break
                            else:
                                if chart_of_account[j1]['Name'] == "Item Purchase":
                                    expenseacc["UID"] = chart_of_account[j1]['UID']
                                    QuerySet3 = expenseacc
                                    break
                        else:
                            if chart_of_account[j1]['Name'] == "Item Purchase":
                                expenseacc["UID"] = chart_of_account[j1]['UID']
                                QuerySet3 = expenseacc
                                break

            if Item[i]['IsSold'] == True:
                QuerySet1["IncomeAccount"] = QuerySet2
                QuerySet1['IsSold'] = True
            if Item[i]['IsPurchased'] == True:
                QuerySet1["ExpenseAccount"] = QuerySet3
                QuerySet1['IsBought'] = True

            for j3 in range(0, len(taxcode_myob)):
                for j02 in range(0, len(xero_tax)):
                    if 'SalesDetails' in Item[i]:
                        if 'TaxType' in Item[i]["SalesDetails"][0] and 'TaxType' in Item[i]["SalesDetails"][0][
                            'TaxType'] != "":
                            if Item[i]["SalesDetails"][0]["TaxType"] == xero_tax[j02]['TaxType']:
                                if xero_tax[j02]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT']:
                                    if taxcode_myob[j3]['Code'] == 'GST':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[j02]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES', 'EXEMPTOUTPUT',
                                                                  'EXEMPTEXPORT']:
                                    if taxcode_myob[j3]['Code'] == 'FRE':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[j02]['TaxType'] in ["INPUTTAXED"]:
                                    if taxcode_myob[j3]['Code'] == 'INP':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[j02]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2"]:
                                    if taxcode_myob[j3]['Code'] == 'N-T':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']

                            QuerySet4["Taxcode"] = taxcode
                            QuerySet1["SellingDetails"] = QuerySet4

                        else:
                            if taxcode_myob[j3]['Code'] == 'N-T':
                                taxcode['UID'] = taxcode_myob[j3]['UID']

                            QuerySet4["Taxcode"] = taxcode
                            QuerySet1["SellingDetails"] = QuerySet4

                    if 'PurchaseDetails' in Item[i]:

                        if 'TaxType' in Item[i]["PurchaseDetails"][0] and Item[i]["PurchaseDetails"][0][
                            "TaxType"] != "":

                            if Item[i]["PurchaseDetails"][0]["TaxType"] == xero_tax[j02]['TaxType']:

                                if xero_tax[j02]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT']:
                                    if taxcode_myob[j3]['Code'] == 'GST':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[j02]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES', 'EXEMPTOUTPUT',
                                                                  'EXEMPTEXPORT']:
                                    if taxcode_myob[j3]['Code'] == 'FRE':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[j02]['TaxType'] in ["INPUTTAXED"]:
                                    if taxcode_myob[j3]['Code'] == 'INP':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[j02]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2"]:
                                    if taxcode_myob[j3]['Code'] == 'N-T':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']

                            QuerySet4["Taxcode"] = taxcode
                            QuerySet1["BuyingDetails"] = QuerySet4

                        else:
                            if taxcode_myob[j3]['Code'] == 'N-T':
                                taxcode['UID'] = taxcode_myob[j3]['UID']

                            QuerySet4["Taxcode"] = taxcode
                            QuerySet1["BuyingDetails"] = QuerySet4

            payload = json.dumps(QuerySet1)
            print(payload)

            id_or_name_value_for_error = (
                Item[i]["Code"]
                if Item[i]["Code"] is not None
                else "")

            payload1, base_url, headers = get_settings_myob(job_id)

            url = f"{base_url}/Inventory/Item"
            if Item[i]["is_pushed"] == 0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, dbname['xero_items'], _id, job_id, task_id,
                                      id_or_name_value_for_error))

            else:
                pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
