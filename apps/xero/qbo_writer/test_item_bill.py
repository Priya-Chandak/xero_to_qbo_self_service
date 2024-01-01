import json
import logging
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job

import logging


def add_xero_item_bill(job_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> test_item_bill -> add_xero_item_bill")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url1 = f"{base_url}/bill?minorversion=14"
        url2 = f"{base_url}/vendorcredit?minorversion=14"
        final_bill1 = db["xero_bill"].find({"job_id": job_id})
        final_bill = []
        for p1 in final_bill1:
            final_bill.append(p1)

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
        for p6 in QBO_Tax:
            QBO_tax.append(p6)

        XERO_COA = db["xero_coa"].find({"job_id": job_id})
        xero_coa1 = []
        for p7 in XERO_COA:
            xero_coa1.append(p7)

        Xero_Items = db["xero_items"].find({"job_id": job_id})
        xero_items = []
        for p8 in Xero_Items:
            xero_items.append(p8)

        bill_arr = []
        vendor_credit_arr = []

        final_bill = final_bill

        for i in range(0, len(final_bill)):
            if (final_bill[i]["Status"] != "DELETED") and (
                    final_bill[i]["Status"] != "VOIDED"
            ):
                if "Line" in final_bill[i]:
                    if final_bill[i]["TotalAmount"] > 0:
                        if (len(final_bill[i]["Line"]) == 1) and (
                                "ItemCode" in final_bill[i]["Line"][0]
                        ):
                            QuerySet = {"Line": []}
                            QuerySet1 = {}
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            TaxLineDetail = {}
                            TaxRate = {}
                            Tax = {}
                            TxnTaxDetail = {"TaxLine": []}
                            Tax["Amount"] = abs(final_bill[i]["TotalTax"])
                            Tax["DetailType"] = "TaxLineDetail"
                            Tax["TaxLineDetail"] = TaxLineDetail
                            TxnTaxDetail["TotalTax"] = abs(final_bill[i]["TotalTax"])
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            TxnTaxDetail["TaxLine"].append(Tax)
                            QuerySet["TxnTaxDetail"] = TxnTaxDetail
                            TaxCodeRef = {}
                            ItemRef = {}

                            QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                            for j1 in range(0, len(QBO_item)):
                                for j2 in range(0, len(xero_items)):
                                    if ("ItemCode" in final_bill[i]["Line"][0]) and (
                                            "AccountCode" in final_bill[i]["Line"][0]
                                    ):
                                        if (
                                                final_bill[i]["Line"][0]["ItemCode"]
                                                + "-"
                                                + final_bill[i]["Line"][0]["AccountCode"]
                                                == QBO_item[j1]["Name"]
                                        ):
                                            ItemRef["value"] = QBO_item[j1]["Id"]

                                    elif ("ItemCode" in final_bill[i]["Line"][0]) and (
                                            ("AccountCode" not in final_bill[i]["Line"][0])
                                    ):
                                        if (
                                                final_bill[i]["Line"][0]["ItemCode"]
                                                == xero_items[j2]["Code"]
                                        ):
                                            if (
                                                    xero_items[j2]["Name"]
                                                    == QBO_item[j1]["Name"]
                                            ):
                                                ItemRef["value"] = QBO_item[j1]["Id"]

                            QuerySet2["Qty"] = final_bill[i]["Line"][0]["Quantity"]
                            QuerySet2["UnitPrice"] = final_bill[i]["Line"][0][
                                "UnitAmount"
                            ]

                            QuerySet2["ItemRef"] = ItemRef

                            taxrate1 = 0
                            for k1 in range(0, len(QBO_tax)):
                                if (
                                        (
                                                final_bill[i]["Line"][0]["TaxType"]
                                                == "BASEXCLUDED"
                                        )
                                        or (final_bill[i]["Line"][0]["TaxType"] == None)
                                        or (final_bill[i]["Line"][0]["TaxType"] == "NONE")
                                ):
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "Input tax (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]

                                elif final_bill[i]["Line"][0]["TaxType"] == "INPUT":
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["TotalTax"]
                                            )

                                elif final_bill[i]["Line"][0]["TaxType"] == "OUTPUT":
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["TotalTax"]
                                            )

                                elif (
                                        final_bill[i]["Line"][0]["TaxType"]
                                        == "EXEMPTEXPENSES"
                                        or final_bill[i]["Line"][0]["TaxType"]
                                        == "EXEMPTOUTPUT"
                                ):
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST-free (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]

                                else:
                                    pass

                            if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                QuerySet1["Amount"] = (
                                        abs(final_bill[i]["TotalAmount"])
                                        / (100 + taxrate1)
                                        * 100
                                )
                                TaxLineDetail["NetAmountTaxable"] = abs(
                                    final_bill[i]["TotalAmount"]
                                    - final_bill[i]["TotalTax"]
                                )
                            else:
                                QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                QuerySet1["Amount"] = final_bill[i]["Line"][0][
                                    "LineAmount"
                                ]
                                TaxLineDetail["NetAmountTaxable"] = abs(
                                    final_bill[i]["TotalAmount"]
                                    - final_bill[i]["TotalTax"]
                                )

                            QuerySet2["TaxCodeRef"] = TaxCodeRef

                            if "supplier_invoice_no" in final_bill[i]:
                                if (
                                        final_bill[i]["supplier_invoice_no"] == None
                                        or final_bill[i]["supplier_invoice_no"] == ""
                                ):
                                    QuerySet["DocNumber"] = final_bill[i]["Inv_No"]
                                elif (
                                        final_bill[i]["supplier_invoice_no"] != ""
                                        or final_bill[i]["supplier_invoice_no"] is not None
                                ):
                                    QuerySet["DocNumber"] = (
                                            final_bill[i]["Inv_No"]
                                            + "-"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                            else:
                                QuerySet["DocNumber"] = final_bill[i]["Inv_No"]

                            if "Description" in final_bill[i]["Line"][0]:
                                QuerySet1["Description"] = final_bill[i]["Line"][0][
                                    "Description"
                                ]
                            else:
                                QuerySet1["Description"] = None

                            if "Comment" in final_bill[i]:
                                QuerySet["PrivateNote"] = final_bill[i]["Comment"]

                            QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                            QuerySet["DueDate"] = final_bill[i]["DueDate"]

                            QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                            QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2

                            # for j1 in range(0, len(QBO_coa)):
                            #     for j2 in range(0, len(xero_coa1)):
                            #         if 'Code' in xero_coa1[j2]:
                            #             if 'AccountCode' in final_bill[i]['Line'][0]:
                            #                 if final_bill[i]['Line'][0]['AccountCode'] == xero_coa1[j2]["Code"]:
                            #                     if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                            #                         QuerySet3['value'] = QBO_coa[j1]["Id"]

                            # QuerySet2['AccountRef'] = QuerySet3

                            for j3 in range(0, len(QBO_supplier)):
                                if QBO_supplier[j3]["DisplayName"].startswith(
                                        final_bill[i]["ContactName"]
                                ) and QBO_supplier[j3]["DisplayName"].endswith(" - S"):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                elif (
                                        final_bill[i]["ContactName"]
                                        == QBO_supplier[j3]["DisplayName"]
                                ):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                else:
                                    pass

                            QuerySet["VendorRef"] = QuerySet4

                            # QuerySet2['ClassRef'] = QuerySet5

                            # for j2 in range(0, len(QBO_class)):
                            #     if final_bill[i]['Line'][0]['Job'] == QBO_class[j2]['Name']:
                            #         QuerySet5['value'] = QBO_class[j2]['Id']
                            #         QuerySet5['name'] = QBO_class[j2]['Name']

                            QuerySet["Line"].append(QuerySet1)

                            bill_arr.append(QuerySet)
                            payload = json.dumps(QuerySet)
                            bill_date = final_bill[i]["TxnDate"][0:10]
                            bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")
                            if start_date1 is not None and end_date1 is not None:
                                if (bill_date1 >= start_date1) and (
                                        bill_date1 <= end_date1
                                ):
                                    response = requests.request(
                                        "POST", url1, headers=headers, data=payload
                                    )
                                    if response.status_code == 401:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   (
                                                       res1["fault"]["error"][0]["message"]
                                                   ).split(";")[0]
                                               ).split("=")[
                                                   1
                                               ] + ": Please Update the Access Token"
                                        add_job_status(job_id, res2, "error")
                                    elif response.status_code == 400:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   res1["Fault"]["Error"][0]["Detail"]
                                               ) + ": {}".format(final_bill[i]["Inv_No"])
                                        add_job_status(job_id, res2, "error")
                                else:
                                    pass

                            else:
                                response = requests.request(
                                    "POST", url1, headers=headers, data=payload
                                )
                                if response.status_code == 401:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               (res1["fault"]["error"][0]["message"]).split(
                                                   ";"
                                               )[0]
                                           ).split("=")[1] + ": Please Update the Access Token"
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               res1["Fault"]["Error"][0]["Detail"]
                                           ) + ": {}".format(final_bill[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                        elif len(final_bill[i]["Line"]) > 1:
                            QuerySet = {"Line": []}
                            TxnTaxDetail = {"TaxLine": []}

                            for j in range(0, len(final_bill[i]["Line"])):
                                if "ItemCode" in final_bill[i]["Line"][j]:
                                    QuerySet1 = {}
                                    QuerySet2 = {}
                                    QuerySet3 = {}
                                    QuerySet4 = {}
                                    QuerySet5 = {}
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
                                    ItemRef = {}
                                    QuerySet["TotalAmt"] = abs(
                                        final_bill[i]["TotalAmount"]
                                    )
                                    taxrate1 = 0

                                    for k1 in range(0, len(QBO_tax)):
                                        if (
                                                (
                                                        final_bill[i]["Line"][j]["TaxType"]
                                                        == "BASEXCLUDED"
                                                )
                                                or (
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == None
                                        )
                                                or (
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "NONE"
                                        )
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "Input tax (purchases)"
                                                        in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "EXEMPTEXPENSES"
                                                or final_bill[i]["Line"][j]["TaxType"]
                                                == "EXEMPTOUTPUT"
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "GST-free (purchases)"
                                                        in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "OUTPUT"
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "GST (purchases)"
                                                        in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "INPUT"
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "GST (purchases)"
                                                        in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "EXEMPTEXPENSES"
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "GST-free (purchases)"
                                                        in QBO_tax[k1]["taxrate_name"]
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
                                                    ] = final_bill[i]["TotalAmount"]
                                                    Tax["Amount"] = (
                                                            abs(final_bill[i]["TotalTax"])
                                                            * taxrate1
                                                    )

                                        else:
                                            pass

                                    if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                        QuerySet[
                                            "GlobalTaxCalculation"
                                        ] = "TaxInclusive"
                                        QuerySet1["Amount"] = (
                                                (final_bill[i]["Line"][j]["LineAmount"])
                                                / (100 + taxrate1)
                                                * 100
                                        )

                                    else:
                                        QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                        QuerySet1["Amount"] = final_bill[i]["Line"][j][
                                            "LineAmount"
                                        ]

                                    if "supplier_invoice_no" in final_bill[i]:
                                        if (
                                                final_bill[i]["supplier_invoice_no"] == None
                                                or final_bill[i]["supplier_invoice_no"]
                                                == ""
                                        ):
                                            QuerySet["DocNumber"] = final_bill[i][
                                                "Inv_No"
                                            ]
                                        elif (
                                                final_bill[i]["supplier_invoice_no"] != ""
                                                or final_bill[i]["supplier_invoice_no"]
                                                is not None
                                        ):
                                            QuerySet["DocNumber"] = (
                                                    final_bill[i]["Inv_No"]
                                                    + "-"
                                                    + final_bill[i]["supplier_invoice_no"]
                                            )
                                    else:
                                        QuerySet["DocNumber"] = final_bill[i]["Inv_No"]

                                    if "Comment" in final_bill[i]:
                                        QuerySet["PrivateNote"] = final_bill[i][
                                            "Comment"
                                        ]

                                    QuerySet2["TaxCodeRef"] = TaxCodeRef
                                    QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                                    QuerySet["DueDate"] = final_bill[i]["DueDate"]
                                    if "Description" in final_bill[i]["Line"][j]:
                                        QuerySet1["Description"] = final_bill[i][
                                            "Line"
                                        ][j]["Description"]

                                    QuerySet1[
                                        "DetailType"
                                    ] = "ItemBasedExpenseLineDetail"
                                    QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2

                                    # for j1 in range(0, len(QBO_coa)):
                                    #     for j2 in range(0, len(xero_coa1)):
                                    #         if 'Code' in xero_coa1[j2]:
                                    #             if 'AccountCode' in final_bill[i]['Line'][j]:
                                    #                 if final_bill[i]['Line'][j]['AccountCode'] == xero_coa1[j2]["Code"]:
                                    #                     if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                                    #                         QuerySet3['value'] = QBO_coa[j1]["Id"]

                                    # QuerySet2['AccountRef'] = QuerySet3

                                    for j3 in range(0, len(QBO_supplier)):
                                        if QBO_supplier[j3]["DisplayName"].startswith(
                                                final_bill[i]["ContactName"]
                                        ) and QBO_supplier[j3]["DisplayName"].endswith(
                                            " - S"
                                        ):
                                            QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                        elif (
                                                final_bill[i]["ContactName"]
                                                == QBO_supplier[j3]["DisplayName"]
                                        ):
                                            QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                        else:
                                            pass

                                    for j1 in range(0, len(QBO_item)):
                                        for j2 in range(0, len(xero_items)):
                                            if (
                                                    "ItemCode" in final_bill[i]["Line"][j]
                                            ) and (
                                                    "AccountCode"
                                                    in final_bill[i]["Line"][j]
                                            ):
                                                if (
                                                        final_bill[i]["Line"][j]["ItemCode"]
                                                        + "-"
                                                        + final_bill[i]["Line"][j][
                                                    "AccountCode"
                                                ]
                                                        == QBO_item[j1]["Name"]
                                                ):
                                                    ItemRef["value"] = QBO_item[j1][
                                                        "Id"
                                                    ]

                                            elif (
                                                    "ItemCode" in final_bill[i]["Line"][j]
                                            ) and (
                                                    (
                                                            "AccountCode"
                                                            not in final_bill[i]["Line"][j]
                                                    )
                                            ):
                                                if (
                                                        final_bill[i]["Line"][j]["ItemCode"]
                                                        == xero_items[j2]["Code"]
                                                ):
                                                    if (
                                                            xero_items[j2]["Name"]
                                                            == QBO_item[j1]["Name"]
                                                    ):
                                                        ItemRef["value"] = QBO_item[j1][
                                                            "Id"
                                                        ]

                                    QuerySet2["Qty"] = final_bill[i]["Line"][j][
                                        "Quantity"
                                    ]
                                    QuerySet2["UnitPrice"] = final_bill[i]["Line"][j][
                                        "UnitAmount"
                                    ]
                                    QuerySet2["ItemRef"] = ItemRef
                                    QuerySet["VendorRef"] = QuerySet4
                                    QuerySet["Line"].append(QuerySet1)

                                    # QuerySet2['ClassRef'] = QuerySet5
                                    # for j2 in range(0, len(QBO_class)):
                                    #     if final_bill[i]['Line'][j]['Job'] == QBO_class[j2]['Name']:
                                    #         QuerySet5['value'] = QBO_class[j2]['Id']
                                    #         QuerySet5['name'] = QBO_class[j2]['Name']
                                else:
                                    pass

                            a = []
                            for p2 in range(0, len(TxnTaxDetail["TaxLine"])):
                                if TxnTaxDetail["TaxLine"][p2] in a:
                                    pass
                                else:
                                    a.append(TxnTaxDetail["TaxLine"][p2])

                            TxnTaxDetail["TaxLine"] = a

                            # for k3 in range(0,len(a)):
                            #     if a[k3]['TaxLineDetail']['TaxRateRef']['value'] == '25':
                            #         a.pop(k3)

                            # QuerySet["Line"].append(QuerySet1)

                            payload = json.dumps(QuerySet)
                            bill_date = final_bill[i]["TxnDate"][0:10]
                            bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")
                            if start_date1 is not None and end_date1 is not None:
                                if (bill_date1 >= start_date1) and (
                                        bill_date1 <= end_date1
                                ):
                                    response = requests.request(
                                        "POST", url1, headers=headers, data=payload
                                    )
                                    if response.status_code == 401:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   (
                                                       res1["fault"]["error"][0]["message"]
                                                   ).split(";")[0]
                                               ).split("=")[
                                                   1
                                               ] + ": Please Update the Access Token"
                                        add_job_status(job_id, res2, "error")
                                    elif response.status_code == 400:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   res1["Fault"]["Error"][0]["Detail"]
                                               ) + ": {}".format(final_bill[i]["Inv_No"])
                                        add_job_status(job_id, res2, "error")
                                else:
                                    pass
                            else:
                                response = requests.request(
                                    "POST", url1, headers=headers, data=payload
                                )
                                if response.status_code == 401:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               (res1["fault"]["error"][0]["message"]).split(
                                                   ";"
                                               )[0]
                                           ).split("=")[1] + ": Please Update the Access Token"
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               res1["Fault"]["Error"][0]["Detail"]
                                           ) + ": {}".format(final_bill[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                    else:
                        if (len(final_bill[i]["Line"]) == 1) and (
                                "ItemCode" in final_bill[i]["Line"][0]
                        ):
                            QuerySet = {"Line": []}
                            QuerySet1 = {}
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
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
                            ItemRef = {}
                            QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                            taxrate1 = 0
                            for j1 in range(0, len(QBO_item)):
                                for j2 in range(0, len(xero_items)):
                                    if ("ItemCode" in final_bill[i]["Line"][0]) and (
                                            "AccountCode" in final_bill[i]["Line"][0]
                                    ):
                                        if (
                                                final_bill[i]["Line"][0]["ItemCode"]
                                                + "-"
                                                + final_bill[i]["Line"][0]["AccountCode"]
                                                == QBO_item[j1]["Name"]
                                        ):
                                            ItemRef["value"] = QBO_item[j1]["Id"]

                                    elif ("ItemCode" in final_bill[i]["Line"][0]) and (
                                            ("AccountCode" not in final_bill[i]["Line"][0])
                                    ):
                                        if (
                                                final_bill[i]["Line"][j]["ItemCode"]
                                                == xero_items[j2]["Code"]
                                        ):
                                            if (
                                                    xero_items[j2]["Name"]
                                                    == QBO_item[j1]["Name"]
                                            ):
                                                ItemRef["value"] = QBO_item[j1]["Id"]

                            QuerySet2["Qty"] = final_bill[i]["Line"][0]["Quantity"]
                            QuerySet2["UnitPrice"] = final_bill[i]["Line"][0][
                                "UnitAmount"
                            ]

                            QuerySet2["ItemRef"] = ItemRef

                            for k1 in range(0, len(QBO_tax)):
                                if (
                                        (
                                                final_bill[i]["Line"][0]["TaxType"]
                                                == "BASEXCLUDED"
                                        )
                                        or (final_bill[i]["Line"][0]["TaxType"] == None)
                                        or (final_bill[i]["Line"][0]["TaxType"] == "NONE")
                                ):
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "Input tax (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
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

                                elif final_bill[i]["Line"][0]["TaxType"] == "INPUT":
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["TotalTax"]
                                            )

                                elif final_bill[i]["Line"][0]["TaxType"] == "OUTPUT":
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
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
                                                final_bill[i]["TotalTax"]
                                            )

                                elif (
                                        final_bill[i]["Line"][0]["TaxType"]
                                        == "EXEMPTEXPENSES"
                                        or final_bill[i]["Line"][0]["TaxType"]
                                        == "EXEMPTOUTPUT"
                                ):
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST-free (purchases)"
                                                in QBO_tax[k1]["taxrate_name"]
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

                                else:
                                    pass

                            if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                QuerySet1["Amount"] = abs(
                                    final_bill[i]["TotalAmount"]
                                    / (100 + taxrate1)
                                    * 100
                                )
                                TaxLineDetail["NetAmountTaxable"] = abs(
                                    final_bill[i]["TotalAmount"]
                                    - final_bill[i]["TotalTax"]
                                )
                            else:
                                QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                QuerySet1["Amount"] = abs(
                                    final_bill[i]["Line"][0]["LineAmount"]
                                )
                                TaxLineDetail["NetAmountTaxable"] = abs(
                                    final_bill[i]["TotalAmount"]
                                    - final_bill[i]["TotalTax"]
                                )

                            QuerySet2["TaxCodeRef"] = TaxCodeRef

                            if "supplier_invoice_no" in final_bill[i]:
                                if (
                                        final_bill[i]["supplier_invoice_no"] == None
                                        or final_bill[i]["supplier_invoice_no"] == ""
                                ):
                                    QuerySet["DocNumber"] = final_bill[i]["Inv_No"]
                                elif (
                                        final_bill[i]["supplier_invoice_no"] != ""
                                        or final_bill[i]["supplier_invoice_no"] is not None
                                ):
                                    QuerySet["DocNumber"] = (
                                            final_bill[i]["Inv_No"]
                                            + "-"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                            else:
                                QuerySet["DocNumber"] = final_bill[i]["Inv_No"]
                            if "Comment" in final_bill[i]:
                                QuerySet["PrivateNote"] = final_bill[i]["Comment"]

                            QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                            if "Description" in final_bill[i]["Line"][0]:
                                QuerySet1["Description"] = final_bill[i]["Line"][0][
                                    "Description"
                                ]
                            else:
                                QuerySet1["Description"] = None
                            QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                            QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2

                            # for j1 in range(0, len(QBO_coa)):
                            #     for j2 in range(0, len(xero_coa1)):
                            #         if 'Code' in xero_coa1[j2]:
                            #             if 'AccountCode' in final_bill[i]['Line'][0]:
                            #                 if final_bill[i]['Line'][0]['AccountCode'] == xero_coa1[j2]["Code"]:
                            #                     if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                            #                         QuerySet3['value'] = QBO_coa[j1]["Id"]

                            # QuerySet2['AccountRef'] = QuerySet3

                            for j3 in range(0, len(QBO_supplier)):
                                if QBO_supplier[j3]["DisplayName"].startswith(
                                        final_bill[i]["ContactName"]
                                ) and QBO_supplier[j3]["DisplayName"].endswith(" - S"):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                elif (
                                        final_bill[i]["ContactName"]
                                        == QBO_supplier[j3]["DisplayName"]
                                ):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                else:
                                    pass
                            QuerySet["VendorRef"] = QuerySet4

                            # QuerySet2['ClassRef'] = QuerySet5

                            # for j2 in range(0, len(QBO_class)):
                            #     if final_bill[i]['Line'][0]['Job'] == QBO_class[j2]['Name']:
                            #         QuerySet5['value'] = QBO_class[j2]['Id']
                            #         QuerySet5['name'] = QBO_class[j2]['Name']

                            QuerySet["Line"].append(QuerySet1)

                            vendor_credit_arr.append(QuerySet)
                            payload = json.dumps(QuerySet)
                            bill_date = final_bill[i]["TxnDate"][0:10]
                            bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")

                            if start_date1 is not None and end_date1 is not None:
                                if (bill_date1 >= start_date1) and (
                                        bill_date1 <= end_date1
                                ):
                                    response = requests.request(
                                        "POST", url2, headers=headers, data=payload
                                    )

                                    if response.status_code == 401:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   (
                                                       res1["fault"]["error"][0]["message"]
                                                   ).split(";")[0]
                                               ).split("=")[
                                                   1
                                               ] + ": Please Update the Access Token"
                                        add_job_status(job_id, res2, "error")
                                    elif response.status_code == 400:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   res1["Fault"]["Error"][0]["Detail"]
                                               ) + ": {}".format(final_bill[i]["Inv_No"])
                                        add_job_status(job_id, res2, "error")

                                else:
                                    pass
                            else:
                                response = requests.request(
                                    "POST", url2, headers=headers, data=payload
                                )

                                if response.status_code == 401:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               (res1["fault"]["error"][0]["message"]).split(
                                                   ";"
                                               )[0]
                                           ).split("=")[1] + ": Please Update the Access Token"
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               res1["Fault"]["Error"][0]["Detail"]
                                           ) + ": {}".format(final_bill[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                        else:
                            QuerySet = {"Line": []}
                            TxnTaxDetail = {"TaxLine": []}

                            for j in range(0, len(final_bill[i]["Line"])):
                                QuerySet1 = {}
                                QuerySet2 = {}
                                QuerySet3 = {}
                                QuerySet4 = {}
                                QuerySet5 = {}
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
                                ItemRef = {}
                                QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])
                                taxrate1 = 0

                                for j1 in range(0, len(QBO_item)):
                                    for j2 in range(0, len(xero_items)):
                                        if (
                                                "ItemCode" in final_bill[i]["Line"][j]
                                        ) and (
                                                "AccountCode" in final_bill[i]["Line"][j]
                                        ):
                                            if (
                                                    final_bill[i]["Line"][j]["ItemCode"]
                                                    + "-"
                                                    + final_bill[i]["Line"][j][
                                                "AccountCode"
                                            ]
                                                    == QBO_item[j1]["Name"]
                                            ):
                                                ItemRef["value"] = QBO_item[j1]["Id"]

                                        elif (
                                                "ItemCode" in final_bill[i]["Line"][j]
                                        ) and (
                                                (
                                                        "AccountCode"
                                                        not in final_bill[i]["Line"][j]
                                                )
                                        ):
                                            if (
                                                    final_bill[i]["Line"][j]["ItemCode"]
                                                    == xero_items[j2]["Code"]
                                            ):
                                                if (
                                                        xero_items[j2]["Name"]
                                                        == QBO_item[j1]["Name"]
                                                ):
                                                    ItemRef["value"] = QBO_item[j1][
                                                        "Id"
                                                    ]

                                QuerySet2["Qty"] = final_bill[i]["Line"][j]["Quantity"]
                                QuerySet2["UnitPrice"] = final_bill[i]["Line"][j][
                                    "UnitAmount"
                                ]

                                QuerySet2["ItemRef"] = ItemRef

                                for k1 in range(0, len(QBO_tax)):
                                    if (
                                            (
                                                    final_bill[i]["Line"][j]["TaxType"]
                                                    == "BASEXCLUDED"
                                            )
                                            or (final_bill[i]["Line"][j]["TaxType"] == None)
                                            or (
                                            final_bill[i]["Line"][j]["TaxType"]
                                            == "NONE"
                                    )
                                    ):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "Input tax (purchases)"
                                                    in QBO_tax[k1]["taxrate_name"]
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
                                                Tax["Amount"] = abs(
                                                    final_bill[i]["TotalTax"]
                                                )

                                    elif final_bill[i]["Line"][j]["TaxType"] == "INPUT":
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST (purchases)"
                                                    in QBO_tax[k1]["taxrate_name"]
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
                                            final_bill[i]["Line"][j]["TaxType"] == "OUTPUT"
                                    ):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST (purchases)"
                                                    in QBO_tax[k1]["taxrate_name"]
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
                                            final_bill[i]["Line"][j]["TaxType"]
                                            == "EXEMPTEXPENSES"
                                            or final_bill[i]["Line"][j]["TaxType"]
                                            == "EXEMPTOUTPUT"
                                    ):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST-free (purchases)"
                                                    in QBO_tax[k1]["taxrate_name"]
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
                                                Tax["Amount"] = (
                                                        abs(final_bill[i]["TotalTax"])
                                                        * taxrate1
                                                )

                                    else:
                                        pass

                                if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                    QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                    QuerySet1["Amount"] = abs(
                                        final_bill[i]["Line"][j]["LineAmount"]
                                    )
                                    TaxLineDetail["NetAmountTaxable"] = (
                                            abs(taxrate1 * final_bill[i]["TotalTax"])
                                            / (100 + taxrate1)
                                            * 100
                                    )

                                else:
                                    QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                    QuerySet1["Amount"] = abs(
                                        final_bill[i]["Line"][j]["LineAmount"]
                                    )
                                    TaxLineDetail["NetAmountTaxable"] = abs(
                                        taxrate1 * final_bill[i]["TotalTax"]
                                    )

                                if "supplier_invoice_no" in final_bill[i]:
                                    if (
                                            final_bill[i]["supplier_invoice_no"] == None
                                            or final_bill[i]["supplier_invoice_no"] == ""
                                    ):
                                        QuerySet["DocNumber"] = final_bill[i]["Inv_No"]
                                    elif (
                                            final_bill[i]["supplier_invoice_no"] != ""
                                            or final_bill[i]["supplier_invoice_no"]
                                            is not None
                                    ):
                                        QuerySet["DocNumber"] = (
                                                final_bill[i]["Inv_No"]
                                                + "-"
                                                + final_bill[i]["supplier_invoice_no"]
                                        )
                                else:
                                    QuerySet["DocNumber"] = final_bill[i]["Inv_No"]

                                if "Comment" in final_bill[i]:
                                    QuerySet["PrivateNote"] = final_bill[i]["Comment"]

                                QuerySet2["TaxCodeRef"] = TaxCodeRef
                                QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                                if "Description" in final_bill[i]["Line"][j]:
                                    QuerySet1["Description"] = final_bill[i]["Line"][j][
                                        "Description"
                                    ]
                                QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                                QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2

                                # for j1 in range(0, len(QBO_coa)):
                                #     for j2 in range(0, len(xero_coa1)):
                                #         if 'Code' in xero_coa1[j2]:
                                #             if 'AccountCode' in final_bill[i]['Line'][j]:
                                #                 if final_bill[i]['Line'][j]['AccountCode'] == xero_coa1[j2]["Code"]:
                                #                     if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                                #                         QuerySet3['value'] = QBO_coa[j1]["Id"]

                                # QuerySet2['AccountRef'] = QuerySet3

                                for j3 in range(0, len(QBO_supplier)):
                                    if QBO_supplier[j3]["DisplayName"].startswith(
                                            final_bill[i]["ContactName"]
                                    ) and QBO_supplier[j3]["DisplayName"].endswith(
                                        " - S"
                                    ):
                                        QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                    elif (
                                            final_bill[i]["ContactName"]
                                            == QBO_supplier[j3]["DisplayName"]
                                    ):
                                        QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                    else:
                                        pass
                                QuerySet["VendorRef"] = QuerySet4

                                # QuerySet2['ClassRef'] = QuerySet5

                                # for j2 in range(0, len(QBO_class)):
                                #     if final_bill[i]['Line'][j]['Job'] == QBO_class[j2]['Name']:
                                #         QuerySet5['value'] = QBO_class[j2]['Id']
                                #         QuerySet5['name'] = QBO_class[j2]['Name']

                            QuerySet["Line"].append(QuerySet1)

                            vendor_credit_arr.append(QuerySet)
                            payload = json.dumps(QuerySet)
                            bill_date = final_bill[i]["TxnDate"][0:10]
                            bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")

                            if start_date1 is not None and end_date1 is not None:
                                if (bill_date1 >= start_date1) and (
                                        bill_date1 <= end_date1
                                ):
                                    response = requests.request(
                                        "POST", url2, headers=headers, data=payload
                                    )
                                    if response.status_code == 401:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   (
                                                       res1["fault"]["error"][0]["message"]
                                                   ).split(";")[0]
                                               ).split("=")[
                                                   1
                                               ] + ": Please Update the Access Token"
                                        add_job_status(job_id, res2, "error")
                                    elif response.status_code == 400:
                                        res1 = json.loads(response.text)
                                        res2 = (
                                                   res1["Fault"]["Error"][0]["Detail"]
                                               ) + ": {}".format(final_bill[i]["Inv_No"])
                                        add_job_status(job_id, res2, "error")
                                else:
                                    pass

                            else:
                                response = requests.request(
                                    "POST", url2, headers=headers, data=payload
                                )
                                if response.status_code == 401:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               (res1["fault"]["error"][0]["message"]).split(
                                                   ";"
                                               )[0]
                                           ).split("=")[1] + ": Please Update the Access Token"
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               res1["Fault"]["Error"][0]["Detail"]
                                           ) + ": {}".format(final_bill[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                else:
                    pass

            else:
                pass
                # print("This is Deleted or Voided Bill")

    except Exception as ex:
        logging.error(ex, exc_info=True)