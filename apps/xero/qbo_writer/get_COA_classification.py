import logging

from apps.util.db_mongo import get_mongodb_database

import logging


def get_xero_classified_coa(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> get_COA_classification -> get_xero_classified_coa")

        dbname = get_mongodb_database()
        coa = dbname["xero_coa"]
        classified_coa = dbname["xero_classified_coa"]
        x = coa.find({"job_id": job_id})

        data1 = []
        for p in x:
            data1.append(p)
        QuerySet1 = data1

        list1 = []

        for q in range(0, len(QuerySet1)):
            QuerySet2 = {}
            QuerySet2['job_id'] = job_id
            QuerySet2['task_id'] = task_id
            QuerySet2['is_pushed'] = 0
            QuerySet2['error'] = None
            QuerySet2['payload'] = None
            QuerySet2['table_name'] = "xero_classified_coa"
            QuerySet2["Name"] = QuerySet1[q]["Name"].replace(":", "-")
            QuerySet2["AccountType"] = QuerySet1[q]["Type"]
            QuerySet2["BankAccountType"] = QuerySet1[q]["BankAccountType"]
            if "Code" in QuerySet1[q]:
                QuerySet2["AcctNum"] = QuerySet1[q]["Code"]

            list1.append(QuerySet2)

        list2 = []
        for i in range(0, len(list1)):
            if "AccountType" in list1[i].keys():
                QuerySet1 = {}
                QuerySet1['job_id'] = job_id
                QuerySet1["Name"] = list1[i]["Name"]
                QuerySet1['task_id'] = task_id
                QuerySet1['error'] = None
                QuerySet1['is_pushed'] = 0
                QuerySet1['table_name'] = "xero_classified_coa"
                if "AcctNum" in list1[i]:
                    QuerySet1["AcctNum"] = list1[i]["AcctNum"]

                if (
                        list1[i]["AccountType"] == "REVENUE"
                        or list1[i]["AccountType"] == "SALES"
                ):
                    QuerySet1["AccountType"] = "Income"
                    QuerySet1["AccountSubType"] = "RevenueGeneral"
                elif list1[i]["AccountType"] == "OTHERINCOME":
                    QuerySet1["AccountType"] = "Other Income"
                    QuerySet1["AccountSubType"] = "OtherOperatingIncome"
                elif (
                        list1[i]["AccountType"] == "EXPENSE"
                        or list1[i]["AccountType"] == "OVERHEADS"
                ):
                    QuerySet1["AccountType"] = "Expense"
                    QuerySet1["AccountSubType"] = "OfficeGeneralAdministrativeExpenses"
                elif list1[i]["AccountType"] == "EXPENSE":
                    QuerySet1["AccountType"] = "Expense"
                    QuerySet1["AccountSubType"] = "OfficeGeneralAdministrativeExpenses"
                elif (
                        list1[i]["AccountType"] == "NONCURRENT"
                        or list1[i]["AccountType"] == "FIXED Asset"
                        or list1[i]["AccountType"] == "Fixed Assets"
                        or list1[i]["AccountType"] == "FIXED"
                ):
                    QuerySet1["AccountType"] = "Fixed Asset"
                    QuerySet1["AccountSubType"] = "OtherFixedAssets"
                elif (
                        list1[i]["AccountType"] == "PREPAYMENT"
                        or list1[i]["AccountType"] == "Asset"
                        or list1[i]["AccountType"] == "INVENTORY"
                        or list1[i]["AccountType"] == "Current Assets"
                        or list1[i]["AccountType"] == "CURRENT"
                ):
                    QuerySet1["AccountType"] = "Other Asset"
                    QuerySet1["AccountSubType"] = "OtherCurrentAssets"
                elif (
                        (list1[i]["AccountType"] == "LIABILITY")
                        or (list1[i]["AccountType"] == "CURRLIAB")
                        or (list1[i]["AccountType"] == "TERMLIAB")
                ):
                    QuerySet1["AccountType"] = "Other Current Liability"
                    QuerySet1["AccountSubType"] = "OtherCurrentLiabilities"
                elif list1[i]["AccountType"] == "EQUITY":
                    QuerySet1["AccountType"] = "Equity"
                    QuerySet1["AccountSubType"] = "OwnersEquity"
                elif (
                        (list1[i]["AccountType"] == "DIRECTCOSTS")
                        or (list1[i]["AccountType"] == "EXEMPTOUTPUT")
                        or (list1[i]["AccountType"] == "Sales")
                ):
                    QuerySet1["AccountType"] = "Cost of Goods Sold"
                    QuerySet1["AccountSubType"] = "CostOfSales"
                elif list1[i]["AccountType"] == "NONCURRENT LIABILITY":
                    QuerySet1["AccountType"] = "Long Term Liability"
                    QuerySet1["AccountSubType"] = "OtherLongTermLiabilities"
                elif (list1[i]["BankAccountType"] == "CREDITCARD") and (list1[i]["AccountType"] == "BANK"):
                    QuerySet1["AccountType"] = "Credit Card"
                    QuerySet1["AccountSubType"] = "CreditCard"
                elif (list1[i]["AccountType"] == "BANK" or list1[i]["AccountType"] == "Banking") and (
                        list1[i]["BankAccountType"] == "BANK"):
                    QuerySet1["AccountType"] = "Bank"
                    QuerySet1["AccountSubType"] = "CashAndCashEquivalents"
                else:
                    pass

                list2.append(QuerySet1)
        
        if len(list2)>0:
            classified_coa.insert_many(list2)
        else:
            print("No data")

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> get_COA_classification -> get_xero_classified_coa", ex)


def get_xero_classified_archived_coa(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> get_COA_classification -> get_xero_classified_coa")

        dbname = get_mongodb_database()
        coa = dbname["xero_archived_coa"]
        classified_coa = dbname["xero_classified_archived_coa"]
        x = coa.find({"job_id": job_id})

        data1 = []
        for p in x:
            data1.append(p)
        QuerySet1 = data1

        list1 = []

        for q in range(0, len(QuerySet1)):
            QuerySet2 = {}
            QuerySet2['job_id'] = job_id
            QuerySet2['task_id'] = task_id
            QuerySet2['is_pushed'] = 0
            QuerySet2['error'] = None
            QuerySet2['payload'] = None
            QuerySet2['table_name'] = "xero_classified_coa"
            QuerySet2["Name"] = QuerySet1[q]["Name"]
            QuerySet2["AccountType"] = QuerySet1[q]["Type"]
            QuerySet2["BankAccountType"] = QuerySet1[q]["BankAccountType"]
            if "Code" in QuerySet1[q]:
                QuerySet2["AcctNum"] = QuerySet1[q]["Code"]

            list1.append(QuerySet2)

        list2 = []
        for i in range(0, len(list1)):
            if "AccountType" in list1[i].keys():
                QuerySet1 = {}
                QuerySet1['job_id'] = job_id
                QuerySet1["Name"] = list1[i]["Name"]
                QuerySet1['task_id'] = task_id
                QuerySet1['error'] = None
                QuerySet1['is_pushed'] = 0
                QuerySet1['table_name'] = "xero_classified_coa"
                if "AcctNum" in list1[i]:
                    QuerySet1["AcctNum"] = list1[i]["AcctNum"]

                if (
                        list1[i]["AccountType"] == "REVENUE"
                        or list1[i]["AccountType"] == "SALES"
                ):
                    QuerySet1["AccountType"] = "Income"
                    QuerySet1["AccountSubType"] = "RevenueGeneral"
                elif list1[i]["AccountType"] == "OTHERINCOME":
                    QuerySet1["AccountType"] = "Other Income"
                    QuerySet1["AccountSubType"] = "OtherOperatingIncome"
                elif (
                        list1[i]["AccountType"] == "EXPENSE"
                        or list1[i]["AccountType"] == "OVERHEADS"
                ):
                    QuerySet1["AccountType"] = "Expense"
                    QuerySet1["AccountSubType"] = "OfficeGeneralAdministrativeExpenses"
                elif list1[i]["AccountType"] in ["EXPENSE", "DEPRECIATN"]:
                    QuerySet1["AccountType"] = "Expense"
                    QuerySet1["AccountSubType"] = "OfficeGeneralAdministrativeExpenses"
                elif (
                        list1[i]["AccountType"] == "NONCURRENT"
                        or list1[i]["AccountType"] == "FIXED Asset"
                        or list1[i]["AccountType"] == "Fixed Assets"
                        or list1[i]["AccountType"] == "FIXED"
                ):
                    QuerySet1["AccountType"] = "Fixed Asset"
                    QuerySet1["AccountSubType"] = "OtherFixedAssets"
                elif (
                        list1[i]["AccountType"] == "PREPAYMENT"
                        or list1[i]["AccountType"] == "Asset"
                        or list1[i]["AccountType"] == "INVENTORY"
                        or list1[i]["AccountType"] == "Current Assets"
                        or list1[i]["AccountType"] == "CURRENT"
                ):
                    QuerySet1["AccountType"] = "Other Asset"
                    QuerySet1["AccountSubType"] = "OtherCurrentAssets"
                elif (
                        (list1[i]["AccountType"] == "LIABILITY")
                        or (list1[i]["AccountType"] == "CURRLIAB")
                        or (list1[i]["AccountType"] == "TERMLIAB")
                ):
                    QuerySet1["AccountType"] = "Other Current Liability"
                    QuerySet1["AccountSubType"] = "OtherCurrentLiabilities"
                elif list1[i]["AccountType"] == "EQUITY":
                    QuerySet1["AccountType"] = "Equity"
                    QuerySet1["AccountSubType"] = "OwnersEquity"
                elif (
                        (list1[i]["AccountType"] == "DIRECTCOSTS")
                        or (list1[i]["AccountType"] == "EXEMPTOUTPUT")
                        or (list1[i]["AccountType"] == "Sales")
                ):
                    QuerySet1["AccountType"] = "Cost of Goods Sold"
                    QuerySet1["AccountSubType"] = "CostOfSales"
                elif list1[i]["AccountType"] == "NONCURRENT LIABILITY":
                    QuerySet1["AccountType"] = "Long Term Liability"
                    QuerySet1["AccountSubType"] = "OtherLongTermLiabilities"
                elif (list1[i]["BankAccountType"] == "CREDITCARD") and (list1[i]["AccountType"] == "BANK"):
                    QuerySet1["AccountType"] = "Credit Card"
                    QuerySet1["AccountSubType"] = "CreditCard"
                elif (list1[i]["AccountType"] == "BANK" or list1[i]["AccountType"] == "Banking") and (
                        list1[i]["BankAccountType"] == "BANK"):
                    QuerySet1["AccountType"] = "Bank"
                    QuerySet1["AccountSubType"] = "CashAndCashEquivalents"
                else:
                    pass

                list2.append(QuerySet1)

        classified_coa.insert_many(list2)

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> get_COA_classification -> get_xero_classified_coa", ex)
