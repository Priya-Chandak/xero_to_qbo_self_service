import json
import logging
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo


import logging



def add_vendorcredit(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_vendorcredit -> add_vendorcredit")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url1 = f"{base_url}/vendorcredit?minorversion=14"
        final_bill1 = db["xero_vendorcredit"].find({"job_id":job_id})
        final_bill = []
        for p1 in final_bill1:
            final_bill.append(p1)

        QBO_COA = db["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id":job_id})
        QBO_supplier = []
        for p3 in QBO_Supplier:
            QBO_supplier.append(p3)

        QBO_Item = db["QBO_Item"].find({"job_id":job_id})
        QBO_item = []
        for p4 in QBO_Item:
            QBO_item.append(p4)

        QBO_Class = db["QBO_Class"].find({"job_id":job_id})
        QBO_class = []
        for p5 in QBO_Class:
            QBO_class.append(p5)

        QBO_Tax = db["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p6 in QBO_Tax:
            QBO_tax.append(p6)

        XERO_COA = db["xero_coa"].find({"job_id":job_id})
        xero_coa1 = []
        for p7 in XERO_COA:
            xero_coa1.append(p7)

        Xero_Items = db["xero_items"].find({"job_id":job_id})
        xero_items = []
        for p8 in Xero_Items:
            xero_items.append(p8)

        vendor_credit_arr = []

        final_bill = final_bill

        for i in range(0, len(final_bill)):
            _id = final_bill[i]['_id']
            task_id = final_bill[i]['task_id']
            
            if final_bill[i]["Status"] not in ["VOIDED","DELETED","SUBMITTED","DRAFT"]:
                if "Line" in final_bill[i]:
                    QuerySet = {"Line": []}
                    TxnTaxDetail = {"TaxLine": []}

                    for j in range(0, len(final_bill[i]["Line"])):
                        if "Quantity" in final_bill[i]["Line"][j]:
                            QuerySet1 = {}
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            TaxLineDetail = {}
                            TaxRate = {}
                            Tax = {}
                            TaxCodeRef = {}
                            ItemRef = {}
                            QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])
                            taxrate1 = 0

                            for j1 in range(0, len(QBO_item)):
                                for j2 in range(0, len(xero_items)):
                                    if ("ItemCode" in final_bill[i]["Line"][j]) and (
                                        "AccountCode" in final_bill[i]["Line"][j]
                                    ):
                                        if (
                                            final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                            == xero_items[j2]["Code"]
                                        ):
                                            if (
                                                xero_items[j2]["Name"]
                                                + "-"
                                                + final_bill[i]["Line"][j][
                                                    "AccountCode"
                                                ]
                                                == QBO_item[j1]["Name"]
                                            ):
                                                ItemRef["value"] = QBO_item[j1]["Id"]

                                    elif ("ItemCode" in final_bill[i]["Line"][j]) and (
                                        ("AccountCode" not in final_bill[i]["Line"][j])
                                    ):
                                        if (
                                            final_bill[i]["Line"][j]["ItemCode"].replace(":","-")
                                            == xero_items[j2]["Code"]
                                        ):
                                            if (
                                                xero_items[j2]["Name"]
                                                == QBO_item[j1]["Name"]
                                            ):
                                                ItemRef["value"] = QBO_item[j1]["Id"]

                            # QuerySet2['Qty'] = final_bill[i]['Line'][j]['Quantity']
                            # QuerySet2['UnitPrice'] = final_bill[i]['Line'][j]['UnitAmount']

                            # QuerySet2['ItemRef'] = ItemRef

                            for k1 in range(0, len(QBO_tax)):
                                if "AccountCode" in final_bill[i]["Line"][j]:
                                    if (
                                        (
                                            final_bill[i]["Line"][j]["TaxType"]
                                            == "BASEXCLUDED"
                                        )
                                        or (final_bill[i]["Line"][j]["TaxType"] == None)
                                        or (
                                            final_bill[i]["Line"][j]["TaxType"]
                                            == "NONE"
                                        )
                                    ):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if "NOTAXP" in QBO_tax[k1]["taxrate_name"]:
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
                                                Tax["Amount"] = abs(
                                                    final_bill[i]["TotalTax"]
                                                )

                                    elif final_bill[i]["Line"][j]["TaxType"] == "INPUT":
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
                                                TaxLineDetail["NetAmountTaxable"] = (
                                                    final_bill[i]["Line"][j][
                                                        "UnitAmount"
                                                    ]
                                                    - final_bill[i]["Line"][j][
                                                        "TaxAmount"
                                                    ]
                                                )
                                                Tax["Amount"] = abs(
                                                    final_bill[i]["TotalTax"]
                                                )

                                    elif (
                                        final_bill[i]["Line"][j]["TaxType"] == "OUTPUT"
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
                                                TaxLineDetail["TaxPercent"] = QBO_tax[
                                                    k1
                                                ]["Rate"]
                                                taxrate1 = QBO_tax[k1]["Rate"]
                                                TaxLineDetail["NetAmountTaxable"] = (
                                                    final_bill[i]["Line"][j][
                                                        "UnitAmount"
                                                    ]
                                                    - final_bill[i]["Line"][j][
                                                        "TaxAmount"
                                                    ]
                                                )
                                                Tax["Amount"] = abs(
                                                    final_bill[i]["TotalTax"]
                                                )

                                    elif (
                                        final_bill[i]["Line"][j]["TaxType"] in ["EXEMPTEXPENSES","EXEMPTOUTPUT","INPUTTAXED"]
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
                                                TaxLineDetail["TaxPercent"] = QBO_tax[
                                                    k1
                                                ]["Rate"]
                                                taxrate1 = QBO_tax[k1]["Rate"]
                                                Tax["Amount"] = (
                                                    abs(final_bill[i]["TotalTax"])
                                                    * taxrate1
                                                )

                                    else:
                                        pass

                            Tax["DetailType"] = "TaxLineDetail"
                            Tax["TaxLineDetail"] = TaxLineDetail
                            TxnTaxDetail["TotalTax"] = abs(final_bill[i]["TotalTax"])

                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            if TaxRate != {}:
                                TxnTaxDetail["TaxLine"].append(Tax)
                            QuerySet["TxnTaxDetail"] = TxnTaxDetail

                            if final_bill[i]["LineAmountTypes"] == "Inclusive":
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                QuerySet1["Amount"] = (
                                    final_bill[i]["Line"][j]["UnitAmount"]
                                    - final_bill[i]["Line"][j]["TaxAmount"]
                                )
                                TaxLineDetail["NetAmountTaxable"] = (
                                    final_bill[i]["Line"][j]["UnitAmount"]
                                    - final_bill[i]["Line"][j]["TaxAmount"]
                                )

                            else:
                                QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                QuerySet1["Amount"] = abs(
                                    final_bill[i]["Line"][j]["LineAmount"]
                                )
                                TaxLineDetail["NetAmountTaxable"] = (
                                    final_bill[i]["Line"][j]["UnitAmount"]
                                    - final_bill[i]["Line"][j]["TaxAmount"]
                                )

                            if "supplier_invoice_no" in final_bill[i]:
                                if (
                                    final_bill[i]["supplier_invoice_no"] == None
                                    or final_bill[i]["supplier_invoice_no"] == ""
                                ):
                                    QuerySet["DocNumber"] = final_bill[i]["Inv_No"][0:15]+final_bill[i]["Inv_ID"][-6:]
                                elif (
                                    final_bill[i]["supplier_invoice_no"] != ""
                                    or final_bill[i]["supplier_invoice_no"] is not None
                                ):
                                    QuerySet["DocNumber"] = (
                                        final_bill[i]["Inv_No"]
                                        + "-"
                                        + final_bill[i]["supplier_invoice_no"]
                                    )
                            else:
                                QuerySet["DocNumber"] = final_bill[i]["Inv_No"][0:21]

                            if "Comment" in final_bill[i]:
                                QuerySet["PrivateNote"] = final_bill[i]["Comment"]

                            QuerySet2["TaxCodeRef"] = TaxCodeRef
                            QuerySet["TxnDate"] = final_bill[i]["TxnDate"]
                            if "Description" in final_bill[i]["Line"][j]:
                                QuerySet1["Description"] = final_bill[i]["Line"][j][
                                    "Description"
                                ]
                            QuerySet1["DetailType"] = "AccountBasedExpenseLineDetail"
                            QuerySet1["AccountBasedExpenseLineDetail"] = QuerySet2

                            
                            for j1 in range(0, len(QBO_coa)):
                                for j2 in range(0, len(xero_coa1)):
                                    if 'Code' in xero_coa1[j2]:
                                        if 'AccountCode' in final_bill[i]['Line'][j]:
                                            if 'AcctNum' in QBO_coa[j1]:
                                                if final_bill[i]['Line'][j]['AccountCode'] == QBO_coa[j1]["AcctNum"]:
                                                    QuerySet3['value'] = QBO_coa[j1]["Id"]
                                                
                                            elif final_bill[i]['Line'][j]['AccountCode'] == xero_coa1[j2]["Code"]:
                                                if xero_coa1[j2]["Name"].lower().strip() == QBO_coa[j1]["FullyQualifiedName"].lower().strip():
                                                    QuerySet3['value'] = QBO_coa[j1]["Id"]

                            QuerySet2['AccountRef'] = QuerySet3
                            
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

                            QuerySet2['ClassRef'] = QuerySet5

                            for j2 in range(0, len(QBO_class)):
                                if final_bill[i]['Line'][j]['TrackingID'] == QBO_class[j2]['Name']:
                                    QuerySet5['value'] = QBO_class[j2]['Id']
                                    QuerySet5['name'] = QBO_class[j2]['Name']

                            if "AccountCode" in final_bill[i]["Line"][j]:
                                QuerySet["Line"].append(QuerySet1)

                    vendor_credit_arr.append(QuerySet)

                    payload = json.dumps(QuerySet)
                    bill_date = final_bill[i]["TxnDate"][0:10]
                    bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")

                    if start_date1 is not None and end_date1 is not None:
                        if (bill_date1 >= start_date1) and (bill_date1 <= end_date1):
                            post_data_in_qbo(url1, headers, payload,db['xero_vendorcredit'],_id, job_id,task_id, final_bill[i]['Inv_No'])
                    else:
                        post_data_in_qbo(url1, headers, payload,db['xero_vendorcredit'],_id, job_id,task_id, final_bill[i]['Inv_No'])
                
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_vendorcredit -> add_vendorcredit", ex)
        
