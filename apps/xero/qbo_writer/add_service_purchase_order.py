import json
import logging
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job

import logging


def add_service_xero_purchase_order(job_id):
    log_config1=log_config(job_id)
    try:
        logger.info(
            "Started executing xero -> qbowriter -> add_service_purchase_order -> add_service_xero_purchase_order")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        xero_purchase_orders = db["xero_purchase_order"].find({"job_id": job_id})
        xero_purchase_order = []
        for p1 in xero_purchase_orders:
            xero_purchase_order.append(p1)

        xero_purchase_order = xero_purchase_order

        QBO_Item = db["QBO_Item"].find({"job_id": job_id})
        QBO_item = []
        for p1 in QBO_Item:
            QBO_item.append(p1)

        QBO_Class = db["QBO_Class"].find({"job_id": job_id})
        QBO_class = []
        for p2 in QBO_Class:
            QBO_class.append(p2)

        QBO_Tax = db["QBO_Tax"].find({"job_id": job_id})
        QBO_tax = []
        for p3 in QBO_Tax:
            QBO_tax.append(p3)

        QBO_COA = db["QBO_COA"].find({"job_id": job_id})
        QBO_coa = []
        for p4 in QBO_COA:
            QBO_coa.append(p4)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id": job_id})
        QBO_supplier = []
        for p5 in QBO_Supplier:
            QBO_supplier.append(p5)

        Xero_COA = db["xero_coa"].find({"job_id": job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        for i in range(0, len(xero_purchase_order)):
            purchase_order = {"Line": []}
            VendorRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            purchase_order["TxnDate"] = xero_purchase_order[i]["Date"]
            purchase_order["DocNumber"] = xero_purchase_order[i]["Number"]
            purchase_order["TotalAmt"] = abs(xero_purchase_order[i]["TotalAmount"])
            APAccountRef = {}
            APAccountRef["name"] = "Accounts Payable (A/P)"
            APAccountRef["value"] = "92"

            subtotal = {}
            for p1 in range(0, len(QBO_supplier)):
                if "Supplier" in xero_purchase_order[i]:
                    if (
                            xero_purchase_order[i]["Supplier"]
                            == QBO_supplier[p1]["DisplayName"]
                    ):
                        VendorRef["value"] = QBO_supplier[p1]["Id"]
                        VendorRef["name"] = QBO_supplier[p1]["DisplayName"]
                    else:
                        pass

                    if "PrimaryEmailAddr" in QBO_supplier[i]:
                        BillEmail["Address"] = QBO_supplier[i]["PrimaryEmailAddr"][
                            "Address"
                        ]

            total_val = 0
            taxrate1 = 0
            line_amount = 0

            for j in range(0, len(xero_purchase_order[i]["Line"])):
                if "Acc_Name" in xero_purchase_order[i]["Line"][j]:
                    TaxLineDetail = {}
                    VendorMemo = {}
                    salesitemline = {}
                    rounding = {}
                    rounding_SalesItemLineDetail = {}
                    AccountRef = {}
                    ClassRef = {}
                    TaxCodeRef = {}
                    AccountRef = {}
                    TaxRate = {}
                    AccountBasedExpenseLineDetail = {}
                    TaxDetail = {}
                    salesitemline["DetailType"] = "AccountBasedExpenseLineDetail"
                    # salesitemline["Description"] = xero_purchase_order[i]['Line'][j]['Description']

                    # for p4 in range(0, len(QBO_class)):
                    #     if xero_purchase_order[i]['Line'][j]['Job'] is not None:
                    #         if xero_purchase_order[i]['Line'][j][
                    #                 'Job'] == QBO_class[p4]["Name"]:
                    #             ClassRef['name'] = QBO_class[p4]["Name"]
                    #             ClassRef['value'] = QBO_class[p4]["Id"]
                    #         else:
                    #             pass

                    for p5 in range(0, len(QBO_coa)):
                        if (
                                xero_purchase_order[i]["Line"][j]["Acc_Name"]
                                == QBO_coa[p5]["Name"]
                        ):
                            AccountRef["name"] = QBO_coa[p5]["Name"]
                            AccountRef["value"] = QBO_coa[p5]["Id"]
                        else:
                            pass

                    for p5 in range(0, len(QBO_coa)):
                        for p51 in range(0, len(xero_coa)):
                            if "Code" in xero_coa[p51]:
                                if (
                                        xero_purchase_order[i]["Line"][j]["Acc_Name"]
                                        == xero_coa[p51]["Code"]
                                ):
                                    if xero_coa[p51]["Name"] == QBO_coa[p5]["Name"]:
                                        AccountRef["name"] = QBO_coa[p5]["Name"]
                                        AccountRef["value"] = QBO_coa[p5]["Id"]

                    # AccountRef['name'] = 'Sales Of Product Income'
                    # AccountRef['value'] = '81'

                    for p6 in range(0, len(QBO_tax)):
                        if (
                                xero_purchase_order[i]["Line"][j]["taxcode"]
                                == "BASEXCLUDED"
                        ):
                            if "taxrate_name" in QBO_tax[p6]:
                                if "N-T (Purchases)" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val = (
                                            total_val
                                            + xero_purchase_order[i]["Line"][j]["Total"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif xero_purchase_order[i]["Line"][j]["taxcode"] == "CAP":
                            if "GST on capital" in QBO_tax[p6]["taxcode_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val += (
                                        xero_purchase_order[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                        elif xero_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
                            if "taxrate_name" in QBO_tax[p6]:
                                if (
                                        "GST-free (purchases)"
                                        in QBO_tax[p6]["taxrate_name"]
                                ):
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                            xero_purchase_order[i]["Line"][j]["Total"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif xero_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                            if "N-T" in QBO_tax[p6]["taxcode_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val += (
                                        xero_purchase_order[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                        elif (
                                xero_purchase_order[i]["Line"][j]["taxcode"]
                                == QBO_tax[p6]["taxcode_name"]
                        ):
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                    xero_purchase_order[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                            )
                        else:
                            pass

                    if xero_purchase_order[i]["IsTaxInclusive"] == "Inclusive":
                        if xero_purchase_order[i]["Subtotal"] > 0:
                            salesitemline["Amount"] = round(
                                xero_purchase_order[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )

                            TxnTaxDetail["TotalTax"] = xero_purchase_order[i][
                                "TotalTax"
                            ]

                            if (
                                    xero_purchase_order[i]["Line"][j]["taxcode"]
                                    == "BASEXCLUDED"
                            ):
                                TaxDetail["Amount"] = xero_purchase_order[i]["TotalTax"]
                                TaxLineDetail["NetAmountTaxable"] = round(
                                    xero_purchase_order[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100,
                                    2,
                                )
                            elif xero_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = xero_purchase_order[
                                    i
                                ]["Line"][j]["Total"]
                            elif xero_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = xero_purchase_order[
                                    i
                                ]["Line"][j]["Total"]
                            else:
                                pass

                            purchase_order["TxnTaxDetail"] = TxnTaxDetail
                            TaxDetail["DetailType"] = "TaxLineDetail"
                            TaxDetail["TaxLineDetail"] = TaxLineDetail
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True

                            TxnTaxDetail["TaxLine"].append(TaxDetail)

                        else:
                            salesitemline["Amount"] = round(
                                xero_purchase_order[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )

                            TxnTaxDetail["TotalTax"] = -xero_purchase_order[i][
                                "TotalTax"
                            ]

                            if (
                                    xero_purchase_order[i]["Line"][j]["taxcode"]
                                    == "BASEXCLUDED"
                            ):
                                TaxDetail["Amount"] = -xero_purchase_order[i][
                                    "TotalTax"
                                ]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        TaxDetail["Amount"] * taxrate1
                                )
                            elif xero_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = -xero_purchase_order[i]["Line"][j]["Total"]
                            elif xero_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = -xero_purchase_order[i]["Line"][j]["Total"]
                            else:
                                pass

                            purchase_order["TxnTaxDetail"] = TxnTaxDetail
                            TaxDetail["DetailType"] = "TaxLineDetail"
                            TaxDetail["TaxLineDetail"] = TaxLineDetail
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True

                            TxnTaxDetail["TaxLine"].append(TaxDetail)

                        purchase_order["GlobalTaxCalculation"] = "TaxInclusive"
                        salesitemline["DetailType"] = "AccountBasedExpenseLineDetail"
                        salesitemline[
                            "AccountBasedExpenseLineDetail"
                        ] = AccountBasedExpenseLineDetail

                        AccountBasedExpenseLineDetail["AccountRef"] = AccountRef
                        AccountBasedExpenseLineDetail["ClassRef"] = ClassRef
                        AccountBasedExpenseLineDetail["TaxCodeRef"] = TaxCodeRef

                        purchase_order["BillEmail"] = BillEmail
                        purchase_order["VendorRef"] = VendorRef
                        purchase_order["APAccountRef"] = APAccountRef

                        purchase_order["Line"].append(salesitemline)

                    else:
                        if xero_purchase_order[i]["Subtotal"] > 0:
                            salesitemline["Amount"] = xero_purchase_order[i]["Line"][j][
                                "Total"
                            ]

                            TxnTaxDetail["TotalTax"] = xero_purchase_order[i][
                                "TotalTax"
                            ]

                            if taxrate1 != 0:
                                TaxDetail["Amount"] = xero_purchase_order[i]["TotalTax"]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        xero_purchase_order[i]["Subtotal"]
                                        - xero_purchase_order[i]["TotalTax"]
                                )
                            else:
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = 0

                        else:
                            salesitemline["Amount"] = xero_purchase_order[i]["Line"][j][
                                "Total"
                            ]

                            TxnTaxDetail["TotalTax"] = -xero_purchase_order[i][
                                "TotalTax"
                            ]

                            if taxrate1 != 0:
                                TaxDetail["Amount"] = xero_purchase_order[i]["TotalTax"]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        xero_purchase_order[i]["Subtotal"]
                                        - xero_purchase_order[i]["TotalTax"]
                                )
                            else:
                                if (
                                        xero_purchase_order[i]["Line"][j]["taxcode"]
                                        == "GST"
                                ):
                                    TaxDetail["Amount"] = -xero_purchase_order[i][
                                        "TotalTax"
                                    ]
                                    TaxLineDetail["NetAmountTaxable"] = (
                                            -xero_purchase_order[i]["Line"][j]["Total"]
                                            / (100 + taxrate1)
                                            * 100
                                    )
                                elif (
                                        xero_purchase_order[i]["Line"][j]["taxcode"]
                                        == "FRE"
                                ):
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail[
                                        "NetAmountTaxable"
                                    ] = -xero_purchase_order[i]["Line"][j]["Total"]
                                elif (
                                        xero_purchase_order[i]["Line"][j]["taxcode"]
                                        == "N-T"
                                ):
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail[
                                        "NetAmountTaxable"
                                    ] = -xero_purchase_order[i]["Line"][j]["Total"]

                        purchase_order["TxnTaxDetail"] = TxnTaxDetail
                        TaxDetail["DetailType"] = "TaxLineDetail"
                        TaxDetail["TaxLineDetail"] = TaxLineDetail
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True
                        salesitemline["DetailType"] = "AccountBasedExpenseLineDetail"
                        salesitemline[
                            "AccountBasedExpenseLineDetail"
                        ] = AccountBasedExpenseLineDetail

                        AccountBasedExpenseLineDetail["AccountRef"] = AccountRef
                        AccountBasedExpenseLineDetail["ClassRef"] = ClassRef
                        AccountBasedExpenseLineDetail["TaxCodeRef"] = TaxCodeRef

                        purchase_order["BillEmail"] = BillEmail
                        purchase_order["VendorRef"] = VendorRef
                        purchase_order["APAccountRef"] = APAccountRef

                        purchase_order["Line"].append(salesitemline)

                        purchase_order["GlobalTaxCalculation"] = "TaxExcluded"

                    line_amount = line_amount + salesitemline["Amount"]
                    line_amount1 = line_amount + xero_purchase_order[i]["TotalTax"]

                a = []

                for p2 in range(0, len(TxnTaxDetail["TaxLine"])):
                    if TxnTaxDetail["TaxLine"][p2] in a:
                        pass
                    else:
                        a.append(TxnTaxDetail["TaxLine"][p2])

                if len(a) >= 1:
                    if xero_purchase_order[i]["IsTaxInclusive"] == "Inclusive":
                        if line_amount1 == xero_purchase_order[i]["TotalAmount"]:
                            pass
                        else:
                            line_amount == xero_purchase_order[i][
                                "TotalAmount"
                            ] - line_amount1
                            if line_amount != 0:
                                ClassRef = {}

                                if xero_purchase_order[i]["Subtotal"] > 0:
                                    rounding["Amount"] = round(
                                        abs(xero_purchase_order[i]["TotalAmount"])
                                        - line_amount1,
                                        2,
                                    )
                                else:
                                    rounding["Amount"] = round(
                                        abs(
                                            xero_purchase_order[i]["TotalAmount"]
                                            - xero_purchase_order[i]["TotalTax"]
                                        )
                                        - line_amount,
                                        2,
                                    )

                                rounding["DetailType"] = "AccountBasedExpenseLineDetail"
                                rounding["Description"] = "Rounding"
                                rounding[
                                    "AccountBasedExpenseLineDetail"
                                ] = rounding_SalesItemLineDetail
                                rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                                rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                                rounding_SalesItemLineDetail["AccountRef"] = AccountRef
                                # TaxDetail['DetailType'] = "TaxLineDetail"
                                # TaxDetail['TaxLineDetail'] = TaxLineDetail
                                # TaxDetail['Amount'] = 0
                                # TaxLineDetail['NetAmountTaxable'] = rounding[
                                #     'Amount']
                                # TaxRate['value'] = '4'
                                # TaxLineDetail['TaxRateRef'] = TaxRate
                                # TaxLineDetail['PercentBased'] = True

                                # TxnTaxDetail['TaxLine'].append(TaxDetail)

                                # purchase_order['Line'].append(rounding)

                    else:
                        if (
                                line_amount1
                                == xero_purchase_order[i]["TotalAmount"]
                                + xero_purchase_order[i]["TotalTax"]
                        ):
                            pass
                        else:
                            line_amount == xero_purchase_order[i][
                                "TotalAmount"
                            ] - line_amount1

                            if line_amount != 0:
                                AccountRef = {}
                                ClassRef = {}
                                TaxCodeRef = {}
                                AccountRef = {}

                                if xero_purchase_order[i]["Subtotal"] > 0:
                                    rounding["Amount"] = (
                                            xero_purchase_order[i]["TotalAmount"]
                                            - line_amount1
                                    )
                                else:
                                    rounding["Amount"] = (
                                            xero_purchase_order[i]["TotalAmount"]
                                            + line_amount1
                                    )

                                rounding["DetailType"] = "AccountBasedExpenseLineDetail"
                                rounding["Description"] = "Rounding"
                                rounding[
                                    "AccountBasedExpenseLineDetail"
                                ] = rounding_SalesItemLineDetail
                                rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                                rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                                # rounding_SalesItemLineDetail[
                                #     "AccountRef"] = AccountRef
                                # TaxDetail['DetailType'] = "TaxLineDetail"
                                # TaxDetail['TaxLineDetail'] = TaxLineDetail
                                # TaxDetail['Amount'] = 0
                                # TaxLineDetail['NetAmountTaxable'] = rounding[
                                #     'Amount']
                                # TaxRate['value'] = '4'
                                # TaxLineDetail['TaxRateRef'] = TaxRate
                                # TaxLineDetail['PercentBased'] = True
                                # TxnTaxDetail['TaxLine'].append(TaxDetail)

                                # purchase_order['Line'].append(rounding)
                            else:
                                pass

            if (
                    purchase_order["Line"][j]["AccountBasedExpenseLineDetail"]["AccountRef"]
                    != {}
            ):
                url1 = "{}/purchaseorder?minorversion=14".format(base_url)
                payload = json.dumps(purchase_order)
                inv_date = xero_purchase_order[i]["Date"][0:10]
                inv_date1 = datetime.strptime(inv_date, "%Y-%m-%d")

                if start_date1 is not None and end_date1 is not None:
                    if (inv_date1 > start_date1) and (inv_date1 < end_date1):
                        response = requests.request(
                            "POST", url1, headers=headers, data=payload
                        )

                        if response.status_code == 401:
                            res1 = json.loads(response.text)
                            res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
                            add_job_status(job_id, res2, "error")
                        elif response.status_code == 400:
                            res1 = json.loads(response.text)
                            res2 = res1["Fault"]["Error"][0]["Detail"] + " : {}".format(
                                xero_purchase_order[i]["Number"]
                            )
                            add_job_status(job_id, res2, "error")

                    else:
                        pass
                else:
                    response = requests.request(
                        "POST", url1, headers=headers, data=payload
                    )
                    if response.status_code == 401:
                        res1 = json.loads(response.text)
                        res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
                        add_job_status(job_id, res2, "error")
                    elif response.status_code == 400:
                        res1 = json.loads(response.text)
                        res2 = res1["Fault"]["Error"][0]["Detail"] + " : {}".format(
                            xero_purchase_order[i]["Number"]
                        )
                        add_job_status(job_id, res2, "error")

            else:
                add_job_status(
                    job_id,
                    "Unable to add purchase order because Item is not present in QBO : {}".format(
                        xero_purchase_order[i]["Number"]
                    ),
                    "error",
                )

    except Exception as ex:
        logging.error(ex, exc_info=True)