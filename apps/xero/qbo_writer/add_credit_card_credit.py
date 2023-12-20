import json
import logging
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_start_end_dates_of_job
from apps.util.qbo_util import post_data_in_qbo

logger = logging.getLogger(__name__)


def add_xero_credit_card_credit(job_id,task_id):
    try:
        logger.info(
            "Started executing xero -> qbowriter -> add_spend_money -> add_xero_receive_money")

        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        purchase_url = f"{base_url}/purchase?minorversion={minorversion}"

        spend_money_data = db["xero_receive_money"]
        spend_money = spend_money_data.find({"job_id": job_id})

        # qbo_coa_data = db["QBO_COA"]
        # qbo_coa = qbo_coa_data.find({"job_id": job_id})

        QBO_COA1 = db["QBO_COA"].find({"job_id":job_id})
        QBO_COA = []
        for p2 in QBO_COA1:
            QBO_COA.append(p2)


        xero_coa_data = db["xero_coa"]
        xero_coa = xero_coa_data.find({"job_id": job_id})

        supplier_data = db["QBO_Supplier"]
        suppliers = supplier_data.find({"job_id": job_id})

        customer_data = db["QBO_Customer"]
        customers = customer_data.find({"job_id": job_id})

        qbo_class_data = db["QBO_Class"]
        qbo_class = qbo_class_data.find({"job_id": job_id})

        qbo_tax_data = db["QBO_Tax"]
        qbo_tax = qbo_tax_data.find({"job_id": job_id})

        
        for transaction in spend_money:
            if transaction["TotalAmount"] >= 0:
                a11=db["QBO_COA"].find({"FullyQualifiedName": transaction.get("BankAccountName").replace(":","-"),'job_id':job_id})
                for x3 in a11:
                    if x3.get("AccountType") == "Credit Card":
                        _id= transaction.get('_id')
                        task_id = transaction.get('task_id')
                        line_items = transaction.get("Line")
                        QuerySet1 = {"Line": []}
                        if transaction.get("Reference")!= None:
                            QuerySet1['DocNumber'] = transaction.get("Reference")[0:20] 
                        for line_item in line_items:
                            QuerySet1["TotalAmt"] = transaction.get("TotalAmount")
                            QuerySet2 = {}
                            QuerySet3 = {}
                            QuerySet4 = {}
                            QuerySet5 = {}
                            QuerySet6 = {}
                            QuerySet7 = {}
                            QuerySet8 = {}
                            QuerySet91 = {}
                            QuerySet92 = {}

                            # a1=db["QBO_COA"].find({"FullyQualifiedName": transaction.get("BankAccountName").strip(),'job_id':job_id})
                            # for x in a1:
                            #     QuerySet2["value"] = x.get("Id")
                            #     QuerySet2["name"] = x.get("Name")

                            for c1 in range(0,len(QBO_COA)):
                                if transaction.get("BankAccountName").strip().lower() == QBO_COA[c1]['FullyQualifiedName'].strip().lower():
                                    QuerySet2["value"]=QBO_COA[c1]['Id']
                                    QuerySet2["name"] =QBO_COA[c1]['FullyQualifiedName']
                                    break
                                elif transaction.get("BankAccountName").replace(":","-") == QBO_COA[c1]['FullyQualifiedName']:
                                    QuerySet2["value"]=QBO_COA[c1]['Id']
                                    QuerySet2["name"] =QBO_COA[c1]['FullyQualifiedName']
                                    break

                            QuerySet1["AccountRef"] = QuerySet2
                    

                            taxrate1 = 0
                            if line_item.get("TaxType") == "BASEXCLUDED" or line_item.get("TaxType") == None or line_item.get("TaxType") == "NONE":
                                t1=db["QBO_Tax"].find({"taxrate_name": "NOTAXS",'job_id':job_id})
                                for x in t1:
                                    QuerySet8["value"] = x.get("taxcode_id")
                                    taxrate = x.get("Rate")
                                    taxrate1 = taxrate

                            elif (line_item.get("TaxType") == "OUTPUT" 
                                or line_item.get("TaxType") == "INPUT"
                                or line_item.get("TaxType") == "INPUT2"
                                or line_item.get("TaxType") == "CAPEXINPUT"):
                                
                                t1=db["QBO_Tax"].find({"taxrate_name": "GST (purchases)",'job_id':job_id})
                                for x in t1:
                                    QuerySet8["value"] = x.get("taxcode_id")
                                    taxrate = x.get("Rate")
                                    taxrate1 = taxrate

                                
                            elif (
                                line_item.get("TaxType") == "EXEMPTCAPITAL"
                                or line_item.get("TaxType") == "EXEMPTEXPENSES"
                                or line_item.get("TaxType") == "EXEMPTEXPORT"
                                or line_item.get("TaxType") == "EXEMPTOUTPUT"
                                or line_item.get("TaxType") == "GSTONCAPIMPORTS"
                                or line_item.get("TaxType") == "GSTONIMPORTS"
                                or line_item.get("TaxType") == "INPUTTAXED"

                            ):
                                t1=db["QBO_Tax"].find({"taxrate_name": "GST-free (purchases)",'job_id':job_id})
                                for x in t1:
                                    QuerySet8["value"] = x.get("taxcode_id")
                                    taxrate = x.get("Rate")
                                    taxrate1 = taxrate
                            
                            # QuerySet1['PrivateNote'] = transaction['memo']

                            if transaction["LineAmountTypes"] == "Inclusive":
                                QuerySet1["GlobalTaxCalculation"] = "TaxInclusive"
                                QuerySet1["PaymentType"] = "CreditCard"
                                QuerySet1["Credit"] = True

                                QuerySet4['TaxCodeRef'] = QuerySet8
                                QuerySet4["TaxInclusiveAmt"] = round(
                                        (line_item.get("LineAmount"))
                                        * (100 + taxrate1)
                                        / 100,
                                        2,
                                    )
                                
                                QuerySet3["Amount"] = round(
                                        (line_item.get("LineAmount"))
                                        / (100 + taxrate1)
                                        * 100,
                                        2,
                                    )
                                

                            elif (
                                transaction["LineAmountTypes"] == "NoTax"
                                or transaction["LineAmountTypes"] == "Exclusive"
                            ):
                                QuerySet1["GlobalTaxCalculation"] = "TaxExcluded"
                                QuerySet1["PaymentType"] = "CreditCard"
                                QuerySet1["Credit"] = True

                                QuerySet4["TaxInclusiveAmt"] = abs(
                                    round(line_item.get("LineAmount"))
                                )
                                QuerySet3["Amount"] =round(line_item.get("LineAmount"), 2)
                                
                                QuerySet4['TaxCodeRef'] = QuerySet8

                            QuerySet1["PaymentType"] = "CreditCard"
                            QuerySet1["TxnDate"] = transaction.get("Date")

                            QuerySet3["Description"] = line_item.get("Description")

                            QuerySet3["DetailType"] = "AccountBasedExpenseLineDetail"
                            QuerySet3["AccountBasedExpenseLineDetail"] = QuerySet4

                            c1=db["QBO_Class"].find({"Name": line_item.get("TrackingName"),'job_id':job_id})
                            for c in c1:
                                QuerySet7['value'] = c.get('Id')
                                QuerySet7['name'] = c.get('Name')
                                break

                            a1=db["QBO_COA"].find({"AcctNum": line_item.get("AccountCode"),'job_id':job_id})
                            for x in a1:
                                QuerySet5["value"] = x.get("Id")
                                QuerySet5["name"] = x.get("Name")
                                break
                            
                            QuerySet4["AccountRef"] = QuerySet5
                            QuerySet4["ClassRef"] = QuerySet7

                                
                            s1 = db["QBO_Supplier"].find({"DisplayName": transaction.get("ContactName"),'job_id':job_id})
                            s2 = db["QBO_Supplier"].find({"DisplayName": {'$regex': '- S$','$regex': f'^{transaction.get("ContactName")}'},'job_id':job_id})
                            c1 = db["QBO_Customer"].find({"DisplayName": transaction.get("ContactName"),'job_id':job_id})
                            c2 = db["QBO_Customer"].find({"DisplayName": {'$regex': '- C$','$regex': f'^{transaction.get("ContactName")}'},'job_id':job_id})
                            
                            for x1 in s1:
                                QuerySet91["value"] = x1.get("Id")
                                QuerySet91["name"] = x1.get("DisplayName")
                                break
                                
                            for x2 in s2:
                                QuerySet91["value"] = x2.get("Id")
                                QuerySet91["name"] = x2.get("DisplayName")
                                break

                            for x3 in c1:
                                QuerySet92["value"] = x3.get("Id")
                                QuerySet92["name"] = x3.get("DisplayName")
                                break

                            for x4 in c2:
                                QuerySet92["value"] = x4.get("Id")
                                QuerySet92["name"] = x4.get("DisplayName")
                                break

                            QuerySet1["EntityRef"] = QuerySet91 if QuerySet91 != {} else QuerySet92
                            QuerySet1["Line"].append(QuerySet3)
                        
                        # if transaction["BankTransactionID"] in ['72a2719c-b5ce-41f8-b1f1-c0b41aa82de5','1637b9a3-6974-40d1-b3b3-6d89dc894faa','68e0bf43-9f16-4042-b5c9-c888375aba08','aafe9632-0073-45f9-896e-b2647642cb83','e6de5cde-6de6-4e62-96eb-585f9429b91f','940c03ad-d799-409b-a04a-65e1d6197a34','f53abed2-0975-4c43-89a9-ab9dfc25af54','c4903136-5f13-4289-b34c-a81d59ce0774','3ef36371-d398-446e-a539-d8f51dc72f67','7602d5a3-59f6-4b2d-a8f5-960ac01ad35b','9bd97658-cccb-4c3c-8e2d-ee2ad160ee57','a8e43d91-4f74-4bb6-9301-79a7c7db3516','23f19997-ed4a-4367-9d41-6730ca6b3a6f','88b21f8c-a5f4-4782-871b-49e4cb358dfc']:
                        spend_money_date = transaction["Date"][0:10]
                        spend_money_date1 = datetime.strptime(spend_money_date, "%Y-%m-%d")
                        payload = json.dumps(QuerySet1)
                        print(payload)
                        if start_date1 is not None and end_date1 is not None:
                            if (spend_money_date1 >= start_date1) and (
                                spend_money_date1 <= end_date1
                            ):
                                post_data_in_qbo(purchase_url, headers, payload,db["xero_receive_money"],_id, job_id,task_id, transaction.get("BankTransactionID"))
                        else:
                            post_data_in_qbo(purchase_url, headers, payload,db["xero_receive_money"],_id, job_id,task_id, transaction.get("BankTransactionID"))
                        
                                    
    except Exception as ex:
        logger.error(
            "Error in xero -> qbowriter  -> add_xero_crc", ex)
        
