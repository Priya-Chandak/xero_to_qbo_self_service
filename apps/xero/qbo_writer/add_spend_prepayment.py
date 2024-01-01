import copy
import json
import logging
from datetime import datetime

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo

logger = logging.getLogger(__name__)


def add_spend_prepayment(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_spend_prepayment -> add_spend_prepayment")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/journalentry?minorversion={minorversion}"
        prepayment1 = db["xero_spend_prepayment"].find({"job_id": job_id})
        prepayment = []
        for p1 in prepayment1:
            prepayment.append(p1)

        QBO_COA = db["QBO_COA"].find({"job_id": job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Class = db["QBO_Class"].find({"job_id": job_id})
        QBO_class = []
        for p3 in QBO_Class:
            QBO_class.append(p3)

        QBO_Tax = db["QBO_Tax"].find({"job_id": job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)

        Xero_COA = db["xero_coa"].find({"job_id": job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id": job_id})
        QBO_supplier = []
        for p7 in QBO_Supplier:
            QBO_supplier.append(p7)

        QuerySet1 = prepayment

        for i in range(0, len(QuerySet1)):
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']

            QuerySet2 = {"Line": []}
            QuerySet10 = {"TaxLine": []}
            QuerySet2["DocNumber"] = QuerySet1[i]["Reference"]

            a = []
            b = []

            sales_tax = 0
            purchase_tax = 0

            for j in range(0, len(QuerySet1[i]["Line"])):
                if "TaxType" in QuerySet1[i]["Line"][j]:
                    if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                        a.append(QuerySet1[i]["Line"][j]["TaxType"])
                    else:
                        b.append(QuerySet1[i]["Line"][j]["TaxType"])

                QuerySet3 = {}
                QuerySet4 = {}
                QuerySet5 = {}
                QuerySet6 = {}
                QuerySet7 = {}
                QuerySet8 = {}
                QuerySet9 = {}

                QuerySet11 = {}
                QuerySet12 = {}
                QuerySet13 = {}
                QuerySet14 = {}
                QuerySet15 = {}

                QuerySet2["TxnTaxDetail"] = QuerySet10
                QuerySet11["DetailType"] = "TaxLineDetail"
                QuerySet11["TaxLineDetail"] = QuerySet12
                QuerySet12["TaxRateRef"] = QuerySet13
                QuerySet12["PercentBased"] = True
                QuerySet10["TaxLine"].append(QuerySet11)

                taxrate1 = 0

                sales = ["BASEXCLUDED", "OUTPUT"]
                purchase = ["INPUT", "EXEMPTEXPENSES", "EXEMPTOUTPUT"]

                if QuerySet1[i]["Line"][j]["TaxType"] in sales:
                    QuerySet4["TaxApplicableOn"] = "Sales"
                    QuerySet7["TaxApplicableOn"] = "Sales"

                elif QuerySet1[i]["Line"][j]["TaxType"] in purchase:
                    QuerySet4["TaxApplicableOn"] = "Purchase"
                    QuerySet7["TaxApplicableOn"] = "Purchase"

                for j4 in range(0, len(QBO_tax)):
                    if "TaxType" in QuerySet1[i]["Line"][j]:
                        if QuerySet1[i]["Line"][j]["TaxType"] == "BASEXCLUDED":
                            if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "NOTAXS" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                            else:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "NOTAXS" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]

                        elif QuerySet1[i]["Line"][j]["TaxType"] == "INPUT":
                            if "taxrate_name" in QBO_tax[j4]:
                                if "GST (sales)" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif QuerySet1[i]["Line"][j]["TaxType"] == "OUTPUT":
                            if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "GST (sales)" in QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                            else:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "GST (sales)" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate

                        elif QuerySet1[i]["Line"][j]["TaxType"] in ["EXEMPTEXPENSES", "INPUTTAXED"]:
                            if "taxrate_name" in QBO_tax[j4]:
                                if "GST free (sales)" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif QuerySet1[i]["Line"][j]["TaxType"] == "EXEMPTOUTPUT":
                            if "taxrate_name" in QBO_tax[j4]:
                                if "GST free (sales)" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif (
                                QuerySet1[i]["Line"][j]["TaxType"]
                                == QBO_tax[j4]["taxcode_name"]
                        ):
                            QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                            QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                            taxrate = QBO_tax[j4]["Rate"]
                            QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                            taxrate1 = taxrate

                if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                    if QuerySet1[i]["LineAmountTypes"] == "Inclusive":
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet3["Amount"] = round(
                            abs(
                                QuerySet1[i]["Line"][j]["LineAmount"]
                                / (100 + taxrate1)
                                * 100
                            ),
                            2,
                        )
                    elif (QuerySet1[i]["LineAmountTypes"] == "Exclusive") or (
                            QuerySet1[i]["LineAmountTypes"] == "NoTax"
                    ):
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet3["Amount"] = abs(
                            round(QuerySet1[i]["Line"][j]["LineAmount"], 2)
                        )

                    if "Description" in QuerySet1[i]["Line"][j]:
                        QuerySet3["Description"] = QuerySet1[i]["Line"][j][
                            "Description"
                        ]
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet4["PostingType"] = "Credit"
                    QuerySet3["JournalEntryLineDetail"] = QuerySet4

                    for k in range(0, len(QBO_coa)):
                        if (
                                QuerySet1[i]["BankAccountName"].upper()
                                == QBO_coa[k]["Name"].upper()
                        ):
                            QuerySet5["value"] = QBO_coa[k]["Id"]
                            QuerySet5["name"] = QBO_coa[k]["Name"]

                    QuerySet4["AccountRef"] = QuerySet5
                    QuerySet4["TaxCodeRef"] = QuerySet15
                    QuerySet4["TaxAmount"] = QuerySet1[i]["Line"][j]["TaxAmount"]
                    sales_tax = sales_tax + QuerySet4["TaxAmount"]
                    QuerySet4["ClassRef"] = QuerySet9
                    QuerySet2["Line"].append(QuerySet3)

                    Q11 = copy.deepcopy(QuerySet3)
                    Q11["JournalEntryLineDetail"]["PostingType"] = "Debit"

                    for p5 in range(0, len(QBO_coa)):
                        for p51 in range(0, len(xero_coa)):
                            if ("Code" in xero_coa[p51]) and (
                                    "AccountCode" in QuerySet1[i]["Line"][j]
                            ):
                                if (
                                        QuerySet1[i]["Line"][j]["AccountCode"]
                                        == xero_coa[p51]["Code"]
                                ):
                                    if xero_coa[p51]["Name"] == QBO_coa[p5]["Name"]:
                                        Q11["JournalEntryLineDetail"]["AccountRef"][
                                            "name"
                                        ] = QBO_coa[p5]["Name"]
                                        Q11["JournalEntryLineDetail"]["AccountRef"][
                                            "value"
                                        ] = QBO_coa[p5]["Id"]
                    Entity = {}
                    EntityRef = {}

                    for v1 in range(0, len(QBO_supplier)):
                        if (
                                QuerySet1[i]["ContactName"]
                                == QBO_supplier[v1]["DisplayName"]
                        ):
                            EntityRef["value"] = QBO_supplier[v1]["Id"]
                            EntityRef["name"] = QBO_supplier[v1]["DisplayName"]
                            Entity["Type"] = "Vendor"

                    Q11["JournalEntryLineDetail"]["Entity"] = Entity
                    Q11["JournalEntryLineDetail"]["Entity"]["EntityRef"] = EntityRef

                    QuerySet2["Line"].append(Q11)

                elif QuerySet1[i]["Line"][j]["LineAmount"] < 0:
                    if QuerySet1[i]["LineAmountTypes"] == "Inclusive":
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet6["Amount"] = round(
                            abs(
                                QuerySet1[i]["Line"][j]["LineAmount"]
                                / (100 + taxrate1)
                                * 100
                            ),
                            2,
                        )
                        if "Description" in QuerySet1[i]["Line"][j]:
                            QuerySet6["Description"] = QuerySet1[i]["Line"][j][
                                "Description"
                            ]

                    elif (QuerySet1[i]["LineAmountTypes"] == "Exclusive") or (
                            (QuerySet1[i]["LineAmountTypes"] == "NoTax")
                    ):
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet6["Amount"] = abs(
                            round(QuerySet1[i]["Line"][j]["LineAmount"], 2)
                        )
                        if "Description" in QuerySet1[i]["Line"][j]:
                            QuerySet6["Description"] = QuerySet1[i]["Line"][j][
                                "Description"
                            ]

                    QuerySet7["PostingType"] = "Debit"
                    QuerySet6["DetailType"] = "JournalEntryLineDetail"
                    QuerySet6["JournalEntryLineDetail"] = QuerySet7
                    for p in range(0, len(QBO_coa)):
                        if (
                                QuerySet1[i]["BankAccountName"].upper()
                                == QBO_coa[p]["Name"].upper()
                        ):
                            QuerySet8["value"] = QBO_coa[p]["Id"]
                            QuerySet8["name"] = QBO_coa[p]["Name"]

                    QuerySet7["AccountRef"] = QuerySet8
                    QuerySet7["TaxCodeRef"] = QuerySet15
                    QuerySet7["TaxAmount"] = abs(QuerySet1[i]["Line"][j]["TaxAmount"])
                    purchase_tax = purchase_tax + QuerySet7["TaxAmount"]
                    QuerySet7["ClassRef"] = QuerySet9
                    QuerySet2["Line"].append(QuerySet6)

            arr = QuerySet10["TaxLine"]
            b1 = {"TaxLine": []}

            b = []
            for i in range(0, len(arr)):
                b.append(arr[i]["TaxLineDetail"]["TaxRateRef"]["value"])

            e = {}
            for i1 in range(0, len(b)):
                e[b[i1]] = b.count(b[i1])

            multiple = dict((k, v) for k, v in e.items() if v > 1)
            single = dict((k, v) for k, v in e.items() if v == 1)

            e1 = []
            for keys in e.keys():
                e1.append(keys)

            new_arr = []
            for k in range(0, len(multiple)):
                e = {}
                TaxLineDetail = {}
                TaxRateRef = {}
                amt = 0
                net_amt = 0

                for i in range(0, len(arr)):
                    if arr[i]["TaxLineDetail"]["TaxRateRef"]["value"] == e1[k]:
                        e["DetailType"] = "TaxLineDetail"
                        TaxLineDetail["TaxRateRef"] = TaxRateRef
                        TaxLineDetail["TaxPercent"] = arr[i]["TaxLineDetail"][
                            "TaxPercent"
                        ]
                        TaxRateRef["value"] = e1[k]

                        e["Amount"] = 0
                        TaxLineDetail["NetAmountTaxable"] = 0
                        e["TaxLineDetail"] = TaxLineDetail

                new_arr.append(e)

            for k3 in range(0, len(arr)):
                if arr[k3]["TaxLineDetail"]["TaxRateRef"]["value"] in single:
                    new_arr.append(arr[k3])

            b1["TaxLine"] = new_arr

            QuerySet2["TxnTaxDetail"] = b1
            payload = json.dumps(QuerySet2)

            journal_date1 = QuerySet1[i]["Date"]

            journal_date = QuerySet1[i]["Date"][0:10]
            journal_date1 = datetime.strptime(journal_date, "%Y-%m-%d")
            print(journal_date1)
            QuerySet1['TxnDate'] = journal_date1

            if start_date1 is not None and end_date1 is not None:
                if (journal_date1 >= start_date1) and (journal_date1 <= end_date1):
                    post_data_in_qbo(url, headers, payload, db["xero_spend_prepayment"], _id, job_id, task_id,
                                     QuerySet1[i]["Reference"])
            else:
                post_data_in_qbo(url, headers, payload, db["xero_spend_prepayment"], _id, job_id, task_id,
                                 QuerySet1[i]["Reference"])

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_spend_prepayment -> add_spend_prepayment", ex)


def add_spend_overpayment(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_spend_prepayment -> add_spend_overpayment")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/journalentry?minorversion={minorversion}"

        overpayment1 = db["xero_spend_overpayment"].find({"job_id": job_id})

        overpayment = []
        for p1 in overpayment1:
            overpayment.append(p1)

        QBO_COA = db["QBO_COA"].find({"job_id": job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Class = db["QBO_Class"].find({"job_id": job_id})
        QBO_class = []
        for p3 in QBO_Class:
            QBO_class.append(p3)

        QBO_Tax = db["QBO_Tax"].find({"job_id": job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)

        Xero_COA = db["xero_coa"].find({"job_id": job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id": job_id})
        QBO_supplier = []
        for p7 in QBO_Supplier:
            QBO_supplier.append(p7)

        QuerySet1 = overpayment

        for i in range(0, len(QuerySet1)):
            print(QuerySet1[i])
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']

            QuerySet2 = {"Line": []}
            QuerySet10 = {"TaxLine": []}
            QuerySet2["DocNumber"] = QuerySet1[i]["Reference"]
            QuerySet2["TxnDate"] = QuerySet1[i]["Date"][0:11]

            a = []
            b = []

            sales_tax = 0
            purchase_tax = 0

            for j in range(0, len(QuerySet1[i]["Line"])):
                if "TaxType" in QuerySet1[i]["Line"][j]:
                    if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                        a.append(QuerySet1[i]["Line"][j]["TaxType"])
                    else:
                        b.append(QuerySet1[i]["Line"][j]["TaxType"])

                QuerySet3 = {}
                QuerySet4 = {}
                QuerySet5 = {}
                QuerySet6 = {}
                QuerySet7 = {}
                QuerySet8 = {}
                QuerySet9 = {}

                QuerySet11 = {}
                QuerySet12 = {}
                QuerySet13 = {}
                QuerySet14 = {}
                QuerySet15 = {}

                QuerySet2["TxnTaxDetail"] = QuerySet10
                QuerySet11["DetailType"] = "TaxLineDetail"
                QuerySet11["TaxLineDetail"] = QuerySet12
                QuerySet12["TaxRateRef"] = QuerySet13
                QuerySet12["PercentBased"] = True
                QuerySet10["TaxLine"].append(QuerySet11)

                taxrate1 = 0

                sales = ["BASEXCLUDED", "OUTPUT", "NONE"]
                purchase = ["INPUT", "EXEMPTEXPENSES", "EXEMPTOUTPUT"]

                if QuerySet1[i]["Line"][j]["TaxType"] in sales:
                    QuerySet4["TaxApplicableOn"] = "Sales"
                    QuerySet7["TaxApplicableOn"] = "Sales"

                elif QuerySet1[i]["Line"][j]["TaxType"] in purchase:
                    QuerySet4["TaxApplicableOn"] = "Purchase"
                    QuerySet7["TaxApplicableOn"] = "Purchase"

                for j4 in range(0, len(QBO_tax)):
                    if "TaxType" in QuerySet1[i]["Line"][j]:
                        if QuerySet1[i]["Line"][j]["TaxType"] == "BASEXCLUDED":
                            if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "NOTAXS" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                            else:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "NOTAXS" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]

                        elif QuerySet1[i]["Line"][j]["TaxType"] == "INPUT":
                            if "taxrate_name" in QBO_tax[j4]:
                                if "GST (sales)" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate


                        elif QuerySet1[i]["Line"][j]["TaxType"] in ["NONE", None, 'BASEXCLUDED']:
                            if "taxrate_name" in QBO_tax[j4]:
                                if "NOTAXS" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif QuerySet1[i]["Line"][j]["TaxType"] == "OUTPUT":
                            if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "GST (sales)" in QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                            else:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "GST (sales)" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate

                        elif QuerySet1[i]["Line"][j]["TaxType"] in ["EXEMPTEXPENSES", "INPUTTAXED"]:
                            if "taxrate_name" in QBO_tax[j4]:
                                if "GST free (sales)" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif QuerySet1[i]["Line"][j]["TaxType"] == "EXEMPTOUTPUT":
                            if "taxrate_name" in QBO_tax[j4]:
                                if "GST free (sales)" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif (
                                QuerySet1[i]["Line"][j]["TaxType"]
                                == QBO_tax[j4]["taxcode_name"]
                        ):
                            QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                            QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                            taxrate = QBO_tax[j4]["Rate"]
                            QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                            taxrate1 = taxrate

                if QuerySet1[i]["Line"][j]["LineAmount"] >= 0:
                    if QuerySet1[i]["LineAmountTypes"] == "Inclusive":
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet3["Amount"] = round(
                            abs(
                                QuerySet1[i]["Line"][j]["LineAmount"]
                                / (100 + taxrate1)
                                * 100
                            ),
                            2,
                        )
                    elif (QuerySet1[i]["LineAmountTypes"] == "Exclusive") or (
                            QuerySet1[i]["LineAmountTypes"] == "NoTax"
                    ):
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet3["Amount"] = abs(
                            round(QuerySet1[i]["Line"][j]["LineAmount"], 2)
                        )

                    if "Description" in QuerySet1[i]["Line"][j]:
                        QuerySet3["Description"] = QuerySet1[i]["Line"][j][
                            "Description"
                        ]
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet4["PostingType"] = "Credit"
                    QuerySet3["JournalEntryLineDetail"] = QuerySet4

                    for k in range(0, len(QBO_coa)):
                        if (
                                QuerySet1[i]["BankAccountName"].upper()
                                == QBO_coa[k]["Name"].upper()
                        ):
                            QuerySet5["value"] = QBO_coa[k]["Id"]
                            QuerySet5["name"] = QBO_coa[k]["Name"]

                    QuerySet4["AccountRef"] = QuerySet5
                    QuerySet4["TaxCodeRef"] = QuerySet15
                    QuerySet4["TaxAmount"] = QuerySet1[i]["Line"][j]["TaxAmount"]
                    sales_tax = sales_tax + QuerySet4["TaxAmount"]
                    QuerySet4["ClassRef"] = QuerySet9
                    QuerySet2["Line"].append(QuerySet3)

                    Q11 = copy.deepcopy(QuerySet3)
                    Q11["JournalEntryLineDetail"]["PostingType"] = "Debit"

                    for p5 in range(0, len(QBO_coa)):
                        if QBO_coa[p5]["AccountType"] == 'Accounts Payable':
                            Q11["JournalEntryLineDetail"]["AccountRef"]["name"] = QBO_coa[p5]["Name"]
                            Q11["JournalEntryLineDetail"]["AccountRef"][
                                "value"
                            ] = QBO_coa[p5]["Id"]

                        # for p51 in range(0, len(xero_coa)):
                        #     if ("Code" in xero_coa[p51]) and (
                        #         "AccountCode" in QuerySet1[i]["Line"][j]
                        #     ):
                        #         if (
                        #             QuerySet1[i]["Line"][j]["AccountCode"]
                        #             == xero_coa[p51]["Code"]
                        #         ):
                        #             if xero_coa[p51]["Name"] == QBO_coa[p5]["Name"]:
                        #                 Q11["JournalEntryLineDetail"]["AccountRef"][
                        #                     "name"
                        #                 ] = QBO_coa[p5]["Name"]
                        #                 Q11["JournalEntryLineDetail"]["AccountRef"][
                        #                     "value"
                        #                 ] = QBO_coa[p5]["Id"]
                    Entity = {}
                    EntityRef = {}

                    for v1 in range(0, len(QBO_supplier)):
                        if (
                                QuerySet1[i]["ContactName"]
                                == QBO_supplier[v1]["DisplayName"]
                        ):
                            EntityRef["value"] = QBO_supplier[v1]["Id"]
                            EntityRef["name"] = QBO_supplier[v1]["DisplayName"]
                            Entity["Type"] = "Vendor"

                    Q11["JournalEntryLineDetail"]["Entity"] = Entity
                    Q11["JournalEntryLineDetail"]["Entity"]["EntityRef"] = EntityRef

                    QuerySet2["Line"].append(Q11)

                elif QuerySet1[i]["Line"][j]["LineAmount"] < 0:
                    if QuerySet1[i]["LineAmountTypes"] == "Inclusive":
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet6["Amount"] = round(
                            abs(
                                QuerySet1[i]["Line"][j]["LineAmount"]
                                / (100 + taxrate1)
                                * 100
                            ),
                            2,
                        )
                        if "Description" in QuerySet1[i]["Line"][j]:
                            QuerySet6["Description"] = QuerySet1[i]["Line"][j][
                                "Description"
                            ]

                    elif (QuerySet1[i]["LineAmountTypes"] == "Exclusive") or (
                            (QuerySet1[i]["LineAmountTypes"] == "NoTax")
                    ):
                        QuerySet12["NetAmountTaxable"] = 0
                        QuerySet11["Amount"] = 0
                        QuerySet6["Amount"] = abs(
                            round(QuerySet1[i]["Line"][j]["LineAmount"], 2)
                        )
                        if "Description" in QuerySet1[i]["Line"][j]:
                            QuerySet6["Description"] = QuerySet1[i]["Line"][j][
                                "Description"
                            ]

                    QuerySet7["PostingType"] = "Debit"
                    QuerySet6["DetailType"] = "JournalEntryLineDetail"
                    QuerySet6["JournalEntryLineDetail"] = QuerySet7
                    for p in range(0, len(QBO_coa)):
                        if (
                                QuerySet1[i]["BankAccountName"].upper()
                                == QBO_coa[p]["Name"].upper()
                        ):
                            print(QBO_coa[p]["Name"], "Debit------------")
                            QuerySet8["value"] = QBO_coa[p]["Id"]
                            QuerySet8["name"] = QBO_coa[p]["Name"]

                    QuerySet7["AccountRef"] = QuerySet8
                    QuerySet7["TaxCodeRef"] = QuerySet15
                    QuerySet7["TaxAmount"] = abs(QuerySet1[i]["Line"][j]["TaxAmount"])
                    purchase_tax = purchase_tax + QuerySet7["TaxAmount"]
                    QuerySet7["ClassRef"] = QuerySet9
                    QuerySet2["Line"].append(QuerySet6)

            arr = QuerySet10["TaxLine"]
            b1 = {"TaxLine": []}

            b = []
            for i in range(0, len(arr)):
                b.append(arr[i]["TaxLineDetail"]["TaxRateRef"]["value"])

            e = {}
            for i1 in range(0, len(b)):
                e[b[i1]] = b.count(b[i1])

            multiple = dict((k, v) for k, v in e.items() if v > 1)
            single = dict((k, v) for k, v in e.items() if v == 1)

            e1 = []
            for keys in e.keys():
                e1.append(keys)

            new_arr = []
            for k in range(0, len(multiple)):
                e = {}
                TaxLineDetail = {}
                TaxRateRef = {}
                amt = 0
                net_amt = 0

                for i in range(0, len(arr)):
                    if arr[i]["TaxLineDetail"]["TaxRateRef"]["value"] == e1[k]:
                        e["DetailType"] = "TaxLineDetail"
                        TaxLineDetail["TaxRateRef"] = TaxRateRef
                        TaxLineDetail["TaxPercent"] = arr[i]["TaxLineDetail"][
                            "TaxPercent"
                        ]
                        TaxRateRef["value"] = e1[k]

                        e["Amount"] = 0
                        TaxLineDetail["NetAmountTaxable"] = 0
                        e["TaxLineDetail"] = TaxLineDetail

                new_arr.append(e)

            for k3 in range(0, len(arr)):
                if arr[k3]["TaxLineDetail"]["TaxRateRef"]["value"] in single:
                    new_arr.append(arr[k3])

            b1["TaxLine"] = new_arr

            QuerySet2["TxnTaxDetail"] = b1
            journal_date = QuerySet1[i]["Date"][0:10]
            journal_date1 = datetime.strptime(journal_date, "%Y-%m-%d")
            print(journal_date1)

            # QuerySet2['TxnDate'] = journal_date1 

            payload = json.dumps(QuerySet2)

            if start_date1 is not None and end_date1 is not None:
                if (journal_date1 >= start_date1) and (journal_date1 <= end_date1):
                    post_data_in_qbo(url, headers, payload, db["xero_spend_overpayment"], _id, job_id, task_id,
                                     QuerySet1[i]["Reference"])
            else:
                post_data_in_qbo(url, headers, payload, db["xero_spend_overpayment"], _id, job_id, task_id,
                                 QuerySet1[i]["Reference"])

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_spend_prepayment -> add_spend_overpayment", ex)
