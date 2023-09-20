import json
import traceback
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job, post_data_in_qbo


def add_service_purchase_order(job_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        service_purchase_orders = db["service_purchase_order"].find({"job_id":job_id})

        service_purchase_order = []
        for p1 in service_purchase_orders:
            service_purchase_order.append(p1)

        service_purchase_order = service_purchase_order

        QBO_Item = db["QBO_Item"].find({"job_id":job_id})
        QBO_item = []
        for p1 in QBO_Item:
            QBO_item.append(p1)

        QBO_Class = db["QBO_Class"].find({"job_id":job_id})
        QBO_class = []
        for p2 in QBO_Class:
            QBO_class.append(p2)

        QBO_Tax = db["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p3 in QBO_Tax:
            QBO_tax.append(p3)

        QBO_COA = db["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p4 in QBO_COA:
            QBO_coa.append(p4)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id":job_id})
        QBO_supplier = []
        for p5 in QBO_Supplier:
            QBO_supplier.append(p5)

        for i in range(0, len(service_purchase_order)):
            purchase_order = {"Line": []}
            VendorRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            purchase_order["TxnDate"] = service_purchase_order[i]["Date"]
            purchase_order["DocNumber"] = service_purchase_order[i]["Number"]
            purchase_order["TotalAmt"] = abs(service_purchase_order[i]["TotalAmount"])
            APAccountRef = {}
            APAccountRef["name"] = "Accounts Payable (A/P)"
            APAccountRef["value"] = "92"

            subtotal = {}
            for p1 in range(0, len(QBO_supplier)):
                if "Supplier" in service_purchase_order[i]:
                    if (
                            service_purchase_order[i]["Supplier"]
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

            for j in range(0, len(service_purchase_order[i]["Line"])):
                if "Acc_Name" in service_purchase_order[i]["Line"][j]:
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
                    salesitemline["Description"] = service_purchase_order[i]["Line"][j][
                        "Description"
                    ]

                    for p4 in range(0, len(QBO_class)):
                        if service_purchase_order[i]["Line"][j]["Job"] is not None:
                            if (
                                    service_purchase_order[i]["Line"][j]["Job"]
                                    == QBO_class[p4]["Name"]
                            ):
                                ClassRef["name"] = QBO_class[p4]["Name"]
                                ClassRef["value"] = QBO_class[p4]["Id"]
                            else:
                                pass

                    for p5 in range(0, len(QBO_coa)):
                        if (
                                service_purchase_order[i]["Line"][j]["Acc_Name"]
                                == QBO_coa[p5]["Name"]
                        ):
                            AccountRef["name"] = QBO_coa[p5]["Name"]
                            AccountRef["value"] = QBO_coa[p5]["Id"]
                        else:
                            pass

                    # AccountRef['name'] = 'Sales Of Product Income'
                    # AccountRef['value'] = '81'

                    for p6 in range(0, len(QBO_tax)):
                        if service_purchase_order[i]["Line"][j]["taxcode"] == "GST":
                            if "taxrate_name" in QBO_tax[p6]:
                                if (
                                        "GST (purchases)"
                                        in QBO_tax[p6]["taxrate_name"]
                                ):
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val = (
                                            total_val
                                            + service_purchase_order[i]["Line"][j]["Total"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif service_purchase_order[i]["Line"][j]["taxcode"] == "CAP":
                            if "GST on capital" in QBO_tax[p6]["taxcode_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val += (
                                        service_purchase_order[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                        elif service_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
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
                                            service_purchase_order[i]["Line"][j]["Total"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif service_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                            if "N-T" in QBO_tax[p6]["taxcode_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val += (
                                        service_purchase_order[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                        elif (
                                service_purchase_order[i]["Line"][j]["taxcode"]
                                == QBO_tax[p6]["taxcode_name"]
                        ):
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                    service_purchase_order[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                            )
                        else:
                            pass

                    if service_purchase_order[i]["IsTaxInclusive"] == True:
                        if service_purchase_order[i]["Subtotal"] > 0:
                            salesitemline["Amount"] = round(
                                service_purchase_order[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )

                            TxnTaxDetail["TotalTax"] = service_purchase_order[i][
                                "TotalTax"
                            ]

                            if service_purchase_order[i]["Line"][j]["taxcode"] == "GST":
                                TaxDetail["Amount"] = service_purchase_order[i][
                                    "TotalTax"
                                ]
                                TaxLineDetail["NetAmountTaxable"] = round(
                                    service_purchase_order[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100,
                                    2,
                                )
                            elif (
                                    service_purchase_order[i]["Line"][j]["taxcode"] == "FRE"
                            ):
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = service_purchase_order[i]["Line"][j]["Total"]
                            elif (
                                    service_purchase_order[i]["Line"][j]["taxcode"] == "N-T"
                            ):
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = service_purchase_order[i]["Line"][j]["Total"]
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
                                service_purchase_order[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )

                            TxnTaxDetail["TotalTax"] = -service_purchase_order[i][
                                "TotalTax"
                            ]

                            if service_purchase_order[i]["Line"][j]["taxcode"] == "GST":
                                TaxDetail["Amount"] = -service_purchase_order[i][
                                    "TotalTax"
                                ]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        TaxDetail["Amount"] * taxrate1
                                )
                            elif (
                                    service_purchase_order[i]["Line"][j]["taxcode"] == "FRE"
                            ):
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = -service_purchase_order[i]["Line"][j]["Total"]
                            elif (
                                    service_purchase_order[i]["Line"][j]["taxcode"] == "N-T"
                            ):
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = -service_purchase_order[i]["Line"][j]["Total"]
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
                        if service_purchase_order[i]["Subtotal"] > 0:
                            salesitemline["Amount"] = service_purchase_order[i]["Line"][
                                j
                            ]["Total"]

                            TxnTaxDetail["TotalTax"] = service_purchase_order[i][
                                "TotalTax"
                            ]

                            if taxrate1 != 0:
                                TaxDetail["Amount"] = service_purchase_order[i][
                                    "TotalTax"
                                ]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        service_purchase_order[i]["Subtotal"]
                                        - service_purchase_order[i]["TotalTax"]
                                )
                            else:
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = 0

                        else:
                            salesitemline["Amount"] = service_purchase_order[i]["Line"][
                                j
                            ]["Total"]

                            TxnTaxDetail["TotalTax"] = -service_purchase_order[i][
                                "TotalTax"
                            ]

                            if taxrate1 != 0:
                                TaxDetail["Amount"] = service_purchase_order[i][
                                    "TotalTax"
                                ]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        service_purchase_order[i]["Subtotal"]
                                        - service_purchase_order[i]["TotalTax"]
                                )
                            else:
                                if (
                                        service_purchase_order[i]["Line"][j]["taxcode"]
                                        == "GST"
                                ):
                                    TaxDetail["Amount"] = -service_purchase_order[i][
                                        "TotalTax"
                                    ]
                                    TaxLineDetail["NetAmountTaxable"] = (
                                            -service_purchase_order[i]["Line"][j]["Total"]
                                            / (100 + taxrate1)
                                            * 100
                                    )
                                elif (
                                        service_purchase_order[i]["Line"][j]["taxcode"]
                                        == "FRE"
                                ):
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail[
                                        "NetAmountTaxable"
                                    ] = -service_purchase_order[i]["Line"][j]["Total"]
                                elif (
                                        service_purchase_order[i]["Line"][j]["taxcode"]
                                        == "N-T"
                                ):
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail[
                                        "NetAmountTaxable"
                                    ] = -service_purchase_order[i]["Line"][j]["Total"]

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
                    line_amount1 = line_amount + service_purchase_order[i]["TotalTax"]

                a = []

                for p2 in range(0, len(TxnTaxDetail["TaxLine"])):
                    if TxnTaxDetail["TaxLine"][p2] in a:
                        pass
                    else:
                        a.append(TxnTaxDetail["TaxLine"][p2])

                if len(a) >= 1:
                    if service_purchase_order[i]["IsTaxInclusive"] == True:
                        if line_amount1 == service_purchase_order[i]["TotalAmount"]:
                            pass
                        else:
                            line_amount == service_purchase_order[i][
                                "TotalAmount"
                            ] - line_amount1
                            if line_amount != 0:
                                ClassRef = {}

                                if service_purchase_order[i]["Subtotal"] > 0:
                                    rounding["Amount"] = round(
                                        abs(service_purchase_order[i]["TotalAmount"])
                                        - line_amount1,
                                        2,
                                    )
                                else:
                                    rounding["Amount"] = round(
                                        abs(
                                            service_purchase_order[i]["TotalAmount"]
                                            - service_purchase_order[i]["TotalTax"]
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

                                purchase_order["Line"].append(rounding)

                    else:
                        if (
                                line_amount1
                                == service_purchase_order[i]["TotalAmount"]
                                + service_purchase_order[i]["TotalTax"]
                        ):
                            pass
                        else:
                            line_amount == service_purchase_order[i][
                                "TotalAmount"
                            ] - line_amount1

                            if line_amount != 0:
                                AccountRef = {}
                                ClassRef = {}
                                TaxCodeRef = {}
                                AccountRef = {}

                                if service_purchase_order[i]["Subtotal"] > 0:
                                    rounding["Amount"] = (
                                            service_purchase_order[i]["TotalAmount"]
                                            - line_amount1
                                    )
                                else:
                                    rounding["Amount"] = (
                                            service_purchase_order[i]["TotalAmount"]
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

                                purchase_order["Line"].append(rounding)
                            else:
                                pass

            if (
                    purchase_order["Line"][j]["AccountBasedExpenseLineDetail"]["AccountRef"]
                    != {}
            ):
                url1 = "{}/purchaseorder?minorversion=14".format(base_url)
                payload = json.dumps(purchase_order)
                inv_date = service_purchase_order[i]["Date"][0:10]
                inv_date1 = datetime.strptime(inv_date, "%Y-%m-%d")

                if start_date1 is not None and end_date1 is not None:
                    if (inv_date1 > start_date1) and (inv_date1 < end_date1):
                        post_data_in_qbo(
                            url1,
                            headers,
                            payload,
                            job_id,
                            service_purchase_order[i]["Number"]
                        )
                    else:
                        pass
                else:
                    post_data_in_qbo(
                        url1,
                        headers,
                        payload,
                        job_id,
                        service_purchase_order[i]["Number"]
                    )
            else:
                add_job_status(
                    job_id,
                    "Unable to add purchase order because Item is not present in QBO : {}".format(
                        service_purchase_order[i]["Number"]
                    ),
                    "error",
                )

    except Exception as ex:
        traceback.print_exc()
        
