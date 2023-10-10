import json

import requests

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


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

        default_coa = [{"Name": "Item Sales",
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
                QuerySet1["DisplayID"] = f"{main_acct}" + default_coa[i]['Number']

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
