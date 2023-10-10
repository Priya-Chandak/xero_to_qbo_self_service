import asyncio
import json

import requests

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_chart_account_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        xero_coa = dbname['xero_coa']
        myob_coa = dbname['chart_of_account']
        xero_taxrate = dbname['xero_taxrate']
        taxcode_myob = dbname['taxcode_myob']

        x = xero_coa.find({"job_id": job_id})
        xero_coa1 = []
        for k in x:
            xero_coa1.append(k)

        myob_coa = myob_coa.find({"job_id": job_id})
        myob_coa1 = []
        for k in myob_coa:
            myob_coa1.append(k)

        p = xero_taxrate.find({"job_id": job_id})
        xero_taxrate1 = []
        for k in p:
            xero_taxrate1.append(k)

        s = taxcode_myob.find({"job_id": job_id})
        taxcode_myob1 = []
        for k in s:
            taxcode_myob1.append(k)

        parent_acc1 = ['Income', 'Expenses', 'Assets', 'Liabilities', 'Equity', 'Cost Of Sales', 'Other Income',
                       'Other Expenses', 'Non Current Liabilities']
        parent_acc = []
        if len(myob_coa1) > 0:
            for j in range(0, len(myob_coa1)):
                if myob_coa1[j]['Name'] in parent_acc1:
                    acc = {}
                    acc['Name'] = myob_coa1[j]['Name']
                    acc['UID'] = myob_coa1[j]['UID']

                    if acc not in parent_acc:
                        parent_acc.append(acc)

        xero_coa1 = xero_coa1

        for i in range(0, len(xero_coa1)):
            print(i)

            _id = xero_coa1[i]['_id']
            task_id = xero_coa1[i]['task_id']
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet3 = {}

            QuerySet1['Name'] = xero_coa1[i]['Name']

            if xero_coa1[i]['Type'] in ["BANK", "Accounts Receivable", "INVENTORY", "CURRENT",
                                        "Inventory Asset account", "Prepayment account", "FIXED Asset", "Fixed Assets",
                                        "FIXED"]:
                main_acct = "1-"
            elif xero_coa1[i]['Type'] in ["CreditCard", "Accounts Payable", "LIABILITY", "CURRLIAB",
                                          "PAYG Liability account", "Superannuation Liability account", "TERMLIAB",
                                          "NONCURRENT LIABILITY", "NONCURRENT"]:
                main_acct = "2-"
            elif xero_coa1[i]['Type'] in ["EQUITY"]:
                main_acct = "3-"
            elif xero_coa1[i]['Type'] in ["REVENUE", "SALES"]:
                main_acct = "4-"
            elif xero_coa1[i]['Type'] in ["DIRECTCOSTS"]:
                main_acct = "5-"
            elif xero_coa1[i]['Type'] in ["EXPENSE", "Superannuation Expense account", "Wages Expense account",
                                          "OVERHEADS"]:
                main_acct = "6-"
            elif xero_coa1[i]['Type'] in ["OTHERINCOME"]:
                main_acct = "8-"
            elif xero_coa1[i]['Type'] in ["OTHEREXPENSE"]:
                main_acct = "9-"

            if 'Code' in xero_coa1[i] and xero_coa1[i]['Code'] != None:

                splitted_code = (xero_coa1[i]['Code']).split(".")
                splitted_join = ("".join(splitted_code))

                splitted_code2 = (xero_coa1[i]['Code']).split("/")
                splitted_join2 = ("".join(splitted_code2))

                # splitted_code3 =(xero_coa1[i]['Code']).split("-")
                # splitted_join3 = splitted_code3[1]

                if len(splitted_join) == 3:
                    QuerySet1["DisplayID"] = f"{main_acct}" + "0" + splitted_join
                elif len(splitted_join) == 4:
                    QuerySet1["DisplayID"] = f"{main_acct}" + splitted_join
                # elif len(splitted_code3) == 4 :
                #     QuerySet1["DisplayID"] = f"{main_acct}" + splitted_join3
                else:
                    QuerySet1["DisplayID"] = f"{main_acct}" + xero_coa1[i]['Code']
                QuerySet1["Number"] = str(xero_coa1[i]['Code'])

            else:
                # TypeError: can only concatenate str (not "int") to str

                QuerySet1["DisplayID"] = f"{main_acct}" + str(9000 + i)
                QuerySet1["Number"] = str(9000 + i)

            if "Type" in xero_coa1[i]:
                if xero_coa1[i]['Type'] == 'BANK':
                    QuerySet1['Type'] = 'Bank'
                elif xero_coa1[i]['Type'] == 'Accounts Receivable':
                    QuerySet1['Type'] = 'AccountsReceivable'
                elif xero_coa1[i]['Type'] == 'INVENTORY' or xero_coa1[i]['Type'] == 'CURRENT' or xero_coa1[i][
                    'Type'] == 'Inventory Asset account' or xero_coa1[i]['Type'] == 'Prepayment account' or \
                        xero_coa1[i]['Type'] == "PREPAYMENT":
                    QuerySet1['Type'] = 'OtherCurrentAsset'
                elif xero_coa1[i]['Type'] == 'FIXED Asset' or xero_coa1[i]['Type'] == 'Fixed Assets' or xero_coa1[i][
                    'Type'] == 'FIXED':
                    QuerySet1['Type'] = 'FixedAsset'
                elif (xero_coa1[i]['Type'] == 'REVENUE') or (xero_coa1[i]['Type'] == 'SALES'):
                    QuerySet1['Type'] = 'Income'
                elif (xero_coa1[i]['Type'] == 'LIABILITY') or (xero_coa1[i]['Type'] == 'CURRLIAB') or (
                        xero_coa1[i]['Type'] == 'PAYG Liability account') or (
                        xero_coa1[i]['Type'] == 'Superannuation Liability account'):
                    QuerySet1['Type'] = 'OtherCurrentLiability'
                elif (xero_coa1[i]['Type'] == 'TERMLIAB'):
                    QuerySet1['Type'] = 'LongTermLiability'
                elif (xero_coa1[i]['Type'] == 'NONCURRENT LIABILITY') or (xero_coa1[i]["Type"] == "NONCURRENT"):
                    QuerySet1['Type'] = 'OtherLiability'
                elif xero_coa1[i]['Type'] == 'EQUITY':
                    QuerySet1['Type'] = 'Equity'
                elif (xero_coa1[i]['Type'] == 'EXPENSE') or (
                        xero_coa1[i]["Type"] == "Superannuation Expense account") or (
                        xero_coa1[i]["Type"] == "Wages Expense account") or (xero_coa1[i]["Type"] == "OVERHEADS") or (
                        xero_coa1[i]["Type"] == "DEPRECIATN"):
                    QuerySet1['Type'] = 'Expense'
                elif xero_coa1[i]['Type'] == 'DIRECTCOSTS':
                    QuerySet1['Type'] = 'CostOfSales'
                elif xero_coa1[i]['Type'] == 'OTHERINCOME':
                    QuerySet1['Type'] = 'OtherIncome'
                elif xero_coa1[i]['Type'] == 'Accounts Payable':
                    QuerySet1['Type'] = 'AccountsPayable'
                elif xero_coa1[i]['Type'] == 'CreditCard':
                    QuerySet1['Type'] = 'CreditCard'
                elif (xero_coa1[i]["Type"] == "OTHEREXPENSE"):
                    QuerySet1['Type'] = 'OtherExpense'
                else:
                    print(xero_coa1[i]['Type'])

            if len(parent_acc) > 0:
                for j1 in range(0, len(parent_acc)):
                    if QuerySet1['Type'] in ['Bank', 'AccountsReceivable', 'OtherCurrentAsset', 'FixedAsset']:
                        if parent_acc[j1]['Name'] == "Assets":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] in ['LongTermLiability', 'CreditCard', 'AccountsPayable', 'OtherLiability',
                                               'OtherCurrentLiability']:
                        if parent_acc[j1]['Name'] == "Liabilities":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] in ['Equity']:
                        if parent_acc[j1]['Name'] == "Equity":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] in ['Income']:
                        if parent_acc[j1]['Name'] == "Income":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] in ['CostOfSales']:
                        if parent_acc[j1]['Name'] == "Cost Of Sales":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] in ['OtherIncome']:
                        if parent_acc[j1]['Name'] == "Other Income":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] in ['OtherExpense']:
                        if parent_acc[j1]['Name'] == "Other Expense":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] == 'Expense':
                        if parent_acc[j1]['Name'] == "Expenses":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] == 'LongTermLiability':
                        if parent_acc[j1]['Name'] == "Non Current Liabilities":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

            QuerySet1["ParentAccount"] = QuerySet3
            QuerySet1["Description"] = None

            for p1 in range(0, len(taxcode_myob1)):
                if "TaxType" in xero_coa1[i]:
                    if xero_coa1[i]['TaxType'] == 'BASEXCLUDED':
                        if taxcode_myob1[p1]['Code'] == 'N-T':
                            QuerySet2['UID'] = taxcode_myob1[p1]['UID']

                    elif xero_coa1[i]['TaxType'] in ['EXEMPTCAPITAL', 'EXEMPTEXPENSES', 'EXEMPTEXPORT', 'EXEMPTOUTPUT']:
                        if taxcode_myob1[p1]['Code'] == 'FRE':
                            QuerySet2['UID'] = taxcode_myob1[p1]['UID']

                    elif xero_coa1[i]['TaxType'] in ['GSTONCAPIMPORTS', 'INPUT', 'GSTONIMPORTS', 'OUTPUT']:
                        if taxcode_myob1[p1]['Code'] == 'GST':
                            QuerySet2['UID'] = taxcode_myob1[p1]['UID']

                    elif xero_coa1[i]['TaxType'] == 'INPUTTAXED':
                        if taxcode_myob1[p1]['Code'] == 'INP':
                            QuerySet2['UID'] = taxcode_myob1[p1]['UID']

                    else:
                        if taxcode_myob1[p1]['Code'] == 'N-T':
                            QuerySet2['UID'] = taxcode_myob1[p1]['UID']

                QuerySet1["TaxCode"] = QuerySet2
            payload = json.dumps(QuerySet1)
            id_or_name_value_for_error = (
                xero_coa1[i]['Name']
                if xero_coa1[i]['Name'] is not None
                else None)

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/GeneralLedger/Account"

            if xero_coa1[i]['is_pushed'] == 0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, dbname['xero_coa'], _id, job_id, task_id,
                                      id_or_name_value_for_error))
            else:
                pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


