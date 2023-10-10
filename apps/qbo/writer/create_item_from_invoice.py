import json

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def create_item_from_invoice(job_id, task_id):
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        Collection = db['item_invoice']
        income_acc1 = db['QBO_income_acc']
        expense_acc1 = db['QBO_expense_acc']
        asset_acc1 = db['QBO_asset_acc']

        x = Collection.find()
        data1 = []
        for p1 in x:
            data1.append(p1)

        QuerySet = data1

        QBO_COA = db['QBO_COA'].find()
        QBO_coa = []
        for p21 in QBO_COA:
            QBO_coa.append(p21)

        income_acc1 = db['QBO_income_acc'].find()
        income_acc = []
        for p2 in income_acc1:
            income_acc.append(p2)

        expense_acc1 = db['QBO_expense_acc'].find()
        expense_acc = []
        for p3 in expense_acc1:
            expense_acc.append(p3)

        asset_acc1 = db['QBO_asset_acc'].find()
        asset_acc = []
        for p4 in asset_acc1:
            asset_acc.append(p4)

        # API = item
        url = f"{base_url}/item?minorversion={minorversion}"

        arr = []
        for i1 in range(0, len(QuerySet)):
            _id = QuerySet[i1]['_id']
            task_id = task_id
            for j in range(0, len(QuerySet[i1]["Item"])):
                if "item_name" not in QuerySet[i1]["Item"][j]:
                    if "acc_id" in QuerySet[i1]["Item"][j]:
                        if QuerySet[i1]["Item"][j]["DisplayID"] not in arr:
                            arr.append(QuerySet[i1]["Item"][j]["DisplayID"])

        print(arr, len(arr), "====================")

        for i in range(0, len(arr)):
            # for j in range(0,len(QuerySet[i]['Item'])):
            # if 'item_name' not in QuerySet[i]['Item'][j]:

            QuerySet1 = {}
            QuerySet3 = {}
            QuerySet4 = {}
            QuerySet5 = {}

            if 'DisplayID' in QuerySet[i]['Item'][j]:
                QuerySet1["Name"] = QuerySet[i]['Item'][j]["DisplayID"]
                QuerySet1["Sku"] = QuerySet[i]['Item'][j]["DisplayID"]

            if 'description' in QuerySet[i]['Item'][j]:
                QuerySet1["Description"] = QuerySet[i]['Item'][j]["description"]
                QuerySet1["PurchaseDesc"] = QuerySet[i]['Item'][j]["description"]

            if 'unit_price' in QuerySet[i]['Item'][j]:
                QuerySet1["UnitPrice"] = QuerySet[i]['Item'][j]["unit_price"]
                QuerySet1["PurchaseCost"] = QuerySet[i]['Item'][j]["unit_price"]

            for j1 in range(0, len(QBO_coa)):
                if "DisplayID" in QuerySet[i]['Item'][j]:
                    if 'AcctNum' in QBO_coa[j1]:
                        if QuerySet[i]['Item'][j]['DisplayID'] == QBO_coa[j1]["AcctNum"]:
                            QuerySet3["value"] = QBO_coa[j1]['Id']
                            QuerySet3["name"] = QBO_coa[j1]['Name']
                    else:
                        if QuerySet[i]['Item'][j]['account_name'].strip().lower() == QBO_coa[j1][
                            "Name"].strip().lower():
                            QuerySet3["value"] = QBO_coa[j1]['Id']
                            QuerySet3["name"] = QBO_coa[j1]['Name']

            QuerySet1["Type"] = "NonInventory"
            if 'quantity' in QuerySet[i]['Item'][j]:
                QuerySet1["TrackQtyOnHand"] = int(QuerySet[i]['Item'][j]["quantity"])
                QuerySet1["QtyOnHand"] = int(QuerySet[i]['Item'][j]["quantity"])

            QuerySet1["InvStartDate"] = QuerySet[i]["invoice_date"]

            QuerySet1["IncomeAccountRef"] = QuerySet3
            QuerySet1["ExpenseAccountRef"] = QuerySet3
            QuerySet1["AssetAccountRef"] = QuerySet3

            payload = json.dumps(QuerySet1)
            print(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            print("--")
            post_data_in_qbo(url, headers, payload, Collection, _id, job_id, task_id, arr[i])

            # if response.status_code == 401:
            #     res1=json.loads(response.text)
            #     res2=(res1['fault']['error'][0]['message']).split(";")[0]
            #     add_job_status(job_id, res2)
            # elif response.status_code == 400:
            #     res1=json.loads(response.text)
            #     res2=(res1['Fault']['Error'][0]['Message'] + ': {}'.format(QuerySet[i]["invoice_no"]))
            #     add_job_status(job_id, res2)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()


def create_item_from_service_invoice(job_id, task_id):
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        Collection = db['service_invoice']
        income_acc1 = db['QBO_income_acc']
        expense_acc1 = db['QBO_expense_acc']
        asset_acc1 = db['QBO_asset_acc']

        x = Collection.find()
        data1 = []
        for p1 in x:
            data1.append(p1)

        QuerySet = data1

        QBO_COA = db['QBO_COA'].find()
        QBO_coa = []
        for p21 in QBO_COA:
            QBO_coa.append(p21)

        income_acc1 = db['QBO_income_acc'].find()
        income_acc = []
        for p2 in income_acc1:
            income_acc.append(p2)

        expense_acc1 = db['QBO_expense_acc'].find()
        expense_acc = []
        for p3 in expense_acc1:
            expense_acc.append(p3)

        asset_acc1 = db['QBO_asset_acc'].find()
        asset_acc = []
        for p4 in asset_acc1:
            asset_acc.append(p4)

        # API = item
        url = f"{base_url}/item?minorversion={minorversion}"

        arr = []
        for i1 in range(0, len(QuerySet)):
            _id = QuerySet[i1]['_id']
            task_id = task_id
            for j in range(0, len(QuerySet[i1]["account"])):
                if "ItemCode" not in QuerySet[i1]["account"][j]:
                    if "acc_id" in QuerySet[i1]["account"][j]:
                        if QuerySet[i1]["account"][j]["acc_id"] not in arr:
                            arr.append(QuerySet[i1]["account"][j]["acc_id"])
        print(arr, len(arr), "====================")

        for i in range(0, len(arr)):

            QuerySet1 = {}
            QuerySet3 = {}

            QuerySet1["Name"] = arr[i]
            QuerySet1["Sku"] = arr[i]

            QuerySet1["UnitPrice"] = 0
            QuerySet1["PurchaseCost"] = 0

            for j1 in range(0, len(QBO_coa)):
                if 'AcctNum' in QBO_coa[j1]:
                    if arr[i] == QBO_coa[j1]["AcctNum"]:
                        QuerySet3["value"] = QBO_coa[j1]['Id']
                        QuerySet3["name"] = QBO_coa[j1]['Name']
                        break

            QuerySet1["Type"] = "NonInventory"
            QuerySet1["IncomeAccountRef"] = QuerySet3
            QuerySet1["ExpenseAccountRef"] = QuerySet3
            QuerySet1["AssetAccountRef"] = QuerySet3

            payload = json.dumps(QuerySet1)
            print(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            print("--")

            post_data_in_qbo(url, headers, payload, Collection, _id, job_id, task_id, arr[i])


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()


def create_item_from_itemcode_acccode(job_id, task_id):
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        Collection = db['item_invoice']

        x = Collection.find()
        data1 = []
        for p1 in x:
            data1.append(p1)

        QuerySet = data1

        # a1=[]
        # for mi in range(0,len(data1)):
        #     if data1[mi]['invoice_no'] in ['IXP2016111809']:
        #         a1.append(data1[mi])

        # QuerySet = a1

        QBO_COA = db['QBO_COA'].find()
        QBO_coa = []
        for p21 in QBO_COA:
            QBO_coa.append(p21)

        qbo_item1 = db['QBO_Item'].find()
        qbo_item = []
        for p21 in qbo_item1:
            qbo_item.append(p21)

        url = f"{base_url}/item?minorversion={minorversion}"
        for i in range(0, len(QuerySet)):
            for j in range(0, len(QuerySet[i]['Item'])):
                if 'item_name' in QuerySet[i]['Item'][j] and 'DisplayID' in QuerySet[i]['Item'][j]:
                    for k in range(0, len(qbo_item)):
                        for j1 in range(0, len(QBO_coa)):
                            item_used = QuerySet[i]['Item'][j]['item_name'].replace(":", "-")
                            if item_used.lower().strip() == qbo_item[k]['Name'].lower().strip():
                                if qbo_item[k]['IncomeAccountRef']["value"] == QBO_coa[j1]['Id']:
                                    if 'AcctNum' in QBO_coa[j1]:
                                        if QuerySet[i]['Item'][j]['DisplayID'] != QBO_coa[j1]['AcctNum']:
                                            QuerySet1 = {}
                                            QuerySet3 = {}

                                            QuerySet1["Name"] = QuerySet[i]['Item'][j]["item_name"] + "-" + \
                                                                QuerySet[i]['Item'][j]["DisplayID"]
                                            QuerySet1["Sku"] = QuerySet1["Name"]
                                            for j11 in range(0, len(QBO_coa)):
                                                if 'AcctNum' in QBO_coa[j11]:
                                                    if QuerySet[i]['Item'][j]['DisplayID'] == QBO_coa[j11]["AcctNum"]:
                                                        QuerySet3["value"] = QBO_coa[j11]['Id']
                                                        QuerySet3["name"] = QBO_coa[j11]['Name']
                                                    else:
                                                        if QuerySet[i]['Item'][j]['account_name'].strip().lower() == \
                                                                QBO_coa[j1]["FullyQualifiedName"].strip().lower():
                                                            QuerySet3["value"] = QBO_coa[j11]['Id']
                                                            QuerySet3["name"] = QBO_coa[j11]['Name']

                                            QuerySet1["Type"] = "NonInventory"

                                            QuerySet1["IncomeAccountRef"] = QuerySet3
                                            QuerySet1["ExpenseAccountRef"] = QuerySet3
                                            QuerySet1["AssetAccountRef"] = QuerySet3

                                            payload = json.dumps(QuerySet1)
                                            print(payload)
                                            response = requests.request("POST", url, headers=headers, data=payload)
                                            print(response)
                                            print("--")

                                            if response.status_code == 401:
                                                res1 = json.loads(response.text)
                                                res2 = (res1['fault']['error'][0]['message']).split(";")[0]
                                                add_job_status(job_id, res2)
                                            elif response.status_code == 400:
                                                res1 = json.loads(response.text)
                                                res2 = (res1['Fault']['Error'][0]['Message'] + ': {}'.format(
                                                    QuerySet[i]["invoice_no"]))
                                                add_job_status(job_id, res2)

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex)
        print(ex)
