import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database


def get_classified_coa(job_id,task_id):
    try:
        db = get_mongodb_database()
        classified_coa = db["classified_coa"]
        (
            base_url,
            headers,
            company_id,
            minorversion,
            get_data_header,
            report_headers,
        ) = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"

        coa = db["chart_of_account"]
        x = coa.find({"job_id": job_id})

        data1 = []
        for p in x:
            data1.append(p)
        QuerySet1 = data1

        list1 = []

        for q in range(0, len(QuerySet1)):
            QuerySet2 = {}
            QuerySet2["Name"] = QuerySet1[q]["Name"].replace(":","-")
            QuerySet2["job_id"] = job_id
            QuerySet2["task_id"] = task_id
            QuerySet2["is_pushed"] = 0
            QuerySet2["table_name"]="classified_coa"
            QuerySet2["AccountType"] = QuerySet1[q]["Account_Type"]
            QuerySet2["AcctNum"] = QuerySet1[q]["DisplayId"]
            QuerySet2["error"] = None
            
            list1.append(QuerySet2)

        list2 = []
        for i in range(0, len(list1)):
            if ("AccountType" in list1[i].keys()) and ("AcctNum" in list1[i].keys()):
                QuerySet1 = {}
                QuerySet1["job_id"] = job_id
                QuerySet1["is_pushed"] = 0
                QuerySet1["error"] = None
                QuerySet1["task_id"] = task_id
                QuerySet1["table_name"]="classified_coa"
            
                QuerySet1["Name"] = list1[i]["Name"]
                QuerySet1["AcctNum"] = list1[i]["AcctNum"]

                if list1[i]["AccountType"] == "Income":
                    QuerySet1["AccountType"] = "Income"
                    QuerySet1["AccountSubType"] = "RevenueGeneral"
                elif list1[i]["AccountType"] == "OtherIncome":
                    QuerySet1["AccountType"] = "Other Income"
                    QuerySet1["AccountSubType"] = "OtherMiscellaneousIncome"
                elif list1[i]["AccountType"] == "AccountReceivable":
                    QuerySet1["AccountType"] = "Accounts Receivable"
                    QuerySet1["AccountSubType"] = "AccountsReceivable"
                elif list1[i]["AccountType"] == "AccountsPayable":
                    QuerySet1["AccountType"] = "Accounts Payable"
                    QuerySet1["AccountSubType"] = "AccountsPayable"
                elif list1[i]["AccountType"] == "Expense":
                    QuerySet1["AccountType"] = "Expense"
                    QuerySet1["AccountSubType"] = "OfficeGeneralAdministrativeExpenses"
                elif list1[i]["AccountType"] == "OtherCurrentLiability":
                    QuerySet1["AccountType"] = "Other Current Liability"
                    QuerySet1["AccountSubType"] = "OtherCurrentLiabilities"
                elif list1[i]["AccountType"] == "OtherExpense":
                    QuerySet1["AccountType"] = "Other Expense"
                    QuerySet1["AccountSubType"] = "OtherMiscellaneousExpense"
                elif list1[i]["AccountType"] == "FixedAsset":
                    QuerySet1["AccountType"] = "Fixed Asset"
                    QuerySet1["AccountSubType"] = "OtherFixedAssets"
                elif (list1[i]["AccountType"] == "OtherAsset") or (
                        list1[i]["AccountType"] == "OtherCurrentAsset"
                ):
                    QuerySet1["AccountType"] = "Other Asset"
                    QuerySet1["AccountSubType"] = "OtherCurrentAssets"
                elif list1[i]["AccountType"] == "AccountsReceivable":
                    QuerySet1["AccountType"] = "Accounts Receivable"
                    QuerySet1["AccountSubType"] = "Accounts Receivable"
                elif list1[i]["AccountType"] == "AccountsPayable":
                    QuerySet1["AccountType"] = "Accounts Payable"
                    QuerySet1["AccountSubType"] = "Accounts Payable"
                elif list1[i]["AccountType"] == "OtherLiability":
                    QuerySet1["AccountType"] = "Other Current Liability"
                    QuerySet1["AccountSubType"] = "OtherCurrentLiabilities"
                elif list1[i]["AccountType"] == "Equity":
                    QuerySet1["AccountType"] = "Equity"
                    QuerySet1["AccountSubType"] = "OwnersEquity"
                elif list1[i]["AccountType"] == "Equity":
                    QuerySet1["AccountType"] = "Equity"
                    QuerySet1["AccountSubType"] = "OwnersEquity"
                elif list1[i]["AccountType"] == "CostOfSales":
                    QuerySet1["AccountType"] = "Cost of Goods Sold"
                    QuerySet1["AccountSubType"] = "CostOfSales"
                elif list1[i]["AccountType"] == "LongTermLiability":
                    QuerySet1["AccountType"] = "Long Term Liability"
                    QuerySet1["AccountSubType"] = "OtherLongTermLiabilities"
                elif (list1[i]["AccountType"] == "Credit Card") or (
                        list1[i]["AccountType"] == "CreditCard"
                ):
                    QuerySet1["AccountType"] = "Credit Card"
                    QuerySet1["AccountSubType"] = "CreditCard"
                elif list1[i]["AccountType"] == "CurrentEarnings":
                    QuerySet1["AccountType"] = "Equity"
                    QuerySet1["AccountSubType"] = "RetainedEarnings"
                elif list1[i]["AccountType"] == "RetainedEarnings":
                    QuerySet1["AccountType"] = "Equity"
                    QuerySet1["AccountSubType"] = "RetainedEarnings"
                elif list1[i]["AccountType"] == "Bank":
                    QuerySet1["AccountType"] = "Bank"
                    QuerySet1["AccountSubType"] = "CashAndCashEquivalents"

                else:
                    pass
                    # QuerySet1['AccountType'] = 'Bank'
                    # QuerySet1['AccountSubType'] = 'CashAndCashEquivalents'

                list2.append(QuerySet1)

        classified_coa.insert_many(list2)

    except Exception as ex:
        traceback.print_exc()
        
