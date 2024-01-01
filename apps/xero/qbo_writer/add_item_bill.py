import json
import logging
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job

logger = logging.getLogger(__name__)


def add_xero_item_bill(job_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_item_bill -> add_xero_item_bill")

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
        for p5 in QBO_Tax:
            QBO_tax.append(p5)

        Xero_Items = db["xero_items"].find({"job_id": job_id})
        xero_items = []
        for p5 in Xero_Items:
            xero_items.append(p5)

        XERO_COA = db["xero_coa"].find({"job_id": job_id})
        xero_coa = []
        for p7 in XERO_COA:
            xero_coa.append(p7)

        bill_arr = []
        vendor_credit_arr = []

        duplicate = ["B0011"]
        for i in range(0, len(final_bill)):
            # if 'Line' in final_bill[i]:
            if final_bill[i]["Inv_No"] in duplicate:
                if final_bill[i]["TotalAmount"] > 0:
                    if len(final_bill[i]["Line"]) == 1:
                        if "ItemCode" in final_bill[i]["Line"][0]:
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
                            AccountRef = {}
                            QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                            taxrate1 = 0
                            if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                for k1 in range(0, len(QBO_tax)):
                                    if (
                                            final_bill[i]["Line"][0]["TaxType"]
                                            == "BASEXCLUDED"
                                    ) or (final_bill[i]["Line"][0]["TaxType"] == None):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if "BAS-W1" in QBO_tax[k1]["taxrate_name"]:
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
                                                    final_bill[i]["TotalAmount"]
                                                    - final_bill[i]["TotalTax"]
                                                )
                                            else:
                                                pass

                                        elif (
                                                final_bill[i]["Line"][0]["TaxType"]
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

                                        elif (
                                                final_bill[i]["Line"][0]["TaxType"]
                                                == "EXEMPTEXPENSES"
                                        ):
                                            if (
                                                    "GST-free (purchases)"
                                                    == QBO_tax[k1]["taxcode_name"]
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

                                QuerySet1["Amount"] = abs(
                                    round(
                                        final_bill[i]["Line"][0]["UnitAmount"]
                                        * final_bill[i]["Line"][0]["Quantity"]
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )
                                )
                                QuerySet2["UnitPrice"] = round(
                                    abs(
                                        final_bill[i]["Line"][0]["UnitAmount"]
                                        / (100 + taxrate1)
                                        * 100
                                    ),
                                    2,
                                )
                            else:
                                QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                for k1 in range(0, len(QBO_tax)):
                                    if (
                                            final_bill[i]["Line"][0]["TaxType"]
                                            == "BASEXCLUDED"
                                    ) or (final_bill[i]["Line"][0]["TaxType"] == None):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if "BAS-W1" in QBO_tax[k1]["taxrate_name"]:
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
                                                    final_bill[i]["TotalAmount"]
                                                    - final_bill[i]["TotalTax"]
                                                )
                                            else:
                                                pass

                                        elif (
                                                final_bill[i]["Line"][0]["TaxType"]
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

                                        elif (
                                                final_bill[i]["Line"][0]["TaxType"]
                                                == "EXEMPTEXPENSES"
                                        ):
                                            if (
                                                    "GST-free (purchases)"
                                                    == QBO_tax[k1]["taxcode_name"]
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

                                QuerySet2["UnitPrice"] = final_bill[i]["Line"][0][
                                    "UnitAmount"
                                ]

                            if "supplier_invoice_no" in final_bill[i]:
                                if (
                                        final_bill[i]["supplier_invoice_no"] != ""
                                        or final_bill[i]["supplier_invoice_no"] is not None
                                ):
                                    QuerySet["DocNumber"] = (
                                            final_bill[i]["supplier_invoice_no"]
                                            + "-"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                                else:
                                    QuerySet["DocNumber"] = final_bill[i]["Inv_No"]
                            else:
                                QuerySet["DocNumber"] = final_bill[i]["Inv_No"]

                            QuerySet2["TaxCodeRef"] = TaxCodeRef

                            if "Description" in final_bill[i]["Line"][0]:
                                QuerySet1["Description"] = final_bill[i]["Line"][0][
                                    "Description"
                                ]
                            QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                            QuerySet["DueDate"] = final_bill[i]["DueDate"]
                            QuerySet1["Amount"] = final_bill[i]["Line"][0]["LineAmount"]
                            QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                            QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                            QuerySet2["Qty"] = final_bill[i]["Line"][0]["Quantity"]
                            QuerySet2["ItemRef"] = QuerySet3

                            for j1 in range(0, len(QBO_item)):
                                for j2 in range(0, len(xero_items)):
                                    if "ItemCode" in final_bill[i]["Line"][0]:
                                        if (
                                                final_bill[i]["Line"][0]["ItemCode"]
                                                == xero_items[j2]["Code"]
                                        ):
                                            if (
                                                    xero_items[j2]["Name"]
                                                    == QBO_item[j1]["Name"]
                                            ):
                                                QuerySet3["value"] = QBO_item[j1]["Id"]

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
                            QuerySet2["ClassRef"] = QuerySet5

                            # for j2 in range(0, len(QBO_class)):
                            #     if 'Job' in final_bill[i]['Line'][0]:
                            #         if final_bill[i]['Line'][0]['Job'] == QBO_class[j2]['Name']:
                            #             QuerySet5['value'] = QBO_class[j2]['Id']
                            #             QuerySet5['name'] = QBO_class[j2]['Name']

                            if final_bill[i]["Line"][0]["Discount"] != 0:
                                discount2["Qty"] = "1"
                                discount2["UnitPrice"] = (
                                        -(
                                                final_bill[i]["Line"][0]["UnitAmount"]
                                                * final_bill[i]["Line"][0]["Quantity"]
                                                / (100 + taxrate1)
                                                * 100
                                        )
                                        * final_bill[i]["Line"][0]["Discount"]
                                        / 100
                                )
                                discount2["TaxCodeRef"] = TaxCodeRef
                                discount2["ItemRef"] = QuerySet3
                                discount2["ClassRef"] = QuerySet5
                                discount1["Description"] = "Discount Given"
                                discount1["DetailType"] = "ItemBasedExpenseLineDetail"
                                discount1["Amount"] = (
                                        -(
                                                final_bill[i]["Line"][0]["UnitAmount"]
                                                * final_bill[i]["Line"][0]["Quantity"]
                                                / (100 + taxrate1)
                                                * 100
                                        )
                                        * final_bill[i]["Line"][0]["Discount"]
                                        / 100
                                )
                                discount1["ItemBasedExpenseLineDetail"] = discount2

                            if discount1 != {}:
                                QuerySet["Line"].append(discount1)

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
                                               ) + "{}".format(final_bill[i]["Inv_No"])
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
                                           ) + "{}".format(final_bill[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                    else:
                        QuerySet = {"Line": []}
                        TxnTaxDetail = {"TaxLine": []}

                        for j in range(0, len(final_bill[i]["Line"])):
                            if "ItemCode" in final_bill[i]["Line"][j]:
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
                                AccountRef = {}
                                QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                                if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                    QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                    taxrate1 = 0
                                    for k1 in range(0, len(QBO_tax)):
                                        if (
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "BASEXCLUDED"
                                        ) or (
                                                final_bill[i]["Line"][j]["TaxType"] == None
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "BAS-W1"
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
                                                    ] = abs(
                                                        QBO_tax[k1]["Rate"]
                                                        * final_bill[i]["TotalTax"]
                                                    )
                                                    Tax["Amount"] = abs(
                                                        final_bill[i]["TotalTax"]
                                                        * taxrate1
                                                    )

                                        elif (
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "CAPEXINPUT"
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
                                                        * taxrate1
                                                    )

                                        elif (
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "OUTPUT"
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "GST (sales)"
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
                                                        * taxrate1
                                                    )

                                        elif (
                                                final_bill[i]["Line"][j]["TaxType"]
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
                                                        * taxrate1
                                                    )

                                        else:
                                            pass

                                    QuerySet1["Amount"] = (
                                            abs(
                                                final_bill[i]["Line"][j]["Quantity"]
                                                * final_bill[i]["Line"][j]["UnitAmount"]
                                            )
                                            / (100 + taxrate1)
                                            * 100
                                    )
                                    QuerySet2["UnitPrice"] = abs(
                                        final_bill[i]["Line"][j]["UnitAmount"]
                                        / (100 + taxrate1)
                                        * 100
                                    )

                                else:
                                    QuerySet["GlobalTaxCalculation"] = "TaxExcluded"

                                if "supplier_invoice_no" in final_bill[i]:
                                    if (
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
                                else:
                                    QuerySet["DocNumber"] = final_bill[i]["Inv_No"]

                                QuerySet2["TaxCodeRef"] = TaxCodeRef

                                QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                                QuerySet["DueDate"] = final_bill[i]["DueDate"]
                                if "Description" in final_bill[i]["Line"][j]:
                                    QuerySet1["Description"] = final_bill[i]["Line"][j][
                                        "Description"
                                    ]
                                QuerySet1["Amount"] = final_bill[i]["Line"][j][
                                    "LineAmount"
                                ]
                                QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                                QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                                QuerySet2["Qty"] = final_bill[i]["Line"][j]["Quantity"]

                                QuerySet2["ItemRef"] = QuerySet3
                                for j1 in range(0, len(QBO_item)):
                                    for j2 in range(0, len(xero_items)):
                                        if "ItemCode" in final_bill[i]["Line"][j]:
                                            if (
                                                    final_bill[i]["Line"][j]["ItemCode"]
                                                    == xero_items[j2]["Code"]
                                            ):
                                                if (
                                                        xero_items[j2]["Name"]
                                                        == QBO_item[j1]["Name"]
                                                ):
                                                    QuerySet3["value"] = QBO_item[j1][
                                                        "Id"
                                                    ]

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

                                if final_bill[i]["Line"][j]["Discount"] != 0:
                                    discount2["Qty"] = "1"
                                    discount2["UnitPrice"] = (
                                            -(
                                                    (
                                                            final_bill[i]["Line"][j]["Quantity"]
                                                            * final_bill[i]["Line"][j]["UnitAmount"]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            )
                                            * final_bill[i]["Line"][j]["Discount"]
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
                                                            final_bill[i]["Line"][j]["Quantity"]
                                                            * final_bill[i]["Line"][j]["UnitAmount"]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            )
                                            * final_bill[i]["Line"][j]["Discount"]
                                            / 100
                                    )
                                    discount1["ItemBasedExpenseLineDetail"] = discount2

                                if discount1 != {} or discount1 is not None:
                                    QuerySet["Line"].append(discount1)
                                else:
                                    pass

                                QuerySet["Line"].append(QuerySet1)

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
                                               (res1["fault"]["error"][0]["message"]).split(
                                                   ";"
                                               )[0]
                                           ).split("=")[1] + ": Please Update the Access Token"
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               res1["Fault"]["Error"][0]["Detail"]
                                           ) + ":{}".format(final_bill[i]["Inv_No"])
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
                                           (res1["fault"]["error"][0]["message"]).split(";")[0]
                                       ).split("=")[1] + ": Please Update the Access Token"
                                add_job_status(job_id, res2, "error")
                            elif response.status_code == 400:
                                res1 = json.loads(response.text)
                                res2 = (
                                           res1["Fault"]["Error"][0]["Detail"]
                                       ) + ":{}".format(final_bill[i]["Inv_No"])
                                add_job_status(job_id, res2, "error")

                else:
                    if len(final_bill[i]["Line"]) == 1:
                        if "ItemCode" in final_bill[i]["Line"][0]:
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
                            AccountRef = {}
                            QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                            taxrate1 = 0
                            if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                for k1 in range(0, len(QBO_tax)):
                                    if (
                                            final_bill[i]["Line"][0]["TaxType"]
                                            == "BASEXCLUDED"
                                    ) or (final_bill[i]["Line"][0]["TaxType"] == None):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if "BAS-W1" in QBO_tax[k1]["taxrate_name"]:
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
                                        else:
                                            pass

                                    elif final_bill[i]["Line"][0]["TaxType"] == "INPUT":
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

                                    elif (
                                            final_bill[i]["Line"][j]["TaxType"]
                                            == "EXEMPTEXPENSES"
                                    ):
                                        if (
                                                "GST-free (purchases)"
                                                == QBO_tax[k1]["taxcode_name"]
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

                                QuerySet1["Amount"] = round(
                                    abs(
                                        final_bill[i]["Line"][0]["Quantity"]
                                        * final_bill[i]["Line"][0]["UnitAmount"]
                                    )
                                    / (100 + taxrate1)
                                    * 100,
                                    2,
                                )
                                QuerySet2["UnitPrice"] = round(
                                    abs(
                                        final_bill[i]["Line"][0]["UnitAmount"]
                                        / (100 + taxrate1)
                                        * 100
                                    ),
                                    3,
                                )

                            if "supplier_invoice_no" in final_bill[i]:
                                if (
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
                            else:
                                QuerySet["DocNumber"] = final_bill[i]["Inv_No"]

                            QuerySet2["TaxCodeRef"] = TaxCodeRef
                            QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                            QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                            if "Description" in final_bill[i]["Line"][0]:
                                QuerySet1["Description"] = final_bill[i]["Line"][0][
                                    "Description"
                                ]
                            QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                            QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                            QuerySet2["Qty"] = abs(final_bill[i]["Line"][0]["Quantity"])
                            QuerySet2["ItemRef"] = QuerySet3

                            for j1 in range(0, len(QBO_item)):
                                if "ItemCode" in final_bill[i]["Line"][0]:
                                    for j2 in range(0, len(xero_items)):
                                        if (
                                                final_bill[i]["Line"][0]["ItemCode"]
                                                == xero_items[j2]["Code"]
                                        ):
                                            if (
                                                    xero_items[j2]["Name"]
                                                    == QBO_item[j1]["Name"]
                                            ):
                                                QuerySet3["value"] = QBO_item[j1]["Id"]

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
                            QuerySet2["ClassRef"] = QuerySet5

                            # for j2 in range(0, len(QBO_class)):
                            #     if final_bill[i]['Line'][0]['Job'] == QBO_class[j2]['Name']:
                            #         QuerySet5['value'] = QBO_class[j2]['Id']
                            #         QuerySet5['name'] = QBO_class[j2]['Name']

                            if final_bill[i]["Line"][0]["Discount"] != 0:
                                discount2["Qty"] = "1"
                                discount2["UnitPrice"] = (
                                        -round(
                                            abs(
                                                final_bill[i]["Line"][0]["Quantity"]
                                                * final_bill[i]["Line"][0]["UnitAmount"]
                                            )
                                            / (100 + taxrate1)
                                            * 100,
                                            2,
                                        )
                                        * final_bill[i]["Line"][0]["Discount"]
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
                                                final_bill[i]["Line"][0]["Quantity"]
                                                * final_bill[i]["Line"][0]["UnitAmount"]
                                            )
                                            / (100 + taxrate1)
                                            * 100,
                                            2,
                                        )
                                        * final_bill[i]["Line"][0]["Discount"]
                                        / 100
                                )
                                discount1["ItemBasedExpenseLineDetail"] = discount2

                            if discount1 != {}:
                                QuerySet["Line"].append(discount1)

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
                                               ) + ":{}".format(final_bill[i]["Inv_No"])
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
                                           ) + ":{}".format(final_bill[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                    else:
                        QuerySet = {"Line": []}
                        TxnTaxDetail = {"TaxLine": []}

                        taxrate1 = 0
                        for j in range(0, len(final_bill[i]["Line"])):
                            if "ItemCode" in final_bill[i]["Line"][j]:
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
                                TxnTaxDetail["TotalTax"] = abs(
                                    final_bill[i]["TotalTax"]
                                )
                                TaxLineDetail["TaxRateRef"] = TaxRate
                                TaxLineDetail["PercentBased"] = True
                                TxnTaxDetail["TaxLine"].append(Tax)
                                QuerySet["TxnTaxDetail"] = TxnTaxDetail
                                TaxCodeRef = {}
                                AccountRef = {}
                                QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                                if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                    QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                    for k1 in range(0, len(QBO_tax)):
                                        if (
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "BASEXCLUDED"
                                        ) or (
                                                final_bill[i]["Line"][j]["TaxType"] == None
                                        ):
                                            if "taxrate_name" in QBO_tax[k1]:
                                                if (
                                                        "BAS-W1"
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

                                        elif (
                                                final_bill[i]["Line"][j]["TaxType"]
                                                == "EXEMPTEXPENSES"
                                        ):
                                            if (
                                                    "GST-free (purchases)"
                                                    == QBO_tax[k1]["taxcode_name"]
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
                                                    final_bill[i]["Line"][j]["Quantity"]
                                                    * final_bill[i]["Line"][j][
                                                        "UnitAmount"
                                                    ],
                                                    2,
                                                )
                                                / (100 + taxrate1)
                                                * 100
                                        )
                                    )
                                    QuerySet2["UnitPrice"] = abs(
                                        final_bill[i]["Line"][j]["UnitAmount"]
                                        / (100 + taxrate1)
                                        * 100
                                    )

                                else:
                                    QuerySet["GlobalTaxCalculation"] = "TaxExcluded"

                                if "supplier_invoice_no" in final_bill[i]:
                                    if (
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
                                else:
                                    QuerySet["DocNumber"] = final_bill[i]["Inv_No"]

                                QuerySet2["TaxCodeRef"] = TaxCodeRef
                                QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                                QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                                if "Description" in final_bill[i]["Line"][j]:
                                    QuerySet1["Description"] = final_bill[i]["Line"][j][
                                        "Description"
                                    ]
                                QuerySet1["DetailType"] = "ItemBasedExpenseLineDetail"
                                QuerySet1["ItemBasedExpenseLineDetail"] = QuerySet2
                                QuerySet2["Qty"] = abs(
                                    final_bill[i]["Line"][j]["Quantity"]
                                )
                                QuerySet2["ItemRef"] = QuerySet3

                                for j1 in range(0, len(QBO_item)):
                                    for j2 in range(0, len(xero_items)):
                                        if "ItemCode" in final_bill[i]["Line"][j]:
                                            if (
                                                    final_bill[i]["Line"][j]["ItemCode"]
                                                    == xero_items[j2]["Code"]
                                            ):
                                                if (
                                                        xero_items[j2]["Name"]
                                                        == QBO_item[j1]["Name"]
                                                ):
                                                    QuerySet3["value"] = QBO_item[j1][
                                                        "Id"
                                                    ]

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

                                QuerySet2["ClassRef"] = QuerySet5

                                # for j2 in range(0, len(QBO_class)):
                                #     if final_bill[i]['Line'][j]['Job'] == QBO_class[j2]['Name']:
                                #         QuerySet5['value'] = QBO_class[j2]['Id']
                                #         QuerySet5['name'] = QBO_class[j2]['Name']

                                if final_bill[i]["Line"][j]["Discount"] != 0:
                                    discount2["Qty"] = "1"
                                    discount2["UnitPrice"] = (
                                            (
                                                round(
                                                    (
                                                            final_bill[i]["Line"][j]["Quantity"]
                                                            * final_bill[i]["Line"][j][
                                                                "UnitAmount"
                                                            ]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100,
                                                    2,
                                                )
                                            )
                                            * final_bill[i]["Line"][j]["Discount"]
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
                                            (
                                                round(
                                                    (
                                                            final_bill[i]["Line"][j]["Quantity"]
                                                            * final_bill[i]["Line"][j][
                                                                "UnitAmount"
                                                            ]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100,
                                                    2,
                                                )
                                            )
                                            * final_bill[i]["Line"][j]["Discount"]
                                            / 100
                                    )
                                    discount1["ItemBasedExpenseLineDetail"] = discount2

                                if discount1 != {} or discount1 is not None:
                                    QuerySet["Line"].insert(j, discount1)
                                else:
                                    pass
                                QuerySet["Line"].insert(j, QuerySet1)

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
                                               (res1["fault"]["error"][0]["message"]).split(
                                                   ";"
                                               )[0]
                                           ).split("=")[1] + ": Please Update the Access Token"
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = (
                                               res1["Fault"]["Error"][0]["Detail"]
                                           ) + ":{}".format(final_bill[i]["Inv_No"])
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
                                           (res1["fault"]["error"][0]["message"]).split(";")[0]
                                       ).split("=")[1] + ": Please Update the Access Token"
                                add_job_status(job_id, res2, "error")
                            elif response.status_code == 400:
                                res1 = json.loads(response.text)
                                res2 = (
                                           res1["Fault"]["Error"][0]["Detail"]
                                       ) + ":{}".format(final_bill[i]["Inv_No"])
                                add_job_status(job_id, res2, "error")

            else:
                pass

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_item_bill -> add_xero_item_bill", ex)
