import json
import traceback
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
from apps.util.qbo_util import get_start_end_dates_of_job
import logging
logger = logging.getLogger(__name__)

def add_credit_card_credit(job_id,task_id):
    try:
        logger.info("Started executing myob -> qbowriter ->  add_credit_card_credit")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()

        received_money = db["received_money"].find({"job_id":job_id})
        received_money1 = []
        for x1 in range(0, db["received_money"].count_documents({'job_id':job_id})):
            received_money1.append(received_money[x1])

        QuerySet = received_money1
        purchase_url = f"{base_url}/purchase?minorversion={minorversion}"

        QBO_COA1 = db["QBO_COA"].find({"job_id":job_id})
        qbo_coa = []
        for k2 in range(0, db["QBO_COA"].count_documents({'job_id':job_id})):
            qbo_coa.append(QBO_COA1[k2])

        Myob_Job = db["job"].find({"job_id":job_id})
        Myob_Job1 = []
        for n in range(0, db["job"].count_documents({'job_id':job_id})):
            Myob_Job1.append(Myob_Job[n])

        QBO_Supplier1 = db["QBO_Supplier"].find({"job_id":job_id})
        QBO_Supplier = []
        for k3 in range(0, db["QBO_Supplier"].count_documents({'job_id':job_id})):
            QBO_Supplier.append(QBO_Supplier1[k3])

        QBO_Customer1 = db["QBO_Customer"].find({"job_id":job_id})
        QBO_Customer = []
        for m in range(0, db["QBO_Customer"].count_documents({'job_id':job_id})):
            QBO_Customer.append(QBO_Customer1[m])

        QBO_Class1 = db["QBO_Class"].find({"job_id":job_id})
        QBO_Class = []
        for n in range(0, db["QBO_Class"].count_documents({'job_id':job_id})):
            QBO_Class.append(QBO_Class1[n])

        QBO_Tax = []
        QBO_tax1 = db["QBO_Tax"].find({"job_id":job_id})
        for p in range(0, db["QBO_Tax"].count_documents({'job_id':job_id})):
            QBO_Tax.append(QBO_tax1[p])

        for i in range(0, len(QuerySet)):
            print(QuerySet[i]["ref_no"])
            _id=QuerySet[i]['_id']
            task_id=QuerySet[i]['task_id']
            
            for j11 in range(0, len(qbo_coa)):
                if (
                        QuerySet[i]["main_account"].lower().strip()
                        == qbo_coa[j11]["Name"].lower().strip()
                ):
                    if qbo_coa[j11]["AccountType"] == "Credit Card":
                        print(i)
                        if len(QuerySet[i]["Line"]) >= 1:
                            QuerySet1 = {"Line": []}
                            for j in range(0, len(QuerySet[i]["Line"])):
                                QuerySet1["TotalAmt"] = abs(QuerySet[i]["total_amount"])
                                QuerySet2 = {}
                                QuerySet3 = {}
                                QuerySet4 = {}
                                QuerySet5 = {}
                                QuerySet6 = {}
                                QuerySet7 = {}
                                QuerySet8 = {}
                                QuerySet9 = {}

                                QuerySet1["AccountRef"] = QuerySet2
                                for j1 in range(0, len(qbo_coa)):
                                    if (
                                            QuerySet[i]["main_account"].lower().strip()
                                            == qbo_coa[j1]["Name"].lower().strip()
                                    ):
                                        QuerySet2["name"] = qbo_coa[j1]["Name"]
                                        QuerySet2["value"] = qbo_coa[j1]["Id"]
                                    else:
                                        pass

                                QuerySet4["TaxCodeRef"] = QuerySet8

                                taxrate1 = 0
                                for j4 in range(0, len(QBO_Tax)):
                                    if QuerySet[i]["Line"][j]["tax_code"] == "GST":
                                        if "taxrate_name" in QBO_Tax[j4]:
                                            if (
                                                    "GST (purchases)"
                                                    in QBO_Tax[j4]["taxrate_name"]
                                            ):
                                                QuerySet8["value"] = QBO_Tax[j4][
                                                    "taxcode_id"
                                                ]
                                                taxrate = QBO_Tax[j4]["Rate"]
                                                taxrate1 = taxrate

                                    elif QuerySet[i]["Line"][j]["tax_code"] == "CAP":
                                        if "taxrate_name" in QBO_Tax[j4]:
                                            if (
                                                    "GST (purchases)"
                                                    in QBO_Tax[j4]["taxrate_name"]
                                            ):
                                                QuerySet8["value"] = QBO_Tax[j4][
                                                    "taxcode_id"
                                                ]
                                                taxrate = QBO_Tax[j4]["Rate"]
                                                taxrate1 = taxrate

                                    elif (
                                            QuerySet[i]["Line"][j]["tax_code"] == "FRE"
                                    ) or (QuerySet[i]["Line"][j]["tax_code"] == "GNR"):
                                        if "taxrate_name" in QBO_Tax[j4]:
                                            if (
                                                    "GST-free (purchases)"
                                                    in QBO_Tax[j4]["taxrate_name"]
                                            ):
                                                QuerySet8["value"] = QBO_Tax[j4][
                                                    "taxcode_id"
                                                ]
                                                taxrate = QBO_Tax[j4]["Rate"]
                                                taxrate1 = taxrate

                                    elif QuerySet[i]["Line"][j]["tax_code"] == "N-T":
                                        if "taxrate_name" in QBO_Tax[j4]:
                                            if "NOTAXP" in QBO_Tax[j4]["taxrate_name"]:
                                                QuerySet8["value"] = QBO_Tax[j4][
                                                    "taxcode_id"
                                                ]
                                                taxrate = QBO_Tax[j4]["Rate"]
                                                taxrate1 = taxrate

                                    elif (
                                            QuerySet[i]["Line"][j]["tax_code"]
                                            == QBO_Tax[j4]["taxcode_name"]
                                    ):
                                        QuerySet8["value"] = QBO_Tax[j4]["taxcode_id"]
                                        taxrate = QBO_Tax[j4]["Rate"]
                                        taxrate1 = taxrate

                                QuerySet1["PrivateNote"] = QuerySet[i]["notes"]

                                if QuerySet[i]["is_tax_inclusive"] == True:
                                    QuerySet1["GlobalTaxCalculation"] = "TaxInclusive"
                                    QuerySet4["TaxInclusiveAmt"] = round(
                                        abs(QuerySet[i]["Line"][j]["line_amount"])
                                        * (100 + taxrate1)
                                        / 100,
                                        2,
                                    )
                                    QuerySet3["Amount"] = round(
                                        abs(
                                            (QuerySet[i]["Line"][j]["line_amount"])
                                            / (100 + taxrate1)
                                            * 100
                                        ),
                                        2,
                                    )

                                elif QuerySet[i]["is_tax_inclusive"] == False:
                                    QuerySet1["GlobalTaxCalculation"] = "TaxExcluded"
                                    QuerySet4["TaxInclusiveAmt"] = round(
                                        abs(QuerySet[i]["Line"][j]["line_amount"])
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )
                                    QuerySet3["Amount"] = round(
                                        abs(QuerySet[i]["Line"][j]["line_amount"]), 2
                                    )

                                QuerySet1["PaymentType"] = "CreditCard"
                                QuerySet1["Credit"] = True

                                QuerySet1["TxnDate"] = QuerySet[i]["date"]

                                if QuerySet[i]["Line"][j]["memo"] is not None:
                                    QuerySet3["Description"] = QuerySet[i]["Line"][j][
                                        "memo"
                                    ]
                                else:
                                    QuerySet3["Description"] = QuerySet[i]["notes"]

                                QuerySet3[
                                    "DetailType"
                                ] = "AccountBasedExpenseLineDetail"
                                QuerySet3["AccountBasedExpenseLineDetail"] = QuerySet4

                                for j2 in range(0, len(QBO_Class)):
                                    if QuerySet[i]["Line"][j]["job"] is not None:
                                        for j3 in range(0, len(Myob_Job1)):
                                            if (
                                                    QuerySet[i]["Line"][j]["job"]
                                                    == Myob_Job1[j3]["Name"]
                                            ):
                                                if (
                                                        QBO_Class[j2][
                                                            "FullyQualifiedName"
                                                        ].startswith(Myob_Job1[j3]["Name"])
                                                ) and (
                                                        QBO_Class[j2][
                                                            "FullyQualifiedName"
                                                        ].endswith(Myob_Job1[j3]["Number"])
                                                ):
                                                    QuerySet7["value"] = QBO_Class[j2][
                                                        "Id"
                                                    ]
                                                    QuerySet7["name"] = QBO_Class[j2][
                                                        "Name"
                                                    ]

                                QuerySet4["ClassRef"] = QuerySet7
                                QuerySet4["AccountRef"] = QuerySet5

                                for j3 in range(0, len(qbo_coa)):
                                    if (
                                            qbo_coa[j3]["Name"].startswith(
                                                QuerySet[i]["Line"][j]["line_account"]
                                            )
                                    ) and (
                                            qbo_coa[j3]["Name"].endswith(
                                                QuerySet[i]["Line"][j]["account_id"]
                                            )
                                    ):
                                        QuerySet5["name"] = qbo_coa[j3]["Name"]
                                        QuerySet5["value"] = qbo_coa[j3]["Id"]

                                    elif (
                                            QuerySet[i]["Line"][j]["line_account"]
                                                    .strip()
                                                    .lower()
                                            == qbo_coa[j3]["Name"].strip().lower()
                                    ):
                                        QuerySet5["name"] = qbo_coa[j3]["Name"]
                                        QuerySet5["value"] = qbo_coa[j3]["Id"]

                                    elif "AcctNum" in qbo_coa[j3]:
                                        if (
                                                QuerySet[i]["Line"][j]["account_id"]
                                                == qbo_coa[j3]["AcctNum"]
                                        ):
                                            QuerySet5["name"] = qbo_coa[j3]["Name"]
                                            QuerySet5["value"] = qbo_coa[j3]["Id"]

                                    else:
                                        pass

                                QuerySet1["DocNumber"] = QuerySet[i]["ref_no"]
                                QuerySet1["EntityRef"] = QuerySet9

                                if QuerySet[i]["contact_type"] == "Supplier":
                                    QuerySet9["name"] = QuerySet[i]["contact_name"]
                                    QuerySet9["type"] = "vendor"
                                    for k1 in range(0, len(QBO_Supplier)):
                                        if (
                                                QuerySet[i]["contact_name"]
                                                == QBO_Supplier[k1]["DisplayName"]
                                        ):
                                            QuerySet9["value"] = QBO_Supplier[k1]["Id"]

                                QuerySet1["Line"].append(QuerySet3)

                            payload = json.dumps(QuerySet1)
                            print(payload)

                            if QuerySet[i]["total_amount"] >= 0:
                                received_money_date = QuerySet[i]["date"][0:10]
                                received_money_date1 = datetime.strptime(
                                    received_money_date, "%Y-%m-%d"
                                )
                                if start_date1 is not None and end_date1 is not None:
                                    if (received_money_date1 >= start_date1) and (
                                            received_money_date1 <= end_date1
                                    ):
                                        post_data_in_qbo(purchase_url, headers, payload,db["received_money"],_id,job_id,task_id, QuerySet[i]["ref_no"])
                                    
                                else:
                                    post_data_in_qbo(purchase_url, headers, payload,db["received_money"],_id,job_id,task_id, QuerySet[i]["ref_no"])
                                    
                                    
                else:
                    pass
    except Exception as ex:
        traceback.print_exc()
        
