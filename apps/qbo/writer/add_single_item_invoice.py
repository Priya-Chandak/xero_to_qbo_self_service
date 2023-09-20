import json
import traceback
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job, post_data_in_qbo


def add_single_item_invoice(job_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        url1 = f"{base_url}/invoice?minorversion={minorversion}"
        single_item_invoice = db["single_item_invoice"].find({"job_id":job_id})

        single = []
        for p1 in single_item_invoice:
            single.append(p1)

        Q1 = single

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

        d = []
        for i in range(0, len(Q1)):
            invoice = {"Line": []}
            itemDetail = {}
            Tax = {}
            SubTotalLine = {}
            discountDetail = {}
            ClassRef = {}
            CustomerMemo = {}
            CustomerRef = {}
            BillEmail = {}
            ItemRef = {}
            SalesItemLineDetail = {}
            discountSalesItemLineDetail = {}
            TaxCodeRef = {}
            ItemAccountRef = {}
            TxnTaxDetail = {"TaxLine": []}
            TaxLineDetail = {}
            TaxRate = {}
            SubTotalLineDetail = {}

            if Q1[i]["IsTaxInclusive"] == True:
                invoice["GlobalTaxCalculation"] = "TaxInclusive"
            else:
                invoice["GlobalTaxCalculation"] = "TaxExcluded"

            if Q1[i]["invoice_no"] in d:
                invoice["DocNumber"] = Q1[i]["invoice_no"] + "-" + Q1[i]["UID"][-4:]
            else:
                invoice["DocNumber"] = Q1[i]["invoice_no"]

            taxrate1 = 0

            for k1 in range(0, len(Q1[i]["Item"])):
                # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                #         Q1[i]['Item'][k1]['ship_quantity']=1

                if Q1[i]["Item"][k1]["unit_price"] == 0:
                    Q1[i]["Item"][k1]["unit_price"] = Q1[i]["Item"][k1]["amount"]

                for j in range(0, len(QBO_item)):
                    if QBO_item[j]["Type"] == "NonInventory":
                        if "Item" in Q1[i]:
                            for j4 in range(0, len(QBO_tax)):
                                if Q1[i]["Item"][k1]["taxcode"] == "GST":
                                    if "taxrate_name" in QBO_tax[j4]:
                                        if "GST (sales)" in QBO_tax[j4]["taxrate_name"]:
                                            TaxCodeRef["value"] = QBO_tax[j4][
                                                "taxcode_id"
                                            ]
                                            taxrate = QBO_tax[j4]["Rate"]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                                "Rate"
                                            ]
                                            TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                            taxrate1 = taxrate

                                elif Q1[i]["Item"][k1]["taxcode"] == "CAP":
                                    if "GST on capital" in QBO_tax[j4]["taxcode_name"]:
                                        TaxCodeRef["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                            "Rate"
                                        ]
                                        TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                        taxrate1 = taxrate

                                elif Q1[i]["Item"][k1]["taxcode"] == "FRE":
                                    if "taxrate_name" in QBO_tax[j4]:
                                        if (
                                                "GST free (sales)"
                                                in QBO_tax[j4]["taxrate_name"]
                                        ):
                                            TaxCodeRef["value"] = QBO_tax[j4][
                                                "taxcode_id"
                                            ]
                                            taxrate = QBO_tax[j4]["Rate"]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                                "Rate"
                                            ]
                                            TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                            taxrate1 = taxrate

                                elif Q1[i]["Item"][k1]["taxcode"] == "N-T":
                                    if "taxrate_name" in QBO_tax[j4]:
                                        if "NOTAXS" in QBO_tax[j4]["taxrate_name"]:
                                            TaxCodeRef["value"] = QBO_tax[j4][
                                                "taxcode_id"
                                            ]
                                            taxrate = QBO_tax[j4]["Rate"]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                                "Rate"
                                            ]
                                            TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                            taxrate1 = taxrate

                                elif (
                                        Q1[i]["Item"][k1]["taxcode"]
                                        == QBO_tax[j4]["taxcode_name"]
                                ):
                                    TaxCodeRef["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                    taxrate1 = taxrate

                            # if Q1[i]['Item'][k1]["item_name"] == QBO_item[j]["Name"]:
                            if "item_name" in Q1[i]["Item"][k1]:
                                if (
                                        Q1[i]["Item"][k1]["item_name"]
                                        == QBO_item[j]["Name"]
                                ):
                                    if Q1[i]["IsTaxInclusive"] == False:
                                        # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                                        itemDetail["Amount"] = abs(
                                            Q1[i]["Item"][k1]["ship_quantity"]
                                            * Q1[i]["Item"][k1]["unit_price"]
                                        )
                                        discountDetail["Amount"] = (
                                                -(
                                                        Q1[i]["Item"][k1]["ship_quantity"]
                                                        * Q1[i]["Item"][k1]["unit_price"]
                                                        * Q1[i]["Item"][k1]["discount"]
                                                )
                                                / 100
                                        )
                                        discountSalesItemLineDetail["Qty"] = 1
                                        discountSalesItemLineDetail["UnitPrice"] = (
                                                -(
                                                        Q1[i]["Item"][k1]["ship_quantity"]
                                                        * Q1[i]["Item"][k1]["unit_price"]
                                                        * Q1[i]["Item"][k1]["discount"]
                                                )
                                                / 100
                                        )
                                        SalesItemLineDetail["Qty"] = Q1[i]["Item"][k1][
                                            "ship_quantity"
                                        ]
                                        SalesItemLineDetail["UnitPrice"] = abs(
                                            Q1[i]["Item"][k1]["unit_price"]
                                        )
                                        SubTotalLine["Amount"] = abs(
                                            Q1[i]["Item"][k1]["amount"]
                                        )
                                        TaxLineDetail["NetAmountTaxable"] = abs(
                                            Q1[i]["Subtotal"]
                                        )
                                        # else:

                                        #     itemDetail["Amount"] = abs(
                                        #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price'])
                                        #     discountDetail['Amount'] = -(
                                        #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']*Q1[i]['Item'][k1]['discount'])/100
                                        #     discountSalesItemLineDetail['Qty'] = 1
                                        #     discountSalesItemLineDetail['UnitPrice'] = -(
                                        #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']*Q1[i]['Item'][k1]['discount'])/100
                                        #     SalesItemLineDetail['Qty'] = Q1[i]['Item'][k1]['ship_quantity']
                                        #     SalesItemLineDetail['UnitPrice'] = abs(
                                        #         Q1[i]['Item'][k1]['unit_price'])
                                        #     SubTotalLine['Amount'] = abs(
                                        #         Q1[i]['Item'][k1]['amount'])
                                        #     TaxLineDetail['NetAmountTaxable'] = abs(
                                        #         Q1[i]['Subtotal'])
                                    else:
                                        # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                                        itemDetail["Amount"] = abs(
                                            round(
                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                * Q1[i]["Item"][k1]["unit_price"]
                                                / (100 + taxrate1)
                                                * 100,
                                                2,
                                            )
                                        )
                                        discountDetail["Amount"] = -round(
                                            (
                                                    (
                                                            (
                                                                    Q1[i]["Item"][k1][
                                                                        "ship_quantity"
                                                                    ]
                                                                    * Q1[i]["Item"][k1][
                                                                        "unit_price"
                                                                    ]
                                                            )
                                                            - Q1[i]["Item"][k1]["amount"]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            2,
                                        )
                                        discountSalesItemLineDetail["Qty"] = 1
                                        discountSalesItemLineDetail[
                                            "UnitPrice"
                                        ] = -round(
                                            (
                                                    (
                                                            (
                                                                    Q1[i]["Item"][k1][
                                                                        "ship_quantity"
                                                                    ]
                                                                    * Q1[i]["Item"][k1][
                                                                        "unit_price"
                                                                    ]
                                                            )
                                                            - Q1[i]["Item"][k1]["amount"]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            2,
                                        )
                                        SalesItemLineDetail["Qty"] = Q1[i]["Item"][k1][
                                            "ship_quantity"
                                        ]
                                        SalesItemLineDetail["UnitPrice"] = abs(
                                            round(
                                                (
                                                        Q1[i]["Item"][k1]["unit_price"]
                                                        / (100 + taxrate1)
                                                        * 100
                                                ),
                                                3,
                                            )
                                        )
                                        SubTotalLine["Amount"] = abs(
                                            round(
                                                (
                                                        Q1[i]["Item"][k1]["amount"]
                                                        / (100 + taxrate1)
                                                        * 100
                                                ),
                                                2,
                                            )
                                        )
                                        TaxLineDetail["NetAmountTaxable"] = round(
                                            Q1[i]["Subtotal"] / (100 + taxrate1) * 100,
                                            2,
                                        )
                                        # else:
                                        #     itemDetail["Amount"] = abs(round(
                                        #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100, 2))
                                        #     discountDetail['Amount'] = -round((((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]
                                        #                                         ['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                        #     discountSalesItemLineDetail['Qty'] = 1
                                        #     discountSalesItemLineDetail['UnitPrice'] = -round(
                                        #         (((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                        #     SalesItemLineDetail['Qty'] = Q1[i]['Item'][k1]['ship_quantity']
                                        #     SalesItemLineDetail['UnitPrice'] = abs(
                                        #         round((Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100), 3))
                                        #     SubTotalLine['Amount'] = abs(
                                        #         round((Q1[i]['Item'][k1]['amount']/(100+taxrate1)*100), 2))
                                        #     TaxLineDetail['NetAmountTaxable'] = round(
                                        #         Q1[i]['Subtotal']/(100+taxrate1)*100, 2)

                                    # if 'Description' in Q1[i]['Item'][k1]:
                                    #     itemDetail["Description"] = Q1[i]['Item'][k1]["description"]
                                    # else:
                                    #     itemDetail["Description"] = None

                                    discountDetail["Description"] = "Discount"

                                    ItemRef["value"] = QBO_item[j]["Id"]
                                    ItemRef["name"] = QBO_item[j]["Name"]

                            elif Q1[i]["Item"][k1]["DisplayID"] == QBO_item[j]["Name"]:
                                if Q1[i]["IsTaxInclusive"] == False:
                                    # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                                    itemDetail["Amount"] = abs(
                                        Q1[i]["Item"][k1]["ship_quantity"]
                                        * Q1[i]["Item"][k1]["unit_price"]
                                    )
                                    discountDetail["Amount"] = (
                                            -(
                                                    Q1[i]["Item"][k1]["ship_quantity"]
                                                    * Q1[i]["Item"][k1]["unit_price"]
                                                    * Q1[i]["Item"][k1]["discount"]
                                            )
                                            / 100
                                    )
                                    discountSalesItemLineDetail["Qty"] = 1
                                    discountSalesItemLineDetail["UnitPrice"] = (
                                            -(
                                                    Q1[i]["Item"][k1]["ship_quantity"]
                                                    * Q1[i]["Item"][k1]["unit_price"]
                                                    * Q1[i]["Item"][k1]["discount"]
                                            )
                                            / 100
                                    )
                                    SalesItemLineDetail["Qty"] = Q1[i]["Item"][k1][
                                        "ship_quantity"
                                    ]
                                    SalesItemLineDetail["UnitPrice"] = abs(
                                        Q1[i]["Item"][k1]["unit_price"]
                                    )
                                    SubTotalLine["Amount"] = abs(
                                        Q1[i]["Item"][k1]["amount"]
                                    )
                                    TaxLineDetail["NetAmountTaxable"] = abs(
                                        Q1[i]["Subtotal"]
                                    )
                                    # else:
                                    #     itemDetail["Amount"] = abs(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price'])
                                    #     discountDetail['Amount'] = -(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']*Q1[i]['Item'][k1]['discount'])/100
                                    #     discountSalesItemLineDetail['Qty'] = 1
                                    #     discountSalesItemLineDetail['UnitPrice'] = -(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']*Q1[i]['Item'][k1]['discount'])/100
                                    #     SalesItemLineDetail['Qty'] = Q1[i]['Item'][k1]['ship_quantity']
                                    #     SalesItemLineDetail['UnitPrice'] = abs(
                                    #         Q1[i]['Item'][k1]['unit_price'])
                                    #     SubTotalLine['Amount'] = abs(
                                    #         Q1[i]['Item'][k1]['amount'])
                                    #     TaxLineDetail['NetAmountTaxable'] = abs(
                                    #         Q1[i]['Subtotal'])
                                else:
                                    # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                                    itemDetail["Amount"] = abs(
                                        round(
                                            Q1[i]["Item"][k1]["ship_quantity"]
                                            * Q1[i]["Item"][k1]["unit_price"]
                                            / (100 + taxrate1)
                                            * 100,
                                            2,
                                        )
                                    )
                                    discountDetail["Amount"] = -round(
                                        (
                                                (
                                                        (
                                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                                * Q1[i]["Item"][k1]["unit_price"]
                                                        )
                                                        - Q1[i]["Item"][k1]["amount"]
                                                )
                                                / (100 + taxrate1)
                                                * 100
                                        ),
                                        2,
                                    )
                                    discountSalesItemLineDetail["Qty"] = 1
                                    discountSalesItemLineDetail["UnitPrice"] = -round(
                                        (
                                                (
                                                        (
                                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                                * Q1[i]["Item"][k1]["unit_price"]
                                                        )
                                                        - Q1[i]["Item"][k1]["amount"]
                                                )
                                                / (100 + taxrate1)
                                                * 100
                                        ),
                                        2,
                                    )
                                    SalesItemLineDetail["Qty"] = Q1[i]["Item"][k1][
                                        "ship_quantity"
                                    ]
                                    SalesItemLineDetail["UnitPrice"] = abs(
                                        round(
                                            (
                                                    Q1[i]["Item"][k1]["unit_price"]
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            3,
                                        )
                                    )
                                    SubTotalLine["Amount"] = abs(
                                        round(
                                            (
                                                    Q1[i]["Item"][k1]["amount"]
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            2,
                                        )
                                    )
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        Q1[i]["Subtotal"] / (100 + taxrate1) * 100, 2
                                    )
                                    # else:
                                    #     itemDetail["Amount"] = abs(round(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100, 2))
                                    #     discountDetail['Amount'] = -round((((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]
                                    #                                         ['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                    #     discountSalesItemLineDetail['Qty'] = 1
                                    #     discountSalesItemLineDetail['UnitPrice'] = -round(
                                    #         (((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                    #     SalesItemLineDetail['Qty'] = Q1[i]['Item'][k1]['ship_quantity']
                                    #     SalesItemLineDetail['UnitPrice'] = abs(
                                    #         round((Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100), 3))
                                    #     SubTotalLine['Amount'] = abs(
                                    #         round((Q1[i]['Item'][k1]['amount']/(100+taxrate1)*100), 2))
                                    #     TaxLineDetail['NetAmountTaxable'] = round(
                                    #         Q1[i]['Subtotal']/(100+taxrate1)*100, 2)

                                # if 'Description' in Q1[i]['Item'][k1]:
                                #     itemDetail["Description"] = Q1[i]['Item'][k1]["description"]
                                # else:
                                #     itemDetail["Description"] = None

                                discountDetail["Description"] = "Discount"

                                ItemRef["value"] = QBO_item[j]["Id"]
                                ItemRef["name"] = QBO_item[j]["Name"]

                    # elif QBO_item[j]["Type"] == "Service":
                    #     for j3 in range(0,len(QBO_item)):
                    #         if 'item_name' in Q1[i]['Item'][k1]:
                    #             if Q1[i]['Item'][k1]["item_name"] == QBO_item[j3]["FullyQualifiedName"]:
                    #                 ItemRef["value"] = QBO_item[j3]["Id"]
                    #                 ItemRef["name"] = QBO_item[j3]["Name"]

                    #         else:
                    #             if Q1[i]['Item'][k1]["DisplayID"] == QBO_item[j3]["FullyQualifiedName"]:
                    #                 ItemRef["value"] = QBO_item[j3]["Id"]
                    #                 ItemRef["name"] = QBO_item[j3]["Name"]

                    elif QBO_item[j]["Type"] == "Service":
                        if "Item" in Q1[i]:
                            for j4 in range(0, len(QBO_tax)):
                                if Q1[i]["Item"][k1]["taxcode"] == "GST":
                                    if "taxrate_name" in QBO_tax[j4]:
                                        if "GST (sales)" in QBO_tax[j4]["taxrate_name"]:
                                            TaxCodeRef["value"] = QBO_tax[j4][
                                                "taxcode_id"
                                            ]
                                            taxrate = QBO_tax[j4]["Rate"]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                                "Rate"
                                            ]
                                            TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                            taxrate1 = taxrate

                                elif Q1[i]["Item"][k1]["taxcode"] == "CAP":
                                    if "GST on capital" in QBO_tax[j4]["taxcode_name"]:
                                        TaxCodeRef["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                            "Rate"
                                        ]
                                        TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                        taxrate1 = taxrate

                                elif Q1[i]["Item"][k1]["taxcode"] == "FRE":
                                    if "taxrate_name" in QBO_tax[j4]:
                                        if (
                                                "GST free (sales)"
                                                in QBO_tax[j4]["taxrate_name"]
                                        ):
                                            TaxCodeRef["value"] = QBO_tax[j4][
                                                "taxcode_id"
                                            ]
                                            taxrate = QBO_tax[j4]["Rate"]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                                "Rate"
                                            ]
                                            TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                            taxrate1 = taxrate

                                elif Q1[i]["Item"][k1]["taxcode"] == "N-T":
                                    if "taxrate_name" in QBO_tax[j4]:
                                        if "NOTAXS" in QBO_tax[j4]["taxrate_name"]:
                                            TaxCodeRef["value"] = QBO_tax[j4][
                                                "taxcode_id"
                                            ]
                                            taxrate = QBO_tax[j4]["Rate"]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[j4][
                                                "Rate"
                                            ]
                                            TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                            taxrate1 = taxrate

                                elif (
                                        Q1[i]["Item"][k1]["taxcode"]
                                        == QBO_tax[j4]["taxcode_name"]
                                ):
                                    TaxCodeRef["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    TaxRate["value"] = QBO_tax[j4]["taxrate_id"]
                                    taxrate1 = taxrate

                            # if Q1[i]['Item'][k1]["item_name"] == QBO_item[j]["Name"]:
                            if "item_name" in Q1[i]["Item"][k1]:
                                if (
                                        Q1[i]["Item"][k1]["item_name"]
                                        == QBO_item[j]["Name"]
                                ):
                                    if Q1[i]["IsTaxInclusive"] == False:
                                        if Q1[i]["Item"][k1]["ship_quantity"] == 0:
                                            itemDetail["Amount"] = abs(
                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                * Q1[i]["Item"][k1]["unit_price"]
                                            )
                                            discountDetail["Amount"] = (
                                                    -(
                                                            Q1[i]["Item"][k1]["ship_quantity"]
                                                            * Q1[i]["Item"][k1]["unit_price"]
                                                            * Q1[i]["Item"][k1]["discount"]
                                                    )
                                                    / 100
                                            )
                                            discountSalesItemLineDetail["Qty"] = 1
                                            discountSalesItemLineDetail["UnitPrice"] = (
                                                    -(
                                                            Q1[i]["Item"][k1]["ship_quantity"]
                                                            * Q1[i]["Item"][k1]["unit_price"]
                                                            * Q1[i]["Item"][k1]["discount"]
                                                    )
                                                    / 100
                                            )
                                            SalesItemLineDetail["Qty"] = Q1[i]["Item"][
                                                k1
                                            ]["ship_quantity"]
                                            SalesItemLineDetail["UnitPrice"] = abs(
                                                Q1[i]["Item"][k1]["unit_price"]
                                            )
                                            SubTotalLine["Amount"] = abs(
                                                Q1[i]["Item"][k1]["amount"]
                                            )
                                            TaxLineDetail["NetAmountTaxable"] = abs(
                                                Q1[i]["Subtotal"]
                                            )
                                        else:
                                            itemDetail["Amount"] = abs(
                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                * Q1[i]["Item"][k1]["unit_price"]
                                            )
                                            discountDetail["Amount"] = (
                                                    -(
                                                            Q1[i]["Item"][k1]["ship_quantity"]
                                                            * Q1[i]["Item"][k1]["unit_price"]
                                                            * Q1[i]["Item"][k1]["discount"]
                                                    )
                                                    / 100
                                            )
                                            discountSalesItemLineDetail["Qty"] = 1
                                            discountSalesItemLineDetail["UnitPrice"] = (
                                                    -(
                                                            Q1[i]["Item"][k1]["ship_quantity"]
                                                            * Q1[i]["Item"][k1]["unit_price"]
                                                            * Q1[i]["Item"][k1]["discount"]
                                                    )
                                                    / 100
                                            )
                                            SalesItemLineDetail["Qty"] = Q1[i]["Item"][
                                                k1
                                            ]["ship_quantity"]
                                            SalesItemLineDetail["UnitPrice"] = abs(
                                                Q1[i]["Item"][k1]["unit_price"]
                                            )
                                            SubTotalLine["Amount"] = abs(
                                                Q1[i]["Item"][k1]["amount"]
                                            )
                                            TaxLineDetail["NetAmountTaxable"] = abs(
                                                Q1[i]["Subtotal"]
                                            )
                                    else:
                                        # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                                        itemDetail["Amount"] = abs(
                                            round(
                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                * Q1[i]["Item"][k1]["unit_price"]
                                                / (100 + taxrate1)
                                                * 100,
                                                2,
                                            )
                                        )
                                        discountDetail["Amount"] = -round(
                                            (
                                                    (
                                                            (
                                                                    Q1[i]["Item"][k1][
                                                                        "ship_quantity"
                                                                    ]
                                                                    * Q1[i]["Item"][k1][
                                                                        "unit_price"
                                                                    ]
                                                            )
                                                            - Q1[i]["Item"][k1]["amount"]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            2,
                                        )
                                        discountSalesItemLineDetail["Qty"] = 1
                                        discountSalesItemLineDetail[
                                            "UnitPrice"
                                        ] = -round(
                                            (
                                                    (
                                                            (
                                                                    Q1[i]["Item"][k1][
                                                                        "ship_quantity"
                                                                    ]
                                                                    * Q1[i]["Item"][k1][
                                                                        "unit_price"
                                                                    ]
                                                            )
                                                            - Q1[i]["Item"][k1]["amount"]
                                                    )
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            2,
                                        )
                                        SalesItemLineDetail["Qty"] = Q1[i]["Item"][k1][
                                            "ship_quantity"
                                        ]
                                        SalesItemLineDetail["UnitPrice"] = abs(
                                            round(
                                                (
                                                        Q1[i]["Item"][k1]["unit_price"]
                                                        / (100 + taxrate1)
                                                        * 100
                                                ),
                                                3,
                                            )
                                        )
                                        SubTotalLine["Amount"] = abs(
                                            round(
                                                (
                                                        Q1[i]["Item"][k1]["amount"]
                                                        / (100 + taxrate1)
                                                        * 100
                                                ),
                                                2,
                                            )
                                        )
                                        TaxLineDetail["NetAmountTaxable"] = round(
                                            Q1[i]["Subtotal"] / (100 + taxrate1) * 100,
                                            2,
                                        )
                                        # else:
                                        #     itemDetail["Amount"] = abs(round(
                                        #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100, 2))
                                        #     discountDetail['Amount'] = -round((((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]
                                        #                                         ['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                        #     discountSalesItemLineDetail['Qty'] = 1
                                        #     discountSalesItemLineDetail['UnitPrice'] = -round(
                                        #         (((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                        #     SalesItemLineDetail['Qty'] = Q1[i]['Item'][k1]['ship_quantity']
                                        #     SalesItemLineDetail['UnitPrice'] = abs(
                                        #         round((Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100), 3))
                                        #     SubTotalLine['Amount'] = abs(
                                        #         round((Q1[i]['Item'][k1]['amount']/(100+taxrate1)*100), 2))
                                        #     TaxLineDetail['NetAmountTaxable'] = round(
                                        #         Q1[i]['Subtotal']/(100+taxrate1)*100, 2)

                                    # if 'Description' in Q1[i]['Item'][k1]:
                                    #     itemDetail["Description"] = Q1[i]['Item'][k1]["description"]
                                    # else:
                                    #     itemDetail["Description"] = None

                                    discountDetail["Description"] = "Discount"

                                    ItemRef["value"] = QBO_item[j]["Id"]
                                    ItemRef["name"] = QBO_item[j]["Name"]

                            elif Q1[i]["Item"][k1]["DisplayID"] == QBO_item[j]["Name"]:
                                if Q1[i]["IsTaxInclusive"] == False:
                                    # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                                    itemDetail["Amount"] = abs(
                                        Q1[i]["Item"][k1]["ship_quantity"]
                                        * Q1[i]["Item"][k1]["unit_price"]
                                    )
                                    discountDetail["Amount"] = (
                                            -(
                                                    Q1[i]["Item"][k1]["ship_quantity"]
                                                    * Q1[i]["Item"][k1]["unit_price"]
                                                    * Q1[i]["Item"][k1]["discount"]
                                            )
                                            / 100
                                    )
                                    discountSalesItemLineDetail["Qty"] = 1
                                    discountSalesItemLineDetail["UnitPrice"] = (
                                            -(
                                                    Q1[i]["Item"][k1]["ship_quantity"]
                                                    * Q1[i]["Item"][k1]["unit_price"]
                                                    * Q1[i]["Item"][k1]["discount"]
                                            )
                                            / 100
                                    )
                                    SalesItemLineDetail["Qty"] = Q1[i]["Item"][k1][
                                        "ship_quantity"
                                    ]
                                    SalesItemLineDetail["UnitPrice"] = abs(
                                        Q1[i]["Item"][k1]["unit_price"]
                                    )
                                    SubTotalLine["Amount"] = abs(
                                        Q1[i]["Item"][k1]["amount"]
                                    )
                                    TaxLineDetail["NetAmountTaxable"] = abs(
                                        Q1[i]["Subtotal"]
                                    )
                                    # else:
                                    #     itemDetail["Amount"] = abs(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price'])
                                    #     discountDetail['Amount'] = -(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']*Q1[i]['Item'][k1]['discount'])/100
                                    #     discountSalesItemLineDetail['Qty'] = 1
                                    #     discountSalesItemLineDetail['UnitPrice'] = -(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']*Q1[i]['Item'][k1]['discount'])/100
                                    #     SalesItemLineDetail['Qty'] = Q1[i]['Item'][k1]['ship_quantity']
                                    #     SalesItemLineDetail['UnitPrice'] = abs(
                                    #         Q1[i]['Item'][k1]['unit_price'])
                                    #     SubTotalLine['Amount'] = abs(
                                    #         Q1[i]['Item'][k1]['amount'])
                                    #     TaxLineDetail['NetAmountTaxable'] = abs(
                                    #         Q1[i]['Subtotal'])
                                else:
                                    # if Q1[i]['Item'][k1]['ship_quantity'] == 0:
                                    itemDetail["Amount"] = abs(
                                        round(
                                            Q1[i]["Item"][k1]["ship_quantity"]
                                            * Q1[i]["Item"][k1]["unit_price"]
                                            / (100 + taxrate1)
                                            * 100,
                                            2,
                                        )
                                    )
                                    discountDetail["Amount"] = -round(
                                        (
                                                (
                                                        (
                                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                                * Q1[i]["Item"][k1]["unit_price"]
                                                        )
                                                        - Q1[i]["Item"][k1]["amount"]
                                                )
                                                / (100 + taxrate1)
                                                * 100
                                        ),
                                        2,
                                    )
                                    discountSalesItemLineDetail["Qty"] = 1
                                    discountSalesItemLineDetail["UnitPrice"] = -round(
                                        (
                                                (
                                                        (
                                                                Q1[i]["Item"][k1]["ship_quantity"]
                                                                * Q1[i]["Item"][k1]["unit_price"]
                                                        )
                                                        - Q1[i]["Item"][k1]["amount"]
                                                )
                                                / (100 + taxrate1)
                                                * 100
                                        ),
                                        2,
                                    )
                                    SalesItemLineDetail["Qty"] = Q1[i]["Item"][k1][
                                        "ship_quantity"
                                    ]
                                    SalesItemLineDetail["UnitPrice"] = abs(
                                        round(
                                            (
                                                    Q1[i]["Item"][k1]["unit_price"]
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            3,
                                        )
                                    )
                                    SubTotalLine["Amount"] = abs(
                                        round(
                                            (
                                                    Q1[i]["Item"][k1]["amount"]
                                                    / (100 + taxrate1)
                                                    * 100
                                            ),
                                            2,
                                        )
                                    )
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        Q1[i]["Subtotal"] / (100 + taxrate1) * 100, 2
                                    )
                                    # else:
                                    #     itemDetail["Amount"] = abs(round(
                                    #         Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100, 2))
                                    #     discountDetail['Amount'] = -round((((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]
                                    #                                         ['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                    #     discountSalesItemLineDetail['Qty'] = 1
                                    #     discountSalesItemLineDetail['UnitPrice'] = -round(
                                    #         (((Q1[i]['Item'][k1]['ship_quantity']*Q1[i]['Item'][k1]['unit_price'])-Q1[i]['Item'][k1]['amount'])/(100+taxrate1)*100), 2)
                                    #     SalesItemLineDetail['Qty'] = Q1[i]['Item'][k1]['ship_quantity']
                                    #     SalesItemLineDetail['UnitPrice'] = abs(
                                    #         round((Q1[i]['Item'][k1]['unit_price']/(100+taxrate1)*100), 3))
                                    #     SubTotalLine['Amount'] = abs(
                                    #         round((Q1[i]['Item'][k1]['amount']/(100+taxrate1)*100), 2))
                                    #     TaxLineDetail['NetAmountTaxable'] = round(
                                    #         Q1[i]['Subtotal']/(100+taxrate1)*100, 2)

                                # if 'Description' in Q1[i]['Item'][k1]:
                                #     itemDetail["Description"] = Q1[i]['Item'][k1]["description"]
                                # else:
                                #     itemDetail["Description"] = None

                                discountDetail["Description"] = "Discount"

                                ItemRef["value"] = QBO_item[j]["Id"]
                                ItemRef["name"] = QBO_item[j]["Name"]

                    for m in range(0, len(QBO_class)):
                        if Q1[i]["Item"][k1]["job"] is not None:
                            if Q1[i]["Item"][k1]["job"] == QBO_class[m]["Name"]:
                                ClassRef["name"] = QBO_class[m]["Name"]
                                ClassRef["value"] = QBO_class[m]["Id"]
                            else:
                                pass

                    for j1 in range(0, len(QBO_coa)):
                        if Q1[i]["Item"][k1]["account_name"] == QBO_coa[j1]["Name"]:
                            ItemAccountRef["name"] = QBO_coa[j1]["Name"]
                            ItemAccountRef["value"] = QBO_coa[j1]["Id"]

                if "comment" in Q1[i]["Item"][k1]:
                    if Q1[i]["Item"][k1]["comment"] is not None:
                        CustomerMemo["value"] = Q1[i]["Item"][k1]["comment"]
                        invoice["PrivateNote"] = Q1[i]["Item"][k1]["comment"]

                for k in range(0, len(QBO_customer)):
                    itemDetail["DetailType"] = "SalesItemLineDetail"
                    discountDetail["DetailType"] = "SalesItemLineDetail"

                    if "customer_name" in Q1[i]:
                        if (
                                Q1[i]["customer_name"].strip()
                                == QBO_customer[k]["DisplayName"].strip()
                        ):
                            CustomerRef["value"] = QBO_customer[k]["Id"]
                            CustomerRef["name"] = QBO_customer[k]["DisplayName"]
                        elif (QBO_customer[k]["DisplayName"]).startswith(
                                Q1[i]["customer_name"]
                        ) and ((QBO_customer[k]["DisplayName"]).endswith("-C")):
                            CustomerRef["value"] = QBO_customer[k]["Id"]
                            CustomerRef["name"] = QBO_customer[k]["DisplayName"]

                        if "PrimaryEmailAddr" in QBO_customer[k]:
                            BillEmail["Address"] = QBO_customer[k]["PrimaryEmailAddr"][
                                "Address"
                            ]

            invoice["CustomerMemo"] = CustomerMemo
            invoice["BillEmail"] = BillEmail
            invoice["CustomerRef"] = CustomerRef
            invoice["TxnDate"] = Q1[i]["invoice_date"]
            invoice["DueDate"] = Q1[i]["due_date"]
            itemDetail["SalesItemLineDetail"] = SalesItemLineDetail
            # itemDetail['Amount'] = Q1[i]['Item'][k1]["amount"]
            itemDetail["Description"] = Q1[i]["Item"][k1]["description"]
            discountDetail["SalesItemLineDetail"] = discountSalesItemLineDetail

            SalesItemLineDetail["ItemRef"] = ItemRef
            SalesItemLineDetail["ClassRef"] = ClassRef
            SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
            SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

            discountSalesItemLineDetail["ItemRef"] = ItemRef
            discountSalesItemLineDetail["ClassRef"] = ClassRef
            discountSalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
            discountSalesItemLineDetail["ItemAccountRef"] = ItemAccountRef
            Tax["Amount"] = abs(Q1[i]["TotalTax"])
            invoice["TxnTaxDetail"] = TxnTaxDetail
            Tax["DetailType"] = "TaxLineDetail"
            Tax["TaxLineDetail"] = TaxLineDetail
            # SubTotalLine['Amount'] = abs(Q1[i]['TotalAmount'])

            SubTotalLine["DetailType"] = "SubTotalLineDetail"
            SubTotalLine["SubTotalLineDetail"] = SubTotalLineDetail
            # SalesItemLineDetail['Qty'] = abs(Q1[i]['Item'][k1]['ship_quantity'])

            # SalesItemLineDetail['UnitPrice'] = abs(
            #     Q1[i]['Item'][k1]['unit_price'])

            TxnTaxDetail["TotalTax"] = abs(Q1[i]["TotalTax"])
            TaxLineDetail["TaxRateRef"] = TaxRate
            TaxLineDetail["PercentBased"] = True
            TaxLineDetail["NetAmountTaxable"] = abs(Q1[i]["Subtotal"])
            TxnTaxDetail["TaxLine"].append(Tax)
            itemDetail["SalesItemLineDetail"] = SalesItemLineDetail
            invoice["Line"].append(itemDetail)
            invoice["Line"].append(SubTotalLine)

            if Q1[i]["Item"][k1]["discount"] > 0:
                invoice["Line"].append(discountDetail)

            if invoice["Line"][k1]["SalesItemLineDetail"]["ItemRef"] != {}:
                if Q1[i]["Subtotal"] >= 0:
                    payload = json.dumps(invoice)
                    inv_date = Q1[i]["invoice_date"][0:10]
                    inv_date1 = datetime.strptime(inv_date, "%Y-%m-%d")
                    if start_date1 is not None and end_date1 is not None:
                        if (inv_date1 >= start_date1) and (inv_date1 < end_date1):
                            post_data_in_qbo(
                                url1,
                                headers,
                                payload,
                                job_id,
                                Q1[i]["invoice_no"]
                            )
                        else:
                            pass

                    else:
                        post_data_in_qbo(
                            url1,
                            headers,
                            payload,
                            job_id,
                            Q1[i]["invoice_no"]
                        )
                else:
                    url2 = "{}/creditmemo?minorversion=14".format(base_url)
                    if Q1[i]["Item"][k1]["ship_quantity"] == 0:
                        SalesItemLineDetail["Qty"] = abs(
                            Q1[i]["Item"][k1]["ship_quantity"]
                        )
                    else:
                        SalesItemLineDetail["Qty"] = abs(
                            Q1[i]["Item"][k1]["ship_quantity"]
                        )

                    SalesItemLineDetail["UnitPrice"] = abs(
                        Q1[i]["Item"][k1]["unit_price"]
                    )
                    itemDetail["Amount"] = abs(Q1[i]["Item"][k1]["amount"])
                    payload = json.dumps(invoice)

                    inv_date = Q1[i]["invoice_date"][0:10]
                    inv_date1 = datetime.strptime(inv_date, "%Y-%m-%d")
                    if start_date1 is not None and end_date1 is not None:
                        if (inv_date1 >= start_date1) and (inv_date1 <= end_date1):
                            post_data_in_qbo(
                                url2,
                                headers,
                                payload,
                                job_id,
                                Q1[i]["invoice_no"]
                            )
                        else:
                            pass
                    else:
                        post_data_in_qbo(
                            url2,
                            headers,
                            payload,
                            job_id,
                            Q1[i]["invoice_no"]
                        )
            else:
                add_job_status(
                    job_id,
                    "Unable to add invoice because Item is not present in QBO : {}".format(
                        single[i]["invoice_no"]
                    ),
                    "error",
                )

    except Exception as ex:
        traceback.print_exc()
        
