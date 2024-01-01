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


def add_open_xero_vendorcredit(job_id,task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_vendorcredit -> add_vendorcredit")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url1 = f"{base_url}/vendorcredit?minorversion=14"
        final_bill1 = db["xero_open_suppliercredit"].find({"job_id":job_id})
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
            print(i)
            _id = final_bill[i]['_id']
            task_id = final_bill[i]['task_id']
            
            if final_bill[i]["Status"] not in ["DELETED"]:
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
                                        if (final_bill[i]["Line"][j]["ItemCode"])!=None:
                                            print(final_bill[i]["Line"][j]["ItemCode"],final_bill[i]["Line"][j]["ItemCode"]==None)
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
                                        if (final_bill[i]["Line"][j]['ItemCode'])!=None:
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

                                    elif final_bill[i]["Line"][j]["TaxType"] in ["INPUT","INPUT2"]:
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
                                # QuerySet["DocNumber"] = final_bill[i]["Inv_No"][0:15]+"-"+final_bill[i]["Inv_ID"][-5:]
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
                                # for j2 in range(0, len(xero_coa1)):
                                #     if 'Code' in xero_coa1[j2]:
                                if 'AccountCode' in final_bill[i]['Line'][j]:
                                    if 'AcctNum' in QBO_coa[j1]:
                                        if final_bill[i]['Line'][j]['AccountCode'] == QBO_coa[j1]["AcctNum"]:
                                            QuerySet3['value'] = QBO_coa[j1]["Id"]
                                            break
                                    
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
                                if 'TrackingID' in final_bill[i]['Line'][j]: 
                                    if final_bill[i]['Line'][j]['TrackingID'] == QBO_class[j2]['Name']:
                                        QuerySet5['value'] = QBO_class[j2]['Id']
                                        QuerySet5['name'] = QBO_class[j2]['Name']
                                        break

                            if "AccountCode" in final_bill[i]["Line"][j]:
                                QuerySet["Line"].append(QuerySet1)

                    vendor_credit_arr.append(QuerySet)

                    payload = json.dumps(QuerySet)
                    
                    post_data_in_qbo(url1, headers, payload,db['xero_open_suppliercredit'],_id, job_id,task_id, final_bill[i]['Inv_No'])
                    
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_vendorcredit -> add_vendorcredit", ex)
        

def add_xero_open_supplier_credit_cash_refund_as_journal(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal1 = dbname["xero_open_supplier_credit_cash_refund"].find({"job_id":job_id})

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

        xero_archived_coa1 = dbname["xero_archived_coa"].find({"job_id":job_id})
        for p7 in xero_archived_coa1:
            xero_coa.append(p7)

        QuerySet1 = journal

        for i in range(0, len(QuerySet1)):
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']
            for j1 in range(0, len(QBO_coa)):
                for j2 in range(0, len(xero_coa)):
                    if QuerySet1[i]["AccountCode"] == xero_coa[j2]["AccountID"]:
                        if (xero_coa[j2]["Name"].strip().lower()== QBO_coa[j1]["FullyQualifiedName"].strip().lower()) or (xero_coa[j2]["Name"].replace(":","-")== QBO_coa[j1]["FullyQualifiedName"]):
                        
                            payment_date = QuerySet1[i]["Date"]
                            payment_date11 = int(payment_date[6:16])
                            journal_date1 = datetime.utcfromtimestamp(
                                payment_date11
                            ).strftime("%Y-%m-%d")

                            QuerySet2 = {"Line": []}
                            TxnTaxDetail = {}
                            QuerySet2["TxnTaxDetail"] = TxnTaxDetail
                            QuerySet2["DocNumber"] = (
                                "OpenVCCR-" + QuerySet1[i]["InvoiceID"][-5:]
                            )
                            QuerySet2['PrivateNote'] = "InvoiceID:- "+QuerySet1[i]['InvoiceID']+" & "+"BillNo:- "+QuerySet1[i]['InvoiceNumber']
                            QuerySet2["TxnDate"] = str(journal_date1)[0:10]

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
                            QuerySet31["PostingType"] = "Debit"
                            QuerySet31["AccountRef"] = QuerySet32

                            QuerySet32["name"] = QBO_coa[j1]["FullyQualifiedName"]
                            QuerySet32["value"] = QBO_coa[j1]["Id"]

                            QuerySet4["Amount"] = QuerySet1[i]["Amount"]
                            QuerySet4["DetailType"] = "JournalEntryLineDetail"
                            QuerySet4["JournalEntryLineDetail"] = QuerySet41
                            QuerySet41["PostingType"] = "Credit"
                            QuerySet41["Entity"] = entity
                            entity["EntityRef"] = EntityRef

                            for j in range(0, len(supplier1)):
                                entity["Type"] = "Vendor"
                                if (
                                    QuerySet1[i]["Contact"].lower()
                                    == supplier1[j]["DisplayName"].lower()
                                ):
                                    EntityRef["name"] = supplier1[j]["DisplayName"]
                                    EntityRef["value"] = supplier1[j]["Id"]
                                    break
                                elif supplier1[j]["DisplayName"].startswith(
                                    QuerySet1[i]["Contact"]
                                ) and supplier1[j]["DisplayName"].endswith("- S"):
                                    EntityRef["name"] = supplier1[j]["DisplayName"]
                                    EntityRef["value"] = supplier1[j]["Id"]
                                    continue
                                
                            QuerySet41["AccountRef"] = QuerySet42

                            for j1 in range(0, len(QBO_coa)):
                                if (
                                    QBO_coa[j1]["AccountType"]
                                    == "Accounts Payable"
                                ):
                                    QuerySet42["value"] = QBO_coa[j1]["Id"]

                            QuerySet2["Line"].append(QuerySet3)
                            QuerySet2["Line"].append(QuerySet4)

                            payload = json.dumps(QuerySet2)

                            post_data_in_qbo(url, headers, payload,dbname['xero_open_supplier_credit_cash_refund'],_id, job_id,task_id, QuerySet1[i]['InvoiceNumber'])
            
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add xero_open_supplier_credit_cash_refund", ex)
