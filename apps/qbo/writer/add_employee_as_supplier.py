import json
import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_employee_as_supplier(job_id):
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        url = f"{base_url}/vendor?minorversion=40"
        employee_data = db["employee"]

        x = employee_data.find({"job_id":job_id})

        data = []
        for k in x:
            data.append(k)

        QuerySet1 = data

        for i in range(0, len(QuerySet1)):

            QuerySet7 = {}
            QuerySet8 = {}
            QuerySet9 = {}

            # if QuerySet1[i]['BSB'] is not None:
            #     QuerySet2['AcctNum'] = QuerySet1[i]['BSB'] + " " + QuerySet1[i]['Bank_Acc_no']
            # else:
            #     QuerySet2['AcctNum'] = QuerySet1[i]['Bank_Acc_no']
            # QuerySet2['TaxIdentifier'] = QuerySet1[i]['ABN']

            if (
                    QuerySet1[i]["Addresses"][0]["Website"] is None
                    or QuerySet1[i]["Addresses"][0]["Website"] == ""
            ):
                QuerySet7["URI"] = "https://google.com"
            else:
                if QuerySet1[i]["Addresses"][0]["Website"].startswith(
                        "https://"
                ) or QuerySet1[i]["Addresses"][0]["Website"].startswith("http://"):
                    QuerySet7["URI"] = QuerySet1[i]["Website"]
                else:
                    QuerySet7["URI"] = "https://" + QuerySet1[i]["Website"]

            # if (QuerySet1[i]['Bank_Acc_Name'] == None) or (QuerySet1[i]['Bank_Acc_Name'] == ""):
            #     QuerySet9['BankAccountName'] = None
            # else:
            #     QuerySet9['BankAccountName'] = QuerySet1[i]['Bank_Acc_Name']

            # if (QuerySet1[i]['BSB']== None) or (QuerySet1[i]['BSB']==""):
            #     QuerySet9['BankBranchIdentifier']=None
            # else:
            #     QuerySet9['BankBranchIdentifier'] = QuerySet1[i]['BSB']

            # if (QuerySet1[i]['Bank_Acc_no']== None) or (QuerySet1[i]['Bank_Acc_no']==""):
            #     QuerySet9['BankAccountNumber']=None
            # else:
            #     QuerySet9['BankAccountNumber'] = QuerySet1[i]['Bank_Acc_no']

            # if (QuerySet1[i]['Statement_Text']== None) or (QuerySet1[i]['Statement_Text']==""):
            #     QuerySet9['StatementText']= 'NA'
            # else:
            #     QuerySet9['StatementText'] = QuerySet1[i]['Statement_Text']

            QuerySet8["FreeFormNumber"] = QuerySet1[i]["Addresses"][0]["Fax"]
            QuerySet2 = {"CompanyName": QuerySet1[i]["Company_Name"], "GivenName": QuerySet1[i]["FirstName"],
                         "FamilyName": QuerySet1[i]["LastName"], "DisplayName": QuerySet1[i]["Company_Name"],
                         "PrintOnCheckName": QuerySet1[i]["Company_Name"][0:110],
                         "BillAddr": {"Line1": QuerySet1[i]["Addresses"][0]["Street"],
                                      "City": QuerySet1[i]["Addresses"][0]["City"],
                                      "Country": QuerySet1[i]["Addresses"][0]["Country"],
                                      "PostalCode": QuerySet1[i]["Addresses"][0]["PostCode"],
                                      "CountrySubDivisionCode": QuerySet1[i]["Addresses"][0]["State"]},
                         "PrimaryPhone": {"FreeFormNumber": QuerySet1[i]["Addresses"][0]["Phone1"]},
                         "Mobile": {"FreeFormNumber": QuerySet1[i]["Addresses"][0]["Phone1"]},
                         "PrimaryEmailAddr": {"Address": QuerySet1[i]["Addresses"][0]["Email"]},
                         "WebAddr": QuerySet7, "Fax": QuerySet8}

            # if QuerySet9['BankAccountName'] == None:
            #     QuerySet9.pop('BankAccountName')
            # if QuerySet9['BankBranchIdentifier'] ==None:
            #     QuerySet9.pop('BankBranchIdentifier')
            # if QuerySet9['BankAccountNumber'] ==None:
            #     QuerySet9.pop('BankAccountNumber')
            # if QuerySet9['StatementText'] ==None:
            #     QuerySet9.pop('StatementText')

            # if len(QuerySet9)==0:
            #     pass
            # elif len(QuerySet9) == 4:
            #     QuerySet2['VendorPaymentBankDetail'] = QuerySet9
            # else:
            #     pass

            post_data_in_qbo(
                url,
                headers,
                json.dumps(QuerySet2),
                job_id,
                QuerySet1[i]["Company_Name"] if QuerySet1[i][
                                                    "Company_Name"] is not None else f'{QuerySet1[i]["FirstName"]} {QuerySet1[i]["LastName"]}'
            )
    except Exception as ex:
        traceback.print_exc()
        
