import sys

from pymongo import MongoClient

from apps.home.data_util import write_task_execution_step, update_task_execution_status
from apps.mmc_settings.all_settings import get_settings_myob


def get_xero_classified_coa_for_myobledger(job_id, task_id):
    try:
        myclient = MongoClient("mongodb://localhost:27017/")
        db = myclient["MMC"]
        classified_coa = db['xero_classified_coa']
        payload, base_url, headers = get_settings_myob(job_id)
        url = f"{base_url}/GeneralLedger/Account"

        coa = db['xero_coa']
        x = coa.find({"job_id": job_id})

        data1 = []
        for p in x:
            data1.append(p)
        data = data1

        list1 = []
        for p in range(0, len(data)):
            Queryset = {}
            Queryset["Name"] = data[p]["Name"]
            Queryset["Type"] = data[p]["Type"]
            if "Code" in data[p]:
                Queryset["Number"] = data[p]["Code"]

            list1.append(Queryset)

        list2 = []
        for i in range(0, len(list1)):
            if ('Type' in list1[i].keys()):
                QuerySet1 = {"job_id": job_id, "task_id": task_id, "is_pushed": 0, "table_name": "xero_classified_coa",
                             'Name': list1[i]['Name']}
                if 'Number' in list1[i]:
                    QuerySet1['Number'] = list1[i]['Number']

                if list1[i]['Type'] == 'BANK':
                    QuerySet1['Type'] = 'Banking'
                elif list1[i]['Type'] == 'FIXED Asset' or list1[i]['Type'] == 'Fixed Assets' or list1[i][
                    'Type'] == 'FIXED':
                    QuerySet1['Type'] = 'Fixed Assets'
                elif list1[i]['Type'] == 'REVENUE':
                    QuerySet1['Type'] = 'Income'
                elif (list1[i]['Type'] == 'LIABILITY') or (list1[i]['Type'] == 'CURRLIAB') or (
                        list1[i]['Type'] == 'PAYG Liability account') or (
                        list1[i]['Type'] == 'Superannuation Liability account'):
                    QuerySet1['Type'] = 'Current Liabilities'
                elif (list1[i]['Type'] == 'TERMLIAB'):
                    QuerySet1['Type'] = 'LongTermLiability'
                elif list1[i]['Type'] == 'EQUITY':
                    QuerySet1['Type'] = 'Equity'
                elif list1[i]['Type'] == 'EXPENSE' or list1[i]["Type"] == "Superannuation Expense account" or list1[i][
                    "Type"] == "Wages Expense account":
                    QuerySet1['Type'] = 'Expense'
                elif list1[i]['Type'] == 'DIRECTCOSTS':
                    QuerySet1['Type'] = 'Cost of Sales'
                elif list1[i]['Type'] == 'OTHERINCOME':
                    QuerySet1['Type'] = 'Other Income'
                elif list1[i]['Type'] == 'Accounts Payable':
                    QuerySet1['Type'] = 'Accounts Payable'
                elif list1[i]['Type'] == 'Accounts Receivable':
                    QuerySet1['Type'] = 'Accounts Receivable'
                elif list1[i]['Type'] == 'CreditCard':
                    QuerySet1['Type'] = 'Credit Card'
                elif list1[i]['Type'] == 'INVENTORY' or list1[i]['Type'] == 'CURRENT' or list1[i][
                    'Type'] == 'Inventory Asset account' or list1[i]['Type'] == 'Prepayment account':
                    QuerySet1['Type'] = 'Current Assets'
                else:
                    pass

                list2.append(QuerySet1)

        classified_coa.insert_many(list2)

        step_name = "Reading data from xero classification chart of account"
        write_task_execution_step(task_id, status=1, step=step_name)

    except Exception as ex:
        step_name = "Access token not valid"
        write_task_execution_step(task_id, status=0, step=step_name)
        update_task_execution_status(task_id, status=0, task_type="read")
        import traceback
        traceback.print_exc()
        print(ex)
        sys.exit(0)
