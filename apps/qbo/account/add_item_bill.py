import json
import traceback
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo
from collections import Counter



def add_item_bill(job_id,task_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url1 = f"{base_url}/bill?minorversion=14"
        url2 = f"{base_url}/vendorcredit?minorversion=14"

        db = get_mongodb_database()

        final_bill1 = db["final_bill"].find({"job_id": job_id})
        final_bill = []
        for p1 in final_bill1:
            final_bill.append(p1)

        Myob_Job = db["job"].find({"job_id": job_id})
        Myob_Job1 = []
        for n in range(0, db["job"].count_documents({"job_id": job_id})):
            Myob_Job1.append(Myob_Job[n])

        QBO_COA = db["QBO_COA"].find({"job_id": job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id": job_id})
        QBO_supplier = []
        for p3 in QBO_Supplier:
            QBO_supplier.append(p3)

        QBO_Item = db["QBO_Item"].find({"job_id": job_id})
        QBO_item = []
        for p4 in QBO_Item:
            QBO_item.append(p4)

        QBO_Class = db["QBO_Class"].find({"job_id": job_id})
        QBO_class = []
        for p5 in QBO_Class:
            QBO_class.append(p5)

        QBO_Tax = db["QBO_Tax"].find({"job_id": job_id})
        QBO_tax = []
        for p5 in QBO_Tax:
            QBO_tax.append(p5)

        bill_arr = []
        vendor_credit_arr = []

        bill_bumbers=[]
        for b1 in range(0,len(final_bill)):
            bill_bumbers.append(final_bill[b1]['invoice_no'])

        data1=[]

        frequency_counter = Counter(bill_bumbers)
        for number, count in frequency_counter.items():
            if count>1:
                data1.append({number:count})
        
        key_list = []


        # final_bill = final_bill

        m1=[]
        for m in range(0,len(final_bill)):
            # if final_bill[m]['LineAmountTypes']=="Exclusive":
            if final_bill[m]['invoice_no'] in ['00000006']:
                m1.append(final_bill[m])

        final_bill = m1

        for i in range(0, len(final_bill)):
            _id=final_bill[i]['_id']
            task_id=task_id
            if "account" in final_bill[i]:
                if final_bill[i]["Total_Amount"] >= 0:
                    if len(final_bill[i]["account"]) == 1:
                        if "Item_name" in final_bill[i]["account"][0]:
                            QuerySet = {"Line": []}
                            QuerySet1 = {}
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            discount1 = {}
                            discount2 = {}
                            TaxLineDetail = {}
                            TaxRate = {}
                            Tax = {"Amount": abs(final_bill[i]["TotalTax"]), "DetailType": "TaxLineDetail",
                                   "TaxLineDetail": TaxLineDetail}
                            TxnTaxDetail = {"TaxLine": [], "TotalTax": abs(final_bill[i]["TotalTax"])}
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            TxnTaxDetail["TaxLine"].append(Tax)
                            QuerySet["TxnTaxDetail"] = TxnTaxDetail
                            TaxCodeRef = {}
                            QuerySet["TotalAmt"] = abs(final_bill[i]["Total_Amount"])

                            taxrate1 = 0

                            if final_bill[i]["Is_Tax_Inclusive"] == True:
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"

                                for k1 in range(0, len(QBO_tax)):
                                    if final_bill[i]["account"][0]["Tax_Code"] in ["GST","GCA","CAP"]:
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST (purchases)"
                                                    == QBO_tax[k1]["taxrate_name"]
                                            ):
                                                TaxRate["value"] = QBO_tax[k1][
                                                    "taxrate_id"
                                                ]
                                                TaxCodeRef["value"] = QBO_tax[k1][
                                                    "taxcode_id"
                                                ]
                                                TaxLineDetail["TaxPercent"] = QBO_tax[
                                                    k1
                                                ]["Rate"]
                                                taxrate1 = QBO_tax[k1]["Rate"]
                                                TaxLineDetail["NetAmountTaxable"] = abs(
                                                    final_bill[i]["Total_Amount"]
                                                    - final_bill[i]["TotalTax"]
                                                )

                                    elif (
                                            final_bill[i]["account"][0]["Tax_Code"] in ["FRE","INP"]
                                    ):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST-free (purchases)"
                                                    == QBO_tax[k1]["taxrate_name"]
                                            ):
                                                TaxRate["value"] = QBO_tax[k1][
                                                    "taxrate_id"
                                                ]
                                                TaxCodeRef["value"] = QBO_tax[k1][
                                                    "taxcode_id"
                                                ]
                                                TaxLineDetail["TaxPercent"] = QBO_tax[
                                                    k1
                                                ]["Rate"]
                                                taxrate1 = QBO_tax[k1]["Rate"]
                                                TaxLineDetail["NetAmountTaxable"] = abs(
                                                    QBO_tax[k1]["Rate"]
                                                    * final_bill[i]["TotalTax"]
                                                )
                                                Tax["Amount"] = abs(
                                                    final_bill[i]["TotalTax"] * taxrate1
                                                )

                                    else:
                                        pass

                                QuerySet1["Amount"] = abs(
                                    round(
                                        final_bill[i]["account"][0]["Unit_Price"]
                                        * final_bill[i]["account"][0]["Quantity"]
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )
                                )
                                QuerySet2["UnitPrice"] = round(
                                    abs(
                                        final_bill[i]["account"][0]["Unit_Price"]
                                        / (100 + taxrate1)
                                        * 100
                                    ),
                                    2,
                                )
                            else:
                                QuerySet["GlobalTaxCalculation"] = "TaxExcluded"

                            QuerySet["DocNumber"] = final_bill[i]["invoice_no"] if final_bill[i]["invoice_no"] not in key_list else final_bill[i]["invoice_no"][0:14]+"-"+final_bill[i]["UID"][-6:] 
                            
                            QuerySet2["TaxCodeRef"] = TaxCodeRef
                            QuerySet1["Description"] = final_bill[i]["account"][0][
                                "Description"
                            ]
                            if ("Comment" in final_bill[i]) and (
                                    "supplier_invoice_no" in final_bill[i]
                            ):
                                if (
                                        (final_bill[i]["supplier_invoice_no"] is not None)
                                        and (final_bill[i]["supplier_invoice_no"] != "")
                                        and (final_bill[i]["Comment"] is not None)
                                        and (final_bill[i]["Comment"] != "")
                                ):
                                    QuerySet["PrivateNote"] = (
                                            final_bill[i]["Comment"]
                                            + " Supplier Invoice Number is:"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                            elif "Comment" in final_bill[i]:
                                QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                            elif "supplier_invoice_no" in final_bill[i]:
                                QuerySet["PrivateNote"] = (
                                        " Supplier Invoice Number is:"
                                        + final_bill[i]["supplier_invoice_no"]
                                )
                            else:
                                pass

                            QuerySet["TxnDate"] = final_bill[i]["Bill_Date"]
                            QuerySet["DueDate"] = final_bill[i]["Due_Date"]
                            QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                            QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                            QuerySet2["Qty"] = final_bill[i]["account"][0]["Quantity"]
                            QuerySet2["ItemRef"] = QuerySet3

                            for j1 in range(0, len(QBO_item)):
                                if (
                                        final_bill[i]["account"][0]["Item_name"]
                                        == QBO_item[j1]["Name"]
                                ):
                                    QuerySet3["value"] = QBO_item[j1]["Id"]
                                elif (
                                        final_bill[i]["account"][0]["DisplayID"]
                                        == QBO_item[j1]["Name"]
                                ):
                                    QuerySet3["value"] = QBO_item[j1]["Id"]

                            QuerySet["VendorRef"] = QuerySet4
                            for j3 in range(0, len(QBO_supplier)):
                                if (
                                        final_bill[i]["Supplier_Name"]
                                        == QBO_supplier[j3]["DisplayName"]
                                ):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]

                            QuerySet2["ClassRef"] = QuerySet5
                            for j2 in range(0, len(QBO_class)):
                                for j4 in range(0, len(Myob_Job1)):
                                    if ("Job" in final_bill[i]["account"][j]) and (
                                            final_bill[i]["account"][j]["Job"] is not None
                                    ):
                                        if (
                                                final_bill[i]["account"][j]["Job"]["Name"]
                                                == Myob_Job1[j4]["Name"]
                                        ):
                                            if (
                                                    QBO_class[j2][
                                                        "FullyQualifiedName"
                                                    ].startswith(Myob_Job1[j4]["Name"])
                                            ) and (
                                                    QBO_class[j2][
                                                        "FullyQualifiedName"
                                                    ].endswith(Myob_Job1[j4]["Number"])
                                            ):
                                                QuerySet5["value"] = QBO_class[j2]["Id"]
                                                QuerySet5["name"] = QBO_class[j2][
                                                    "Name"
                                                ]

                            if final_bill[i]["account"][0]["Discount"] != 0:
                                discount2["Qty"] = "1"
                                discount2["UnitPrice"] = (
                                        -(
                                                final_bill[i]["account"][0]["Unit_Price"]
                                                * final_bill[i]["account"][0]["Quantity"]
                                                / (100 + taxrate1)
                                                * 100
                                        )
                                        * final_bill[i]["account"][0]["Discount"]
                                        / 100
                                )
                                discount2["TaxCodeRef"] = TaxCodeRef
                                discount2["ItemRef"] = QuerySet3
                                discount2["ClassRef"] = QuerySet5
                                discount1["Description"] = "Discount Given"
                                discount1["DetailType"] = "ItemBasedExpenseLineDetail"
                                discount1["Amount"] = (
                                        -(
                                                final_bill[i]["account"][0]["Unit_Price"]
                                                * final_bill[i]["account"][0]["Quantity"]
                                                / (100 + taxrate1)
                                                * 100
                                        )
                                        * final_bill[i]["account"][0]["Discount"]
                                        / 100
                                )
                                discount1["ItemBasedExpenseLineDetail"] = discount2

                            if discount1 != {}:
                                QuerySet["Line"].append(discount1)

                            if QuerySet1!={}:
                                QuerySet["Line"].append(QuerySet1)

                            # bill_arr.append(QuerySet)
                            QuerySet["Line"] = [item for item in a if not (isinstance(item, dict) and not bool(item))]

                            payload = json.dumps(QuerySet)

                            bill_date = final_bill[i]["Bill_Date"][0:10]
                            bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")

                            if start_date1 is not None and end_date1 is not None:
                                if (bill_date1 >= start_date1) and (
                                        bill_date1 < end_date1
                                ):
                                    post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                            else:
                                post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                    else:
                        QuerySet = {"Line": []}
                        TxnTaxDetail = {"TaxLine": []}

                        for j in range(0, len(final_bill[i]["account"])):
                            if "Item_name" in final_bill[i]["account"][j]:
                                QuerySet1 = {}
                                QuerySet2 = {}
                                QuerySet3 = {}
                                QuerySet4 = {}
                                QuerySet5 = {}
                                discount1 = {}
                                discount2 = {}
                                TaxLineDetail = {}
                                TaxRate = {}
                                Tax = {}
                                Tax["DetailType"] = "TaxLineDetail"
                                Tax["TaxLineDetail"] = TaxLineDetail
                                TxnTaxDetail["TotalTax"] = abs(
                                    final_bill[i]["TotalTax"]
                                )
                                TaxLineDetail["TaxRateRef"] = TaxRate
                                TaxLineDetail["PercentBased"] = True
                                TxnTaxDetail["TaxLine"].append(Tax)
                                QuerySet["TxnTaxDetail"] = TxnTaxDetail
                                TaxCodeRef = {}
                                QuerySet["TotalAmt"] = abs(
                                    final_bill[i]["Total_Amount"]
                                )

                                if final_bill[i]["Is_Tax_Inclusive"] == True:
                                    QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                    for k1 in range(0, len(QBO_tax)):
                                        if (
                                                final_bill[i]["account"][j]["Tax_Code"]
                                                in ["GST","GCA","CAP"]
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "GST (purchases)"
                                                        == QBO_tax[k1]["taxrate_name"]
                                                ):
                                                    TaxRate["value"] = QBO_tax[k1][
                                                        "taxrate_id"
                                                    ]
                                                    TaxCodeRef["value"] = QBO_tax[k1][
                                                        "taxcode_id"
                                                    ]
                                                    TaxLineDetail[
                                                        "TaxPercent"
                                                    ] = QBO_tax[k1]["Rate"]
                                                    taxrate1 = QBO_tax[k1]["Rate"]
                                                    TaxLineDetail[
                                                        "NetAmountTaxable"
                                                    ] = abs(
                                                        QBO_tax[k1]["Rate"]
                                                        * final_bill[i]["TotalTax"]
                                                    )
                                                    Tax["Amount"] = abs(
                                                        final_bill[i]["TotalTax"]
                                                    )

                                        elif (
                                                final_bill[i]["account"][j]["Tax_Code"]
                                                in ["FRE","INP"]
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "GST-free (purchases)"
                                                        == QBO_tax[k1]["taxrate_name"]
                                                ):
                                                    TaxRate["value"] = QBO_tax[k1][
                                                        "taxrate_id"
                                                    ]
                                                    TaxCodeRef["value"] = QBO_tax[k1][
                                                        "taxcode_id"
                                                    ]
                                                    TaxLineDetail[
                                                        "TaxPercent"
                                                    ] = QBO_tax[k1]["Rate"]
                                                    taxrate1 = QBO_tax[k1]["Rate"]
                                                    TaxLineDetail[
                                                        "NetAmountTaxable"
                                                    ] = abs(
                                                        QBO_tax[k1]["Rate"]
                                                        * final_bill[i]["TotalTax"]
                                                    )
                                                    Tax["Amount"] = abs(
                                                        final_bill[i]["TotalTax"]
                                                        * taxrate1
                                                    )

                                        else:
                                            pass

                                    QuerySet1["Amount"] = (
                                            abs(
                                                final_bill[i]["account"][j]["Quantity"]
                                                * final_bill[i]["account"][j]["Unit_Price"]
                                            )
                                            / (100 + taxrate1)
                                            * 100
                                    )
                                    QuerySet2["UnitPrice"] = abs(
                                        final_bill[i]["account"][j]["Unit_Price"]
                                        / (100 + taxrate1)
                                        * 100
                                    )

                                else:
                                    QuerySet["GlobalTaxCalculation"] = "TaxExcluded"

                                QuerySet["DocNumber"] = final_bill[i]["invoice_no"] if final_bill[i]["invoice_no"] not in key_list else final_bill[i]["invoice_no"][0:14]+"-"+final_bill[i]["UID"][-6:] 
                            
                                QuerySet2["TaxCodeRef"] = TaxCodeRef

                                if ("Comment" in final_bill[i]) and (
                                        "supplier_invoice_no" in final_bill[i]
                                ):
                                    if (
                                            (
                                                    final_bill[i]["supplier_invoice_no"]
                                                    is not None
                                            )
                                            and (final_bill[i]["supplier_invoice_no"] != "")
                                            and (final_bill[i]["Comment"] is not None)
                                            and (final_bill[i]["Comment"] != "")
                                    ):
                                        QuerySet["PrivateNote"] = (
                                                final_bill[i]["Comment"]
                                                + " Supplier Invoice Number is:"
                                                + final_bill[i]["supplier_invoice_no"]
                                        )
                                elif "Comment" in final_bill[i]:
                                    QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                                elif "supplier_invoice_no" in final_bill[i]:
                                    QuerySet["PrivateNote"] = (
                                            " Supplier Invoice Number is:"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                                else:
                                    pass

                                QuerySet["TxnDate"] = final_bill[i]["Bill_Date"]
                                QuerySet["DueDate"] = final_bill[i]["Due_Date"]
                                QuerySet1["Description"] = final_bill[i]["account"][j][
                                    "Description"
                                ]
                                QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                                QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                                QuerySet2["Qty"] = final_bill[i]["account"][j][
                                    "Quantity"
                                ]

                                QuerySet2["ItemRef"] = QuerySet3
                                for j1 in range(0, len(QBO_item)):
                                    if (
                                            final_bill[i]["account"][j]["Item_name"]
                                            == QBO_item[j1]["Name"]
                                    ):
                                        QuerySet3["value"] = QBO_item[j1]["Id"]
                                    elif (
                                            final_bill[i]["account"][j]["DisplayID"]
                                            == QBO_item[j1]["Name"]
                                    ):
                                        QuerySet3["value"] = QBO_item[j1]["Id"]

                                QuerySet["VendorRef"] = QuerySet4
                                for j3 in range(0, len(QBO_supplier)):
                                    if (
                                            final_bill[i]["Supplier_Name"]
                                            == QBO_supplier[j3]["DisplayName"]
                                    ):
                                        QuerySet4["value"] = QBO_supplier[j3]["Id"]

                                QuerySet2["ClassRef"] = QuerySet5
                                for j2 in range(0, len(QBO_class)):
                                    for j4 in range(0, len(Myob_Job1)):
                                        if ("Job" in final_bill[i]["account"][j]) and (
                                                final_bill[i]["account"][j]["Job"]
                                                is not None
                                        ):
                                            if (
                                                    final_bill[i]["account"][j]["Job"][
                                                        "Name"
                                                    ]
                                                    == Myob_Job1[j4]["Name"]
                                            ):
                                                if (
                                                        QBO_class[j2][
                                                            "FullyQualifiedName"
                                                        ].startswith(Myob_Job1[j4]["Name"])
                                                ) and (
                                                        QBO_class[j2][
                                                            "FullyQualifiedName"
                                                        ].endswith(Myob_Job1[j4]["Number"])
                                                ):
                                                    QuerySet5["value"] = QBO_class[j2][
                                                        "Id"
                                                    ]
                                                    QuerySet5["name"] = QBO_class[j2][
                                                        "Name"
                                                    ]

                                if final_bill[i]["account"][j]["Discount"] != 0:
                                    discount2["Qty"] = "1"
                                    discount2["UnitPrice"] = (
                                            -(
                                                    (
                                                            final_bill[i]["account"][j]["Quantity"]
                                                            * final_bill[i]["account"][j][
                                                                "Unit_Price"
                                                            ]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            )
                                            * final_bill[i]["account"][j]["Discount"]
                                            / 100
                                    )
                                    discount2["TaxCodeRef"] = TaxCodeRef
                                    discount2["ItemRef"] = QuerySet3
                                    discount2["ClassRef"] = QuerySet5
                                    discount1["Description"] = "Discount Given"
                                    discount1[
                                        "DetailType"
                                    ] = "ItemBasedExpenseLineDetail"
                                    discount1["Amount"] = (
                                            -(
                                                    (
                                                            final_bill[i]["account"][j]["Quantity"]
                                                            * final_bill[i]["account"][j][
                                                                "Unit_Price"
                                                            ]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            )
                                            * final_bill[i]["account"][j]["Discount"]
                                            / 100
                                    )
                                    discount1["ItemBasedExpenseLineDetail"] = discount2

                                if discount1 != {} or discount1 is not None:
                                    QuerySet["Line"].append(discount1)
                                else:
                                    pass

                                if QuerySet1!={}:
                                    QuerySet["Line"].append(QuerySet1)
                            post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                        else:
                            post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                else:
                    if len(final_bill[i]["account"]) == 1:
                        QuerySet = {"Line": []}
                        QuerySet1 = {}
                        QuerySet2 = {}
                        QuerySet3 = {}
                        QuerySet4 = {}
                        QuerySet5 = {}
                        discount1 = {}
                        discount2 = {}
                        TxnTaxDetail = {"TaxLine": []}
                        TaxLineDetail = {}
                        TaxRate = {}
                        Tax = {}
                        Tax["Amount"] = abs(final_bill[i]["TotalTax"])
                        Tax["DetailType"] = "TaxLineDetail"
                        Tax["TaxLineDetail"] = TaxLineDetail
                        TxnTaxDetail["TotalTax"] = abs(final_bill[i]["TotalTax"])
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True
                        TxnTaxDetail["TaxLine"].append(Tax)
                        QuerySet["TxnTaxDetail"] = TxnTaxDetail
                        TaxCodeRef = {}
                        QuerySet["TotalAmt"] = abs(final_bill[i]["Total_Amount"])

                        taxrate1 = 0
                        if final_bill[i]["Is_Tax_Inclusive"] == True:
                            QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                            for k1 in range(0, len(QBO_tax)):
                                if final_bill[i]["account"][0]["Tax_Code"] in ["GST","GCA","CAP"]:
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST (purchases)"
                                                == QBO_tax[k1]["taxrate_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]
                                            TaxLineDetail["NetAmountTaxable"] = abs(
                                                QBO_tax[k1]["Rate"]
                                                * final_bill[i]["TotalTax"]
                                            )
                                elif final_bill[i]["account"][0]["Tax_Code"] in ["FRE","INP"]:
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST-free (purchases)"
                                                == QBO_tax[k1]["taxrate_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]
                                            TaxLineDetail["NetAmountTaxable"] = abs(
                                                QBO_tax[k1]["Rate"]
                                                * final_bill[i]["TotalTax"]
                                            )
                                            Tax["Amount"] = abs(
                                                final_bill[i]["TotalTax"] * taxrate1
                                            )
                                else:
                                    pass

                            QuerySet1["Amount"] = round(
                                abs(
                                    final_bill[i]["account"][0]["Quantity"]
                                    * final_bill[i]["account"][0]["Unit_Price"]
                                )
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )
                            QuerySet2["UnitPrice"] = round(
                                abs(
                                    final_bill[i]["account"][0]["Unit_Price"]
                                    / (100 + taxrate1)
                                    * 100
                                ),
                                3,
                            )

                        else:
                            QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                            for k1 in range(0, len(QBO_tax)):
                                if final_bill[i]["account"][0]["Tax_Code"] in ["GST","GCA","CAP"]:
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST (purchases)"
                                                == QBO_tax[k1]["taxrate_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]
                                            TaxLineDetail["NetAmountTaxable"] = abs(
                                                QBO_tax[k1]["Rate"]
                                                * final_bill[i]["TotalTax"]
                                            )
                                elif final_bill[i]["account"][0]["Tax_Code"] in ["FRE","INP"]:
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST-free (purchases)"
                                                == QBO_tax[k1]["taxrate_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]
                                            TaxLineDetail["NetAmountTaxable"] = abs(
                                                QBO_tax[k1]["Rate"]
                                                * final_bill[i]["TotalTax"]
                                            )
                                            Tax["Amount"] = abs(
                                                final_bill[i]["TotalTax"] * taxrate1
                                            )
                                else:
                                    pass

                            QuerySet1["Amount"] = abs(
                                final_bill[i]["account"][0]["Quantity"]
                                * final_bill[i]["account"][0]["Unit_Price"]
                            )
                            QuerySet2["UnitPrice"] = abs(
                                final_bill[i]["account"][0]["Unit_Price"]
                            )

                        QuerySet["DocNumber"] = final_bill[i]["invoice_no"] if final_bill[i]["invoice_no"] not in key_list else final_bill[i]["invoice_no"][0:14]+"-"+final_bill[i]["UID"][-6:] 
                            
                        QuerySet2["TaxCodeRef"] = TaxCodeRef

                        if ("Comment" in final_bill[i]) and (
                                "supplier_invoice_no" in final_bill[i]
                        ):
                            if (
                                    (final_bill[i]["supplier_invoice_no"] is not None)
                                    and (final_bill[i]["supplier_invoice_no"] != "")
                                    and (final_bill[i]["Comment"] is not None)
                                    and (final_bill[i]["Comment"] != "")
                            ):
                                QuerySet["PrivateNote"] = (
                                        final_bill[i]["Comment"]
                                        + " Supplier Invoice Number is:"
                                        + final_bill[i]["supplier_invoice_no"]
                                )
                        elif "Comment" in final_bill[i]:
                            QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                        elif "supplier_invoice_no" in final_bill[i]:
                            QuerySet["PrivateNote"] = (
                                    " Supplier Invoice Number is:"
                                    + final_bill[i]["supplier_invoice_no"]
                            )
                        else:
                            pass

                        QuerySet["TxnDate"] = final_bill[i]["Bill_Date"]
                        QuerySet1["Description"] = final_bill[i]["account"][0][
                            "Description"
                        ]
                        QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                        QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                        QuerySet2["Qty"] = abs(final_bill[i]["account"][0]["Quantity"])
                        QuerySet2["ItemRef"] = QuerySet3

                        for j1 in range(0, len(QBO_item)):
                            if (
                                    final_bill[i]["account"][0]["Item_name"]
                                    == QBO_item[j1]["Name"]
                            ):
                                QuerySet3["value"] = QBO_item[j1]["Id"]
                            elif (
                                    final_bill[i]["account"][0]["DisplayID"]
                                    == QBO_item[j1]["Name"]
                            ):
                                QuerySet3["value"] = QBO_item[j1]["Id"]

                        QuerySet["VendorRef"] = QuerySet4

                        for j3 in range(0, len(QBO_supplier)):
                            if (
                                    final_bill[i]["Supplier_Name"]
                                    == QBO_supplier[j3]["DisplayName"]
                            ):
                                QuerySet4["value"] = QBO_supplier[j3]["Id"]

                        QuerySet2["ClassRef"] = QuerySet5

                        for j2 in range(0, len(QBO_class)):
                            for j4 in range(0, len(Myob_Job1)):
                                if ("Job" in final_bill[i]["account"][j]) and (
                                        final_bill[i]["account"][j]["Job"] is not None
                                ):
                                    if (
                                            final_bill[i]["account"][j]["Job"]["Name"]
                                            == Myob_Job1[j4]["Name"]
                                    ):
                                        if (
                                                QBO_class[j2][
                                                    "FullyQualifiedName"
                                                ].startswith(Myob_Job1[j4]["Name"])
                                        ) and (
                                                QBO_class[j2][
                                                    "FullyQualifiedName"
                                                ].endswith(Myob_Job1[j4]["Number"])
                                        ):
                                            QuerySet5["value"] = QBO_class[j2]["Id"]
                                            QuerySet5["name"] = QBO_class[j2]["Name"]

                        if final_bill[i]["account"][0]["Discount"] != 0:
                            discount2["Qty"] = "1"
                            discount2["UnitPrice"] = (
                                    -round(
                                        abs(
                                            final_bill[i]["account"][0]["Quantity"]
                                            * final_bill[i]["account"][0]["Unit_Price"]
                                        )
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )
                                    * final_bill[i]["account"][0]["Discount"]
                                    / 100
                            )
                            discount2["TaxCodeRef"] = TaxCodeRef
                            discount2["ItemRef"] = QuerySet3
                            discount2["ClassRef"] = QuerySet5
                            discount1["Description"] = "Discount Given"
                            discount1["DetailType"] = "ItemBasedExpenseLineDetail"
                            discount1["Amount"] = (
                                    -round(
                                        abs(
                                            final_bill[i]["account"][0]["Quantity"]
                                            * final_bill[i]["account"][0]["Unit_Price"]
                                        )
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )
                                    * final_bill[i]["account"][0]["Discount"]
                                    / 100
                            )
                            discount1["ItemBasedExpenseLineDetail"] = discount2

                        if discount1 != {}:
                            QuerySet["Line"].append(discount1)

                        if QuerySet1!={}:
                            QuerySet["Line"].append(QuerySet1)

                        # vendor_credit_arr.append(QuerySet)
                        QuerySet["Line"] = [item for item in a if not (isinstance(item, dict) and not bool(item))]

                        payload = json.dumps(QuerySet)
                        bill_date = final_bill[i]["Bill_Date"][0:10]
                        bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")

                        if start_date1 is not None and end_date1 is not None and (
                                start_date1 <= bill_date1 < end_date1):
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                        else:
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                    else:
                        QuerySet = {"Line": []}
                        TxnTaxDetail = {"TaxLine": []}

                        taxrate1 = 0
                        for j in range(0, len(final_bill[i]["account"])):
                            QuerySet1 = {}
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            discount1 = {}
                            discount2 = {}
                            TaxLineDetail = {}
                            TaxRate = {}
                            Tax = {}
                            Tax["Amount"] = abs(final_bill[i]["TotalTax"])
                            Tax["DetailType"] = "TaxLineDetail"
                            Tax["TaxLineDetail"] = TaxLineDetail
                            TxnTaxDetail["TotalTax"] = abs(final_bill[i]["TotalTax"])
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            TxnTaxDetail["TaxLine"].append(Tax)
                            QuerySet["TxnTaxDetail"] = TxnTaxDetail
                            TaxCodeRef = {}
                            QuerySet["TotalAmt"] = abs(final_bill[i]["Total_Amount"])

                            if final_bill[i]["Is_Tax_Inclusive"] == True:
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                for k1 in range(0, len(QBO_tax)):
                                    if final_bill[i]["account"][j]["Tax_Code"] in ["GST","GCA","CAP"]:
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST (purchases)"
                                                    == QBO_tax[k1]["taxrate_name"]
                                            ):
                                                TaxRate["value"] = QBO_tax[k1][
                                                    "taxrate_id"
                                                ]
                                                TaxCodeRef["value"] = QBO_tax[k1][
                                                    "taxcode_id"
                                                ]
                                                TaxLineDetail["TaxPercent"] = QBO_tax[
                                                    k1
                                                ]["Rate"]
                                                taxrate1 = QBO_tax[k1]["Rate"]
                                                TaxLineDetail["NetAmountTaxable"] = abs(
                                                    QBO_tax[k1]["Rate"]
                                                    * final_bill[i]["TotalTax"]
                                                )
                                                Tax["Amount"] = abs(
                                                    final_bill[i]["TotalTax"]
                                                )

                                    elif (
                                            final_bill[i]["account"][j]["Tax_Code"] in ["FRE","INP"]
                                    ):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST-free (purchases)"
                                                    == QBO_tax[k1]["taxrate_name"]
                                            ):
                                                TaxRate["value"] = QBO_tax[k1][
                                                    "taxrate_id"
                                                ]
                                                TaxCodeRef["value"] = QBO_tax[k1][
                                                    "taxcode_id"
                                                ]
                                                TaxLineDetail["TaxPercent"] = QBO_tax[
                                                    k1
                                                ]["Rate"]
                                                taxrate1 = QBO_tax[k1]["Rate"]
                                                TaxLineDetail["NetAmountTaxable"] = abs(
                                                    QBO_tax[k1]["Rate"]
                                                    * final_bill[i]["TotalTax"]
                                                )
                                                Tax["Amount"] = abs(
                                                    final_bill[i]["TotalTax"] * taxrate1
                                                )

                                    else:
                                        pass

                                QuerySet1["Amount"] = abs(
                                    (
                                            round(
                                                final_bill[i]["account"][j]["Quantity"]
                                                * final_bill[i]["account"][j]["Unit_Price"],
                                                2,
                                            )
                                            / (100 + taxrate1)
                                            * 100
                                    )
                                )
                                QuerySet2["UnitPrice"] = abs(
                                    final_bill[i]["account"][j]["Unit_Price"]
                                    / (100 + taxrate1)
                                    * 100
                                )

                            else:
                                QuerySet["GlobalTaxCalculation"] = "TaxExcluded"

                            QuerySet["DocNumber"] = final_bill[i]["invoice_no"] if final_bill[i]["invoice_no"] not in key_list else final_bill[i]["invoice_no"][0:14]+"-"+final_bill[i]["UID"][-6:] 
                            
                            QuerySet2["TaxCodeRef"] = TaxCodeRef
                            if ("Comment" in final_bill[i]) and (
                                    "supplier_invoice_no" in final_bill[i]
                            ):
                                if (
                                        (final_bill[i]["supplier_invoice_no"] is not None)
                                        and (final_bill[i]["supplier_invoice_no"] != "")
                                        and (final_bill[i]["Comment"] is not None)
                                        and (final_bill[i]["Comment"] != "")
                                ):
                                    QuerySet["PrivateNote"] = (
                                            final_bill[i]["Comment"]
                                            + " Supplier Invoice Number is:"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                            elif "Comment" in final_bill[i]:
                                QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                            elif "supplier_invoice_no" in final_bill[i]:
                                QuerySet["PrivateNote"] = (
                                        " Supplier Invoice Number is:"
                                        + final_bill[i]["supplier_invoice_no"]
                                )
                            else:
                                pass

                            QuerySet["TxnDate"] = final_bill[i]["Bill_Date"]
                            QuerySet1["Description"] = final_bill[i]["account"][j][
                                "Description"
                            ]
                            QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                            QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                            QuerySet2["Qty"] = abs(
                                final_bill[i]["account"][j]["Quantity"]
                            )
                            QuerySet2["ItemRef"] = QuerySet3

                            for j1 in range(0, len(QBO_item)):
                                if (
                                        final_bill[i]["account"][j]["Item_name"]
                                        == QBO_item[j1]["Name"]
                                ):
                                    QuerySet3["value"] = QBO_item[j1]["Id"]
                                elif (
                                        final_bill[i]["account"][j]["DisplayID"]
                                        == QBO_item[j1]["Name"]
                                ):
                                    QuerySet3["value"] = QBO_item[j1]["Id"]

                            QuerySet["VendorRef"] = QuerySet4
                            for j3 in range(0, len(QBO_supplier)):
                                if (
                                        final_bill[i]["Supplier_Name"]
                                        == QBO_supplier[j3]["DisplayName"]
                                ):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]

                            QuerySet2["ClassRef"] = QuerySet5

                            for j2 in range(0, len(QBO_class)):
                                for j4 in range(0, len(Myob_Job1)):
                                    if ("Job" in final_bill[i]["account"][j]) and (
                                            final_bill[i]["account"][j]["Job"] is not None
                                    ):
                                        if (
                                                final_bill[i]["account"][j]["Job"]["Name"]
                                                == Myob_Job1[j4]["Name"]
                                        ):
                                            if (
                                                    QBO_class[j2][
                                                        "FullyQualifiedName"
                                                    ].startswith(Myob_Job1[j4]["Name"])
                                            ) and (
                                                    QBO_class[j2][
                                                        "FullyQualifiedName"
                                                    ].endswith(Myob_Job1[j4]["Number"])
                                            ):
                                                QuerySet5["value"] = QBO_class[j2]["Id"]
                                                QuerySet5["name"] = QBO_class[j2][
                                                    "Name"
                                                ]

                            if final_bill[i]["account"][j]["Discount"] != 0:
                                discount2["Qty"] = "1"
                                discount2["UnitPrice"] = (
                                        (
                                            round(
                                                (
                                                        final_bill[i]["account"][j]["Quantity"]
                                                        * final_bill[i]["account"][j][
                                                            "Unit_Price"
                                                        ]
                                                )
                                                / (100 + taxrate1)
                                                * 100,
                                                2,
                                            )
                                        )
                                        * final_bill[i]["account"][j]["Discount"]
                                        / 100
                                )
                                discount2["TaxCodeRef"] = TaxCodeRef
                                discount2["ItemRef"] = QuerySet3
                                discount2["ClassRef"] = QuerySet5
                                discount1["Description"] = "Discount Given"
                                discount1["DetailType"] = "ItemBasedExpenseLineDetail"
                                discount1["Amount"] = (
                                        (
                                            round(
                                                (
                                                        final_bill[i]["account"][j]["Quantity"]
                                                        * final_bill[i]["account"][j][
                                                            "Unit_Price"
                                                        ]
                                                )
                                                / (100 + taxrate1)
                                                * 100,
                                                2,
                                            )
                                        )
                                        * final_bill[i]["account"][j]["Discount"]
                                        / 100
                                )
                                discount1["ItemBasedExpenseLineDetail"] = discount2

                            if discount1 != {} or discount1 is not None:
                                QuerySet["Line"].append(discount1)
                            else:
                                pass
                            if QuerySet1!={}:
                                QuerySet["Line"].append(QuerySet1)
                            
                        QuerySet["Line"] = [item for item in a if not (isinstance(item, dict) and not bool(item))]
                        

                        # vendor_credit_arr.append(QuerySet)
                        payload = json.dumps(QuerySet)
                        bill_date = final_bill[i]["Bill_Date"][0:10]
                        bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")
                        if start_date1 is not None and end_date1 is not None and (
                                start_date1 <= bill_date1 < end_date1):
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                        else:
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

    except Exception as ex:
        traceback.print_exc()
        
