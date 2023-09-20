import json
import traceback
from datetime import datetime

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo
from apps.util.qbo_util import get_start_end_dates_of_job


def add_journal(job_id,task_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)

        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        url = f"{base_url}/journalentry?minorversion={minorversion}"

        journal_data = db["journal"]

        journal1 = []
        for p1 in db["journal"].find({'job_id':job_id}):
            journal1.append(p1)

        QBO_COA = db["QBO_COA"].find({"job_id":job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)

        QBO_Class = db["QBO_Class"].find({"job_id":job_id})
        QBO_class = []
        for p3 in QBO_Class:
            QBO_class.append(p3)

        QBO_Tax = db["QBO_Tax"].find({"job_id":job_id})
        QBO_tax = []
        for p4 in QBO_Tax:
            QBO_tax.append(p4)

        QBO_Customer = db["QBO_Customer"].find({"job_id":job_id})
        QBO_Customer1 = []
        for p5 in QBO_Customer:
            QBO_Customer1.append(p5)

        QBO_Supplier = db["QBO_Supplier"].find({"job_id":job_id})
        QBO_Supplier1 = []
        for p6 in QBO_Supplier:
            QBO_Supplier1.append(p6)

        QuerySet1 = journal1

        for i in range(0, len(QuerySet1)):
            _id=QuerySet1[i]['_id']
            task_id=QuerySet1[i]['task_id']
            
            try:
                journal_date = QuerySet1[i]["Date"]
                journal_date11 = journal_date[0:10]
                journal_date1 = datetime.strptime(journal_date11, "%Y-%m-%d")

            except Exception as ex:
                pass

            QuerySet2 = {"Line": []}
            QuerySet10 = {"TaxLine": []}

            a = []
            b = []
            for j in range(0, len(QuerySet1[i]["is_credit_debit"])):
                if "taxcode" in QuerySet1[i]["is_credit_debit"][j]:
                    if QuerySet1[i]["is_credit_debit"][j]["IsCredit"] == True:
                        a.append(QuerySet1[i]["is_credit_debit"][j]["taxcode"])
                    else:
                        b.append(QuerySet1[i]["is_credit_debit"][j]["taxcode"])

                QuerySet3 = {}
                QuerySet4 = {}
                QuerySet5 = {}
                QuerySet6 = {}
                QuerySet7 = {}
                QuerySet8 = {}
                QuerySet9 = {}

                QuerySet11 = {}
                QuerySet12 = {}
                QuerySet13 = {}
                QuerySet14 = {}
                QuerySet15 = {}
                Entity = {}
                EntityRef = {}

                QuerySet2["TxnTaxDetail"] = QuerySet10
                QuerySet2["DocNumber"] = QuerySet1[i]["Referrence_No"]
                QuerySet2["TxnDate"] = QuerySet1[i]["Date"][0:10]
                QuerySet2["PrivateNote"] = QuerySet1[i]["Memo"]
                QuerySet11["DetailType"] = "TaxLineDetail"
                QuerySet11["TaxLineDetail"] = QuerySet12
                QuerySet12["TaxRateRef"] = QuerySet13
                QuerySet12["PercentBased"] = True

                taxrate1 = 0

                purchase = ["NOTAXP"]
                sales = ["FRE", "CAP", "GST", "N-T", "GCA", "NOTAXS", "INP", None]

                if QuerySet1[i]["is_credit_debit"][j]["taxcode"] in sales:
                    QuerySet4["TaxApplicableOn"] = "Sales"
                    QuerySet7["TaxApplicableOn"] = "Sales"

                elif QuerySet1[i]["is_credit_debit"][j]["taxcode"] in purchase:
                    QuerySet4["TaxApplicableOn"] = "Purchase"
                    QuerySet7["TaxApplicableOn"] = "Purchase"

                for j4 in range(0, len(QBO_tax)):
                    if "taxcode" in QuerySet1[i]["is_credit_debit"][j]:
                        if (QuerySet1[i]["is_credit_debit"][j]["taxcode"] == "GST") or (
                                QuerySet1[i]["is_credit_debit"][j]["taxcode"] == "GCA"
                        ):
                            if QuerySet1[i]["is_credit_debit"][j]["IsCredit"] == True:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "GST (sales)" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                            else:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if "GST (sales)" == QBO_tax[j4]["taxrate_name"]:
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]

                        elif QuerySet1[i]["is_credit_debit"][j]["taxcode"] == "CAP":
                            if "taxrate_name" in QBO_tax[j4]:
                                if "GST (sales)" == QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif QuerySet1[i]["is_credit_debit"][j]["taxcode"] == "FRE":
                            if QuerySet1[i]["is_credit_debit"][j]["IsCredit"] == True:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if (
                                            "GST free (sales)"
                                            == QBO_tax[j4]["taxrate_name"]
                                    ):
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate
                            else:
                                if "taxrate_name" in QBO_tax[j4]:
                                    if (
                                            "GST free (sales)"
                                            == QBO_tax[j4]["taxrate_name"]
                                    ):
                                        QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                        QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                        taxrate = QBO_tax[j4]["Rate"]
                                        QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                        taxrate1 = taxrate

                        elif (
                                QuerySet1[i]["is_credit_debit"][j]["taxcode"] == "N-T"
                        ) or (QuerySet1[i]["is_credit_debit"][j]["taxcode"] == None):
                            if "taxrate_name" in QBO_tax[j4]:
                                if "NOTAXS" in QBO_tax[j4]["taxrate_name"]:
                                    QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                                    QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                                    taxrate = QBO_tax[j4]["Rate"]
                                    QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                                    taxrate1 = taxrate

                        elif (
                                QuerySet1[i]["is_credit_debit"][j]["taxcode"]
                                == QBO_tax[j4]["taxcode_name"]
                        ):
                            QuerySet13["value"] = QBO_tax[j4]["taxrate_id"]
                            QuerySet15["value"] = QBO_tax[j4]["taxcode_id"]
                            taxrate = QBO_tax[j4]["Rate"]
                            QuerySet12["TaxPercent"] = QBO_tax[j4]["Rate"]
                            taxrate1 = taxrate

                if QuerySet1[i]["is_credit_debit"][j]["IsCredit"] == True:
                    QuerySet12["NetAmountTaxable"] = -QuerySet1[i]["is_credit_debit"][
                        j
                    ]["line_amount"]
                    QuerySet11["Amount"] = -QuerySet1[i]["is_credit_debit"][j][
                        "Tax_Amount"
                    ]

                    #             QuerySet12['NetAmountTaxable'] = - \
                    #                 (QuerySet1[i]['is_credit_debit'][j]['line_amount'])

                    QuerySet3["Amount"] = QuerySet1[i]["is_credit_debit"][j][
                        "line_amount"
                    ]
                    QuerySet3["Description"] = QuerySet1[i]["is_credit_debit"][j][
                        "Description"
                    ]
                    QuerySet3["DetailType"] = "JournalEntryLineDetail"
                    QuerySet4["PostingType"] = "Credit"

                    QuerySet3["JournalEntryLineDetail"] = QuerySet4

                    for k in range(0, len(QBO_coa)):
                        if (
                                QuerySet1[i]["is_credit_debit"][j]["Account_Name"]
                                == QBO_coa[k]["FullyQualifiedName"]
                        ):
                            if QBO_coa[k]["AccountType"] == "Accounts Receivable":
                                for c1 in range(0, len(QBO_Customer1)):
                                    if (
                                            QBO_Customer1[c1]["FullyQualifiedName"]
                                            == "No Name - C"
                                    ):
                                        EntityRef["name"] = QBO_Customer1[c1][
                                            "FullyQualifiedName"
                                        ]
                                        EntityRef["value"] = QBO_Customer1[c1]["Id"]
                                        Entity["Type"] = "Customer"
                                        Entity["EntityRef"] = EntityRef

                            elif QBO_coa[k]["AccountType"] == "Accounts Payable":
                                for s1 in range(0, len(QBO_Supplier1)):
                                    if (
                                            QBO_Supplier1[s1]["DisplayName"]
                                            == "No Name - S"
                                    ):
                                        EntityRef["name"] = QBO_Supplier1[s1][
                                            "DisplayName"
                                        ]
                                        EntityRef["value"] = QBO_Supplier1[s1]["Id"]
                                        Entity["EntityRef"] = EntityRef
                                        Entity["Type"] = "Vendor"

                            QuerySet4["Entity"] = Entity

                        if 'AcctNum' in QBO_coa[k]:
                            if QuerySet1[i]["is_credit_debit"][j]["DisplayID"]== QBO_coa[k]["AcctNum"]:
                                QuerySet5["value"] = QBO_coa[k]["Id"]
                                QuerySet5["name"] = QBO_coa[k]["Name"]
                                break
                        
                        
                    for m1 in range(0, len(QBO_class)):
                        if "Job" in QuerySet1[i]["is_credit_debit"][j]:
                            if (
                                    QuerySet1[i]["is_credit_debit"][j]["Job"]
                                    == QBO_class[m1]["Name"]
                            ):
                                QuerySet9["value"] = QBO_class[m1]["Id"]
                                QuerySet9["name"] = QBO_class[m1]["Name"]

                    QuerySet4["AccountRef"] = QuerySet5
                    QuerySet4["TaxCodeRef"] = QuerySet15
                    QuerySet4["TaxAmount"] = QuerySet1[i]["is_credit_debit"][j][
                        "Tax_Amount"
                    ]
                    QuerySet4["ClassRef"] = QuerySet9
                    QuerySet2["Line"].append(QuerySet3)
                    QuerySet10["TaxLine"].append(QuerySet11)

                elif QuerySet1[i]["is_credit_debit"][j]["IsCredit"] == False:
                    QuerySet12["NetAmountTaxable"] = QuerySet1[i]["is_credit_debit"][j][
                        "line_amount"
                    ]
                    QuerySet2["DocNumber"] = QuerySet1[i]["Referrence_No"]
                    QuerySet11["Amount"] = QuerySet1[i]["is_credit_debit"][j][
                        "Tax_Amount"
                    ]
                    # QuerySet12['NetAmountTaxable'] = QuerySet1[i]['is_credit_debit'][j]['line_amount']
                    QuerySet6["Amount"] = QuerySet1[i]["is_credit_debit"][j][
                        "line_amount"
                    ]
                    QuerySet6["Description"] = QuerySet1[i]["is_credit_debit"][j][
                        "Description"
                    ]
                    QuerySet7["PostingType"] = "Debit"

                    for m1 in range(0, len(QBO_class)):
                        if "Job" in QuerySet1[i]["is_credit_debit"][j]:
                            if (
                                    QuerySet1[i]["is_credit_debit"][j]["Job"]
                                    == QBO_class[m1]["Name"]
                            ):
                                QuerySet9["value"] = QBO_class[m1]["Id"]
                                QuerySet9["name"] = QBO_class[m1]["Name"]

                    QuerySet6["DetailType"] = "JournalEntryLineDetail"

                    QuerySet6["JournalEntryLineDetail"] = QuerySet7
                    for p in range(0, len(QBO_coa)):
                        
                        if (
                                QuerySet1[i]["is_credit_debit"][j]["Account_Name"]
                                == QBO_coa[p]["FullyQualifiedName"]
                        ):
                            if QBO_coa[p]["AccountType"] == "Accounts Receivable":
                                for c1 in range(0, len(QBO_Customer1)):
                                    if (
                                            QBO_Customer1[c1]["FullyQualifiedName"]
                                            == "No Name - C"
                                    ):
                                        EntityRef["name"] = QBO_Customer1[c1][
                                            "FullyQualifiedName"
                                        ]
                                        EntityRef["value"] = QBO_Customer1[c1]["Id"]
                                        Entity["Type"] = "Customer"
                                        Entity["EntityRef"] = EntityRef

                            elif QBO_coa[p]["AccountType"] == "Accounts Payable":
                                for s1 in range(0, len(QBO_Supplier1)):
                                    if (
                                            QBO_Supplier1[s1]["DisplayName"]
                                            == "No Name - S"
                                    ):
                                        EntityRef["name"] = QBO_Supplier1[s1][
                                            "DisplayName"
                                        ]
                                        EntityRef["value"] = QBO_Supplier1[s1]["Id"]
                                        Entity["EntityRef"] = EntityRef
                                        Entity["Type"] = "Vendor"

                            QuerySet7["Entity"] = Entity

                        if 'AcctNum' in QBO_coa[p]:
                            if QuerySet1[i]["is_credit_debit"][j]["DisplayID"]== QBO_coa[p]["AcctNum"]:
                                QuerySet8["value"] = QBO_coa[p]["Id"]
                                QuerySet8["name"] = QBO_coa[p]["Name"]
                                break
                        
                    QuerySet7["AccountRef"] = QuerySet8
                    QuerySet7["TaxCodeRef"] = QuerySet15

                    QuerySet7["TaxAmount"] = QuerySet1[i]["is_credit_debit"][j][
                        "Tax_Amount"
                    ]
                    QuerySet7["ClassRef"] = QuerySet9
                    QuerySet2["Line"].append(QuerySet6)
                    QuerySet10["TaxLine"].append(QuerySet11)

            # arr = QuerySet10['TaxLine']
            # print(arr)
            # print("--")
            # b1 = {'TaxLine': []}

            # b=[]
            # for i in range(0,len(arr)):
            #     b.append(arr[i]['TaxLineDetail']['TaxRateRef']['value'])

            # print(b)
            # print("--")

            # e={}
            # for i1 in range(0,len(b)):
            #     e[b[i1]] = b.count(b[i1])

            # multiple=dict((k, v) for k, v in e.items() if v > 1)
            # single=dict((k, v) for k, v in e.items() if v == 1)

            # print(multiple,"This is multiple")
            # print(single,"This is single")

            # e1=[]
            # for keys in e.keys():
            #     e1.append(keys)

            # new_arr=[]
            # print(arr,"This is arr")
            # for k in range(0,len(arr)):
            #     e={}
            #     TaxLineDetail = {}
            #     TaxRateRef={}
            #     amt = 0
            #     net_amt = 0

            #     for i in range(0,len(arr)):
            #         if arr[i]['TaxLineDetail']['TaxRateRef']['value'] == e1[k]:
            #             print(e1[k])
            #             e['DetailType'] = 'TaxLineDetail'
            #             TaxLineDetail['TaxRateRef'] = TaxRateRef
            #             TaxLineDetail['TaxPercent'] = arr[i]['TaxLineDetail']['TaxPercent']
            #             TaxRateRef['value'] = e1[k]
            #             amt = amt + arr[i]['Amount']
            #             print(amt)
            #             net_amt = net_amt + arr[i]['TaxLineDetail']['NetAmountTaxable']
            #             e['Amount'] = round(amt,2)
            #             print(e['Amount'])
            #             TaxLineDetail['NetAmountTaxable'] = round(net_amt/(100+taxrate1)*100,2)
            #             e['TaxLineDetail'] = TaxLineDetail

            #         new_arr.append(e)

            #     print(new_arr)
            # print("====")
            # for k3 in range(0,len(arr)):
            #     if arr[k3]['TaxLineDetail']['TaxRateRef']['value'] in single:
            #         new_arr.append(arr[k3])

            # b1['TaxLine'] = new_arr

            # QuerySet2['TxnTaxDetail'] = b1
            # payload = json.dumps(QuerySet2)

            arr = QuerySet10["TaxLine"]

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

            for k in range(0, len(e1)):
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

            for k3 in range(0, len(arr)):
                if 'value' in arr[k3]["TaxLineDetail"]["TaxRateRef"]: 
                    if arr[k3]["TaxLineDetail"]["TaxRateRef"]["value"] in single:
                        new_arr.append(arr[k3])

            b1["TaxLine"] = new_arr

            QuerySet2["TxnTaxDetail"] = b1

            payload = json.dumps(QuerySet2)
            print("-----")
            print(payload)

            if start_date1 is not None and end_date1 is not None:
                if (journal_date1 >= start_date1) and (journal_date1 <= end_date1):
                    post_data_in_qbo(url, headers, payload,journal_data,_id,job_id,task_id, QuerySet1[i]["Referrence_No"])
                else:
                    print("No Journal Avaialble within this date")
        
            else:
                post_data_in_qbo(url, headers, payload,journal_data,_id,job_id,task_id, QuerySet1[i]["Referrence_No"])
                                        
                    
    except Exception as ex:
        traceback.print_exc()
        