def add_xero_chart_of_account_as_default_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        myob_coa = dbname['chart_of_account']
        taxcode_myob = dbname['taxcode_myob']

        myob_coa = myob_coa.find({"job_id": job_id})
        myob_coa1 = []
        for k in myob_coa:
            myob_coa1.append(k)

        s = taxcode_myob.find({"job_id": job_id})
        taxcode_myob1 = []
        for k in s:
            taxcode_myob1.append(k)

        parent_acc1 = ['Income', 'Cost Of Sales']
        parent_acc = []
        if len(myob_coa1) > 0:
            for j in range(0, len(myob_coa1)):
                if myob_coa1[j]['Name'] in parent_acc1:
                    acc = {}
                    acc['Name'] = myob_coa1[j]['Name']
                    acc['UID'] = myob_coa1[j]['UID']

                    if acc not in parent_acc:
                        parent_acc.append(acc)

        default_coa = [{"Name": "Item Sale",
                        "Type": "SALES",
                        "Number": 9999,
                        "Description": "",
                        "TaxType": "N-T"},
                       {"Name": "Item Purchase",
                        "Type": "DIRECTCOSTS",
                        "Number": 9991,
                        "Description": "",
                        "TaxType": "N-T"

                        }]
        for i in range(0, len(default_coa)):
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet3 = {}

            QuerySet1['Name'] = default_coa[i]['Name']

            if default_coa[i]['Type'] in ["SALES"]:
                main_acct = "4-"
            elif default_coa[i]['Type'] in ["DIRECTCOSTS"]:
                main_acct = "5-"

            if 'Number' in default_coa[i] and default_coa[i]['Number'] != None:
                QuerySet1["DisplayID"] = f"{main_acct}" + str(default_coa[i]['Number'])

            if "Type" in default_coa[i]:

                if (default_coa[i]['Type'] == 'REVENUE') or (default_coa[i]['Type'] == 'SALES'):
                    QuerySet1['Type'] = 'Income'

                elif default_coa[i]['Type'] == 'DIRECTCOSTS':
                    QuerySet1['Type'] = 'CostOfSales'

            if len(parent_acc) > 0:
                for j1 in range(0, len(parent_acc)):
                    if QuerySet1['Type'] in ['Income']:
                        if parent_acc[j1]['Name'] == "Income":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

                    elif QuerySet1['Type'] in ['CostOfSales']:
                        if parent_acc[j1]['Name'] == "Cost Of Sales":
                            QuerySet3['Name'] = parent_acc[j1]['Name']
                            QuerySet3['UID'] = parent_acc[j1]['UID']

            QuerySet1["ParentAccount"] = QuerySet3
            QuerySet1["Description"] = None

            for p1 in range(0, len(taxcode_myob1)):
                if "TaxType" in default_coa[i]:
                    if default_coa[i]['TaxType'] == 'N-T':
                        if taxcode_myob1[p1]['Code'] == 'N-T':
                            QuerySet2['UID'] = taxcode_myob1[p1]['UID']

                QuerySet1["TaxCode"] = QuerySet2
            payload = json.dumps(QuerySet1)
            print(payload)
            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/GeneralLedger/Account"
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
