import json
import logging
from datetime import datetime

import requests
from collections import Counter

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo

logger = logging.getLogger(__name__)


def add_xero_credit_note(job_id,task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_xero_credit_note -> add_xero_credit_note")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        xero_creditnote = db["xero_creditnote"].find({"job_id":job_id})
        multiple_invoice = []
        for p1 in xero_creditnote:
            multiple_invoice.append(p1)

        # m1=[]
        # for m in range(0,len(multiple_invoice)):
        #     # if multiple_invoice[m]['LineAmountTypes']=="Exclusive":
        #     if multiple_invoice[m]['Inv_No'] in ['CN-0882']:
        #         m1.append(multiple_invoice[m])

        # multiple_invoice = m1

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

        # multiple_invoice = multiple_invoice

        bill_bumbers=[]
        for b1 in range(0,len(multiple_invoice)):
            bill_bumbers.append(multiple_invoice[b1]['Inv_No'])

        data1=[]

        frequency_counter = Counter(bill_bumbers)
        for number, count in frequency_counter.items():
            if count>1:
                data1.append({number:count})
        
        key_list = []

        non_items = []

        for i in range(0, len(multiple_invoice)):
            print(i)
            print(multiple_invoice[i]['Inv_No'])
            _id = multiple_invoice[i]['_id']
            task_id = multiple_invoice[i]['task_id']
            
            invoice = {"Line": []}
            CustomerRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            invoice["TxnDate"] = multiple_invoice[i]["TxnDate"]
            # invoice["DueDate"] = multiple_invoice[i]["DueDate"]
            
            if multiple_invoice[i]["Inv_No"] in key_list:
                invoice["DocNumber"] = multiple_invoice[i]["Inv_No"][0:14]+"-"+multiple_invoice[i]["Inv_ID"][-6:]
                break
            else:
                if len(str(multiple_invoice[i]["Inv_No"]))>21:
                    invoice["DocNumber"] = multiple_invoice[i]["Inv_No"][0:14]+"-"+multiple_invoice[i]["Inv_ID"][-6:]
                else:
                    invoice["DocNumber"] = multiple_invoice[i]["Inv_No"][0:21]
            
            invoice["TotalAmt"] = abs(multiple_invoice[i]["TotalAmount"])
            invoice["HomeTotalAmt"] = abs(multiple_invoice[i]["TotalAmount"])
            subtotal = {}

            for p1 in range(0, len(QBO_customer)):
                if "ContactName" in multiple_invoice[i]:
                    if (
                        multiple_invoice[i]["ContactName"].strip()
                        == QBO_customer[p1]["DisplayName"].strip()
                    ):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                    elif (QBO_customer[p1]["DisplayName"]).startswith(
                        multiple_invoice[i]["ContactName"]
                    ) and ((QBO_customer[p1]["DisplayName"]).endswith("- C")):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]

            if (
                multiple_invoice[i]["LineAmountTypes"] == "Exclusive"
                or multiple_invoice[i]["LineAmountTypes"] == "NoTax"
            ):
                invoice["GlobalTaxCalculation"] = "TaxExcluded"
            else:
                invoice["GlobalTaxCalculation"] = "TaxInclusive"

            total_val = 0
            taxrate1 = 0
            line_amount = 0

            for j in range(len(multiple_invoice[i]["Line"])):
                print(j)
                if (
                    "AccountCode" in multiple_invoice[i]["Line"][j]
                ):
                    print(j,"acc")
                    TaxLineDetail = {}
                    CustomerMemo = {}
                    salesitemline = {}
                    discount = {}
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
                    discount["Description"] = "Discount"

                    # if multiple_invoice[i]['Line'][j]['Quantity'] == 0:
                    #     multiple_invoice[i]['Line'][j]['Quantity'] = multiple_invoice[i]['Line'][j]['Quantity']
                    # else:
                    #     multiple_invoice[i]['Line'][j]['Quantity'] = multiple_invoice[i]['Line'][j]['Quantity']
                    if multiple_invoice[i]["Line"][j]["Quantity"] == 0:
                        multiple_invoice[i]["Line"][j]["Quantity"] = 1

                    if multiple_invoice[i]["Line"][j]["UnitAmount"] == 0:
                        multiple_invoice[i]["Line"][j]["UnitAmount"] = multiple_invoice[
                            i
                        ]["Line"][j]["LineAmount"]

                    for p3 in range(0, len(QBO_item)):
                        salesitemline["Description"] = multiple_invoice[i]["Line"][j][
                            "Description"
                        ]

                        if "ItemCode" in multiple_invoice[i]["Line"][j] and multiple_invoice[i]["Line"][j]['ItemCode']!=None:
                            if "Sku" in QBO_item[p3]:
                                if "AccountCode" in multiple_invoice[i]["Line"][j]:
                                    if (
                                        multiple_invoice[i]["Line"][j]["ItemCode"].replace(":","-")
                                        + "-"
                                        + multiple_invoice[i]["Line"][j]["AccountCode"]
                                        == QBO_item[p3]["Sku"]
                                    ):
                                        ItemRef["name"] = QBO_item[p3]["Name"]
                                        ItemRef["value"] = QBO_item[p3]["Id"]
                                        break

                                    elif (
                                        multiple_invoice[i]["Line"][j]["ItemCode"].replace(":","-")
                                        == QBO_item[p3]["Sku"]
                                    ):
                                        ItemRef["name"] = QBO_item[p3]["Name"]
                                        ItemRef["value"] = QBO_item[p3]["Id"]
                                        break

                                elif (
                                    multiple_invoice[i]["Line"][j]["ItemCode"].replace(":","-")
                                    == QBO_item[p3]["Sku"]
                                ):
                                    ItemRef["name"] = QBO_item[p3]["Name"]
                                    ItemRef["value"] = QBO_item[p3]["Id"]
                                    break

                        elif "AccountCode" in multiple_invoice[i]["Line"][j]:
                            if "Sku" in QBO_item[p3]:
                                if (
                                    multiple_invoice[i]["Line"][j]["AccountCode"]
                                    == QBO_item[p3]["Sku"]
                                ):
                                    ItemRef["name"] = QBO_item[p3]["Name"]
                                    ItemRef["value"] = QBO_item[p3]["Id"]
                                    break
                            else:
                                for p5 in range(0, len(QBO_coa)):
                                    if "AcctNum" in QBO_coa[p5]:
                                        if (
                                            multiple_invoice[i]["Line"][j][
                                                "AccountCode"
                                            ]
                                            == QBO_coa[p5]["AcctNum"]
                                        ):
                                            if (
                                                QBO_coa[p5]["Name"]
                                                == QBO_item[p3]["Name"]
                                            ):
                                                ItemRef["name"] = QBO_item[p3]["Name"]
                                                ItemRef["value"] = QBO_item[p3]["Id"]
                                                break

                        
                        
                    for p4 in range(0, len(QBO_class)):
                        if "job" in multiple_invoice[i]["Line"][j]: 
                            if multiple_invoice[i]["Line"][j]["job"] is not None:
                                if (
                                    multiple_invoice[i]["Line"][j]["job"]
                                    == QBO_class[p4]["Name"]
                                ):
                                    ClassRef["name"] = QBO_class[p4]["Name"]
                                    ClassRef["value"] = QBO_class[p4]["Id"]
                                else:
                                    pass

                    for p5 in range(0, len(QBO_coa)):
                        if "AccountCode" in multiple_invoice[i]["Line"][j]:
                            if "AcctNum" in QBO_coa[p5]:
                                if (
                                    multiple_invoice[i]["Line"][j]["AccountCode"]
                                    == QBO_coa[p5]["AcctNum"]
                                ):
                                    ItemAccountRef["name"] = QBO_coa[p5]["Name"]
                                    ItemAccountRef["value"] = QBO_coa[p5]["Id"]

                    for p6 in range(0, len(QBO_tax)):
                        if "TaxType" in multiple_invoice[i]["Line"][j]:
                            if (
                                multiple_invoice[i]["Line"][j]["TaxType"] == "OUTPUT"
                                or multiple_invoice[i]["Line"][j]["TaxType"] == "GST"
                                or multiple_invoice[i]["Line"][j]["TaxType"] == "INPUT"
                                or multiple_invoice[i]["Line"][j]["TaxType"] == "INPUT2"
                            ):
                                if "taxrate_name" in QBO_tax[p6]:
                                    if "GST (sales)" in QBO_tax[p6]["taxrate_name"]:
                                        TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                        taxrate = QBO_tax[p6]["Rate"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6][
                                            "Rate"
                                        ]
                                        TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                        taxrate1 = taxrate
                                        total_val = (
                                            total_val
                                            + multiple_invoice[i]["Line"][j][
                                                "LineAmount"
                                            ]
                                            / (100 + taxrate1)
                                            * 100
                                        )

                            elif multiple_invoice[i]["Line"][j]["TaxType"] == "CAP":
                                if "GST on capital" in QBO_tax[p6]["taxcode_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    taxrate = QBO_tax[p6]["Rate"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    taxrate1 = taxrate
                                    total_val += (
                                        multiple_invoice[i]["Line"][j]["amount"]
                                        / (100 + taxrate1)
                                        * 100
                                    )

                            elif multiple_invoice[i]["Line"][j]["TaxType"] in ['FRE','EXEMPTEXPENSES','EXEMPTOUTPUT']:
                                if "taxrate_name" in QBO_tax[p6]:
                                    if (
                                        "GST free (sales)"
                                        in QBO_tax[p6]["taxrate_name"]
                                    ):
                                        TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                        taxrate = QBO_tax[p6]["Rate"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6][
                                            "Rate"
                                        ]
                                        TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                        taxrate1 = taxrate
                                        total_val += (
                                            multiple_invoice[i]["Line"][j]["LineAmount"]
                                            / (100 + taxrate1)
                                            * 100
                                        )

                            elif (
                                multiple_invoice[i]["Line"][j]["TaxType"] == "N-T"
                                or multiple_invoice[i]["Line"][j]["TaxType"]
                                == "BASEXCLUDED"
                                or multiple_invoice[i]["Line"][j]["TaxType"] == None
                                or multiple_invoice[i]["Line"][j]["TaxType"] == "NONE"
                            ):
                                if "taxrate_name" in QBO_tax[p6]:
                                    if "NOTAXS" in QBO_tax[p6]["taxrate_name"]:
                                        TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                        taxrate = QBO_tax[p6]["Rate"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[p6][
                                            "Rate"
                                        ]
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

                            if (
                                multiple_invoice[i]["LineAmountTypes"] == "Exclusive"
                                or multiple_invoice[i]["LineAmountTypes"] == "NoTax"
                            ):
                                if multiple_invoice[i]["SubTotal"] >= 0:
                                    SalesItemLineDetail["Qty"] = multiple_invoice[i][
                                        "Line"
                                    ][j]["Quantity"]
                                    SalesItemLineDetail["UnitPrice"] = multiple_invoice[
                                        i
                                    ]["Line"][j]["UnitAmount"]
                                    salesitemline["Amount"] = round(
                                        multiple_invoice[i]["Line"][j]["UnitAmount"]
                                        * multiple_invoice[i]["Line"][j]["Quantity"],
                                        2,
                                    )
                                    SalesItemLineDetail["TaxInclusiveAmt"] = (
                                        salesitemline["Amount"] * (100 + taxrate1) / 100
                                    )

                                    subtotal["Amount"] = multiple_invoice[i]["SubTotal"]
                                    TxnTaxDetail["TotalTax"] = multiple_invoice[i][
                                        "TotalTax"
                                    ]

                                    if "Discount" in multiple_invoice[i]["Line"][j]:
                                        discount_SalesItemLineDetail["Qty"] = 1
                                        discount_SalesItemLineDetail["UnitPrice"] = (
                                            -(
                                                multiple_invoice[i]["Line"][j][
                                                    "Quantity"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "UnitAmount"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "Discount"
                                                ]
                                            )
                                            / 100
                                        )
                                        discount["Amount"] = (
                                            -(
                                                multiple_invoice[i]["Line"][j][
                                                    "Quantity"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "UnitAmount"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "Discount"
                                                ]
                                            )
                                            / 100
                                        )

                                    if taxrate1 != 0:
                                        TaxDetail["Amount"] = multiple_invoice[i][
                                            "TotalTax"
                                        ]
                                        TaxLineDetail["NetAmountTaxable"] = round(
                                            multiple_invoice[i]["SubTotal"]
                                            - multiple_invoice[i]["TotalTax"],
                                            2,
                                        )
                                    else:
                                        TaxDetail["Amount"] = 0
                                        TaxLineDetail["NetAmountTaxable"] = 0

                                else:
                                    if "Discount" in multiple_invoice[i]["Line"][j]:
                                        discount_SalesItemLineDetail["Qty"] = -1
                                        discount_SalesItemLineDetail["UnitPrice"] = (
                                            multiple_invoice[i]["Line"][j]["Quantity"]
                                            * multiple_invoice[i]["Line"][j][
                                                "UnitAmount"
                                            ]
                                            * multiple_invoice[i]["Line"][j]["Discount"]
                                        ) / 100
                                        discount["Amount"] = (
                                            multiple_invoice[i]["Line"][j]["Quantity"]
                                            * multiple_invoice[i]["Line"][j][
                                                "UnitAmount"
                                            ]
                                            * multiple_invoice[i]["Line"][j]["Discount"]
                                        ) / 100

                                    SalesItemLineDetail["Qty"] = -multiple_invoice[i][
                                        "Line"
                                    ][j]["Quantity"]
                                    SalesItemLineDetail["UnitPrice"] = multiple_invoice[
                                        i
                                    ]["Line"][j]["UnitAmount"]
                                    salesitemline["Amount"] = round(
                                        multiple_invoice[i]["Line"][j]["UnitAmount"]
                                        * multiple_invoice[i]["Line"][j]["Quantity"],
                                        2,
                                    )
                                    SalesItemLineDetail["TaxInclusiveAmt"] = (
                                        salesitemline["Amount"] * (100 + taxrate1) / 100
                                    )

                                    subtotal["Amount"] = -multiple_invoice[i][
                                        "SubTotal"
                                    ]
                                    TxnTaxDetail["TotalTax"] = -multiple_invoice[i][
                                        "TotalTax"
                                    ]

                                    if taxrate1 != 0:
                                        TaxDetail["Amount"] = multiple_invoice[i][
                                            "TotalTax"
                                        ]
                                        TaxLineDetail["NetAmountTaxable"] = (
                                            multiple_invoice[i]["SubTotal"]
                                            - multiple_invoice[i]["TotalTax"]
                                        )
                                    else:
                                        if (
                                            multiple_invoice[i]["Line"][j]["TaxType"]
                                            == "GST"
                                            or multiple_invoice[i]["Line"][j]["TaxType"]
                                            == "INPUT"
                                            or multiple_invoice[i]["Line"][j]["TaxType"]
                                            == "OUTPUT"
                                        ):
                                            TaxDetail["Amount"] = -multiple_invoice[i][
                                                "TotalTax"
                                            ]
                                            TaxLineDetail["NetAmountTaxable"] = -round(
                                                multiple_invoice[i]["Line"][j][
                                                    "LineAmount"
                                                ]
                                                / (100 + taxrate1)
                                                * 100,
                                                2,
                                            )
                                        elif (
                                            multiple_invoice[i]["Line"][j]["TaxType"]
                                            in ['FRE','EXEMPTEXPENSES','EXEMPTOUTPUT']
                                        ):
                                            TaxDetail["Amount"] = 0
                                            TaxLineDetail["NetAmountTaxable"] = -round(
                                                multiple_invoice[i]["Line"][j][
                                                    "LineAmount"
                                                ],
                                                2,
                                            )
                                        elif (
                                            multiple_invoice[i]["Line"][j]["TaxType"]
                                            == "N-T"
                                        ):
                                            TaxDetail["Amount"] = 0
                                            TaxLineDetail["NetAmountTaxable"] = -round(
                                                multiple_invoice[i]["Line"][j][
                                                    "LineAmount"
                                                ],
                                                2,
                                            )

                                # invoice['TxnTaxDetail'] = TxnTaxDetail
                                TaxDetail["DetailType"] = "TaxLineDetail"
                                TaxDetail["TaxLineDetail"] = TaxLineDetail
                                TaxLineDetail["TaxRateRef"] = TaxRate
                                TaxLineDetail["PercentBased"] = True
                                discount["DetailType"] = "SalesItemLineDetail"
                                discount[
                                    "SalesItemLineDetail"
                                ] = discount_SalesItemLineDetail
                                discount_SalesItemLineDetail["ItemRef"] = ItemRef
                                discount_SalesItemLineDetail["ClassRef"] = ClassRef
                                discount_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                                discount_SalesItemLineDetail[
                                    "ItemAccountRef"
                                ] = ItemAccountRef

                            else:
                                if multiple_invoice[i]["SubTotal"] >= 0:
                                    SalesItemLineDetail["Qty"] = multiple_invoice[i][
                                        "Line"
                                    ][j]["Quantity"]
                                    #                 SalesItemLineDetail['UnitPrice'] = abs(multiple_invoice[i]['Line'][j]['UnitAmount'])
                                    SalesItemLineDetail["UnitPrice"] = (
                                        multiple_invoice[i]["Line"][j]["UnitAmount"]
                                        / (100 + taxrate1)
                                        * 100
                                    )
                                    salesitemline["Amount"] = round(
                                        SalesItemLineDetail["Qty"]
                                        * SalesItemLineDetail["UnitPrice"],
                                        2,
                                    )
                                    SalesItemLineDetail["TaxInclusiveAmt"] = (
                                        salesitemline["Amount"] * (100 + taxrate1) / 100
                                    )

                                    subtotal["Amount"] = (
                                        multiple_invoice[i]["SubTotal"]
                                        - multiple_invoice[i]["TotalTax"]
                                    )
                                    TxnTaxDetail["TotalTax"] = multiple_invoice[i][
                                        "TotalTax"
                                    ]

                                    # if multiple_invoice[i]['IsDiscounted'] == True:
                                    #     discount_SalesItemLineDetail['Qty'] = 1
                                    #     discount_SalesItemLineDetail['UnitPrice'] = -(multiple_invoice[i]['Line'][j]['Quantity'] *
                                    #         multiple_invoice[i]['Line'][j]['UnitAmount'] *
                                    #         multiple_invoice[i]['Line'][j]['Discount'] /
                                    #         (100 + taxrate1))
                                    #     discount['Amount'] = -round(
                                    #         (multiple_invoice[i]['Line'][j]['Quantity'] *
                                    #         multiple_invoice[i]['Line'][j]['UnitAmount'] *
                                    #         multiple_invoice[i]['Line'][j]['Discount'] /
                                    #         (100 + taxrate1)), 2)

                                else:
                                    SalesItemLineDetail["Qty"] = -multiple_invoice[i][
                                        "Line"
                                    ][j]["Quantity"]
                                    #                 SalesItemLineDetail['UnitPrice'] = abs(multiple_invoice[i]['Line'][j]['UnitAmount'])
                                    SalesItemLineDetail["UnitPrice"] = (
                                        multiple_invoice[i]["Line"][j]["UnitAmount"]
                                        / (100 + taxrate1)
                                        * 100
                                    )
                                    salesitemline["Amount"] = round(
                                        SalesItemLineDetail["Qty"]
                                        * SalesItemLineDetail["UnitPrice"],
                                        2,
                                    )
                                    SalesItemLineDetail["TaxInclusiveAmt"] = (
                                        salesitemline["Amount"] * (100 + taxrate1) / 100
                                    )

                                    subtotal["Amount"] = -(
                                        multiple_invoice[i]["SubTotal"]
                                        - multiple_invoice[i]["TotalTax"]
                                    )
                                    TxnTaxDetail["TotalTax"] = -multiple_invoice[i][
                                        "TotalTax"
                                    ]

                                    # if multiple_invoice[i]['IsDiscounted'] == True:
                                    #     discount_SalesItemLineDetail['Qty'] = -1
                                    #     discount_SalesItemLineDetail['UnitPrice'] = round(
                                    #         (multiple_invoice[i]['Line'][j]['Quantity'] *
                                    #         multiple_invoice[i]['Line'][j]['UnitAmount'] *
                                    #         multiple_invoice[i]['Line'][j]['Discount'] /
                                    #         (100 + taxrate1)), 2)
                                    #     discount['Amount'] = round(
                                    #         (multiple_invoice[i]['Line'][j]['Quantity'] *
                                    #         multiple_invoice[i]['Line'][j]['UnitAmount'] *
                                    #         multiple_invoice[i]['Line'][j]['Discount'] /
                                    #         (100 + taxrate1)), 2)

                            #                 salesitemline["Amount"] = abs(round(
                            #                     (multiple_invoice[i]['Line'][j]['UnitAmount']*multiple_invoice[i]['Line'][j]['Quantity']/(100+taxrate1)*100), 2))
                            #                 subtotal['Amount'] = abs(round((total_val), 2))
                            # invoice['TxnTaxDetail'] = TxnTaxDetail
                            TaxDetail["DetailType"] = "TaxLineDetail"
                            TaxDetail["TaxLineDetail"] = TaxLineDetail
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            discount["DetailType"] = "SalesItemLineDetail"
                            discount[
                                "SalesItemLineDetail"
                            ] = discount_SalesItemLineDetail
                            discount_SalesItemLineDetail["ItemRef"] = ItemRef
                            discount_SalesItemLineDetail["ClassRef"] = ClassRef
                            discount_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                            discount_SalesItemLineDetail[
                                "ItemAccountRef"
                            ] = ItemAccountRef

                            if multiple_invoice[i]["SubTotal"] >= 0:
                                if (
                                    multiple_invoice[i]["Line"][j]["TaxType"] == "GST"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "INPUT"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "OUTPUT"
                                ):
                                    TaxDetail["Amount"] = multiple_invoice[i][
                                        "TotalTax"
                                    ]
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        multiple_invoice[i]["Line"][j]["LineAmount"]
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )
                                elif multiple_invoice[i]["Line"][j]["TaxType"] in ['FRE','EXEMPTEXPENSES','EXEMPTOUTPUT']:
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        multiple_invoice[i]["Line"][j]["LineAmount"], 2
                                    )
                                elif multiple_invoice[i]["Line"][j]["TaxType"] == "N-T":
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        multiple_invoice[i]["Line"][j]["LineAmount"], 2
                                    )
                                else:
                                    pass
                            else:
                                if (
                                    multiple_invoice[i]["Line"][j]["TaxType"] == "GST"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "INPUT"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "OUTPUT"
                                ):
                                    TaxDetail["Amount"] = -multiple_invoice[i][
                                        "TotalTax"
                                    ]
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        TaxDetail["Amount"] * taxrate1, 2
                                    )
                                elif multiple_invoice[i]["Line"][j]["TaxType"] in ['FRE','EXEMPTEXPENSES','EXEMPTOUTPUT']:
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = -round(
                                        multiple_invoice[i]["Line"][j]["LineAmount"], 2
                                    )
                                elif multiple_invoice[i]["Line"][j]["TaxType"] == "N-T":
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = -round(
                                        multiple_invoice[i]["Line"][j]["LineAmount"], 2
                                    )
                                else:
                                    pass

                    subtotal["DetailType"] = "SubTotalLineDetail"
                    subtotal["SubTotalLineDetail"] = SubTotalLineDetail
                    salesitemline["DetailType"] = "SalesItemLineDetail"
                    salesitemline["SalesItemLineDetail"] = SalesItemLineDetail
                    if ItemRef != {}:
                        SalesItemLineDetail["ItemRef"] = ItemRef
                    SalesItemLineDetail["ClassRef"] = ClassRef
                    SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                    SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                    discount["DetailType"] = "SalesItemLineDetail"
                    discount["SalesItemLineDetail"] = discount_SalesItemLineDetail
                    discount_SalesItemLineDetail["ItemRef"] = ItemRef
                    discount_SalesItemLineDetail["ClassRef"] = ClassRef
                    discount_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                    discount_SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                    invoice["BillEmail"] = BillEmail
                    invoice["CustomerRef"] = CustomerRef

                    # if 'discount' in multiple_invoice[i]['Line'][j]:
                    #     if multiple_invoice[i]['Line'][j]['Discount'] > 0:
                    #         invoice["Line"].append(discount)
                    #         print("appended")
                    #     else:
                    #         print("not")

                    invoice["Line"].append(salesitemline)
                    if "Amount" in discount and discount["Amount"] != 0:
                        invoice["Line"].append(discount)

                    TxnTaxDetail["TaxLine"].append(TaxDetail)
                    if (
                        (discount != {} or discount is not None)
                        and ("Amount" in discount)
                        and ("Amount" in salesitemline)
                    ):
                        line_amount = (
                            line_amount + salesitemline["Amount"] + discount["Amount"]
                        )
                    else:
                        line_amount = line_amount  # + salesitemline["Amount"]

                    line_amount1 = line_amount + multiple_invoice[i]["TotalTax"]

            a = []

            for p2 in range(0, len(TxnTaxDetail["TaxLine"])):
                if TxnTaxDetail["TaxLine"][p2] in a:
                    pass
                else:
                    a.append(TxnTaxDetail["TaxLine"][p2])

            TxnTaxDetail["TaxLine"] = a
            # invoice["Line"].append(subtotal)

            if len(a) >= 1:
                if multiple_invoice[i]["LineAmountTypes"] == "TaxInclusive":
                    if line_amount1 == multiple_invoice[i]["TotalAmount"]:
                        pass
                    else:
                        line_amount == multiple_invoice[i]["TotalAmount"] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}
                            rounding_SalesItemLineDetail["Qty"] = 1

                            if multiple_invoice[i]["SubTotal"] >= 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                    abs(multiple_invoice[i]["TotalAmount"])
                                    - line_amount1
                                )
                                rounding["Amount"] = round(
                                    abs(multiple_invoice[i]["TotalAmount"])
                                    - line_amount1,
                                    2,
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                    abs(
                                        multiple_invoice[i]["TotalAmount"]
                                        - multiple_invoice[i]["TotalTax"]
                                    )
                                    - line_amount
                                )
                                rounding["Amount"] = round(
                                    abs(
                                        multiple_invoice[i]["TotalAmount"]
                                        - multiple_invoice[i]["TotalTax"]
                                    )
                                    - line_amount,
                                    2,
                                )

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"
                            ] = rounding_SalesItemLineDetail

                            for p3 in range(0, len(QBO_item)):
                                if QBO_item[p3]["FullyQualifiedName"] == "Rounding":
                                    ItemRef["name"] = QBO_item[p3]["FullyQualifiedName"]
                                    ItemRef["value"] = QBO_item[p3]["Id"]
                                    ItemAccountRef["name"] = QBO_item[p3][
                                        "IncomeAccountRef"
                                    ]["name"]
                                    ItemAccountRef["value"] = QBO_item[p3][
                                        "IncomeAccountRef"
                                    ]["value"]

                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"
                            ] = ItemAccountRef
                            TaxDetail["DetailType"] = "TaxLineDetail"
                            TaxDetail["TaxLineDetail"] = TaxLineDetail
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = rounding["Amount"]

                            for p6 in range(0, len(QBO_tax)):
                                if "GST free (sales)" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[p6]["Rate"]

                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            # TxnTaxDetail['TaxLine'].append(TaxDetail)

                            invoice["Line"].append(rounding)

                else:
                    if line_amount1 == multiple_invoice[i]["TotalAmount"]:
                        pass
                    else:
                        line_amount == multiple_invoice[i]["TotalAmount"] - line_amount1
                        if line_amount != 0:
                            ItemRef = {}
                            ClassRef = {}
                            TaxCodeRef = {}
                            ItemAccountRef = {}

                            rounding_SalesItemLineDetail["Qty"] = 1
                            if multiple_invoice[i]["SubTotal"] >= 0:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                    multiple_invoice[i]["TotalAmount"] - line_amount1
                                )
                                rounding["Amount"] = (
                                    multiple_invoice[i]["TotalAmount"] - line_amount1
                                )
                            else:
                                rounding_SalesItemLineDetail["UnitPrice"] = (
                                    multiple_invoice[i]["TotalAmount"] + line_amount1
                                )
                                rounding["Amount"] = (
                                    multiple_invoice[i]["TotalAmount"] + line_amount1
                                )

                            rounding["DetailType"] = "SalesItemLineDetail"
                            rounding["Description"] = "Rounding"
                            rounding[
                                "SalesItemLineDetail"
                            ] = rounding_SalesItemLineDetail

                            for p3 in range(0, len(QBO_item)):
                                if QBO_item[p3]["FullyQualifiedName"] == "Rounding":
                                    ItemRef["name"] = QBO_item[p3]["FullyQualifiedName"]
                                    ItemRef["value"] = QBO_item[p3]["Id"]
                                    ItemAccountRef["name"] = QBO_item[p3][
                                        "IncomeAccountRef"
                                    ]["name"]
                                    ItemAccountRef["value"] = QBO_item[p3][
                                        "IncomeAccountRef"
                                    ]["value"]

                            for p6 in range(0, len(QBO_tax)):
                                if "GST free (sales)" in QBO_tax[p6]["taxrate_name"]:
                                    TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]
                                    TaxRate["value"] = QBO_tax[p6]["taxrate_id"]

                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef
                            rounding_SalesItemLineDetail["ClassRef"] = ClassRef
                            rounding_SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef
                            rounding_SalesItemLineDetail[
                                "ItemAccountRef"
                            ] = ItemAccountRef
                            TaxDetail["DetailType"] = "TaxLineDetail"
                            TaxDetail["TaxLineDetail"] = TaxLineDetail
                            TaxDetail["Amount"] = 0
                            TaxLineDetail["NetAmountTaxable"] = rounding["Amount"]

                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            # TxnTaxDetail['TaxLine'].append(TaxDetail)

                            invoice["Line"].append(rounding)

            arr = TxnTaxDetail["TaxLine"]
            b1 = {"TaxLine": []}

            b = []
            for i2 in range(0, len(arr)):
                if 'value' in arr[i2]["TaxLineDetail"]["TaxRateRef"]: 
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
                    if arr[i4]["TaxLineDetail"]["TaxRateRef"]["value"] == e1[k]:
                        e["DetailType"] = "TaxLineDetail"
                        TaxLineDetail["TaxRateRef"] = TaxRateRef
                        TaxLineDetail["TaxPercent"] = arr[i4]["TaxLineDetail"][
                            "TaxPercent"
                        ]
                        TaxRateRef["value"] = e1[k]

                        amt = amt + arr[i4]["Amount"]
                        net_amt = net_amt + arr[i4]["TaxLineDetail"]["NetAmountTaxable"]
                        e["Amount"] = round(amt, 2)
                        TaxLineDetail["NetAmountTaxable"] = round(net_amt, 2)
                        e["TaxLineDetail"] = TaxLineDetail

                new_arr.append(e)

            for k3 in range(0, len(arr)):
                if 'value' in arr[k3]["TaxLineDetail"]["TaxRateRef"]: 
                    if arr[k3]["TaxLineDetail"]["TaxRateRef"]["value"] in single:
                        new_arr.append(arr[k3])

            b1["TaxLine"] = new_arr

            # TxnTaxDetail['TxnTaxDetail'] = b1
            # TxnTaxDetail['TaxLine'].append(TaxDetail)

            invoice["TxnTaxDetail"] = b1

            invoice["Line"].append(subtotal)
            # invoice["Line"].append(salesitemline)
            
            if multiple_invoice[i]["Status"] not in ["VOIDED","DELETED","SUBMITTED"]:
                if "SalesItemLineDetail" in invoice["Line"][0]:
                        count_of_items_not_found=0
                        line_item_count=len(invoice['Line'])-1
                            
                        for line in range(0,len(invoice['Line'])-1):
                            print(line)
                            print(invoice['Line'][line])
                            print("---------------")
                            if 'SalesItemLineDetail' in invoice['Line'][line]: 
                                if invoice['Line'][line]['SalesItemLineDetail']['ItemRef'] != {}:
                                    count_of_items_not_found+=0
                                else:
                                    count_of_items_not_found+=1
                                
                        # print(count_of_items_not_found,line_item_count,count_of_items_not_found==line_item_count)

                        if count_of_items_not_found>0:
                            print("Item Not pushed")
                        else:
                            url2 = "{}/creditmemo?minorversion=14".format(base_url)
                            payload = json.dumps(invoice)
                            inv_date = multiple_invoice[i]["TxnDate"][0:10]
                            inv_date1 = datetime.strptime(inv_date, "%Y-%m-%d")
                            if start_date1 is not None and end_date1 is not None:
                                if (inv_date1 >= start_date1) and (inv_date1 <= end_date1):
                                    post_data_in_qbo(url2, headers, payload,db['xero_creditnote'],_id, job_id,task_id, multiple_invoice[i]['Inv_No'])
                            

                else:
                    post_data_in_qbo(url2, headers, payload,db['xero_creditnote'],_id, job_id,task_id, multiple_invoice[i]['Inv_No'])
                
        
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_xero_credit_note -> add_xero_credit_note", ex)
        

