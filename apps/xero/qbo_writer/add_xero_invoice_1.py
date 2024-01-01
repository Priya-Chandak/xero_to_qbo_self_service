import json
import logging
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job

logger = logging.getLogger(__name__)


def add_xero_invoice(job_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_xero_invoice_1 -> add_xero_invoice")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        multiple_item_invoice = dbname["xero_invoice"].find({"job_id": job_id})

        multiple_invoice = []
        for p1 in multiple_item_invoice:
            multiple_invoice.append(p1)

        multiple_invoice = multiple_invoice[0:5]

        # multiple_invoice=[]
        # d=['INV-0067']
        # for j in range(0,len(multiple_invoice1)):
        #     if multiple_invoice1[j]['Inv_No'] in d:
        #         multiple_invoice.append(multiple_invoice1[j])

        multiple_invoice = multiple_invoice[1:10]

        QBO_Item = dbname["QBO_Item"].find({"job_id": job_id})
        QBO_item = []
        for p1 in QBO_Item:
            QBO_item.append(p1)

        QBO_Class = dbname["QBO_Class"].find({"job_id": job_id})
        QBO_class = []
        for p2 in QBO_Class:
            QBO_class.append(p2)

        QBO_Tax = dbname["QBO_Tax"].find({"job_id": job_id})
        QBO_tax = []
        for p3 in QBO_Tax:
            QBO_tax.append(p3)

        QBO_COA1 = dbname["QBO_COA"].find({"job_id": job_id})
        QBO_COA = []
        for p4 in QBO_COA:
            QBO_COA.append(p4)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id": job_id})
        QBO_customer = []
        for p5 in QBO_Customer:
            QBO_customer.append(p5)

        Xero_COA = dbname["xero_coa"].find({"job_id": job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        for i in range(0, len(multiple_invoice)):
            invoice = {"Line": []}
            CustomerRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            invoice["TxnDate"] = multiple_invoice[i]["TxnDate"]
            invoice["DueDate"] = multiple_invoice[i]["DueDate"]
            invoice["DocNumber"] = multiple_invoice[i]["Inv_No"]
            #     invoice['TotalAmt'] = multiple_invoice[i]['TotalAmount']
            #     invoice['HomeTotalAmt'] = multiple_invoice[i]['TotalAmount']

            subtotal = {}

            for p1 in range(0, len(QBO_customer)):
                if "ContactName" in multiple_invoice[i]:
                    if QBO_customer[p1]["DisplayName"].startswith(
                            multiple_invoice[i]["ContactName"]
                    ) and QBO_customer[p1]["DisplayName"].endswith(" - C"):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                    elif (
                            multiple_invoice[i]["ContactName"]
                            == QBO_customer[p1]["DisplayName"]
                    ):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                    else:
                        pass

                    #  if 'PrimaryEmailAddr' in QBO_customer[i]:
                    #     BillEmail['Address'] = QBO_customer[i]['PrimaryEmailAddr']['Address']

            if multiple_invoice[i]["LineAmountTypes"] in ["Exclusive", "NoTax"]:
                invoice["GlobalTaxCalculation"] = "TaxExcluded"
            else:
                invoice["GlobalTaxCalculation"] = "TaxInclusive"

            total_val = 0
            taxrate1 = 0

            for j in range(len(multiple_invoice[i]["Line"])):
                ClassRef = {}
                TaxLineDetail = {}
                CustomerMemo = {}
                salesitemline = {}
                discount = {}
                ItemRef = {}
                SalesItemLineDetail = {}
                discount_SalesItemLineDetail = {}
                rounding_SalesItemLineDetail = {}
                TaxCodeRef = {}
                ItemAccountRef = {}
                TaxRate = {}
                SubTotalLineDetail = {}
                TaxDetail = {}

                salesitemline["DetailType"] = "SalesItemLineDetail"

                for p3 in range(0, len(QBO_item)):
                    if "ItemCode" in multiple_invoice[i]["Line"][j]:
                        if "Sku" in QBO_item[p3]:
                            if (
                                    multiple_invoice[i]["Line"][j]["ItemCode"]
                                    == QBO_item[p3]["Sku"]
                            ):
                                ItemRef["value"] = QBO_item[p3]["Id"]
                    # if 'Name' in multiple_invoice[i]['Line'][j]:
                    #     if ('Name' in multiple_invoice[i]['Line'][j]) and ('AccountCode' in multiple_invoice[i]['Line'][j]):
                    #         if multiple_invoice[i]['Line'][j]['Name'] +"-"+ multiple_invoice[i]['Line'][j]['AccountCode'] == QBO_item[p3]['Name']:
                    #             ItemRef['value'] = QBO_item[p3]["Id"]

                    #     elif multiple_invoice[i]['Line'][j]['Name'] == QBO_item[p3]['Name']:
                    #         ItemRef['name'] = QBO_item[p3]['Name']
                    #         ItemRef['value'] = QBO_item[p3]['Id']

                    else:
                        if (
                                multiple_invoice[i]["Line"][j]["AccountCode"]
                                == QBO_item[p3]["Name"]
                        ):
                            ItemRef["name"] = QBO_item[p3]["Name"]
                            ItemRef["value"] = QBO_item[p3]["Id"]

                # for p4 in range(0, len(QBO_class)):
                #     if multiple_invoice[i]['Line'][j]['job'] is not None:
                #         if multiple_invoice[i]['Line'][j]['job'] == QBO_class[p4]["Name"]:
                #             ClassRef['name'] = QBO_class[p4]["Name"]
                #             ClassRef['value'] = QBO_class[p4]["Id"]
                #         else:
                #             pass

                for p5 in range(0, len(QBO_COA)):
                    for p51 in range(0, len(xero_coa)):
                        if ("Code" in xero_coa[p51]) and (
                                "AccountCode" in multiple_invoice[i]["Line"][j]
                        ):
                            if multiple_invoice[i]["Line"][j]["AccountCode"] == "200":
                                ItemAccountRef["name"] = "Sales"
                                ItemAccountRef["value"] = "113"

                            elif (
                                    multiple_invoice[i]["Line"][j]["AccountCode"]
                                    == xero_coa[p51]["Code"]
                            ):
                                if (
                                        xero_coa[p51]["Name"].lower().strip()
                                        == QBO_COA[p5]["Name"].lower().strip()
                                ):
                                    ItemAccountRef["name"] = QBO_COA[p5]["Name"]
                                    ItemAccountRef["value"] = QBO_COA[p5]["Id"]

                if ("TaxType" in multiple_invoice[i]["Line"][j]) and (
                        ("AccountCode" in multiple_invoice[i]["Line"][j])
                ):
                    for p6 in range(0, len(QBO_tax)):
                        if multiple_invoice[i]["Line"][j]["TaxType"] == "BASEXCLUDED":
                            if "taxrate_name" in QBO_tax[p6]:
                                if "NOTAXS" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val = (
                                            total_val
                                            + multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif multiple_invoice[i]["Line"][j]["TaxType"] == "OUTPUT":
                            if "taxrate_name" in QBO_tax[p6]:
                                if "GST (sales)" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif (
                                (multiple_invoice[i]["Line"][j]["TaxType"] == None)
                                or (multiple_invoice[i]["Line"][j]["TaxType"] == "NONE")
                                or (multiple_invoice[i]["Line"][j]["TaxType"] == "TAX001")
                        ):
                            if "taxrate_name" in QBO_tax[p6]:
                                if "NOTAXS" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif multiple_invoice[i]["Line"][j]["TaxType"] == "NONE":
                            if "taxrate_name" in QBO_tax[p6]:
                                if "NOTAXS" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif (
                                multiple_invoice[i]["Line"][j]["TaxType"] == "EXEMPTCAPITAL"
                                or multiple_invoice[i]["Line"][j]["TaxType"]
                                == "EXEMPTEXPENSES"
                                or multiple_invoice[i]["Line"][j]["TaxType"]
                                == "EXEMPTEXPORT"
                        ):
                            if "taxrate_name" in QBO_tax[p6]:
                                if "GST free (sales)" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif (
                                multiple_invoice[i]["Line"][j]["TaxType"] == "EXEMPTOUTPUT"
                        ):
                            if "taxrate_name" in QBO_tax[p6]:
                                if "GST free (sales)" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif (
                                multiple_invoice[i]["Line"][j]["TaxType"] == "CAPEXINPUT"
                                or multiple_invoice[i]["Line"][j]["TaxType"] == "INPUT"
                        ):
                            if "taxrate_name" in QBO_tax[p6]:
                                if "GST (sales)" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif (
                                multiple_invoice[i]["Line"][j]["TaxType"]
                                == "GSTONCAPIMPORTS"
                                or multiple_invoice[i]["Line"][j]["TaxType"]
                                == "GSTONIMPORTS"
                        ):
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
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                    )

                        elif (
                                multiple_invoice[i]["Line"][j]["TaxType"]
                                == QBO_tax[p6]["taxcode_name"]
                        ):
                            TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                            taxrate = QBO_tax[p6]["Rate"]
                            TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                            TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                            taxrate1 = taxrate
                            total_val += (
                                    multiple_invoice[i]["Line"][j]["LineAmount"]
                                    / (100 + taxrate1)
                                    * 100
                            )
                        else:
                            pass

                        if (multiple_invoice[i]["LineAmountTypes"] == "Exclusive") or (
                                multiple_invoice[i]["LineAmountTypes"] == "NoTax"
                        ):
                            if "AccountCode" in multiple_invoice[i]["Line"][j]:
                                if "Discount" in multiple_invoice[i]["Line"][j]:
                                    discount_SalesItemLineDetail["Qty"] = 1
                                    discount_SalesItemLineDetail["UnitPrice"] = (
                                            -(
                                                    multiple_invoice[i]["Line"][j]["Quantity"]
                                                    * multiple_invoice[i]["Line"][j][
                                                        "UnitAmount"
                                                    ]
                                                    * multiple_invoice[i]["Line"][j]["Discount"]
                                            )
                                            / 100
                                    )
                                    discount["Amount"] = (
                                            -(
                                                    multiple_invoice[i]["Line"][j]["Quantity"]
                                                    * multiple_invoice[i]["Line"][j][
                                                        "UnitAmount"
                                                    ]
                                                    * multiple_invoice[i]["Line"][j]["Discount"]
                                            )
                                            / 100
                                    )
                                SalesItemLineDetail["Qty"] = abs(
                                    multiple_invoice[i]["Line"][j]["Quantity"]
                                )
                                SalesItemLineDetail["UnitPrice"] = abs(
                                    multiple_invoice[i]["Line"][j]["UnitAmount"]
                                )
                                salesitemline["Amount"] = abs(
                                    (
                                            multiple_invoice[i]["Line"][j]["UnitAmount"]
                                            * multiple_invoice[i]["Line"][j]["Quantity"]
                                    )
                                )
                                subtotal["Amount"] = multiple_invoice[i]["SubTotal"]

                                invoice["TxnTaxDetail"] = TxnTaxDetail
                                TaxDetail["DetailType"] = "TaxLineDetail"
                                TaxDetail["TaxLineDetail"] = TaxLineDetail
                                TxnTaxDetail["TotalTax"] = abs(
                                    multiple_invoice[i]["TotalTax"]
                                )
                                TaxLineDetail["TaxRateRef"] = TaxRate
                                TaxLineDetail["PercentBased"] = True

                                if taxrate1 != 0:
                                    TaxDetail["Amount"] = multiple_invoice[i][
                                        "TotalTax"
                                    ]
                                    TaxLineDetail["NetAmountTaxable"] = (
                                            multiple_invoice[i]["SubTotal"]
                                            - multiple_invoice[i]["TotalTax"]
                                    )
                                else:
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = 0

                        else:
                            if "AccountCode" in multiple_invoice[i]["Line"][j]:
                                if "Discount" in multiple_invoice[i]["Line"][j]:
                                    discount_SalesItemLineDetail["Qty"] = 1
                                    discount_SalesItemLineDetail["UnitPrice"] = -round(
                                        (
                                                multiple_invoice[i]["Line"][j]["Quantity"]
                                                * multiple_invoice[i]["Line"][j][
                                                    "UnitAmount"
                                                ]
                                                * multiple_invoice[i]["Line"][j]["Discount"]
                                                / (100 + taxrate1)
                                        ),
                                        2,
                                    )
                                    discount["Amount"] = -round(
                                        (
                                                multiple_invoice[i]["Line"][j]["Quantity"]
                                                * multiple_invoice[i]["Line"][j][
                                                    "UnitAmount"
                                                ]
                                                * multiple_invoice[i]["Line"][j]["Discount"]
                                                / (100 + taxrate1)
                                        ),
                                        2,
                                    )
                                SalesItemLineDetail["Qty"] = abs(
                                    multiple_invoice[i]["Line"][j]["Quantity"]
                                )
                                #                 SalesItemLineDetail['UnitPrice'] = abs(multiple_invoice[i]['Line'][j]['UnitAmount'])
                                # SalesItemLineDetail['UnitPrice'] = abs(
                                #     round(multiple_invoice[i]['Line'][j]['UnitAmount']/(100+taxrate1)*100, 2))
                                # salesitemline["Amount"] = SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                SalesItemLineDetail["UnitPrice"] = round(
                                    multiple_invoice[i]["Line"][j]["UnitAmount"]
                                    / (taxrate1 + 100)
                                    * 100,
                                    4,
                                )
                                # salesitemline["Amount"] = SalesItemLineDetail['Qty']*SalesItemLineDetail['UnitPrice']
                                salesitemline["Amount"] = round(
                                    SalesItemLineDetail["UnitPrice"]
                                    * SalesItemLineDetail["Qty"],
                                    2,
                                )
                                SalesItemLineDetail[
                                    "TaxInclusiveAmt"
                                ] = multiple_invoice[i]["Line"][j]["LineAmount"]

                                #                 salesitemline["Amount"] = abs(round(
                                #                     (multiple_invoice[i]['Line'][j]['UnitAmount']*multiple_invoice[i]['Line'][j]['Quantity']/(100+taxrate1)*100), 2))
                                #                 subtotal['Amount'] = abs(round((total_val), 2))
                                # subtotal['Amount'] = multiple_invoice[i]['SubTotal'] - multiple_invoice[i]['TotalTax']
                                subtotal["Amount"] = multiple_invoice[i]["SubTotal"]
                                invoice["TxnTaxDetail"] = TxnTaxDetail
                                TaxDetail["DetailType"] = "TaxLineDetail"
                                TaxDetail["TaxLineDetail"] = TaxLineDetail
                                TxnTaxDetail["TotalTax"] = abs(
                                    multiple_invoice[i]["TotalTax"]
                                )
                                TaxLineDetail["TaxRateRef"] = TaxRate
                                TaxLineDetail["PercentBased"] = True

                                t = ["TAX001", "BASEXCLUDED", "NONE", None, ""]
                                if multiple_invoice[i]["Line"][j]["TaxType"] in t:
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = 0
                                elif (
                                        multiple_invoice[i]["Line"][j]["TaxType"]
                                        == "OUTPUT"
                                ) or (
                                        multiple_invoice[i]["Line"][j]["TaxType"] == "INPUT"
                                ):
                                    TaxDetail["Amount"] = multiple_invoice[i][
                                        "TotalTax"
                                    ]
                                    TaxLineDetail[
                                        "NetAmountTaxable"
                                    ] = multiple_invoice[i]["SubTotal"]

                subtotal["DetailType"] = "SubTotalLineDetail"
                subtotal["SubTotalLineDetail"] = SubTotalLineDetail
                salesitemline["DetailType"] = "SalesItemLineDetail"
                salesitemline["SalesItemLineDetail"] = SalesItemLineDetail

                SalesItemLineDetail["ItemRef"] = ItemRef
                SalesItemLineDetail["ClassRef"] = ClassRef
                SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef
                salesitemline["Description"] = multiple_invoice[i]["Line"][j][
                    "Description"
                ]

                discount["DetailType"] = "SalesItemLineDetail"
                discount["SalesItemLineDetail"] = discount_SalesItemLineDetail
                discount["Description"] = "Discount"
                discount_SalesItemLineDetail["ItemRef"] = ItemRef
                discount_SalesItemLineDetail["ClassRef"] = ClassRef
                discount_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                discount_SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                invoice["BillEmail"] = BillEmail
                invoice["CustomerRef"] = CustomerRef

                if "AccountCode" in multiple_invoice[i]["Line"][j]:
                    invoice["Line"].append(salesitemline)

                if "Discount" in multiple_invoice[i]["Line"][j]:
                    if multiple_invoice[i]["Line"][j]["Discount"] > 0:
                        invoice["Line"].append(discount)

                TxnTaxDetail["TaxLine"].append(TaxDetail)

            # a = []
            # for p2 in range(0,len(TxnTaxDetail['TaxLine'])):
            #     if TxnTaxDetail['TaxLine'][p2] in a:
            #         pass
            #     else:
            #         a.append(TxnTaxDetail['TaxLine'][p2])

            # TxnTaxDetail['TaxLine'] = a
            arr = TxnTaxDetail["TaxLine"]

            b1 = {"TaxLine": []}
            b = []
            for i2 in range(0, len(arr)):
                if (arr[i2] != {}) and (arr[i2]["TaxLineDetail"]["TaxRateRef"] != {}):
                    b.append(arr[i2]["TaxLineDetail"]["TaxRateRef"]["value"])

            e = {}
            for i1 in range(0, len(b)):
                e[b[i1]] = b.count(b[i1])

            multiple = dict((k, v) for k, v in e.items() if v > 1)
            single = dict((k, v) for k, v in e.items() if v == 1)

            e1 = []
            for keys in e.keys():
                e1.append(keys)

            new_arr = []
            for k in range(0, len(multiple)):
                e = {}
                TaxLineDetail = {}
                TaxRateRef = {}
                amt = 0
                net_amt = 0
                for i4 in range(0, len(arr)):
                    if arr[i4] != {}:
                        if arr[i4]["TaxLineDetail"]["TaxRateRef"]["value"] == e1[k]:
                            e["DetailType"] = "TaxLineDetail"
                            TaxLineDetail["TaxRateRef"] = TaxRateRef
                            TaxLineDetail["TaxPercent"] = arr[i4]["TaxLineDetail"][
                                "TaxPercent"
                            ]
                            TaxRateRef["value"] = e1[k]

                            amt = amt + arr[i4]["Amount"]
                            net_amt = (
                                    net_amt + arr[i4]["TaxLineDetail"]["NetAmountTaxable"]
                            )
                            e["Amount"] = round(amt, 2)
                            TaxLineDetail["NetAmountTaxable"] = round(net_amt, 2)
                            e["TaxLineDetail"] = TaxLineDetail

                new_arr.append(e)

            for k3 in range(0, len(arr)):
                if (arr[k3] != {}) and (arr[k3]["TaxLineDetail"]["TaxRateRef"] != {}):
                    if arr[k3]["TaxLineDetail"]["TaxRateRef"]["value"] in single:
                        new_arr.append(arr[k3])

            b1["TaxLine"] = new_arr

            # TxnTaxDetail['TxnTaxDetail'] = b1
            # TxnTaxDetail['TaxLine'].append(TaxDetail)

            invoice["TxnTaxDetail"] = b1

            invoice["Line"].append(subtotal)

            inv_date = multiple_invoice[i]["TxnDate"][0:10]
            inv_date1 = datetime.strptime(inv_date, "%Y-%m-%d")

            if start_date1 is not None and end_date1 is not None:
                if (inv_date1 >= start_date1) and (inv_date1 <= end_date1):
                    if invoice["Line"][0]["SalesItemLineDetail"]["ItemRef"] != {}:
                        if (
                                (multiple_invoice[i]["Line"][j]["Quantity"] >= 0)
                                and (multiple_invoice[i]["Line"][j]["UnitAmount"] >= 0)
                        ) or (
                                (multiple_invoice[i]["Line"][j]["Quantity"] < 0)
                                and (multiple_invoice[i]["Line"][j]["UnitAmount"] < 0)
                        ):
                            url1 = "{}/invoice?minorversion=14".format(base_url)

                            payload = json.dumps(invoice)

                            if (
                                    multiple_invoice[i]["Status"] != "VOIDED"
                                    or multiple_invoice[i]["Status"] != "DELETED"
                            ):
                                response = requests.request(
                                    "POST", url1, headers=headers, data=payload
                                )

                                if response.status_code == 401:
                                    res1 = json.loads(response.text)
                                    res2 = (res1["fault"]["error"][0]["message"]).split(
                                        ";"
                                    )[0]
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = res1["Fault"]["Error"][0][
                                               "Message"
                                           ] + ": {}".format(multiple_invoice[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                        else:
                            url2 = "{}/creditmemo?minorversion=14".format(base_url)
                            payload = json.dumps(invoice)
                            if (
                                    multiple_invoice[i]["Status"] != "VOIDED"
                                    or multiple_invoice[i]["Status"] != "DELETED"
                            ):
                                response = requests.request(
                                    "POST", url2, headers=headers, data=payload
                                )
                                if response.status_code == 401:
                                    res1 = json.loads(response.text)
                                    res2 = (res1["fault"]["error"][0]["message"]).split(
                                        ";"
                                    )[0]
                                    add_job_status(job_id, res2, "error")
                                elif response.status_code == 400:
                                    res1 = json.loads(response.text)
                                    res2 = res1["Fault"]["Error"][0][
                                               "Message"
                                           ] + ": {}".format(multiple_invoice[i]["Inv_No"])
                                    add_job_status(job_id, res2, "error")

                    else:
                        pass

                else:
                    pass

                # else:
                #     add_job_status(job_id, "Unable to add invoice because Item is not present in QBO : {}".format(multiple_invoice[i]['Inv_No']) ,"error")
                #     print("Unable to add invoice because Item is not present in QBO")
            else:
                # if ((multiple_invoice[i]['Line'][j]['Quantity'] >= 0) and (multiple_invoice[i]['Line'][j]['UnitAmount'] >= 0)) or ((multiple_invoice[i]['Line'][j]['Quantity'] < 0) and (multiple_invoice[i]['Line'][j]['UnitAmount'] < 0)):
                if multiple_invoice[i]["TotalAmount"] >= 0:
                    if multiple_invoice[i]["Inv_No"] == "INV-0271":
                        url1 = "{}/invoice?minorversion=14".format(base_url)
                        payload = json.dumps(invoice)
                        if (
                                multiple_invoice[i]["Status"] != "VOIDED"
                                or multiple_invoice[i]["Status"] != "DELETED"
                        ):
                            response = requests.request(
                                "POST", url1, headers=headers, data=payload
                            )

                            if response.status_code == 401:
                                res1 = json.loads(response.text)
                                res2 = (res1["fault"]["error"][0]["message"]).split(
                                    ";"
                                )[0]
                                add_job_status(job_id, res2, "error")
                            elif response.status_code == 400:
                                res1 = json.loads(response.text)
                                res2 = res1["Fault"]["Error"][0][
                                           "Message"
                                       ] + ": {}".format(multiple_invoice[i]["Inv_No"])
                                add_job_status(job_id, res2, "error")

                else:
                    url2 = "{}/creditmemo?minorversion=14".format(base_url)
                    payload = json.dumps(invoice)
                    if (
                            multiple_invoice[i]["Status"] != "VOIDED"
                            or multiple_invoice[i]["Status"] != "DELETED"
                    ):
                        response = requests.request(
                            "POST", url2, headers=headers, data=payload
                        )
                        if response.status_code == 401:
                            res1 = json.loads(response.text)
                            res2 = (res1["fault"]["error"][0]["message"]).split(";")[0]
                            add_job_status(job_id, res2, "error")
                        elif response.status_code == 400:
                            res1 = json.loads(response.text)
                            res2 = res1["Fault"]["Error"][0]["Message"] + ": {}".format(
                                multiple_invoice[i]["Inv_No"]
                            )
                            add_job_status(job_id, res2, "error")

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_xero_invoice_1 -> add_xero_invoice", ex)
