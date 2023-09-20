import json
import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_supplier(job_id,task_id):
    
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        url = f"{base_url}/vendor?minorversion=40"
        supplier_data = db["supplier"]
        customer_data = db["customer"]

        supplier = supplier_data.find({"job_id":job_id})
        customer = customer_data.find({"job_id":job_id})

        cust1 = []
        for k1 in customer:
            cust1.append(k1)

        supp1 = []
        for k2 in supplier:
            supp1.append(k2)

        supplier1 = []

        for i in range(0, len(supp1)):
            if "CompanyName" in supp1[i] and supp1[i]["CompanyName"]!=None:
                supplier1.append(supp1[i]["CompanyName"].replace(":","-"))
            elif "FirstName" in supp1[i] and "LastName" in supp1[i]:
                if supp1[i]["FirstName"]!=None and supp1[i]["LastName"]!=None:
                    supplier1.append(supp1[i]["FirstName"].replace(":","-") + " " + supp1[i]["LastName"].replace(":","-"))

        customer1 = []
        for i in range(0, len(cust1)):
            if "Company_Name" in cust1[i] and cust1[i]["Company_Name"]!=None:
                customer1.append(cust1[i]["Company_Name"].replace(":","-"))
            elif "First_Name" in cust1[i] and "Last_Name" in cust1[i]:
                if cust1[i]["First_Name"]!=None and cust1[i]["Last_Name"]!=None:
                    customer1.append(cust1[i]["First_Name"].replace(":","-") + " " + cust1[i]["Last_Name"].replace(":","-"))

        common_contact = []
        customer_set = set(customer1)
        supplier_set = set(supplier1)

        if customer_set & supplier_set:
            common_contact.append((customer_set & supplier_set))
        else:
            pass

        if len(common_contact) > 0:
            common_contact1 = list(common_contact[0])

        QuerySet1 = supp1

        for i in range(0, len(QuerySet1)):
            _id=QuerySet1[i]['_id']
            task_id=QuerySet1[i]['task_id']
            
            QuerySet2 = {}
            QuerySet3 = {}
            QuerySet4 = {}
            QuerySet6 = {}
            QuerySet7 = {}
            QuerySet8 = {}
            QuerySet9 = {}

            if QuerySet1[i]["BSB"] is not None:
                QuerySet2["AcctNum"] = (
                        QuerySet1[i]["BSB"] + " " + QuerySet1[i]["Bank_Acc_no"]
                )
            else:
                QuerySet2["AcctNum"] = QuerySet1[i]["Bank_Acc_no"]

            if len(common_contact) > 0:
                if QuerySet1[i]["CompanyName"] is not None:
                    if QuerySet1[i]["CompanyName"] in common_contact1:
                        QuerySet2["CompanyName"] = QuerySet1[i]["CompanyName"].replace(":","-") + "-S"
                        QuerySet2["DisplayName"] = QuerySet1[i]["CompanyName"].replace(":","-") + "-S"
                        QuerySet2["PrintOnCheckName"] = (
                                QuerySet1[i]["CompanyName"] + "-S"
                        )
                    else:
                        QuerySet2["CompanyName"] = QuerySet1[i]["CompanyName"].replace(":","-")
                        QuerySet2["DisplayName"] = QuerySet1[i]["CompanyName"].replace(":","-")
                        QuerySet2["PrintOnCheckName"] = QuerySet1[i]["CompanyName"].replace(":","-")
            else:
                if QuerySet1[i]["CompanyName"]!=None:
                    QuerySet2["CompanyName"] = QuerySet1[i]["CompanyName"].replace(":","-")
                    QuerySet2["DisplayName"] = QuerySet1[i]["CompanyName"].replace(":","-")
                    QuerySet2["PrintOnCheckName"] = QuerySet1[i]["CompanyName"].replace(":","-")

            if 'FirstName' in QuerySet1[i] and QuerySet1[i]["FirstName"]!=None:
                QuerySet2["GivenName"] = QuerySet1[i]["FirstName"].replace(":","-")
            if 'LastName' in QuerySet1[i] and QuerySet1[i]["LastName"]!=None:
                QuerySet2["FamilyName"] = QuerySet1[i]["LastName"].replace(":","-")
            QuerySet2["TaxIdentifier"] = QuerySet1[i]["ABN"]

            if QuerySet1[i] in ["Street"]:
                QuerySet3["Line1"] = QuerySet1[i]["Street"]
            else:
                pass

            QuerySet3["City"] = QuerySet1[i]["city"]
            QuerySet3["Country"] = QuerySet1[i]["Country"]
            QuerySet3["PostalCode"] = QuerySet1[i]["PostCode"]
            QuerySet3["CountrySubDivisionCode"] = QuerySet1[i]["State"]
            QuerySet4["FreeFormNumber"] = QuerySet1[i]["Phone"]

            if QuerySet1[i]["Email"] is not None:
                QuerySet6["Address"] = QuerySet1[i]["Email"].strip()

            # if QuerySet1[i]["Website"] is None or QuerySet1[i]["Website"] == "":
            #     QuerySet7["URI"] = "https://google.com"
            # else:
            #     if QuerySet1[i]["Website"].startswith("https://") or QuerySet1[i][
            #         "Website"
            #     ].startswith("http://"):
            #         QuerySet7["URI"] = QuerySet1[i]["Website"]
            #     else:
            #         QuerySet7["URI"] = "https://" + QuerySet1[i]["Website"]

            if (QuerySet1[i]["Bank_Acc_Name"] is None) or (
                    QuerySet1[i]["Bank_Acc_Name"] == ""
            ):
                QuerySet9["BankAccountName"] = None
            else:
                QuerySet9["BankAccountName"] = QuerySet1[i]["Bank_Acc_Name"]

            if (QuerySet1[i]["BSB"] is None) or (QuerySet1[i]["BSB"] == ""):
                QuerySet9["BankBranchIdentifier"] = None
            else:
                QuerySet9["BankBranchIdentifier"] = QuerySet1[i]["BSB"]

            if (QuerySet1[i]["Bank_Acc_no"] is None) or (
                    QuerySet1[i]["Bank_Acc_no"] == ""
            ):
                QuerySet9["BankAccountNumber"] = None
            else:
                QuerySet9["BankAccountNumber"] = QuerySet1[i]["Bank_Acc_no"]

            if (QuerySet1[i]["Statement_Text"] is None) or (
                    QuerySet1[i]["Statement_Text"] == ""
            ):
                QuerySet9["StatementText"] = "NA"
            else:
                QuerySet9["StatementText"] = QuerySet1[i]["Statement_Text"]

            QuerySet8["FreeFormNumber"] = QuerySet1[i]["Fax"]
            QuerySet2["BillAddr"] = QuerySet3
            QuerySet2["PrimaryPhone"] = QuerySet4
            QuerySet2["Mobile"] = QuerySet4
            QuerySet2["PrimaryEmailAddr"] = QuerySet6
            QuerySet2["WebAddr"] = QuerySet7
            QuerySet2["Fax"] = QuerySet8

            if QuerySet9["BankAccountName"] is None:
                QuerySet9.pop("BankAccountName")
            if QuerySet9["BankBranchIdentifier"] is None:
                QuerySet9.pop("BankBranchIdentifier")
            if QuerySet9["BankAccountNumber"] is None:
                QuerySet9.pop("BankAccountNumber")
            if QuerySet9["StatementText"] is None:
                QuerySet9.pop("StatementText")

            if len(QuerySet9) == 0:
                pass
            elif len(QuerySet9) == 4:
                QuerySet2["VendorPaymentBankDetail"] = QuerySet9


            post_data_in_qbo(url, headers, json.dumps(QuerySet2),supplier_data,_id,job_id,task_id, QuerySet1[i]['CompanyName'])
            
    except Exception as ex:
        traceback.print_exc()
        
