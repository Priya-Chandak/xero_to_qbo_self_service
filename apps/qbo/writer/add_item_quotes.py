import json
import traceback
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job


def add_item_quote(job_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        item_quotes = db["item_quote"].find({"job_id":job_id})

        item_quote = []
        for p1 in item_quotes:
            item_quote.append(p1)

        item_quote = item_quote

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

        for i in range(0, len(item_quote)):
            _id=item_quote[i]['_id']
            task_id=item_quote[i]['task_id']
            
            quote = {"Line": []}
            CustomerRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            quote["TxnDate"] = item_quote[i]["Date"]
            quote["DocNumber"] = item_quote[i]["Number"]
            quote["TotalAmt"] = abs(item_quote[i]["TotalAmount"])
            quote["HomeTotalAmt"] = abs(item_quote[i]["TotalAmount"])

            subtotal = {}
            for p1 in range(0, len(QBO_customer)):
                if "Customer" in item_quote[i]:
                    if item_quote[i]["Customer"] == QBO_customer[p1]["DisplayName"]:
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                    
                    if "PrimaryEmailAddr" in QBO_customer[i]:
                        BillEmail["Address"] = QBO_customer[i]["PrimaryEmailAddr"][
                            "Address"
                        ]

            total_val = 0
            taxrate1 = 0
            line_amount = 0

            for j in range(len(item_quote[i]["Line"])):
                TaxLineDetail = {}
                CustomerMemo = {}
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
                    # SalesItemLineDetail['Description'] = item_quote[i]['Line'][p3]['description']
                    if item_quote[i]["Line"][j]["Item_Name"] == QBO_item[p3]["Name"]:
                        ItemRef["name"] = QBO_item[p3]["Name"]
                        ItemRef["value"] = QBO_item[p3]["Id"]

                    else:
                        pass

                for p4 in range(0, len(QBO_class)):
                    if item_quote[i]["Line"][j]["Job"] is not None:
                        if item_quote[i]["Line"][j]["Job"] == QBO_class[p4]["Name"]:
                            ClassRef["name"] = QBO_class[p4]["Name"]
                            ClassRef["value"] = QBO_class[p4]["Id"]
                        else:
                            pass

                for p5 in range(0, len(QBO_coa)):
                    if item_quote[i]["Line"][j]["Acc_Name"] == QBO_coa[p5]["Name"]:
                        ItemAccountRef["name"] = QBO_coa[p5]["Name"]
                        ItemAccountRef["value"] = QBO_coa[p5]["Id"]

                for p6 in range(0, len(QBO_tax)):
                    if item_quote[i]["Line"][j]["taxcode"] == "GST":
                        if "taxrate_name" in QBO_tax[p6]:
                            if "GST (sales)" in QBO_tax[p6]["taxrate_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val = (
                                        total_val
                                        + item_quote[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                    elif item_quote[i]["Line"][j]["taxcode"] == "CAP":
                        if "GST on capital" in QBO_tax[p6]["taxcode_name"]:
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                    item_quote[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                            )

                    elif item_quote[i]["Line"][j]["taxcode"] == "FRE":
                        if "taxrate_name" in QBO_tax[p6]:
                            if "GST free (sales)" in QBO_tax[p6]["taxrate_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                taxrate = QBO_tax[p6]["Rate"]
                                TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                taxrate1 = taxrate
                                total_val += (
                                        item_quote[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )

                    elif item_quote[i]["Line"][j]["taxcode"] == "N-T":
                        if "N-T" in QBO_tax[p6]["taxcode_name"]:
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                    item_quote[i]["Line"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                            )

                    elif (
                            item_quote[i]["Line"][j]["taxcode"]
                            == QBO_tax[p6]["taxcode_name"]
                    ):
                        TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                        taxrate = QBO_tax[p6]["Rate"]
                        TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                        TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                        taxrate1 = taxrate
                        total_val += (
                                item_quote[i]["Line"][j]["Total"] / (100 + taxrate1) * 100
                        )
                    else:
                        pass

                if item_quote[i]["IsTaxInclusive"] == True:
                    if item_quote[i]["Subtotal"] > 0:
                        SalesItemLineDetail["Qty"] = item_quote[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        #                 SalesItemLineDetail['UnitPrice'] = abs(item_quote[i]['Line'][j]['UnitPrice'])
                        SalesItemLineDetail["UnitPrice"] = round(
                            item_quote[i]["Line"][j]["UnitPrice"]
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
                            item_quote[i]["Subtotal"] - item_quote[i]["TotalTax"], 2
                        )
                        TxnTaxDetail["TotalTax"] = item_quote[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = 1
                        discount_SalesItemLineDetail["UnitPrice"] = -round(
                            (
                                    item_quote[i]["Line"][j]["ShipQuantity"]
                                    * item_quote[i]["Line"][j]["UnitPrice"]
                                    * item_quote[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )
                        DiscountPercent["Amount"] = -round(
                            (
                                    item_quote[i]["Line"][j]["ShipQuantity"]
                                    * item_quote[i]["Line"][j]["UnitPrice"]
                                    * item_quote[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )

                        if item_quote[i]["Line"][j]["taxcode"] == "GST":
                            TaxDetail["Amount"] = item_quote[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = round(
                                item_quote[i]["Line"][j]["Total"]
                                / (100 + taxrate1)
                                * 100,
                                2,
                            )
                        elif item_quote[i]["Line"][j]["taxcode"] == "FRE":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = item_quote[i]["Line"][
                                j
                            ]["Total"]
                        elif item_quote[i]["Line"][j]["taxcode"] == "N-T":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = item_quote[i]["Line"][
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
                        SalesItemLineDetail["Qty"] = -item_quote[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        #                 SalesItemLineDetail['UnitPrice'] = abs(item_quote[i]['Line'][j]['UnitPrice'])
                        SalesItemLineDetail["UnitPrice"] = round(
                            item_quote[i]["Line"][j]["UnitPrice"]
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
                                item_quote[i]["Subtotal"] - item_quote[i]["TotalTax"]
                        )
                        TxnTaxDetail["TotalTax"] = -item_quote[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = -1
                        discount_SalesItemLineDetail["UnitPrice"] = round(
                            (
                                    item_quote[i]["Line"][j]["ShipQuantity"]
                                    * item_quote[i]["Line"][j]["UnitPrice"]
                                    * item_quote[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )
                        DiscountPercent["Amount"] = round(
                            (
                                    item_quote[i]["Line"][j]["ShipQuantity"]
                                    * item_quote[i]["Line"][j]["UnitPrice"]
                                    * item_quote[i]["Line"][j]["DiscountPercent"]
                                    / (100 + taxrate1)
                            ),
                            2,
                        )

                        if item_quote[i]["Line"][j]["taxcode"] == "GST":
                            TaxDetail["Amount"] = -item_quote[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                    TaxDetail["Amount"] * taxrate1
                            )
                        elif item_quote[i]["Line"][j]["taxcode"] == "FRE":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = -item_quote[i]["Line"][
                                j
                            ]["Total"]
                        elif item_quote[i]["Line"][j]["taxcode"] == "N-T":
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = -item_quote[i]["Line"][
                                j
                            ]["Total"]
                        else:
                            pass

                        #                 salesitemline["Amount"] = abs(round(
                        #                     (item_quote[i]['Line'][j]['UnitPrice']*item_quote[i]['Line'][j]['ShipQuantity']/(100+taxrate1)*100), 2))
                        #                 subtotal['Amount'] = abs(round((total_val), 2))
                        quote["TxnTaxDetail"] = TxnTaxDetail
                        TaxDetail["DetailType"] = "TaxLineDetail"
                        TaxDetail["TaxLineDetail"] = TaxLineDetail
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True
                        TxnTaxDetail["TaxLine"].append(TaxDetail)

                    quote["GlobalTaxCalculation"] = "TaxInclusive"

                else:
                    if item_quote[i]["Subtotal"] > 0:
                        SalesItemLineDetail["Qty"] = item_quote[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        SalesItemLineDetail["UnitPrice"] = item_quote[i]["Line"][j][
                            "UnitPrice"
                        ]
                        salesitemline["Amount"] = round(
                            item_quote[i]["Line"][j]["UnitPrice"]
                            * item_quote[i]["Line"][j]["ShipQuantity"],
                            2,
                        )
                        subtotal["Amount"] = item_quote[i]["Subtotal"]
                        TxnTaxDetail["TotalTax"] = item_quote[i]["TotalTax"]
                        discount_SalesItemLineDetail["Qty"] = 1
                        discount_SalesItemLineDetail["UnitPrice"] = (
                                -(
                                        item_quote[i]["Line"][j]["ShipQuantity"]
                                        * item_quote[i]["Line"][j]["UnitPrice"]
                                        * item_quote[i]["Line"][j]["DiscountPercent"]
                                )
                                / 100
                        )
                        DiscountPercent["Amount"] = (
                                -(
                                        item_quote[i]["Line"][j]["ShipQuantity"]
                                        * item_quote[i]["Line"][j]["UnitPrice"]
                                        * item_quote[i]["Line"][j]["DiscountPercent"]
                                )
                                / 100
                        )

                        if taxrate1 != 0:
                            TaxDetail["Amount"] = item_quote[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                    item_quote[i]["Subtotal"] - item_quote[i]["TotalTax"]
                            )
                        else:
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = 0

                    else:
                        discount_SalesItemLineDetail["Qty"] = -1
                        discount_SalesItemLineDetail["UnitPrice"] = (
                                                                            item_quote[i]["Line"][j]["ShipQuantity"]
                                                                            * item_quote[i]["Line"][j]["UnitPrice"]
                                                                            * item_quote[i]["Line"][j][
                                                                                "DiscountPercent"]
                                                                    ) / 100
                        DiscountPercent["Amount"] = (
                                                            item_quote[i]["Line"][j]["ShipQuantity"]
                                                            * item_quote[i]["Line"][j]["UnitPrice"]
                                                            * item_quote[i]["Line"][j]["DiscountPercent"]
                                                    ) / 100

                        SalesItemLineDetail["Qty"] = -item_quote[i]["Line"][j][
                            "ShipQuantity"
                        ]
                        SalesItemLineDetail["UnitPrice"] = item_quote[i]["Line"][j][
                            "UnitPrice"
                        ]
                        salesitemline["Amount"] = round(
                            item_quote[i]["Line"][j]["UnitPrice"]
                            * item_quote[i]["Line"][j]["ShipQuantity"],
                            2,
                        )
                        subtotal["Amount"] = -item_quote[i]["Subtotal"]
                        TxnTaxDetail["TotalTax"] = -item_quote[i]["TotalTax"]

                        if taxrate1 != 0:
                            TaxDetail["Amount"] = item_quote[i]["TotalTax"]
                            TaxLineDetail["NetAmountTaxable"] = (
                                    item_quote[i]["Subtotal"] - item_quote[i]["TotalTax"]
                            )
                        else:
                            if item_quote[i]["Line"][j]["taxcode"] == "GST":
                                TaxDetail["Amount"] = -item_quote[i]["TotalTax"]
                                TaxLineDetail["NetAmountTaxable"] = (
                                        -item_quote[i]["Line"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100
                                )
                            elif item_quote[i]["Line"][j]["taxcode"] == "FRE":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = -item_quote[i][
                                    "Line"
                                ][j]["Total"]
                            elif item_quote[i]["Line"][j]["taxcode"] == "N-T":
                                TaxDetail["Amount"] = 0
                                TaxLineDetail["NetAmountTaxable"] = -item_quote[i][
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

                if item_quote[i]["Line"][j]["DiscountPercent"] > 0:
                    quote["Line"].append(DiscountPercent)

                line_amount = (
                        line_amount + salesitemline["Amount"] + DiscountPercent["Amount"]
                )
                line_amount1 = line_amount + item_quote[i]["TotalTax"]

            a = []

            for p2 in range(0, len(TxnTaxDetail["TaxLine"])):
                if TxnTaxDetail["TaxLine"][p2] in a:
                    pass
                else:
                    a.append(TxnTaxDetail["TaxLine"][p2])

            # TxnTaxDetail['TaxLine'] = a

            if len(a) >= 1:
                if item_quote[i]["IsTaxInclusive"]:
                    if line_amount1 == item_quote[i]["TotalAmount"]:
                        pass
                    else:
                        line_amount == item_quote[i]["TotalAmount"] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            # TaxCodeRef = {}
                            ItemAccountRef = {}
                            rounding_SalesItemLineDetail["Qty"] = 1

                            if item_quote[i]["Subtotal"] > 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = round(
                                    abs(item_quote[i]["TotalAmount"]) - line_amount1, 2
                                )
                                rounding["Amount"] = round(
                                    abs(item_quote[i]["TotalAmount"]) - line_amount1, 2
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = round(
                                    abs(
                                        item_quote[i]["TotalAmount"]
                                        - item_quote[i]["TotalTax"]
                                    )
                                    - line_amount,
                                    2,
                                )
                                rounding["Amount"] = round(
                                    abs(
                                        item_quote[i]["TotalAmount"]
                                        - item_quote[i]["TotalTax"]
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
                            == item_quote[i]["TotalAmount"] + item_quote[i]["TotalTax"]
                    ):
                        pass
                    else:
                        line_amount == item_quote[i]["TotalAmount"] - line_amount1

                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}

                            rounding_SalesItemLineDetail["Qty"] = 1
                            if item_quote[i]["Subtotal"] > 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                        item_quote[i]["TotalAmount"] - line_amount1
                                )
                                rounding["Amount"] = (
                                        item_quote[i]["TotalAmount"] - line_amount1
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                        item_quote[i]["TotalAmount"] + line_amount1
                                )
                                rounding["Amount"] = (
                                        item_quote[i]["TotalAmount"] + line_amount1
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
                #         if ((item_quote[i]['Line'][j]['ShipQuantity'] >= 0) and (item_quote[i]['Line'][j]['UnitPrice'] >= 0)) or ((item_quote[i]['Line'][j]['ShipQuantity'] < 0) and (item_quote[i]['Line'][j]['UnitPrice'] < 0)):
                url1 = "{}/estimate?minorversion=14".format(base_url)
                payload = json.dumps(quote)
                inv_date = item_quote[i]["Date"][0:10]
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
                                item_quote[i]["Number"]
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
                            item_quote[i]["Number"]
                        )
                        add_job_status(job_id, res2, "error")

            else:
                add_job_status(
                    job_id,
                    "Unable to add invoice because Item is not present in QBO : {}".format(
                        item_quote[i]["Number"]
                    ),
                    "error",
                )

    except Exception as ex:
        traceback.print_exc()
        
