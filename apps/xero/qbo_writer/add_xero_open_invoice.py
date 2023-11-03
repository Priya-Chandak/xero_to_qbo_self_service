import json
import logging
from datetime import datetime
import requests
from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo


logger = logging.getLogger(__name__)

from datetime import datetime, timedelta, timezone
import math

def add_xero_open_invoice(job_id,task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_xero_invoice -> add_xero_invoice")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        multiple_item_invoice = dbname["xero_open_invoice"].find({"job_id":job_id})

        multiple_invoice = []
        for p1 in multiple_item_invoice:
            multiple_invoice.append(p1)

        multiple_invoice = multiple_invoice

        QBO_Item = dbname["QBO_Item"].find({"job_id":job_id})
        QBO_item = []
        for p1 in QBO_Item:
            QBO_item.append(p1)

        QBO_Class = dbname["QBO_Class"].find({"job_id":job_id})
        QBO_class = []
        for p2 in QBO_Class:
            QBO_class.append(p2)

        QBO_Tax = dbname["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p3 in QBO_Tax:
            QBO_tax.append(p3)

        QBO_COA = dbname["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for c4 in QBO_COA:
            QBO_coa.append(c4)

        QBO_Customer = dbname["QBO_Customer"].find({"job_id":job_id})
        QBO_customer = []
        for p5 in QBO_Customer:
            QBO_customer.append(p5)

        non_items = []

        for i in range(0, len(multiple_invoice)):
            print(multiple_invoice[i]['Inv_No'])
            _id = multiple_invoice[i]['_id']
            task_id = multiple_invoice[i]['task_id']
            
            invoice = {"Line": []}
            CustomerRef = {}
            BillEmail = {}
            TxnTaxDetail = {"TaxLine": []}
            invoice["TxnDate"] = multiple_invoice[i]["TxnDate"]
            invoice["DueDate"] = multiple_invoice[i]["DueDate"]
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
                        multiple_invoice[i]["ContactName"].strip().lower()
                        == QBO_customer[p1]["DisplayName"].strip().lower()
                    ):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                    elif (
                        multiple_invoice[i]["ContactName"]
                        == QBO_customer[p1]["DisplayName"]
                    ):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                    elif (QBO_customer[p1]["DisplayName"]).startswith(
                        multiple_invoice[i]["ContactName"]
                    ) and ((QBO_customer[p1]["DisplayName"]).endswith("- C")):
                        CustomerRef["value"] = QBO_customer[p1]["Id"]
                        CustomerRef["name"] = QBO_customer[p1]["DisplayName"]
                        break
                   
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
                if (
                   "AccountCode" in multiple_invoice[i]["Line"][j]
                ):
                    print(j)
                    TaxLineDetail = {}
                    CustomerMemo = {}
                    salesitemline = {}
                    discount = {}
                    rounding = {}
                    SalesItemLineDetail = {}
                    discount_SalesItemLineDetail = {}
                    rounding_SalesItemLineDetail = {}
                    ItemRef1 = {}
                    ItemRef ={}
                    ClassRef = {}
                    TaxCodeRef = {}
                    ItemAccountRef = {}
                    TaxRate = {}
                    SubTotalLineDetail = {}
                    TaxDetail = {}
                    salesitemline["DetailType"] = "SalesItemLineDetail"
                    discount["Description"] = "Discount"

                    # if multiple_invoice[i]["Line"][j]["Quantity"] == 0:
                    #     multiple_invoice[i]["Line"][j]["Quantity"] = 1

                    # if multiple_invoice[i]["Line"][j]["UnitAmount"] == 0:
                    #     multiple_invoice[i]["Line"][j]["UnitAmount"] = multiple_invoice[
                    #         i
                    #     ]["Line"][j]["LineAmount"]

                    salesitemline["Description"] = multiple_invoice[i]["Line"][j][
                            "Description"
                        ]
                    
                    for p4 in range(0, len(QBO_item)):
                        if "ItemCode" in multiple_invoice[i]["Line"][j] and "AccountCode" in multiple_invoice[i]["Line"][j]:
                            if QBO_item[p4]["Name"]==(multiple_invoice[i]["Line"][j]["ItemCode"].replace(":","-")+"-"+multiple_invoice[i]["Line"][j]["AccountCode"]):
                                ItemRef1["name"] = QBO_item[p4]["Name"]
                                ItemRef1["value"] = QBO_item[p4]["Id"]
                                break
                            elif QBO_item[p4]["Name"]==(multiple_invoice[i]["Line"][j]["ItemCode"]+"-"+multiple_invoice[i]["Line"][j]["AccountCode"]):
                                ItemRef1["name"] = QBO_item[p4]["Name"]
                                ItemRef1["value"] = QBO_item[p4]["Id"]
                                break
                            else:
                                if 'Sku' in QBO_item[p4]:
                                    if multiple_invoice[i]["Line"][j]["ItemCode"].replace(":","-")== QBO_item[p4]["Sku"]:
                                        ItemRef1["name"] = QBO_item[p4]["Name"]
                                        ItemRef1["value"] = QBO_item[p4]["Id"]
                                        continue
                                    elif multiple_invoice[i]["Line"][j]["ItemCode"]== QBO_item[p4]["Sku"]:
                                        ItemRef1["name"] = QBO_item[p4]["Name"]
                                        ItemRef1["value"] = QBO_item[p4]["Id"]
                                        continue
                                else:
                                    if multiple_invoice[i]["Line"][j]["ItemCode"].replace(":","-")== QBO_item[p4]["Name"]:
                                        ItemRef1["name"] = QBO_item[p4]["Name"]
                                        ItemRef1["value"] = QBO_item[p4]["Id"]
                                        continue
                        
                        elif "ItemCode" not in multiple_invoice[i]["Line"][j] and "AccountCode" in multiple_invoice[i]["Line"][j]:
                            if "Sku" in QBO_item[p4]:
                                if (
                                    multiple_invoice[i]["Line"][j]["AccountCode"]
                                    == QBO_item[p4]["Sku"]
                                ):
                                    ItemRef1["name"] = QBO_item[p4]["Name"]
                                    ItemRef1["value"] = QBO_item[p4]["Id"]
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
                                                == QBO_item[p4]["Name"]
                                            ):
                                                ItemRef1["name"] = QBO_item[p4]["Name"]
                                                ItemRef1["value"] = QBO_item[p4]["Id"]
                                                break
                    
                    if "job" in multiple_invoice[i]["Line"][j]:
                        for p41 in range(0, len(QBO_class)):
                            if multiple_invoice[i]["Line"][j]["job"] is not None:
                                if (
                                    multiple_invoice[i]["Line"][j]["job"]
                                    == QBO_class[p41]["Name"]
                                ):
                                    ClassRef["name"] = QBO_class[p41]["Name"]
                                    ClassRef["value"] = QBO_class[p41]["Id"]
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
                        else:
                            if QBO_coa[p5]["Name"] == "Services":
                                ItemAccountRef["name"] = QBO_coa[p5]["Name"]
                                ItemAccountRef["value"] = QBO_coa[p5]["Id"]

                    for p6 in range(0, len(QBO_tax)):
                        if "TaxType" not in multiple_invoice[i]["Line"][j]:
                            if "taxrate_name" in QBO_tax[p6]:
                                if QBO_tax[p6]["taxrate_name"] == "Input tax (sales)":
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

                        elif "TaxType" in multiple_invoice[i]["Line"][j]:
                            if (
                                multiple_invoice[i]["Line"][j]["TaxType"] == "OUTPUT"
                                or multiple_invoice[i]["Line"][j]["TaxType"] == "GST"
                                or multiple_invoice[i]["Line"][j]["TaxType"] == "INPUT"
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

                            elif (
                                multiple_invoice[i]["Line"][j]["TaxType"] == "FRE"
                                or multiple_invoice[i]["Line"][j]["TaxType"]
                                == "EXEMPTOUTPUT"
                            ):
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
                                    salesitemline["Amount"] =multiple_invoice[i]["Line"][j]["UnitAmount"]* multiple_invoice[i]["Line"][j]["Quantity"]
                                    SalesItemLineDetail["TaxInclusiveAmt"] = round(
                                        salesitemline["Amount"]
                                        * (100 + taxrate1)
                                        / 100,
                                        2,
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
                                    salesitemline["Amount"] = multiple_invoice[i]["Line"][j]["UnitAmount"]* multiple_invoice[i]["Line"][j]["Quantity"]
                                    SalesItemLineDetail["TaxInclusiveAmt"] = round(
                                        salesitemline["Amount"]
                                        * (100 + taxrate1)
                                        / 100,
                                        2,
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
                                            == "FRE"
                                            or multiple_invoice[i]["Line"][j]["TaxType"]
                                            == "EXEMPTOUTPUT"
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
                                            or multiple_invoice[i]["Line"][j]["TaxType"]
                                            == "BASEXCLUDED"
                                            or multiple_invoice[i]["Line"][j]["TaxType"]
                                            == "NONE"
                                            or multiple_invoice[i]["Line"][j]["TaxType"]
                                            == None
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
                                discount_SalesItemLineDetail["ItemRef"] = ItemRef1 
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
                                    salesitemline["Amount"] = SalesItemLineDetail["Qty"]* SalesItemLineDetail["UnitPrice"]
                                    SalesItemLineDetail["TaxInclusiveAmt"] = round(
                                        salesitemline["Amount"] * (100 + taxrate1) / 100,2
                                    )

                                    subtotal["Amount"] = (
                                        multiple_invoice[i]["SubTotal"]
                                        - multiple_invoice[i]["TotalTax"]
                                    )
                                    TxnTaxDetail["TotalTax"] = multiple_invoice[i][
                                        "TotalTax"
                                    ]

                                    if multiple_invoice[i]["IsDiscounted"] == True:
                                        discount_SalesItemLineDetail["Qty"] = 1
                                        discount_SalesItemLineDetail["UnitPrice"] = -(
                                            multiple_invoice[i]["Line"][j]["Quantity"]
                                            * multiple_invoice[i]["Line"][j][
                                                "UnitAmount"
                                            ]
                                            * multiple_invoice[i]["Line"][j]["Discount"]
                                            / (100 + taxrate1)
                                        )
                                        discount["Amount"] = -round(
                                            (
                                                multiple_invoice[i]["Line"][j][
                                                    "Quantity"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "UnitAmount"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "Discount"
                                                ]
                                                / (100 + taxrate1)
                                            ),
                                            2,
                                        )

                                else:
                                    SalesItemLineDetail["Qty"] = -multiple_invoice[i][
                                        "Line"
                                    ][j]["Quantity"]
                                    #                 SalesItemLineDetail['UnitPrice'] = abs(multiple_invoice[i]['Line'][j]['UnitAmount'])
                                    SalesItemLineDetail["UnitPrice"] = round(
                                        multiple_invoice[i]["Line"][j]["UnitAmount"]
                                        / (100 + taxrate1)
                                        * 100,2
                                    )
                                    salesitemline["Amount"] =SalesItemLineDetail["Qty"]* SalesItemLineDetail["UnitPrice"]
                                    SalesItemLineDetail["TaxInclusiveAmt"] = round(
                                        salesitemline["Amount"] * (100 + taxrate1) / 100,2
                                    )

                                    subtotal["Amount"] = -(
                                        multiple_invoice[i]["SubTotal"]
                                        - multiple_invoice[i]["TotalTax"]
                                    )
                                    TxnTaxDetail["TotalTax"] = -multiple_invoice[i][
                                        "TotalTax"
                                    ]

                                    if multiple_invoice[i]["IsDiscounted"] == True:
                                        discount_SalesItemLineDetail["Qty"] = -1
                                        discount_SalesItemLineDetail[
                                            "UnitPrice"
                                        ] = round(
                                            (
                                                multiple_invoice[i]["Line"][j][
                                                    "Quantity"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "UnitAmount"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "Discount"
                                                ]
                                                / (100 + taxrate1)
                                            ),
                                            2,
                                        )
                                        discount["Amount"] = round(
                                            (
                                                multiple_invoice[i]["Line"][j][
                                                    "Quantity"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "UnitAmount"
                                                ]
                                                * multiple_invoice[i]["Line"][j][
                                                    "Discount"
                                                ]
                                                / (100 + taxrate1)
                                            ),
                                            2,
                                        )

                            TaxDetail["DetailType"] = "TaxLineDetail"
                            TaxDetail["TaxLineDetail"] = TaxLineDetail
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            discount["DetailType"] = "SalesItemLineDetail"
                            discount[
                                "SalesItemLineDetail"
                            ] = discount_SalesItemLineDetail
                            discount_SalesItemLineDetail["ItemRef"] = ItemRef1 
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
                                elif (
                                    multiple_invoice[i]["Line"][j]["TaxType"] == "FRE"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "EXEMPTOUTPUT"
                                ):
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        multiple_invoice[i]["Line"][j]["LineAmount"], 2
                                    )
                                elif (
                                    multiple_invoice[i]["Line"][j]["TaxType"] == "N-T"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "BASEXCLUDED"
                                    or multiple_invoice[i]["Line"][j]["TaxType"] == None
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "NONE"
                                ):
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
                                elif (
                                    multiple_invoice[i]["Line"][j]["TaxType"] == "FRE"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "EXEMPTOUTPUT"
                                ):
                                    TaxDetail["Amount"] = 0
                                    TaxLineDetail["NetAmountTaxable"] = -round(
                                        multiple_invoice[i]["Line"][j]["LineAmount"], 2
                                    )
                                elif (
                                    multiple_invoice[i]["Line"][j]["TaxType"] == "N-T"
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "BASEXCLUDED"
                                    or multiple_invoice[i]["Line"][j]["TaxType"] == None
                                    or multiple_invoice[i]["Line"][j]["TaxType"]
                                    == "NONE"
                                ):
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
                    # if ItemRef!={}:
                    SalesItemLineDetail["ItemRef"] = ItemRef1 if ItemRef1!={} else ItemRef
                    SalesItemLineDetail["ClassRef"] = ClassRef
                    if TaxCodeRef == {}:
                        for p6 in range(0, len(QBO_tax)):
                            if "Input tax" in QBO_tax[p6]["taxcode_name"]:
                                TaxCodeRef["value"] = QBO_tax[p6]["taxcode_id"]

                    SalesItemLineDetail["TaxCodeRef"] = TaxCodeRef

                    SalesItemLineDetail["ItemAccountRef"] = ItemAccountRef

                    discount["DetailType"] = "SalesItemLineDetail"
                    discount["SalesItemLineDetail"] = discount_SalesItemLineDetail
                    discount_SalesItemLineDetail["ItemRef"] = ItemRef1 if ItemRef1!={} else ItemRef
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
                    if round(line_amount1,2) == multiple_invoice[i]["TotalAmount"]:
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

                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef1 if ItemRef1!={} else ItemRef
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
                    if round(line_amount1,2) == multiple_invoice[i]["TotalAmount"]:
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

                            rounding_SalesItemLineDetail["ItemRef"] = ItemRef1 if ItemRef1!={} else ItemRef
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
                if 'TaxLineDetail' in arr[i2]:
                    if arr[i2]["TaxLineDetail"]["TaxRateRef"] != {}:
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
                    if 'value' in arr[i4]["TaxLineDetail"]["TaxRateRef"]: 
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

            # for k3 in range(0,len(arr)):
            #     if arr[k3]['TaxLineDetail']['TaxRateRef'] != {}:
            #         if arr[k3]['TaxLineDetail']['TaxRateRef'] in single:
            #             new_arr.append(arr[k3])

            # b1["TaxLine"] = new_arr

            TxnTaxDetail['TxnTaxDetail'] = b1
            # TxnTaxDetail['TaxLine'].append(TaxDetail)

            # invoice["TxnTaxDetail"] = b1

            invoice["Line"].append(subtotal)
            print(invoice)
            # invoice["Line"].append(salesitemline)

            
            if multiple_invoice[i]["TotalAmount"] >= 0:
                if "SalesItemLineDetail" in invoice["Line"][0]:
                    count_of_items_not_found=0
                    line_item_count=len(invoice['Line'])-1
                        
                    for line in range(0,len(invoice['Line'])-1):
                        if 'SalesItemLineDetail' in invoice['Line'][line]: 
                            if invoice['Line'][line]['SalesItemLineDetail']['ItemRef'] != {}:
                                count_of_items_not_found+=0
                            else:
                                count_of_items_not_found+=1
                            
                    # print(count_of_items_not_found,line_item_count,count_of_items_not_found==line_item_count)

                    if count_of_items_not_found>0:
                        print("Item Not pushed")
                    else:
                        url1 = "{}/invoice?minorversion=14".format(base_url)
                        payload = json.dumps(invoice)
                        
                        post_data_in_qbo(url1, headers, payload,dbname['xero_open_invoice'],_id, job_id,task_id, multiple_invoice[i]['Inv_No'])
                        
                
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_xero_invoice -> add_xero_invoice", ex)
        
