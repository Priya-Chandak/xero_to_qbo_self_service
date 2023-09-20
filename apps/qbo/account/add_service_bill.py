import json
import traceback
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo
from collections import Counter



def add_service_bill(job_id,task_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url1 = f"{base_url}/bill?minorversion=14"
        url2 = f"{base_url}/vendorcredit?minorversion=14"

        db = get_mongodb_database()

        final_bill1 = db["final_bill"].find({"job_id": job_id})

        final_bill = []
        for p1 in final_bill1:
            final_bill.append(p1)

        # m1=[]
        # for m in range(0,len(final_bill)):
        #     # if final_bill[m]['LineAmountTypes']=="Exclusive":
        #     if final_bill[m]['invoice_no'] in ['I11151993']:
        #         m1.append(final_bill[m])

        # final_bill = m1

        Myob_Job = db["job"].find({"job_id": job_id})
        Myob_Job1 = []
        for n in range(0, db["job"].count_documents({"job_id": job_id})):
            Myob_Job1.append(Myob_Job[n])

        QBO_COA = db["QBO_COA"].find({"job_id": job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id": job_id})
        QBO_supplier = []
        for p3 in QBO_Supplier:
            QBO_supplier.append(p3)

        QBO_Item = db["QBO_Item"].find({"job_id": job_id})
        QBO_item = []
        for p4 in QBO_Item:
            QBO_item.append(p4)

        QBO_Class = db["QBO_Class"].find({"job_id": job_id})
        QBO_class = []
        for p5 in QBO_Class:
            QBO_class.append(p5)

        QBO_Tax = db["QBO_Tax"].find({"job_id": job_id})
        QBO_tax = []
        for p6 in QBO_Tax:
            QBO_tax.append(p6)

        bill_arr = []
        vendor_credit_arr = []

        bill_bumbers=[]
        for b1 in range(0,len(final_bill)):
            bill_bumbers.append(final_bill[b1]['invoice_no'])

        data1=[]

        frequency_counter = Counter(bill_bumbers)
        for number, count in frequency_counter.items():
            if count>1:
                data1.append({number:count})
        
        key_list = []

        for i in range(0, len(final_bill)):
            print(i)
            _id = final_bill[i]['_id']
            task_id = final_bill[i]['task_id']
            # if 'account' in final_bill[i]:
            #     print(len(final_bill[i]['account']))
            # elif 'Item' in final_bill[i]:
            #     print(len(final_bill[i]['Item']))
            # else:
            #     print("Both are absent")

            if "account" in final_bill[i]:
                if final_bill[i]["Total_Amount"] >= 0:
                    if len(final_bill[i]["account"]) >= 1:
                        QuerySet = {"Line": []}
                        QuerySet["DocNumber"] = final_bill[i]["invoice_no"] if final_bill[i]["invoice_no"] not in key_list else final_bill[i]["invoice_no"][0:14]+"-"+final_bill[i]["UID"][-6:] 
                            
                        TxnTaxDetail = {"TaxLine": []}

                        for j in range(0, len(final_bill[i]["account"])):
                            if "Item_name" not in final_bill[i]["account"][j]:
                                QuerySet1 = {}
                                QuerySet2 = {}
                                QuerySet3 = {}
                                QuerySet4 = {}
                                QuerySet5 = {}
                                TaxLineDetail = {}
                                TaxRate = {}
                                Tax = {}
                                # Tax["DetailType"] = "TaxLineDetail"
                                # Tax["TaxLineDetail"] = TaxLineDetail
                                # TxnTaxDetail["TotalTax"] = abs(
                                #     final_bill[i]["TotalTax"]
                                # )
                                # TaxLineDetail["TaxRateRef"] = TaxRate
                                # TaxLineDetail["PercentBased"] = True
                                # TxnTaxDetail["TaxLine"].append(Tax)
                                # QuerySet["TxnTaxDetail"] = TxnTaxDetail
                                TaxCodeRef = {}
                                QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                                for k1 in range(0, len(QBO_tax)):
                                    if (
                                            final_bill[i]["account"][j]["Tax_Code"] in ["GST","GCA","CAP"]
                                    ) :
                                        if (
                                                "GST on purchases"
                                                == QBO_tax[k1]["taxcode_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]
                                            TaxLineDetail["NetAmountTaxable"] = abs(
                                                QBO_tax[k1]["Rate"]
                                                * final_bill[i]["TotalTax"]
                                            )
                                            Tax["Amount"] = final_bill[i]["TotalTax"]

                                    if (
                                            final_bill[i]["account"][j]["Tax_Code"] == "N-T"
                                    ) or (
                                            final_bill[i]["account"][j]["Tax_Code"] == None
                                    ):
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if "NOTAXP" == QBO_tax[k1]["taxrate_name"]:
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
                                                TaxLineDetail["NetAmountTaxable"] = abs(
                                                    QBO_tax[k1]["Rate"]
                                                    * final_bill[i]["TotalTax"]
                                                )
                                                Tax["Amount"] = 0

                                    elif (
                                            final_bill[i]["account"][j]["Tax_Code"] in ["FRE","INP","GNR"]
                                    ) :
                                        if "taxrate_name" in QBO_tax[k1]:
                                            if (
                                                    "GST-free (purchases)"
                                                    == QBO_tax[k1]["taxrate_name"]
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
                                                TaxLineDetail[
                                                    "NetAmountTaxable"
                                                ] = final_bill[i]["Total_Amount"]
                                                Tax["Amount"] = final_bill[i][
                                                    "TotalTax"
                                                ]

                                    else:
                                        pass

                                if final_bill[i]["Is_Tax_Inclusive"] == True:
                                    QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                    QuerySet1["Amount"] = round(
                                        final_bill[i]["account"][j]["Total"]
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )

                                else:
                                    QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                    QuerySet1["Amount"] = final_bill[i]["account"][j][
                                        "Total"
                                    ]

                                if ("Comment" in final_bill[i]) and (
                                        "supplier_invoice_no" in final_bill[i]
                                ):
                                    if (
                                            (
                                                    final_bill[i]["supplier_invoice_no"]
                                                    is not None
                                            )
                                            and (final_bill[i]["supplier_invoice_no"] != "")
                                            and (final_bill[i]["Comment"] is not None)
                                            and (final_bill[i]["Comment"] != "")
                                    ):
                                        QuerySet["PrivateNote"] = (
                                                final_bill[i]["Comment"]
                                                + " Supplier Invoice Number is:"
                                                + final_bill[i]["supplier_invoice_no"]
                                        )
                                elif "Comment" in final_bill[i]:
                                    QuerySet["PrivateNote"] = final_bill[i]["Comment"]

                                elif "supplier_invoice_no" in final_bill[i]:
                                    if final_bill[i]["supplier_invoice_no"] is not None:
                                        QuerySet["PrivateNote"] = (
                                                " Supplier Invoice Number is:"
                                                + final_bill[i]["supplier_invoice_no"]
                                        )

                                QuerySet2["TaxCodeRef"] = TaxCodeRef
                                QuerySet["TxnDate"] = final_bill[i]["Bill_Date"]
                                QuerySet["DueDate"] = final_bill[i]["Due_Date"]
                                QuerySet1["Description"] = final_bill[i]["account"][j][
                                    "Description"
                                ]
                                QuerySet1[
                                    "DetailType"
                                ] = "AccountBasedExpenseLineDetail"
                                QuerySet1["AccountBasedExpenseLineDetail"] = QuerySet2
                                QuerySet2["AccountRef"] = QuerySet3
                                for j1 in range(0, len(QBO_coa)):
                                    if "Account_Name" in final_bill[i]["account"][j]:
                                        if (
                                                QBO_coa[j1]["FullyQualifiedName"]
                                        ).startswith(
                                            final_bill[i]["account"][j]["Account_Name"]
                                        ) and (
                                                QBO_coa[j1]["FullyQualifiedName"]
                                        ).endswith(
                                            final_bill[i]["account"][j]["DisplayID"]
                                        ):
                                            QuerySet3["value"] = QBO_coa[j1]["Id"]

                                        elif (
                                                final_bill[i]["account"][j]["Account_Name"]
                                                        .lower()
                                                        .strip()
                                                == QBO_coa[j1]["FullyQualifiedName"]
                                                        .lower()
                                                        .strip()
                                        ):
                                            QuerySet3["value"] = QBO_coa[j1]["Id"]

                                QuerySet["VendorRef"] = QuerySet4

                                for j3 in range(0, len(QBO_supplier)):
                                    if (
                                            final_bill[i]["Supplier_Name"].lower().strip()
                                            == QBO_supplier[j3]["DisplayName"]
                                            .lower()
                                            .strip()
                                    ):
                                        QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                    elif (QBO_supplier[j3]["DisplayName"]).startswith(
                                            final_bill[i]["Supplier_Name"]
                                    ) and (
                                            (QBO_supplier[j3]["DisplayName"]).endswith("-S")
                                    ):
                                        QuerySet4["value"] = QBO_supplier[j3]["Id"]

                                QuerySet2["ClassRef"] = QuerySet5

                                for j2 in range(0, len(QBO_class)):
                                    for j4 in range(0, len(Myob_Job1)):
                                        if ("Job" in final_bill[i]["account"][j]) and (
                                                final_bill[i]["account"][j]["Job"]
                                                is not None
                                        ):
                                            if (
                                                    final_bill[i]["account"][j]["Job"][
                                                        "Name"
                                                    ]
                                                    == Myob_Job1[j4]["Name"]
                                            ):
                                                if (
                                                        QBO_class[j2][
                                                            "FullyQualifiedName"
                                                        ].startswith(Myob_Job1[j4]["Name"])
                                                ) and (
                                                        QBO_class[j2][
                                                            "FullyQualifiedName"
                                                        ].endswith(Myob_Job1[j4]["Number"])
                                                ):
                                                    QuerySet5["value"] = QBO_class[j2][
                                                        "Id"
                                                    ]
                                                    QuerySet5["name"] = QBO_class[j2][
                                                        "Name"
                                                    ]

                                if QuerySet2["AccountRef"] != {}:
                                    QuerySet["Line"].append(QuerySet1)

                        # arr = QuerySet["TxnTaxDetail"]["TaxLine"]

                        # new_arr = []
                        # for r in range(0, len(arr)):
                        #     if arr[r] in new_arr:
                        #         pass
                        #     else:
                        #         new_arr.append(arr[r])

                        # QuerySet["TxnTaxDetail"]["TaxLine"] = new_arr

                        payload = json.dumps(QuerySet)
                        print(payload)
                        bill_date = final_bill[i]["Bill_Date"][0:10]

                        bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")
                        if start_date1 is not None and end_date1 is not None and (
                                start_date1 <= bill_date1 <= end_date1):
                            post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                        else:
                            post_data_in_qbo(url1, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])
                else:
                    if len(final_bill[i]["account"]) == 1:
                        QuerySet = {"Line": []}
                        QuerySet["DocNumber"] = final_bill[i]["invoice_no"] if final_bill[i]["invoice_no"] not in key_list else final_bill[i]["invoice_no"][0:14]+"-"+final_bill[i]["UID"][-6:] 
                            
                        QuerySet1 = {}
                        QuerySet2 = {}
                        QuerySet3 = {}
                        QuerySet4 = {}
                        QuerySet5 = {}
                        TxnTaxDetail = {"TaxLine": []}
                        TaxLineDetail = {}
                        TaxRate = {}
                        Tax = {"Amount": abs(final_bill[i]["TotalTax"]), "DetailType": "TaxLineDetail",
                               "TaxLineDetail": TaxLineDetail}
                        TxnTaxDetail["TotalTax"] = abs(final_bill[i]["TotalTax"])
                        TaxLineDetail["TaxRateRef"] = TaxRate
                        TaxLineDetail["PercentBased"] = True
                        TxnTaxDetail["TaxLine"].append(Tax)
                        QuerySet["TxnTaxDetail"] = TxnTaxDetail
                        TaxCodeRef = {}
                        QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])
                        for k1 in range(0, len(QBO_tax)):
                            if (final_bill[i]["account"][0]["Tax_Code"] ["GST","GCA","CAP"]):
                                if "GST on purchases" == QBO_tax[k1]["taxcode_name"]:
                                    TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                    TaxCodeRef["value"] = QBO_tax[k1]["taxcode_id"]
                                    TaxLineDetail["TaxPercent"] = QBO_tax[k1]["Rate"]
                                    taxrate1 = QBO_tax[k1]["Rate"]
                                    TaxLineDetail["NetAmountTaxable"] = round(
                                        abs(
                                            QBO_tax[k1]["Rate"]
                                            * final_bill[i]["TotalTax"]
                                        ),
                                        2,
                                    )

                            elif (final_bill[i]["account"][0]["Tax_Code"] == "N-T") or (
                                    final_bill[i]["account"][0]["Tax_Code"] == None
                            ):
                                if "taxrate_name" in QBO_tax[k1]:
                                    if "NOTAXP" == QBO_tax[k1]["taxrate_name"]:
                                        TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                        TaxCodeRef["value"] = QBO_tax[k1]["taxcode_id"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                            "Rate"
                                        ]
                                        taxrate1 = QBO_tax[k1]["Rate"]
                                        TaxLineDetail["NetAmountTaxable"] = round(
                                            abs(
                                                QBO_tax[k1]["Rate"]
                                                * final_bill[i]["TotalTax"]
                                            ),
                                            2,
                                        )

                            elif (final_bill[i]["account"][0]["Tax_Code"])in ["FRE","INP","GNR"]:
                                if "taxrate_name" in QBO_tax[k1]:
                                    if (
                                            "GST-free (purchases)"
                                            == QBO_tax[k1]["taxrate_name"]
                                    ):
                                        TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                        TaxCodeRef["value"] = QBO_tax[k1]["taxcode_id"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                            "Rate"
                                        ]
                                        taxrate1 = QBO_tax[k1]["Rate"]
                                        TaxLineDetail["NetAmountTaxable"] = round(
                                            abs(
                                                QBO_tax[k1]["Rate"]
                                                * final_bill[i]["TotalTax"]
                                            ),
                                            2,
                                        )

                            else:
                                pass

                        if final_bill[i]["Is_Tax_Inclusive"] == True:
                            QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                            QuerySet1["Amount"] = abs(
                                final_bill[i]["account"][0]["Total"]
                                / (100 + taxrate1)
                                * 100
                            )
                            TaxLineDetail["NetAmountTaxable"] = abs(
                                final_bill[i]["Total_Amount"]
                                - final_bill[i]["TotalTax"]
                            )
                        else:
                            QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                            QuerySet1["Amount"] = abs(
                                final_bill[i]["account"][0]["Total"]
                            )
                            TaxLineDetail["NetAmountTaxable"] = abs(
                                final_bill[i]["Total_Amount"]
                                - final_bill[i]["TotalTax"]
                            )

                        QuerySet2["TaxCodeRef"] = TaxCodeRef

                        if ("Comment" in final_bill[i]) and (
                                "supplier_invoice_no" in final_bill[i]
                        ):
                            if (
                                    (final_bill[i]["supplier_invoice_no"] is not None)
                                    and (final_bill[i]["supplier_invoice_no"] != "")
                                    and (final_bill[i]["Comment"] is not None)
                                    and (final_bill[i]["Comment"] != "")
                            ):
                                QuerySet["PrivateNote"] = (
                                        final_bill[i]["Comment"]
                                        + " Supplier Invoice Number is:"
                                        + final_bill[i]["supplier_invoice_no"]
                                )
                        elif "Comment" in final_bill[i]:
                            QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                        elif "supplier_invoice_no" in final_bill[i]:
                            if final_bill[i]["supplier_invoice_no"] is not None:
                                QuerySet["PrivateNote"] = (
                                        " Supplier Invoice Number is:"
                                        + final_bill[i]["supplier_invoice_no"]
                                )
                        else:
                            pass

                        QuerySet["TxnDate"] = final_bill[i]["Bill_Date"]
                        if "Description" in final_bill[i]["account"][0]:
                            QuerySet1["Description"] = final_bill[i]["account"][0][
                                "Description"
                            ]
                        QuerySet1["DetailType"] = "AccountBasedExpenseLineDetail"
                        QuerySet1["AccountBasedExpenseLineDetail"] = QuerySet2
                        QuerySet2["AccountRef"] = QuerySet3

                        for j1 in range(0, len(QBO_coa)):
                            if "Account_Name" in final_bill[i]["account"][0]:
                                if (QBO_coa[j1]["FullyQualifiedName"]).startswith(
                                        final_bill[i]["account"][0]["Account_Name"]
                                ) and (QBO_coa[j1]["FullyQualifiedName"]).endswith(
                                    final_bill[i]["account"][0]["DisplayID"]
                                ):
                                    QuerySet3["value"] = QBO_coa[j1]["Id"]

                                elif (
                                        final_bill[i]["account"][0]["Account_Name"]
                                                .lower()
                                                .strip()
                                        == QBO_coa[j1]["FullyQualifiedName"].lower().strip()
                                ):
                                    QuerySet3["value"] = QBO_coa[j1]["Id"]

                        QuerySet["VendorRef"] = QuerySet4

                        for j3 in range(0, len(QBO_supplier)):
                            if (
                                    final_bill[i]["Supplier_Name"]
                                    == QBO_supplier[j3]["DisplayName"]
                            ):
                                QuerySet4["value"] = QBO_supplier[j3]["Id"]
                            elif (QBO_supplier[j3]["DisplayName"]).startswith(
                                    final_bill[i]["Supplier_Name"]
                            ) and ((QBO_supplier[j3]["DisplayName"]).endswith("-S")):
                                QuerySet4["value"] = QBO_supplier[j3]["Id"]

                        QuerySet2["ClassRef"] = QuerySet5

                        for j2 in range(0, len(QBO_class)):
                            for j4 in range(0, len(Myob_Job1)):
                                if ("Job" in final_bill[i]["account"][0]) and (
                                        final_bill[i]["account"][0]["Job"] is not None
                                ):
                                    if (
                                            final_bill[i]["account"][0]["Job"]["Name"]
                                            == Myob_Job1[j4]["Name"]
                                    ):
                                        if (
                                                QBO_class[j2][
                                                    "FullyQualifiedName"
                                                ].startswith(Myob_Job1[j4]["Name"])
                                        ) and (
                                                QBO_class[j2][
                                                    "FullyQualifiedName"
                                                ].endswith(Myob_Job1[j4]["Number"])
                                        ):
                                            QuerySet5["value"] = QBO_class[j2]["Id"]
                                            QuerySet5["name"] = QBO_class[j2]["Name"]

                        if QuerySet2["AccountRef"] != {}:
                            QuerySet["Line"].append(QuerySet1)

                        vendor_credit_arr.append(QuerySet)
                        payload = json.dumps(QuerySet)
                        print(payload)
                        bill_date = final_bill[i]["Bill_Date"][0:10]
                        bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")
                        if start_date1 is not None and end_date1 is not None and (
                                start_date1 <= bill_date1 <= end_date1):
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])
                        else:
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])
                    else:
                        QuerySet = {"Line": []}
                        QuerySet["DocNumber"] = final_bill[i]["invoice_no"] if final_bill[i]["invoice_no"] not in key_list else final_bill[i]["invoice_no"][0:14]+"-"+final_bill[i]["UID"][-6:] 
                        TxnTaxDetail = {"TaxLine": []}
                        for j in range(0, len(final_bill[i]["account"])):
                            QuerySet1 = {}
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            TaxLineDetail = {}
                            TaxRate = {}
                            Tax = {}
                            Tax["DetailType"] = "TaxLineDetail"
                            Tax["TaxLineDetail"] = TaxLineDetail
                            TxnTaxDetail["TotalTax"] = abs(final_bill[i]["TotalTax"])
                            TaxLineDetail["TaxRateRef"] = TaxRate
                            TaxLineDetail["PercentBased"] = True
                            TxnTaxDetail["TaxLine"].append(Tax)
                            QuerySet["TxnTaxDetail"] = TxnTaxDetail
                            TaxCodeRef = {}
                            QuerySet["TotalAmt"] = abs(final_bill[i]["TotalAmount"])

                            for k1 in range(0, len(QBO_tax)):
                                if (
                                        final_bill[i]["account"][j]["Tax_Code"] ["GST","GCA","CAP"]
                                ) :
                                    if (
                                            "GST on purchases"
                                            == QBO_tax[k1]["taxcode_name"]
                                    ):
                                        TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                        TaxCodeRef["value"] = QBO_tax[k1]["taxcode_id"]
                                        TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                            "Rate"
                                        ]
                                        taxrate1 = QBO_tax[k1]["Rate"]
                                        Tax["Amount"] = abs(final_bill[i]["TotalTax"])

                                if (
                                        final_bill[i]["account"][j]["Tax_Code"] == "N-T"
                                ) or (final_bill[i]["account"][j]["Tax_Code"] == None):
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if "NOTAXP" == QBO_tax[k1]["taxrate_name"]:
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]
                                            Tax["Amount"] = 0

                                elif (
                                        final_bill[i]["account"][j]["Tax_Code"]) in ["FRE","INP","GNR"]:
                                    if "taxrate_name" in QBO_tax[k1]:
                                        if (
                                                "GST-free (purchases)"
                                                == QBO_tax[k1]["taxrate_name"]
                                        ):
                                            TaxRate["value"] = QBO_tax[k1]["taxrate_id"]
                                            TaxCodeRef["value"] = QBO_tax[k1][
                                                "taxcode_id"
                                            ]
                                            TaxLineDetail["TaxPercent"] = QBO_tax[k1][
                                                "Rate"
                                            ]
                                            taxrate1 = QBO_tax[k1]["Rate"]
                                            Tax["Amount"] = (
                                                    abs(final_bill[i]["TotalTax"])
                                                    * taxrate1
                                            )

                                else:
                                    pass

                            if final_bill[i]["Is_Tax_Inclusive"] == True:
                                QuerySet["GlobalTaxCalculation"] = "TaxInclusive"
                                QuerySet1["Amount"] = abs(
                                    final_bill[i]["account"][j]["Total"]
                                    / (100 + taxrate1)
                                    * 100
                                )
                                TaxLineDetail["NetAmountTaxable"] = (
                                        abs(taxrate1 * final_bill[i]["TotalTax"])
                                        / (100 + taxrate1)
                                        * 100
                                )

                            else:
                                QuerySet["GlobalTaxCalculation"] = "TaxExcluded"
                                QuerySet1["Amount"] = abs(
                                    final_bill[i]["account"][j]["Total"]
                                )
                                TaxLineDetail["NetAmountTaxable"] = abs(
                                    taxrate1 * final_bill[i]["TotalTax"]
                                )

                           
                            if ("Comment" in final_bill[i]) and (
                                    "supplier_invoice_no" in final_bill[i]
                            ):
                                if (
                                        (final_bill[i]["supplier_invoice_no"] is not None)
                                        and (final_bill[i]["supplier_invoice_no"] != "")
                                        and (final_bill[i]["Comment"] is not None)
                                        and (final_bill[i]["Comment"] != "")
                                ):
                                    QuerySet["PrivateNote"] = (
                                            final_bill[i]["Comment"]
                                            + " Supplier Invoice Number is:"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                            elif "Comment" in final_bill[i]:
                                QuerySet["PrivateNote"] = final_bill[i]["Comment"]
                            elif "supplier_invoice_no" in final_bill[i]:
                                if final_bill[i]["supplier_invoice_no"] is not None:
                                    QuerySet["PrivateNote"] = (
                                            " Supplier Invoice Number is:"
                                            + final_bill[i]["supplier_invoice_no"]
                                    )
                            else:
                                pass

                            QuerySet2["TaxCodeRef"] = TaxCodeRef
                            QuerySet["TxnDate"] = final_bill[i]["Bill_Date"]
                            QuerySet1["Description"] = final_bill[i]["account"][j][
                                "Description"
                            ]
                            QuerySet1["DetailType"] = "AccountBasedExpenseLineDetail"
                            QuerySet1["AccountBasedExpenseLineDetail"] = QuerySet2
                            QuerySet2["AccountRef"] = QuerySet3

                            for j1 in range(0, len(QBO_coa)):
                                if "Account_Name" in final_bill[i]["account"][j]:
                                    if (QBO_coa[j1]["FullyQualifiedName"]).startswith(
                                            final_bill[i]["account"][j]["Account_Name"]
                                    ) and (QBO_coa[j1]["FullyQualifiedName"]).endswith(
                                        final_bill[i]["account"][j]["DisplayID"]
                                    ):
                                        QuerySet3["value"] = QBO_coa[j1]["Id"]
                                    elif (
                                            final_bill[i]["account"][j]["Account_Name"]
                                                    .lower()
                                                    .strip()
                                            == QBO_coa[j1]["FullyQualifiedName"]
                                                    .lower()
                                                    .strip()
                                    ):
                                        QuerySet3["value"] = QBO_coa[j1]["Id"]

                            QuerySet["VendorRef"] = QuerySet4
                            for j3 in range(0, len(QBO_supplier)):
                                if (
                                        final_bill[i]["Supplier_Name"]
                                        == QBO_supplier[j3]["DisplayName"]
                                ):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]
                                elif (QBO_supplier[j3]["DisplayName"]).startswith(
                                        final_bill[i]["Supplier_Name"]
                                ) and (
                                        (QBO_supplier[j3]["DisplayName"]).endswith("-S")
                                ):
                                    QuerySet4["value"] = QBO_supplier[j3]["Id"]

                            QuerySet2["ClassRef"] = QuerySet5

                            for j2 in range(0, len(QBO_class)):
                                for j4 in range(0, len(Myob_Job1)):
                                    if ("Job" in final_bill[i]["account"][j]) and (
                                            final_bill[i]["account"][j]["Job"] is not None
                                    ):
                                        if (
                                                final_bill[i]["account"][j]["Job"]["Name"]
                                                == Myob_Job1[j4]["Name"]
                                        ):
                                            if (
                                                    QBO_class[j2][
                                                        "FullyQualifiedName"
                                                    ].startswith(Myob_Job1[j4]["Name"])
                                            ) and (
                                                    QBO_class[j2][
                                                        "FullyQualifiedName"
                                                    ].endswith(Myob_Job1[j4]["Number"])
                                            ):
                                                QuerySet5["value"] = QBO_class[j2]["Id"]
                                                QuerySet5["name"] = QBO_class[j2][
                                                    "Name"
                                                ]
                            if QuerySet2["AccountRef"] != {}:
                                QuerySet["Line"].append(QuerySet1)

                        vendor_credit_arr.append(QuerySet)
                        payload = json.dumps(QuerySet)
                        print(payload)
                        bill_date = final_bill[i]["Bill_Date"][0:10]
                        bill_date1 = datetime.strptime(bill_date, "%Y-%m-%d")
                        if start_date1 is not None and end_date1 is not None and (
                                start_date1 <= bill_date1 <= end_date1):
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

                        else:
                            post_data_in_qbo(url2, headers, payload,db['final_bill'],_id,job_id,task_id, final_bill[i]['invoice_no'])

    except Exception as ex:
        traceback.print_exc()
        