def add_xero_open_credit_memo_cash_refund_as_journal(job_id,task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_xero_open_credit_memo_cash_refund_as_journal")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_open_credit_memo_cash_refund"].find({"job_id":job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        supplier = dbname["QBO_Supplier"].find({"job_id":job_id})
        supplier1 = []
        for k in supplier:
            supplier1.append(k)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p3 in QBO_Customer:
            QBO_customer.append(p3)

        QBO_Tax = dbname["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)

        Xero_COA = dbname["xero_coa"].find({"job_id":job_id})
        xero_coa = []
        for p6 in Xero_COA:
            xero_coa.append(p6)

        xero_arc_coa = dbname["xero_archived_coa"].find({"job_id":job_id})
        for p7 in xero_arc_coa:
            xero_coa.append(p7)

        QuerySet1 = journal

        for i in range(0, len(QuerySet1)):
            print(i)
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']
            for j1 in range(0, len(QBO_coa)):
                for j2 in range(0, len(xero_coa)):
                    if QuerySet1[i]["AccountCode"] == xero_coa[j2]["AccountID"]:
                        if (xero_coa[j2]["Name"].strip().lower()== QBO_coa[j1]["FullyQualifiedName"].strip().lower()) or (xero_coa[j2]["Name"].replace(":","-")== QBO_coa[j1]["FullyQualifiedName"]):
                            if QBO_coa[j1]["AccountType"] == "Bank":
                                payment_date = QuerySet1[i]["Date"]
                                payment_date11 = int(payment_date[6:16])
                                journal_date1 = datetime.utcfromtimestamp(
                                    payment_date11
                                ).strftime("%Y-%m-%d")

                                QuerySet2 = {"Line": []}
                                TxnTaxDetail = {}
                                QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                                QuerySet2["DocNumber"] = (
                                    "OpenCNCR-" + QuerySet1[i]["InvoiceID"][-5:]
                                )
                                
                                QuerySet2["TxnDate"] = str(journal_date1)[0:10]
                                QuerySet2['PrivateNote'] = "InvoiceID:- "+QuerySet1[i]['InvoiceID']+" & "+"InvoiceNo:- "+QuerySet1[i]['InvoiceNumber']

                                QuerySet3 = {}
                                QuerySet31 = {}
                                QuerySet32 = {}

                                QuerySet4 = {}
                                QuerySet41 = {}
                                QuerySet42 = {}
                                entity = {}
                                EntityRef = {}

                                QuerySet3["Amount"] = QuerySet1[i]["Amount"]
                                QuerySet3["DetailType"] = "JournalEntryLineDetail"
                                QuerySet3["JournalEntryLineDetail"] = QuerySet31
                                QuerySet31["PostingType"] = "Credit"
                                QuerySet31["AccountRef"] = QuerySet32

                                QuerySet32["name"] = QBO_coa[j1]["FullyQualifiedName"]
                                QuerySet32["value"] = QBO_coa[j1]["Id"]

                                QuerySet4["Amount"] = QuerySet1[i]["Amount"]
                                QuerySet4["DetailType"] = "JournalEntryLineDetail"
                                QuerySet4["JournalEntryLineDetail"] = QuerySet41
                                QuerySet41["PostingType"] = "Debit"
                                QuerySet41["Entity"] = entity
                                entity["EntityRef"] = EntityRef

                                for c1 in range(0, len(QBO_customer)):
                                    entity["Type"] = "Customer"
                                    if (
                                        QuerySet1[i]["Contact"].lower()
                                        == QBO_customer[c1]["DisplayName"].lower()
                                    ):
                                        EntityRef["name"] = QBO_customer[c1]["DisplayName"]
                                        EntityRef["value"] = QBO_customer[c1]["Id"]
                                    elif QBO_customer[c1]["DisplayName"].startswith(
                                        QuerySet1[i]["Contact"]
                                    ) and QBO_customer[c1]["DisplayName"].endswith("- C"):
                                        EntityRef["name"] = QBO_customer[c1]["DisplayName"]
                                        EntityRef["value"] = QBO_customer[c1]["Id"]
                                    
                                QuerySet41["AccountRef"] = QuerySet42

                                for j11 in range(0, len(QBO_coa)):
                                    if (
                                        QBO_coa[j11]["AccountType"]
                                        == "Accounts Receivable"
                                    ):
                                        QuerySet42["name"] = QBO_coa[j11][
                                            "FullyQualifiedName"
                                        ]
                                        QuerySet42["value"] = QBO_coa[j11]["Id"]

                                QuerySet2["Line"].append(QuerySet3)
                                QuerySet2["Line"].append(QuerySet4)

                                # if QuerySet1[i]['InvoiceNumber']=='REG#14':
                                payload = json.dumps(QuerySet2)
                                print(i)
                                print(payload)
                                print("===")
                                

                                post_data_in_qbo(url, headers, payload,dbname['xero_open_credit_memo_cash_refund'],_id, job_id,task_id, QuerySet1[i]['InvoiceNumber'])
                
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_xero_open_credit_memo_cash_refund", ex)

