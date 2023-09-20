import json
import traceback
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job, post_data_in_qbo


def add_item_purchase_order(job_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()

        item_purchase_orders = db["item_purchase_order"].find({"job_id":job_id})

        item_purchase_order = []
        for p1 in item_purchase_orders:
            item_purchase_order.append(p1)

        item_purchase_order = item_purchase_order

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

        for i in range(0, len(item_purchase_order)):
            purchase_order = {"Line": []}
            VendorRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            purchase_order["TxnDate"] = item_purchase_order[i]["Date"]
            purchase_order["DocNumber"] = item_purchase_order[i]["Number"]
            purchase_order["TotalAmt"] = abs(item_purchase_order[i]["TotalAmount"])
            APAccountRef = {}
            APAccountRef["name"] = "Accounts Payable (A/P)"
            APAccountRef["value"] = "92"

            subtotal = {}
            for p1 in range(0, len(QBO_supplier)):
                if "Supplier" in item_purchase_order[i]:
                    if (
                            item_purchase_order[i]["Supplier"]
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

            for j in range(0, len(item_purchase_order[i]["Line"])):
                TaxLineDetail = {}
                VendorMemo = {}
                salesitemline = {}
                DiscountPercent = {}
                rounding = {}
                discount_SalesItemLineDetail = {}
                rounding_SalesItemLineDetail = {}
                ItemRef = {}
                ClassRef = {}
                TaxCodeRef = {}
                ItemAccountRef = {}
                TaxRate = {}
                ItemBasedExpenseLineDetail = {}
                TaxDetail = {}
                salesitemline["DetailType"] = "ItemBasedExpenseLineDetail"
                DiscountPercent["Description"] = "Discount"

                for p3 in range(0, len(QBO_item)):
                    if "Item_Name" in item_purchase_order[i]["Line"][j]:
                        if (
                                item_purchase_order[i]["Line"][j]["Item_Name"]
                                == QBO_item[p3]["Name"]
                        ):
                            ItemRef["name"] = QBO_item[p3]["Name"]
                            ItemRef["value"] = QBO_item[p3]["Id"]
                        else:
                            pass

                for p4 in range(0, len(QBO_class)):
                    if item_purchase_order[i]["Line"][j]["Job"] is not None:
                        if (
                                item_purchase_order[i]["Line"][j]["Job"]
                                == QBO_class[p4]["Name"]
                        ):
                            ClassRef["name"] = QBO_class[p4]["Name"]
                            ClassRef["value"] = QBO_class[p4]["Id"]
                        else:
                            pass

                # for p5 in range(0, len(QBO_coa)):
                #     if item_purchase_order[i]['Line'][j][
                #             'Acc_Name'] == QBO_coa[p5]['Name']:
                #         ItemAccountRef['name'] = QBO_coa[p5]['Name']
                #         ItemAccountRef['value'] = QBO_coa[p5]['Id']
                # ItemAccountRef['name'] = 'Sales Of Product Income'
                # ItemAccountRef['value'] = '81'

                for p6 in range(0, len(QBO_tax)):
                    if item_purchase_order[i]["Line"][j]["taxcode"] == "GST":
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
                                        + item_purchase_order[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                    elif item_purchase_order[i]["Line"][j]["taxcode"] == "CAP":
                        if "GST on capital" in QBO_tax[p6]["taxcode_name"]:
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                    item_purchase_order[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                            )

                    elif item_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
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
                                        item_purchase_order[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                    elif item_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                        if "N-T" in QBO_tax[p6]["taxcode_name"]:
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                    item_purchase_order[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                            )

                    elif (
                            item_purchase_order[i]["Line"][j]["taxcode"]
                            == QBO_tax[p6]["taxcode_name"]
                    ):
                        TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                        taxrate = QBO_tax[p6]["Rate"]
                        TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                        TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                        taxrate1 = taxrate
                        total_val += (
                                item_purchase_order[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100
                        )
                    else:
                        pass

                if item_purchase_order[i]["IsTaxInclusive"] == True:
                    if item_purchase_order[i]["Subtotal"] > 0:
                        ItemBasedExpenseLineDetail["Qty"] = item_purchase_order[i][
                            "Line"
                        ][j]["BillQuantity"]
                        ItemBasedExpenseLineDetail["UnitPrice"] = round(
                            item_purchase_order[i]["Line"][j]["UnitPrice"]
                            / (100 + taxrate1)
                            * 100,
                            2,
                        )
                        salesitemline["Amount"] = round(
                            ItemBasedExpenseLineDetail["Qty"]
                            * ItemBasedExpenseLineDetail["UnitPrice"],
                            2,
                        )

                        TxnTaxDetail["TotalTax"] = item_purchase_order[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = 1
                        discount_SalesItemLineDetail["UnitPrice"] = -round(
                            (
                                    item_purchase_order[i]["Line"][j]["BillQuantity"]
                                    * item_purchase_order[i]["Line"][j]["UnitPrice"]
                                    * item_purchase_order[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )
                        DiscountPercent["Amount"] = -round(
                            (
                                    item_purchase_order[i]["Line"][j]["BillQuantity"]
                                    * item_purchase_order[i]["Line"][j]["UnitPrice"]
                                    * item_purchase_order[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )

                        if item_purchase_order[i]["Line"][j]["taxcode"] == "GST":
                            TaxDetail["Amount"] = item_purchase_order[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = round(
                                item_purchase_order[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )
                        elif item_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = item_purchase_order[i][
                                "Line"
                            ][j]["Total"]
                        elif item_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = item_purchase_order[i][
                                "Line"
                            ][j]["Total"]
                        else:
                            pass

                        purchase_order["TxnTaxDetail"] = TxnTaxDetail
                        TaxDetail["DetailType"] = "TaxLineDetail"
                        TaxDetail["TaxLineDetail"] = TaxLineDetail
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True

                        TxnTaxDetail["TaxLine"].append(TaxDetail)

                    else:
                        ItemBasedExpenseLineDetail["Qty"] = -item_purchase_order[i][
                            "Line"
                        ][j]["BillQuantity"]
                        ItemBasedExpenseLineDetail["UnitPrice"] = round(
                            item_purchase_order[i]["Line"][j]["UnitPrice"]
                            / (100 + taxrate1)
                            * 100,
                            2,
                        )
                        salesitemline["Amount"] = round(
                            ItemBasedExpenseLineDetail["Qty"]
                            * ItemBasedExpenseLineDetail["UnitPrice"],
                            2,
                        )

                        TxnTaxDetail["TotalTax"] = -item_purchase_order[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = -1
                        discount_SalesItemLineDetail["UnitPrice"] = round(
                            (
                                    item_purchase_order[i]["Line"][j]["BillQuantity"]
                                    * item_purchase_order[i]["Line"][j]["UnitPrice"]
                                    * item_purchase_order[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )
                        DiscountPercent["Amount"] = round(
                            (
                                    item_purchase_order[i]["Line"][j]["BillQuantity"]
                                    * item_purchase_order[i]["Line"][j]["UnitPrice"]
                                    * item_purchase_order[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )

                        if item_purchase_order[i]["Line"][j]["taxcode"] == "GST":
                            TaxDetail["Amount"] = -item_purchase_order[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                    TaxDetail["Amount"] * taxrate1
                            )
                        elif item_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = -item_purchase_order[i][
                                "Line"
                            ][j]["Total"]
                        elif item_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = -item_purchase_order[i][
                                "Line"
                            ][j]["Total"]
                        else:
                            pass

                        purchase_order["TxnTaxDetail"] = TxnTaxDetail
                        TaxDetail["DetailType"] = "TaxLineDetail"
                        TaxDetail["TaxLineDetail"] = TaxLineDetail
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True

                        TxnTaxDetail["TaxLine"].append(TaxDetail)

                    purchase_order["GlobalTaxCalculation"] = "TaxInclusive"
                    salesitemline["DetailType"] = "ItemBasedExpenseLineDetail"
                    salesitemline[
                        "ItemBasedExpenseLineDetail"
                    ] = ItemBasedExpenseLineDetail

                    ItemBasedExpenseLineDetail["ItemRef"] = ItemRef
                    ItemBasedExpenseLineDetail["ClassRef"] = ClassRef
                    ItemBasedExpenseLineDetail["TaxCodeRef"] = TaxCodeRef

                    DiscountPercent["DetailType"] = "ItemBasedExpenseLineDetail"
                    DiscountPercent[
                        "ItemBasedExpenseLineDetail"
                    ] = discount_SalesItemLineDetail
                    discount_SalesItemLineDetail["ItemRef"] = ItemRef
                    discount_SalesItemLineDetail["ClassRef"] = ClassRef
                    discount_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                    purchase_order["BillEmail"] = BillEmail
                    purchase_order["VendorRef"] = VendorRef
                    purchase_order["APAccountRef"] = APAccountRef

                    purchase_order["Line"].append(salesitemline)

                else:
                    if item_purchase_order[i]["Subtotal"] > 0:
                        ItemBasedExpenseLineDetail["Qty"] = item_purchase_order[i][
                            "Line"
                        ][j]["BillQuantity"]
                        ItemBasedExpenseLineDetail["UnitPrice"] = item_purchase_order[
                            i
                        ]["Line"][j]["UnitPrice"]
                        salesitemline["Amount"] = round(
                            item_purchase_order[i]["Line"][j]["UnitPrice"]
                            * item_purchase_order[i]["Line"][j]["BillQuantity"],
                            2,
                        )

                        TxnTaxDetail["TotalTax"] = item_purchase_order[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = 1
                        discount_SalesItemLineDetail["UnitPrice"] = (
                                -(
                                        item_purchase_order[i]["Line"][j]["BillQuantity"]
                                        * item_purchase_order[i]["Line"][j]["UnitPrice"]
                                        * item_purchase_order[i]["Line"][j]["DiscountPercent"]
                                )
                                / 100
                        )
                        DiscountPercent["Amount"] = (
                                -(
                                        item_purchase_order[i]["Line"][j]["BillQuantity"]
                                        * item_purchase_order[i]["Line"][j]["UnitPrice"]
                                        * item_purchase_order[i]["Line"][j]["DiscountPercent"]
                                )
                                / 100
                        )

                        if taxrate1 != 0:
                            TaxDetail["Amount"] = item_purchase_order[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                    item_purchase_order[i]["Subtotal"]
                                    - item_purchase_order[i]["TotalTax"]
                            )
                        else:
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = 0

                    else:
                        discount_SalesItemLineDetail["Qty"] = -1
                        discount_SalesItemLineDetail["UnitPrice"] = (
                                                                            item_purchase_order[i]["Line"][j][
                                                                                "BillQuantity"]
                                                                            * item_purchase_order[i]["Line"][j][
                                                                                "UnitPrice"]
                                                                            * item_purchase_order[i]["Line"][j][
                                                                                "DiscountPercent"]
                                                                    ) / 100
                        DiscountPercent["Amount"] = (
                                                            item_purchase_order[i]["Line"][j]["BillQuantity"]
                                                            * item_purchase_order[i]["Line"][j]["UnitPrice"]
                                                            * item_purchase_order[i]["Line"][j]["DiscountPercent"]
                                                    ) / 100

                        ItemBasedExpenseLineDetail["Qty"] = -item_purchase_order[i][
                            "Line"
                        ][j]["BillQuantity"]
                        ItemBasedExpenseLineDetail["UnitPrice"] = item_purchase_order[
                            i
                        ]["Line"][j]["UnitPrice"]
                        salesitemline["Amount"] = round(
                            item_purchase_order[i]["Line"][j]["UnitPrice"]
                            * item_purchase_order[i]["Line"][j]["BillQuantity"],
                            2,
                        )

                        TxnTaxDetail["TotalTax"] = -item_purchase_order[i]["TotalTax"]

                        if taxrate1 != 0:
                            TaxDetail["Amount"] = item_purchase_order[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                    item_purchase_order[i]["Subtotal"]
                                    - item_purchase_order[i]["TotalTax"]
                            )
                        else:
                            if item_purchase_order[i]["Line"][j]["taxcode"] == "GST":
                                TaxDetail["Amount"] = -item_purchase_order[i][
                                    "TotalTax"
                                ]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        -item_purchase_order[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )
                            elif item_purchase_order[i]["Line"][j]["taxcode"] == "FRE":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = -item_purchase_order[i]["Line"][j]["Total"]
                            elif item_purchase_order[i]["Line"][j]["taxcode"] == "N-T":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail[
                                    "NetAmountTaxable"
                                ] = -item_purchase_order[i]["Line"][j]["Total"]

                    purchase_order["TxnTaxDetail"] = TxnTaxDetail
                    TaxDetail["DetailType"] = "TaxLineDetail"
                    TaxDetail["TaxLineDetail"] = TaxLineDetail
                    TaxLineDetail["TaxRateRef"] = TaxRate
                    TaxLineDetail["PercentBased"] = True
                    salesitemline["DetailType"] = "ItemBasedExpenseLineDetail"
                    salesitemline[
                        "ItemBasedExpenseLineDetail"
                    ] = ItemBasedExpenseLineDetail

                    ItemBasedExpenseLineDetail["ItemRef"] = ItemRef
                    ItemBasedExpenseLineDetail["ClassRef"] = ClassRef
                    ItemBasedExpenseLineDetail["TaxCodeRef"] = TaxCodeRef

                    DiscountPercent["DetailType"] = "ItemBasedExpenseLineDetail"
                    DiscountPercent[
                        "ItemBasedExpenseLineDetail"
                    ] = discount_SalesItemLineDetail
                    discount_SalesItemLineDetail["ItemRef"] = ItemRef
                    discount_SalesItemLineDetail["ClassRef"] = ClassRef
                    discount_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                    purchase_order["BillEmail"] = BillEmail
                    purchase_order["VendorRef"] = VendorRef
                    purchase_order["APAccountRef"] = APAccountRef

                    purchase_order["Line"].append(salesitemline)

                    purchase_order["GlobalTaxCalculation"] = "TaxExcluded"

                if item_purchase_order[i]["Line"][j]["DiscountPercent"] > 0:
                    purchase_order["Line"].append(DiscountPercent)

                line_amount = (
                        line_amount + salesitemline["Amount"] + DiscountPercent["Amount"]
                )
                line_amount1 = line_amount + item_purchase_order[i]["TotalTax"]

            a = []

            for p2 in range(0, len(TxnTaxDetail["TaxLine"])):
                if TxnTaxDetail["TaxLine"][p2] in a:
                    pass
                else:
                    a.append(TxnTaxDetail["TaxLine"][p2])

            if len(a) >= 1:
                if item_purchase_order[i]["IsTaxInclusive"]:
                    if line_amount1 == item_purchase_order[i]["TotalAmount"]:
                        pass
                    else:
                        line_amount == item_purchase_order[i][
                            "TotalAmount"
                        ] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            ItemAccountRef = {}
                            rounding_SalesItemLineDetail["Qty"] = 1

                            if item_purchase_order[i]["Subtotal"] > 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = round(
                                    abs(item_purchase_order[i]["TotalAmount"])
                                    - line_amount1,
                                    2,
                                )
                                rounding["Amount"] = round(
                                    abs(item_purchase_order[i]["TotalAmount"])
                                    - line_amount1,
                                    2,
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = round(
                                    abs(
                                        item_purchase_order[i]["TotalAmount"]
                                        - item_purchase_order[i]["TotalTax"]
                                    )
                                    - line_amount,
                                    2,
                                )
                                rounding["Amount"] = round(
                                    abs(
                                        item_purchase_order[i]["TotalAmount"]
                                        - item_purchase_order[i]["TotalTax"]
                                    )
                                    - line_amount,
                                    2,
                                )

                            rounding["DetailType"] = "ItemBasedExpenseLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "ItemBasedExpenseLineDetail"
                            ] = rounding_SalesItemLineDetail
                            ItemRef["name"] = "Rounding"
                            ItemRef["value"] = "12886"
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                            # rounding_SalesItemLineDetail[
                            #     "ItemAccountRef"] = ItemAccountRef
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
                            == item_purchase_order[i]["TotalAmount"]
                            + item_purchase_order[i]["TotalTax"]
                    ):
                        pass
                    else:
                        line_amount == item_purchase_order[i][
                            "TotalAmount"
                        ] - line_amount1

                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}

                            rounding_SalesItemLineDetail["Qty"] = 1
                            if item_purchase_order[i]["Subtotal"] > 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                        item_purchase_order[i]["TotalAmount"] - line_amount1
                                )
                                rounding["Amount"] = (
                                        item_purchase_order[i]["TotalAmount"] - line_amount1
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                        item_purchase_order[i]["TotalAmount"] + line_amount1
                                )
                                rounding["Amount"] = (
                                        item_purchase_order[i]["TotalAmount"] + line_amount1
                                )

                            rounding["DetailType"] = "ItemBasedExpenseLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "ItemBasedExpenseLineDetail"
                            ] = rounding_SalesItemLineDetail
                            ItemRef["name"] = "Rounding"
                            ItemRef["value"] = "12886"
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                            # rounding_SalesItemLineDetail[
                            #     "ItemAccountRef"] = ItemAccountRef
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

            if purchase_order["Line"][j]["ItemBasedExpenseLineDetail"]["ItemRef"] != {}:
                url1 = "{}/purchaseorder?minorversion=14".format(base_url)
                payload = json.dumps(purchase_order)
                inv_date = item_purchase_order[i]["Date"][0:10]
                inv_date1 = datetime.strptime(inv_date, "%Y-%m-%d")

                if start_date1 is not None and end_date1 is not None:
                    if (inv_date1 > start_date1) and (inv_date1 < end_date1):
                        post_data_in_qbo(
                            url1,
                            headers,
                            payload,
                            job_id,
                            item_purchase_order[i]["Number"]
                        )
                    else:
                        pass
                else:
                    post_data_in_qbo(
                        url1,
                        headers,
                        payload,
                        job_id,
                        item_purchase_order[i]["Number"]
                    )
            else:
                add_job_status(
                    job_id,
                    "Unable to add purchase order because Item is not present in QBO : {}".format(
                        item_purchase_order[i]["Number"]
                    ),
                    "error",
                )
    except Exception as ex:
        traceback.print_exc()
        
