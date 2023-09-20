import traceback

from apps.home.data_util import add_job_status
from apps.util.db_mongo import get_mongodb_database


def account_reference(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        Collection1 = dbname["QBO_COA"]
        income_acc1 = dbname["QBO_income_acc"]
        expense_acc1 = dbname["QBO_expense_acc"]
        asset_acc1 = dbname["QBO_asset_acc"]

        x = Collection1.find({"job_id": job_id})
        data1 = []
        for p1 in range(0, Collection1.count_documents({job_id:job_id})):
            data1.append(x[p1])

        income_acc = []
        expense_acc = []
        asset_acc = []

        for i in range(0, len(data1)):
            QuerySet1 = {"job_id": job_id, "task_id": task_id, 'table_name': "professional_bill", 'error': None,
                         "is_pushed": 0}
            QuerySet2 = {"job_id": job_id, "task_id": task_id, 'table_name': "professional_bill", 'error': None,
                         "is_pushed": 0}
            QuerySet3 = {"job_id": job_id, "task_id": task_id, 'table_name': "professional_bill", 'error': None,
                         "is_pushed": 0}

            if (
                    data1[i]["AccountType"] == "Other Current Asset"
                    or data1[i]["AccountType"] == "Fixed Asset"
            ):
                QuerySet3["Name"] = data1[i]["Name"]
                QuerySet3["value"] = data1[i]["Id"]
                QuerySet3["AccountType"] = "Other Current Asset"
                QuerySet3["AccountSubType"] = "Inventory"
                asset_acc.append(QuerySet3)

            elif (
                    data1[i]["AccountType"] == "Expense"
                    or data1[i]["AccountType"] == "Other Expense"
                    or data1[i]["AccountType"] == "Cost of Goods Sold"
            ):
                QuerySet2["Name"] = data1[i]["Name"]
                QuerySet2["value"] = data1[i]["Id"]
                QuerySet2["AccountType"] = "Cost of Goods Sold"
                QuerySet2["AccountSubType"] = "SuppliesMaterialsCogs"
                expense_acc.append(QuerySet2)

            elif (
                    data1[i]["AccountType"] == "Income"
                    or data1[i]["AccountType"] == "Other Income"
            ):
                QuerySet1["Name"] = data1[i]["Name"]
                QuerySet1["value"] = data1[i]["Id"]
                QuerySet1["AccountType"] = "Income"
                QuerySet1["AccountSubType"] = "SalesOfProductIncome"
                income_acc.append(QuerySet1)

        asset_acc1.insert_many(asset_acc)
        expense_acc1.insert_many(expense_acc)
        income_acc1.insert_many(income_acc)
    except Exception as ex:
        traceback.print_exc()
        
