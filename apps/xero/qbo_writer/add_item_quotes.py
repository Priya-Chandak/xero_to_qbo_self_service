import json
import logging
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job

logger = logging.getLogger(__name__)



def add_xero_item_quote(job_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_item_quotes -> add_xero_item_quote")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        item_quotes = db["xero_quotes"].find({"job_id":job_id})

        xero_quotes = []
        for p1 in item_quotes:
            xero_quotes.append(p1)

        xero_quotes = xero_quotes

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

        QBO_Customer = db["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p5 in QBO_Customer:
            QBO_customer.append(p5)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id":job_id})
        QBO_supplier = []
        for p7 in QBO_Supplier:
            QBO_supplier.append(p7)

        Xero_COA = db["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        for i in range(0, len(xero_quotes)):
            quote = {"Line": []}
            CustomerRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            quote["TxnDate"] = xero_quotes[i]["Date"]
            quote["DocNumber"] = xero_quotes[i]["Number"]
            quote["TotalAmt"] = abs(xero_quotes[i]["TotalAmount"])
            quote["HomeTotalAmt"] = abs(xero_quotes[i]["TotalAmount"])

            subtotal = {}
            if "Customer" in xero_quotes[i]:
                for p1 in range(0, len(QBO_customer)):
                    if (
                        xero_quotes[i]["Customer"] == QBO_customer[p1]["DisplayName"]
                    ) or (
                        xero_quotes[i]["Customer"]
                        == QBO_customer[p1]["DisplayName"] + " - C"
                    ):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                    else:
                        for p1 in range(0, len(QBO_supplier)):
                            if (
                                xero_quotes[i]["Customer"]
                                == QBO_supplier[p1]["DisplayName"]
                            ) or (
                                xero_quotes[i]["Customer"]
                                == QBO_supplier[p1]["DisplayName"] + " - S"
                            ):
                                CustomerRef["value"] = QBO_supplier[p1]["Id"]
                                CustomerRef["name"] = QBO_supplier[p1]["DisplayName"]

            total_val = 0
            taxrate1 = 0
            line_amount = 0

            for j in range(len(xero_quotes[i]["Line"])):
                TaxLineDetail = {}

                salesitemline = {}
                DiscountPercent = {}
                rounding = {}
                SalesItemLineDetail = {}
                discount_SalesItemLineDetail = {}
                rounding_SalesItemLineDetail = {}
                ItemRef = {}
                ClassRef = {}
                TaxCodeRef = {}
                ItemAccountRef = {}
                TaxRate = {}
                SubTotalLineDetail = {}
                TaxDetail = {}
                salesitemline["DetailType"] = "SalesItemLineDetail"
                DiscountPercent["Description"] = "Discount"

                for p3 in range(0, len(QBO_item)):
                    if xero_quotes[i]["Line"][j]["Item_Name"] == QBO_item[p3]["Name"]:
                        ItemRef["name"] = QBO_item[p3]["Name"]
                        ItemRef["value"] = QBO_item[p3]["Id"]
                    else:
                        pass

                for p5 in range(0, len(QBO_coa)):
                    for p51 in range(0, len(xero_coa)):
                        if "Code" in xero_coa[p51]:
                            if (
                                xero_quotes[i]["Line"][j]["Acc_Name"]
                                == xero_coa[p51]["Code"]
                            ):
                                if xero_coa[p51]["Name"] == QBO_coa[p5]["Name"]:
                                    ItemAccountRef["name"] = QBO_coa[p5]["Name"]
                                    ItemAccountRef["value"] = QBO_coa[p5]["Id"]

                for p6 in range(0, len(QBO_tax)):
                    if xero_quotes[i]["Line"][j]["taxcode"] == "BASEXCLUDED":
                        if "taxrate_name" in QBO_tax[p6]:
                            if "N-T (Sales)" in QBO_tax[p6]["taxrate_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val = (
                                    total_val
                                    + xero_quotes[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                                )

                    elif xero_quotes[i]["Line"][j]["taxcode"] == "CAP":
                        if "GST on capital" in QBO_tax[p6]["taxcode_name"]:
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                xero_quotes[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100
                            )

                    elif xero_quotes[i]["Line"][j]["taxcode"] == "FRE":
                        if "taxrate_name" in QBO_tax[p6]:
                            if "GST free (sales)" in QBO_tax[p6]["taxrate_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val += (
                                    xero_quotes[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                                )

                    elif xero_quotes[i]["Line"][j]["taxcode"] == "N-T":
                        if "N-T" in QBO_tax[p6]["taxcode_name"]:
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                xero_quotes[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100
                            )

                    elif (
                        xero_quotes[i]["Line"][j]["taxcode"]
                        == QBO_tax[p6]["taxcode_name"]
                    ):
                        TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                        taxrate = QBO_tax[p6]["Rate"]
                        TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                        TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                        taxrate1 = taxrate
                        total_val += (
                            xero_quotes[i]["Line"][j]["Total"] / (100 + taxrate1) * 100
                        )
                    else:
                        pass

                if xero_quotes[i]["IsTaxInclusive"] == "INCLUSIVE":
                    if xero_quotes[i]["Subtotal"] > 0:
                        SalesItemLineDetail["Qty"] = xero_quotes[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        #                 SalesItemLineDetail['UnitPrice'] = abs(xero_quotes[i]['Line'][j]['UnitPrice'])
                        SalesItemLineDetail["UnitPrice"] = round(
                            xero_quotes[i]["Line"][j]["UnitPrice"]
                            / (100 + taxrate1)
                            * 100,
                            2,
                        )
                        salesitemline["Amount"] = round(
                            SalesItemLineDetail["Qty"]
                            * SalesItemLineDetail["UnitPrice"],
                            2,
                        )
                        subtotal["Amount"] = round(
                            xero_quotes[i]["Subtotal"] - xero_quotes[i]["TotalTax"], 2
                        )
                        TxnTaxDetail["TotalTax"] = xero_quotes[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = 1
                        discount_SalesItemLineDetail["UnitPrice"] = -round(
                            (
                                xero_quotes[i]["Line"][j]["ShipQuantity"]
                                * xero_quotes[i]["Line"][j]["UnitPrice"]
                                * xero_quotes[i]["Line"][j]["DiscountPercent"]
                                / (100 + taxrate1)
                            ),
                            2,
                        )
                        DiscountPercent["Amount"] = -round(
                            (
                                xero_quotes[i]["Line"][j]["ShipQuantity"]
                                * xero_quotes[i]["Line"][j]["UnitPrice"]
                                * xero_quotes[i]["Line"][j]["DiscountPercent"]
                                / (100 + taxrate1)
                            ),
                            2,
                        )

                        if xero_quotes[i]["Line"][j]["taxcode"] == "BASEXCLUDED":
                            TaxDetail["Amount"] = xero_quotes[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = round(
                                xero_quotes[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )
                        elif xero_quotes[i]["Line"][j]["taxcode"] == "FRE":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = xero_quotes[i]["Line"][
                                j
                            ]["Total"]
                        elif xero_quotes[i]["Line"][j]["taxcode"] == "N-T":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = xero_quotes[i]["Line"][
                                j
                            ]["Total"]
                        else:
                            pass

                        quote["TxnTaxDetail"] = TxnTaxDetail
                        TaxDetail["DetailType"] = "TaxLineDetail"
                        TaxDetail["TaxLineDetail"] = TaxLineDetail
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True
                        TxnTaxDetail["TaxLine"].append(TaxDetail)

                    else:
                        SalesItemLineDetail["Qty"] = -xero_quotes[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        #                 SalesItemLineDetail['UnitPrice'] = abs(xero_quotes[i]['Line'][j]['UnitPrice'])
                        SalesItemLineDetail["UnitPrice"] = round(
                            xero_quotes[i]["Line"][j]["UnitPrice"]
                            / (100 + taxrate1)
                            * 100,
                            2,
                        )
                        salesitemline["Amount"] = round(
                            SalesItemLineDetail["Qty"]
                            * SalesItemLineDetail["UnitPrice"],
                            2,
                        )
                        subtotal["Amount"] = -(
                            xero_quotes[i]["Subtotal"] - xero_quotes[i]["TotalTax"]
                        )
                        TxnTaxDetail["TotalTax"] = -xero_quotes[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = -1
                        discount_SalesItemLineDetail["UnitPrice"] = round(
                            (
                                xero_quotes[i]["Line"][j]["ShipQuantity"]
                                * xero_quotes[i]["Line"][j]["UnitPrice"]
                                * xero_quotes[i]["Line"][j]["DiscountPercent"]
                                / (100 + taxrate1)
                            ),
                            2,
                        )
                        DiscountPercent["Amount"] = round(
                            (
                                xero_quotes[i]["Line"][j]["ShipQuantity"]
                                * xero_quotes[i]["Line"][j]["UnitPrice"]
                                * xero_quotes[i]["Line"][j]["DiscountPercent"]
                                / (100 + taxrate1)
                            ),
                            2,
                        )

                        if xero_quotes[i]["Line"][j]["taxcode"] == "GST":
                            TaxDetail["Amount"] = -xero_quotes[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                TaxDetail["Amount"] * taxrate1
                            )
                        elif xero_quotes[i]["Line"][j]["taxcode"] == "FRE":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = -xero_quotes[i]["Line"][
                                j
                            ]["Total"]
                        elif xero_quotes[i]["Line"][j]["taxcode"] == "N-T":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = -xero_quotes[i]["Line"][
                                j
                            ]["Total"]
                        else:
                            pass

                        #                 salesitemline["Amount"] = abs(round(
                        #                     (xero_quotes[i]['Line'][j]['UnitPrice']*xero_quotes[i]['Line'][j]['ShipQuantity']/(100+taxrate1)*100), 2))
                        #                 subtotal['Amount'] = abs(round((total_val), 2))
                        quote["TxnTaxDetail"] = TxnTaxDetail
                        TaxDetail["DetailType"] = "TaxLineDetail"
                        TaxDetail["TaxLineDetail"] = TaxLineDetail
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True

                        TxnTaxDetail["TaxLine"].append(TaxDetail)

                    quote["GlobalTaxCalculation"] = "TaxInclusive"

                else:
                    if xero_quotes[i]["Subtotal"] > 0:
                        SalesItemLineDetail["Qty"] = xero_quotes[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        SalesItemLineDetail["UnitPrice"] = xero_quotes[i]["Line"][j][
                            "UnitPrice"
                        ]
                        salesitemline["Amount"] = round(
                            xero_quotes[i]["Line"][j]["UnitPrice"]
                            * xero_quotes[i]["Line"][j]["ShipQuantity"],
                            2,
                        )
                        subtotal["Amount"] = xero_quotes[i]["Subtotal"]
                        TxnTaxDetail["TotalTax"] = xero_quotes[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = 1
                        discount_SalesItemLineDetail["UnitPrice"] = (
                            -(
                                xero_quotes[i]["Line"][j]["ShipQuantity"]
                                * xero_quotes[i]["Line"][j]["UnitPrice"]
                                * xero_quotes[i]["Line"][j]["DiscountPercent"]
                            )
                            / 100
                        )
                        DiscountPercent["Amount"] = (
                            -(
                                xero_quotes[i]["Line"][j]["ShipQuantity"]
                                * xero_quotes[i]["Line"][j]["UnitPrice"]
                                * xero_quotes[i]["Line"][j]["DiscountPercent"]
                            )
                            / 100
                        )

                        if taxrate1 != 0:
                            TaxDetail["Amount"] = xero_quotes[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                xero_quotes[i]["Subtotal"] - xero_quotes[i]["TotalTax"]
                            )
                        else:
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = 0

                    else:
                        discount_SalesItemLineDetail["Qty"] = -1
                        discount_SalesItemLineDetail["UnitPrice"] = (
                            xero_quotes[i]["Line"][j]["ShipQuantity"]
                            * xero_quotes[i]["Line"][j]["UnitPrice"]
                            * xero_quotes[i]["Line"][j]["DiscountPercent"]
                        ) / 100
                        DiscountPercent["Amount"] = (
                            xero_quotes[i]["Line"][j]["ShipQuantity"]
                            * xero_quotes[i]["Line"][j]["UnitPrice"]
                            * xero_quotes[i]["Line"][j]["DiscountPercent"]
                        ) / 100

                        SalesItemLineDetail["Qty"] = -xero_quotes[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        SalesItemLineDetail["UnitPrice"] = xero_quotes[i]["Line"][j][
                            "UnitPrice"
                        ]
                        salesitemline["Amount"] = round(
                            xero_quotes[i]["Line"][j]["UnitPrice"]
                            * xero_quotes[i]["Line"][j]["ShipQuantity"],
                            2,
                        )
                        subtotal["Amount"] = -xero_quotes[i]["Subtotal"]
                        TxnTaxDetail["TotalTax"] = -xero_quotes[i]["TotalTax"]

                        if taxrate1 != 0:
                            TaxDetail["Amount"] = xero_quotes[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                xero_quotes[i]["Subtotal"] - xero_quotes[i]["TotalTax"]
                            )
                        else:
                            if xero_quotes[i]["Line"][j]["taxcode"] == "GST":
                                TaxDetail["Amount"] = -xero_quotes[i]["TotalTax"]
                                TaxLineDetail["NetAmountTaxable"] = (
                                    -xero_quotes[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                                )
                            elif xero_quotes[i]["Line"][j]["taxcode"] == "FRE":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = -xero_quotes[i][
                                    "Line"
                                ][j]["Total"]
                            elif xero_quotes[i]["Line"][j]["taxcode"] == "N-T":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = -xero_quotes[i][
                                    "Line"
                                ][j]["Total"]

                    quote["TxnTaxDetail"] = TxnTaxDetail
                    TaxDetail["DetailType"] = "TaxLineDetail"
                    TaxDetail["TaxLineDetail"] = TaxLineDetail
                    TaxLineDetail["TaxRateRef"] = TaxRate
                    TaxLineDetail["PercentBased"] = True

                    quote["GlobalTaxCalculation"] = "TaxExcluded"

                subtotal["DetailType"] = "SubTotalLineDetail"
                subtotal["SubTotalLineDetail"] = SubTotalLineDetail
                salesitemline["DetailType"] = "SalesItemLineDetail"
                salesitemline["SalesItemLineDetail"] = SalesItemLineDetail

                SalesItemLineDetail["ItemRef"] = ItemRef
                SalesItemLineDetail["ClassRef"] = ClassRef
                SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                DiscountPercent["DetailType"] = "SalesItemLineDetail"
                DiscountPercent["SalesItemLineDetail"] = discount_SalesItemLineDetail
                discount_SalesItemLineDetail["ItemRef"] = ItemRef
                discount_SalesItemLineDetail["ClassRef"] = ClassRef
                discount_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                discount_SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef
                quote["BillEmail"] = BillEmail
                quote["CustomerRef"] = CustomerRef

                quote["Line"].append(salesitemline)

                if xero_quotes[i]["Line"][j]["DiscountPercent"] > 0:
                    quote["Line"].append(DiscountPercent)

                line_amount = (
                    line_amount + salesitemline["Amount"] + DiscountPercent["Amount"]
                )
                line_amount1 = line_amount + xero_quotes[i]["TotalTax"]

            a = []

            for p2 in range(0, len(TxnTaxDetail["TaxLine"])):
                if TxnTaxDetail["TaxLine"][p2] in a:
                    pass
                else:
                    a.append(TxnTaxDetail["TaxLine"][p2])

            # TxnTaxDetail['TaxLine'] = a

            if len(a) >= 1:
                if xero_quotes[i]["IsTaxInclusive"] == "INCLUSIVE":
                    if line_amount1 == xero_quotes[i]["TotalAmount"]:
                        pass
                    else:
                        line_amount == xero_quotes[i]["TotalAmount"] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            # TaxCodeRef = {}
                            ItemAccountRef = {}
                            rounding_SalesItemLineDetail["Qty"] = 1

                            if xero_quotes[i]["Subtotal"] > 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = round(
                                    abs(xero_quotes[i]["TotalAmount"]) - line_amount1, 2
                                )
                                rounding["Amount"] = round(
                                    abs(xero_quotes[i]["TotalAmount"]) - line_amount1, 2
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = round(
                                    abs(
                                        xero_quotes[i]["TotalAmount"]
                                        - xero_quotes[i]["TotalTax"]
                                    )
                                    - line_amount,
                                    2,
                                )
                                rounding["Amount"] = round(
                                    abs(
                                        xero_quotes[i]["TotalAmount"]
                                        - xero_quotes[i]["TotalTax"]
                                    )
                                    - line_amount,
                                    2,
                                )

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"
                            ] = rounding_SalesItemLineDetail
                            ItemRef["name"] = "Rounding"
                            ItemRef["value"] = "12886"
                            ItemAccountRef["name"] = "Sales Of Product Income"
                            ItemAccountRef["value"] = "81"
                            # TaxCodeRef['value'] = "5"
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"
                            ] = ItemAccountRef
                            # TaxDetail['DetailType'] = "TaxLineDetail"
                            # TaxDetail['TaxLineDetail'] = TaxLineDetail
                            # TaxDetail['Amount'] = 0
                            # TaxLineDetail['NetAmountTaxable'] = rounding[
                            #     'Amount']
                            # TaxRate['value'] = '4'
                            # TaxLineDetail['TaxRateRef'] = TaxRate
                            # TaxLineDetail['PercentBased'] = True

                            # TxnTaxDetail['TaxLine'].append(TaxDetail)

                            quote["Line"].append(rounding)

                else:
                    if (
                        line_amount1
                        == xero_quotes[i]["TotalAmount"] + xero_quotes[i]["TotalTax"]
                    ):
                        pass
                    else:
                        line_amount == xero_quotes[i]["TotalAmount"] - line_amount1

                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}

                            rounding_SalesItemLineDetail["Qty"] = 1
                            if xero_quotes[i]["Subtotal"] > 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                    xero_quotes[i]["TotalAmount"] - line_amount1
                                )
                                rounding["Amount"] = (
                                    xero_quotes[i]["TotalAmount"] - line_amount1
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                    xero_quotes[i]["TotalAmount"] + line_amount1
                                )
                                rounding["Amount"] = (
                                    xero_quotes[i]["TotalAmount"] + line_amount1
                                )

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"
                            ] = rounding_SalesItemLineDetail
                            ItemRef["name"] = "Rounding"
                            ItemRef["value"] = "12886"
                            ItemAccountRef["name"] = "Sales Of Product Income"
                            ItemAccountRef["value"] = "81"
                            # TaxCodeRef['value'] = "5"
                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"
                            ] = ItemAccountRef
                            # TaxDetail['DetailType'] = "TaxLineDetail"
                            # TaxDetail['TaxLineDetail'] = TaxLineDetail
                            # TaxDetail['Amount'] = 0
                            # TaxLineDetail['NetAmountTaxable'] = rounding[
                            #     'Amount']
                            # TaxRate['value'] = '4'
                            # TaxLineDetail['TaxRateRef'] = TaxRate
                            # TaxLineDetail['PercentBased'] = True
                            # TxnTaxDetail['TaxLine'].append(TaxDetail)

                            quote["Line"].append(rounding)
                        else:
                            pass
            quote["Line"].append(subtotal)

            if quote["Line"][j]["SalesItemLineDetail"]["ItemRef"] != {}:
                #         if ((xero_quotes[i]['Line'][j]['ShipQuantity'] >= 0) and (xero_quotes[i]['Line'][j]['UnitPrice'] >= 0)) or ((xero_quotes[i]['Line'][j]['ShipQuantity'] < 0) and (xero_quotes[i]['Line'][j]['UnitPrice'] < 0)):
                url1 = "{}/estimate?minorversion=14".format(base_url)
                payload = json.dumps(quote)
                inv_date = xero_quotes[i]["Date"][0:10]
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
                                xero_quotes[i]["Number"]
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
                            xero_quotes[i]["Number"]
                        )
                        add_job_status(job_id, res2, "error")

            else:
                add_job_status(
                    job_id,
                    "Unable to add invoice because Item is not present in QBO : {}".format(
                        xero_quotes[i]["Number"]
                    ),
                    "error",
                )

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_item_quotes -> add_xero_item_quote", ex)
        
