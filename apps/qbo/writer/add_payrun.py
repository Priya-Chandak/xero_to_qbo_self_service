import json
import traceback
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job, post_data_in_qbo


def add_payrun(job_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()

        C1 = db["employee_payroll_advice"]
        x1 = C1.find({"job_id": job_id})

        payrun1 = []
        for q in x1:
            payrun1.append(q)

        QuerySet = payrun1

        purchase_url = f"{base_url}/purchase?minorversion={minorversion}"

        QBO_COA1 = db["QBO_COA"].find({"job_id": job_id})
        QBO_COA = []
        for k2 in range(0, db["QBO_COA"].count_documents({})):
            QBO_COA.append(QBO_COA1[k2])

        QBO_Supplier1 = db["QBO_Supplier"].find({"job_id": job_id})
        QBO_Supplier = []
        for k3 in range(0, db["QBO_Supplier"].count_documents({})):
            QBO_Supplier.append(QBO_Supplier1[k3])

        QBO_Customer1 = db["QBO_Customer"].find({"job_id": job_id})
        QBO_Customer = []
        for m in range(0, db["QBO_Customer"].count_documents({})):
            QBO_Customer.append(QBO_Customer1[m])

        QBO_Employee1 = db["QBO_Employee"].find({"job_id": job_id})
        QBO_Employee = []
        for m in range(0, db["QBO_Employee"].count_documents({})):
            QBO_Employee.append(QBO_Employee1[m])

        QBO_Class1 = db["QBO_Class"].find({"job_id": job_id})
        QBO_Class = []
        for n in range(0, db["QBO_Class"].count_documents({})):
            QBO_Class.append(QBO_Class1[n])

        QBO_Tax = []
        QBO_tax1 = db["QBO_Tax"].find({"job_id": job_id})
        for p in range(0, db["QBO_Tax"].count_documents({})):
            QBO_Tax.append(QBO_tax1[p])

        journal_transaction = []
        journal_transaction1 = db["journal_transaction"].find({"job_id": job_id})
        for p in range(0, db["journal_transaction"].count_documents({})):
            journal_transaction.append(journal_transaction1[p])

        employee_payroll_advice = []
        employee_payroll_advice1 = db["employee_payroll_advice"].find({"job_id": job_id})
        for p in range(0, db["employee_payroll_advice"].count_documents({})):
            employee_payroll_advice.append(employee_payroll_advice1[p])

        journal_transaction = []
        journal_transaction1 = db["journal_transaction"].find({"job_id": job_id})
        for p in range(0, db["journal_transaction"].count_documents({})):
            journal_transaction.append(journal_transaction1[p])

        for i in range(0, len(QuerySet)):
            if QuerySet[i]["ChequeNumber"] == "129":
                QuerySet1 = {"Line": []}
                AccountRef = {}
                EntityRef = {}

                for i2 in range(0, len(journal_transaction)):
                    if (
                            QuerySet[i]["ChequeNumber"]
                            == journal_transaction[i2]["DisplayID"]
                    ):
                        for j11 in range(0, len(QBO_COA)):
                            if (
                                    journal_transaction[i2]["Lines"][0]["account"]["Name"]
                                    == QBO_COA[j11]["FullyQualifiedName"]
                            ):
                                if QBO_COA[j11]["AccountType"] == "Bank":
                                    AccountRef["name"] = QBO_COA[j11][
                                        "FullyQualifiedName"
                                    ]
                                    AccountRef["value"] = QBO_COA[j11]["Id"]

                QuerySet1["AccountRef"] = AccountRef

                for i1 in range(0, len(QBO_Employee)):
                    if (
                            QuerySet[i]["Employee"]["Name"]
                            == QBO_Employee[i1]["DisplayName"]
                    ):
                        EntityRef["name"] = QBO_Employee[i1]["DisplayName"]
                        EntityRef["value"] = QBO_Employee[i1]["Id"]
                        EntityRef["type"] = "Employee"

                QuerySet1["EntityRef"] = EntityRef
                QuerySet1["GlobalTaxCalculation"] = "TaxExcluded"
                QuerySet1["DocNumber"] = QuerySet[i]["ChequeNumber"]
                QuerySet1["TxnDate"] = QuerySet[i]["PaymentDate"][0:10]
                QuerySet1["PaymentType"] = "Cash"

                for j in range(0, len(QuerySet[i]["Lines"])):
                    QuerySet2 = {}
                    AccountBasedExpenseLineDetail = {}
                    LineAccountRef = {}
                    TaxCodeRef = {}

                    if QuerySet[i]["Lines"][j]["Amount"] is not None:
                        QuerySet2["Amount"] = QuerySet[i]["Lines"][j]["Amount"]
                    else:
                        QuerySet2["Amount"] = 0
                    QuerySet2["Description"] = QuerySet[i]["Lines"][j][
                        "PayrollCategory"
                    ]["Name"]
                    QuerySet2["DetailType"] = "AccountBasedExpenseLineDetail"
                    QuerySet2[
                        "AccountBasedExpenseLineDetail"
                    ] = AccountBasedExpenseLineDetail

                    for j1 in range(0, len(QBO_COA)):
                        if (
                                QuerySet[i]["Lines"][j]["PayrollCategory"]["Type"] == "Wage"
                        ) or QuerySet[i]["Lines"][j]["PayrollCategory"][
                            "Type"
                        ] == "Entitlement":
                            if (
                                    QBO_COA[j1]["FullyQualifiedName"]
                                    == "Do Not Allocate - Wages & Salaries"
                            ):
                                LineAccountRef["name"] = QBO_COA[j1][
                                    "FullyQualifiedName"
                                ]
                                LineAccountRef["value"] = QBO_COA[j1]["Id"]

                        if QuerySet[i]["Lines"][j]["PayrollCategory"]["Type"] == "Tax":
                            if (
                                    QBO_COA[j1]["FullyQualifiedName"]
                                    == "PAYG Withholding Payable"
                            ):
                                LineAccountRef["name"] = QBO_COA[j1][
                                    "FullyQualifiedName"
                                ]
                                LineAccountRef["value"] = QBO_COA[j1]["Id"]

                        if (
                                QuerySet[i]["Lines"][j]["PayrollCategory"]["Type"]
                                == "Superannuation"
                        ):
                            if QBO_COA[j1]["FullyQualifiedName"] == "Superannuation":
                                LineAccountRef["name"] = QBO_COA[j1][
                                    "FullyQualifiedName"
                                ]
                                LineAccountRef["value"] = QBO_COA[j1]["Id"]

                        AccountBasedExpenseLineDetail["AccountRef"] = LineAccountRef

                    for j1 in range(0, len(QBO_Tax)):
                        if "Out of Scope" in QBO_Tax[j1]["taxcode_name"]:
                            TaxCodeRef["value"] = QBO_Tax[j1]["taxcode_id"]

                        AccountBasedExpenseLineDetail["TaxCodeRef"] = TaxCodeRef

                    QuerySet1["Line"].append(QuerySet2)

                payload = json.dumps(QuerySet1)

                if QuerySet[i]["NetPay"] > 0:
                    payrun_date = QuerySet[i]["PaymentDate"][0:10]
                    payrun_date1 = datetime.strptime(payrun_date, "%Y-%m-%d")
                    if start_date1 is not None and end_date1 is not None:
                        if (payrun_date1 >= start_date1) and (
                                payrun_date1 <= end_date1
                        ):
                            post_data_in_qbo(
                                purchase_url,
                                headers,
                                payload,
                                job_id,
                                QuerySet[i]["ChequeNumber"]
                            )
                        else:
                            pass
                    else:
                        post_data_in_qbo(
                            purchase_url,
                            headers,
                            payload,
                            job_id,
                            QuerySet[i]["ChequeNumber"]
                        )
    except Exception as ex:
        traceback.print_exc()
        
